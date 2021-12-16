# -*- coding:utf-8 -*-
"""
    plugin.py
    ~~~~~~~~
    插件基类

    :author: Fufu, 2021/6/9
"""
import functools
import json
from abc import ABC, abstractmethod
from asyncio import Queue, events
from contextvars import copy_context
from typing import Any, List, Optional, Tuple, Union

from .fn import gen_data_fn
from .metric import Metric


class RootPlugin(ABC):
    """插件基类"""

    # 模块名称, 如: input, aggs, processor, output
    module = ''

    # 插件名称, 如: cpu, console, default
    name = ''

    # 别名, 指当前实例代表哪个插件
    alias = ''

    def __init__(self, conf: Any) -> None:
        # 插件配置
        self.conf = conf
        # 生成数据函数集
        self.gen_data_fn = gen_data_fn()

    @abstractmethod
    async def run(self) -> None:
        """插件启动方法"""
        pass

    def get_interval(self, default: int = 60) -> int:
        """
        特殊参数, 时间间隔(秒)
        优先级: 插件配置 > 系统配置 > 默认值

        :param default:
        :return:
        """
        interval = self.get_plugin_conf_value('interval', 0)
        if interval < 1:
            interval = self.conf.get_conf_value('main|interval', default)

        return default if interval < 1 else interval

    def get_conf_value(
            self,
            key_path: str,
            default: Any = None,
            *,
            fix_type: bool = True
    ) -> Any:
        """
        按路径字符串获取配置项值(优先: 当前插件配置项 > 主配置项)
        默认转换为默认值相同类型, None 除外

        :param key_path:
        :param default:
        :param fix_type: 是否强制修正为 default 相同类型
        :return:
        """
        value = self.get_plugin_conf_value(key_path)
        if not value:
            value = self.conf.get_conf_value(f'main|{key_path}', default, fix_type=False)

        if fix_type:
            return self.conf.get_same_type(default, value)

        return value

    def get_plugin_conf_value(
            self,
            key_path: str = '',
            default: Any = None,
            *,
            fix_type: bool = True
    ) -> Any:
        """
        按路径字符串获取配置项值(仅当前插件配置项)
        默认转换为默认值相同类型, None 除外

        :param key_path: str, e.g. auth.token
        :param default:
        :param fix_type: 是否强制修正为 default 相同类型
        :return:
        """
        if key_path == '':
            return self.conf.get_conf_value(f'{self.module}|{self.name}', {}, fix_type=True)

        return self.conf.get_conf_value(f'{self.module}|{self.name}|{key_path}', default, fix_type=fix_type)

    def get_plugin_conf_ab_value(
            self,
            key_path_ab: Union[List, Tuple],
            default: Any = None,
            *,
            fix_type: bool = True
    ) -> Any:
        """
        按路径字符串获取配置项值(仅当前插件配置项)
        路径 A 不存在或为空则继续下一个路径获取
        默认转换为默认值相同类型, None 除外

        :param key_path_ab:
        :param default:
        :param fix_type: 是否强制修正为 default 相同类型
        :return:
        """
        for key_path in key_path_ab:
            value = self.get_plugin_conf_value(key_path, fix_type=False)
            if value:
                if fix_type:
                    return self.conf.get_same_type(default, value)
                return value

        return default

    def metric(
            self,
            data: Optional[dict] = None,
            *,
            tag: str = 'metric',
            info: Optional[dict] = None,
    ) -> Metric:
        """生成 Metric 数据对象, 附带服务器标识信息"""
        return Metric(self.name, data, tag=tag, info=info if isinstance(info, dict) else self.conf.info)

    async def use_common_plugin(self, metric: Metric, key_path: str = '') -> Metric:
        """根据配置调用同模块插件"""
        for key, plugin_conf in self.get_plugin_conf_value(key_path, {}).items():
            if key.startswith('use_plugin_'):
                plugin_name = key.split('use_plugin_', 1)[1]
                if not plugin_name:
                    continue

                plugin_cls = self.conf.get_plugin_obj('common', plugin_name)
                if not plugin_cls:
                    continue

                metric = await plugin_cls(self.conf, self.module, self.name, metric, plugin_conf).run()

        return metric

    @staticmethod
    def metrics_as_dict(metrics: List[Metric]) -> List[dict]:
        """指标数据列表转为字典"""
        return [m.as_dict for m in metrics] if metrics else []

    @staticmethod
    def metrics_as_json(metrics: List[Metric]) -> str:
        """指标数据列表转为 JSON"""
        return json.dumps(BasePlugin.metrics_as_dict(metrics)) if metrics else ''

    def use_func_data(self, conf_func: List[str], data: Optional[dict] = None) -> dict:
        """根据配置执行数据项生成函数"""
        data = data if isinstance(data, dict) else {}
        for c in conf_func:
            c = str(c)
            fn_args = c.split(',,')
            fn = self.gen_data_fn.get(fn_args[0])
            if not fn:
                continue

            args = fn_args[1:] if len(fn_args) > 1 else []
            try:
                res = fn(*args)
            except Exception as e:
                # 异常时把函数名作为参数传递(以便调试)
                res = {c: str(e)}

            # 合并数据项
            data.update(res)

        return data

    @staticmethod
    async def to_thread(func, /, *args, **kwargs):
        """
        来自于 python3.9+ asyncio.to_thread, 在协程中异步执行阻塞事件

        Asynchronously run function *func* in a separate thread.

        Any *args and **kwargs supplied for this function are directly passed
        to *func*. Also, the current :class:`contextvars.Context` is propagated,
        allowing context variables from the main thread to be accessed in the
        separate thread.

        Return a coroutine that can be awaited to get the eventual result of *func*.
        """
        loop = events.get_running_loop()
        ctx = copy_context()
        func_call = functools.partial(ctx.run, func, *args, **kwargs)
        return await loop.run_in_executor(None, func_call)


class BasePlugin(RootPlugin, ABC):
    """插件基类(队列)"""

    def __init__(self, conf: Any, in_queue: Optional[Queue], out_queue: Optional[Queue]) -> None:
        super().__init__(conf)

        # 数据队列
        self.in_queue = in_queue
        self.out_queue = out_queue
