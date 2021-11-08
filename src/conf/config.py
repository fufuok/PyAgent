# -*- coding:utf-8 -*-
"""
    config.py
    ~~~~~~~~

    :author: Fufu, 2021/6/9
"""
import os
import os.path
import sys
from hashlib import md5
from typing import Any, Callable

from loguru import logger
from yaml import safe_load

from .plugins import PLUGINS


class Config:
    """系统配置"""
    debug = False
    reload_sec = 60
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

    def reload(self) -> None:
        """重新加载所有配置"""
        self.main = self.get_yaml_file(os.path.join(self.etc_dir, 'main.yaml'))
        self.debug = self.get_conf_value('main|debug', False)
        self.info = self.get_conf_value('main|info', {})
        self.reload_sec = self.get_conf_value('main|reload_sec', 60)

        for module in self.modules:
            conf = {'default': {}}
            # 开启的插件 + 主配置中可能的公共插件
            plugins = set(self.main.get('open', []) + self.main.get(f'common_{module}', []))
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
        return self.get_yaml_file(os.path.join(self.etc_dir, conf_module, f'{conf_name}.yaml'))

    @staticmethod
    def get_yaml_file(yaml_file: str) -> dict:
        """读取 YAML 配置文件"""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                conf = Config.get_yaml(f.read())
                return conf if isinstance(conf, dict) else {}
        except Exception:
            return {}

    @staticmethod
    def get_yaml(yaml_conf: str) -> dict:
        """读取 YAML 配置"""
        try:
            conf = safe_load(yaml_conf)
            return conf if conf else {}
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
