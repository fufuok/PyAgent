# -*- coding:utf-8 -*-
"""
    config.py
    ~~~~~~~~

    :author: Fufu, 2021/6/9
"""
import os
import os.path
import sys
import time
from hashlib import md5
from typing import Any, Callable, Union

from envcrypto import get_environ, set_environ
from loguru import logger
from yaml import safe_dump, safe_load

from .plugins import PLUGINS
from ..libs.helper import extend_dict, get_dict_value, get_hash
from ..libs.net import request


class Config:
    """系统配置"""
    debug = False
    reload_sec = 300
    windows = os.name == 'nt'

    # 主配置
    main = {}

    # 服务器信息
    info = {}

    # 插件配置
    input = {}
    processor = {}
    aggs = {}
    output = {}

    # 插件集
    plugins = {}

    # 工作中, 公共的, 开启的插件名称
    plugins_working = set()
    plugins_common = set()
    plugins_open = set()

    # 模块
    modules = ['input', 'processor', 'aggs', 'output', 'common']

    # 日志配置签名
    _logger_conf_md5 = ''

    def __init__(self) -> None:
        # 运行根目录
        self.root_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        # 脚本文件根目录
        self.src_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        # 配置文件目录
        self.etc_dir = os.path.join(self.root_dir, 'etc')

        # 初始化配置
        self.reload()

        # 初始化插件(扫描目录, 自动发现)
        # self.plugins = {x: self.get_plugins(x) for x in self.modules}
        # 初始化插件(打包使用, 需要静态注册到 plugins.py)
        self.plugins = PLUGINS

    async def update(self) -> None:
        """从配置中心获取并更新 main.yaml, host.yaml"""
        update_api = self.get_conf_value('main|update_api', '').strip()
        if not update_api:
            return

        # 配置获取方法和接口需要自定义, 以下是简单 token POST 请求 API 示例: token=md5(timestamp+api_key)
        # 推荐的 token 加密方案:
        # 先加密 API 请求密钥并写入系统环境变量
        # Windows: set PYAGENT_CONFIG_API_KEY=*****
        # Linux: export PYAGENT_CONFIG_API_KEY=*****
        # 加密方法如下, 用 encrypted 的值替换上面 ***** 的内容:
        # encrypted = set_environ('tmp', '您的TOKEN值-Test', '自定义的加密密钥')
        # print(f'export PYAGENT_CONFIG_API_KEY={encrypted}')
        # 如: Linux 里执行: export PYAGENT_CONFIG_API_KEY=bbM1VU6LkCDM3pV67ELEBDvgH4YTkeoaBypVQhJYUuzwvZ
        # 程序里使用下面的代码解密后使用
        api_key = get_environ('PYAGENT_CONFIG_API_KEY', '自定义的加密密钥')
        timestamp = int(time.time())
        token = get_hash(f'{timestamp}{api_key}')

        new_conf = await request(f'{update_api}?time={timestamp}&token={token}')

        main_conf = get_dict_value(new_conf, 'data|main', {})
        host_conf = get_dict_value(new_conf, 'data|host', {})
        if not main_conf:
            logger.warning(f'配置更新失败, 默认主配置有误: {new_conf.get("msg")}')
            return

        # 更新默认主配置文件
        self.dump_yaml_file(main_conf, os.path.join(self.etc_dir, 'main.yaml'))
        # 更新主机配置文件
        self.dump_yaml_file(host_conf, os.path.join(self.etc_dir, 'host.yaml'))

    def reload(self) -> None:
        """
        重新加载所有配置
        配置优先级: 各插件目录(input/processor/aggs/output) > host.yaml > main.yaml
        """
        # 加载主配置
        main = self.load_yaml_file(os.path.join(self.etc_dir, 'main.yaml'))
        if not main or get_dict_value(main, 'interval', 0) <= 0:
            logger.warning('配置加载失败, 默认主配置有误')
            return

        # 加载主机个性化主配置
        host = self.load_yaml_file(os.path.join(self.etc_dir, 'host.yaml'))

        # 扩展合并主配置
        self.main = extend_dict(main, host)

        self.debug = self.get_conf_value('main|debug', False)
        self.info = self.get_conf_value('main|info', {})
        self.reload_sec = max(self.get_conf_value('main|reload_sec', 300), 10)
        self.plugins_open = get_dict_value(self.main, 'open', set())

        for module in self.modules:
            conf = {'default': {}}
            # 主配置中的公共插件
            plugins_common = get_dict_value(self.main, f'common_{module}', set())
            self.plugins_common.update(plugins_common)
            # 开启的插件 + 公共插件
            plugins = plugins_common | self.plugins_open
            for name in plugins:
                # 初始化插件配置
                conf.update({name: {}})
                # 主配置中的插件配置
                main_plugin_conf = self.get_conf_value(f'main|{module}|{name}', {})
                main_plugin_conf and isinstance(main_plugin_conf, dict) and conf[name].update(main_plugin_conf)
                # 插件配置文件
                plugin_conf = self.get_conf(module, name)
                plugin_conf and conf[name].update(plugin_conf)
            setattr(self, module, conf)

        # 初始化日志
        self.init_logger()

    def get_conf_value(
            self,
            key_path: str,
            default: Any = None,
            *,
            fix_type: bool = True
    ) -> Any:
        """
        按路径字符串获取配置项值
        默认转换为默认值相同类型, None 除外

        :param key_path: str, e.g. input|demo|interval
        :param default:
        :param fix_type: 是否强制修正为 default 相同类型
        :return:
        """
        keys = key_path.split('|')
        if not hasattr(self, keys[0]):
            return default

        # 配置项: self.main, self.input...
        dt = getattr(self, keys[0])

        if len(keys) == 1:
            return dt

        value = dt
        for key in keys[1:]:
            try:
                value = value.get(key, None)
                if value is None:
                    return default
            except Exception:
                return default

        if fix_type:
            return self.get_same_type(default, value)

        return value

    @staticmethod
    def get_same_type(src: Any, dst: Any) -> Any:
        """将 dst 的类型转换为 src 相同的类型"""
        if src is None:
            return dst

        if isinstance(src, bool):
            return str(dst) in ('1', 't', 'T', 'true', 'TRUE', 'True')

        try:
            return type(src)(dst)
        except Exception:
            return src

    def get_conf(
            self, conf_module: str, conf_name: str
    ) -> dict:
        """按模块和名称获取配置"""
        return self.load_yaml_file(os.path.join(self.etc_dir, conf_module, f'{conf_name}.yaml'))

    @staticmethod
    def dump_yaml_file(data: dict, yaml_file: str) -> Union[str, bytes]:
        """写入 YAML 配置文件"""
        try:
            with open(yaml_file, 'w', encoding='utf-8') as f:
                return safe_dump(data, f, allow_unicode=True)
        except Exception as e:
            logger.warning(f'配置文件写入失败: {e}')
            return ''

    @staticmethod
    def load_yaml_file(yaml_file: str) -> dict:
        """读取 YAML 配置文件"""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                conf = safe_load(f)
                return conf if isinstance(conf, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def load_yaml(yaml_conf: str) -> dict:
        """读取 YAML 配置"""
        try:
            conf = safe_load(yaml_conf)
            return conf if isinstance(conf, dict) else {}
        except Exception:
            return {}

    def get_plugin_obj(
            self, module: str, name: str, default: Any = None
    ) -> Callable:
        """获取插件对象"""
        return self.plugins.get(module, {}).get(name, default)

    def get_plugins(self, module: str) -> dict:
        """获取插件列表"""
        plugins = {}
        path = os.path.join(self.src_dir, module)
        for _, _, files in os.walk(path):
            for f in files:
                name, ext = os.path.splitext(f)
                cls_name = name.title()
                if ext == '.py':
                    mod = __import__(f'src.{module}.{name}', fromlist=[__name__])
                    hasattr(mod, cls_name) and plugins.update({name: getattr(mod, cls_name)})

        return plugins

    def init_logger(self) -> None:
        """初始化日志"""
        logger_conf_md5 = md5('{}.{}'.format(self.get_conf_value('main|log'), self.debug).encode()).hexdigest()
        if logger_conf_md5 == self._logger_conf_md5:
            return

        self._logger_conf_md5 = logger_conf_md5
        logger.remove()

        if self.debug:
            # 控制台日志
            logger.add(
                sys.stderr,
                level='DEBUG',
                format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
                       '<level>{level}</level> | '
                       '<cyan>{name}</cyan>.<cyan>{function}</cyan>:<cyan>{line}</cyan> | '
                       '<level>{message}</level>',
            )

        # 文件日志
        logger.add(
            self.get_conf_value('main|log|file', os.path.join(self.root_dir, 'log', 'pyagent.log')),
            level=self.get_conf_value('main|log|level', 'INFO'),
            rotation=self.get_conf_value('main|log|rotation', '50 MB'),
            retention=self.get_conf_value('main|log|retention', '10 days'),
            compression=self.get_conf_value('main|log|compression', 'zip'),
            format=self.get_conf_value('main|log|format',
                                       '{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}.{function}:{line} | {message}'),
            enqueue=True,
        )
        logger.debug('日志初始化完成')

    def __str__(self) -> str:
        return str(self.__dict__)
