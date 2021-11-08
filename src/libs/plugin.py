# -*- coding:utf-8 -*-
"""
    plugin.py
    ~~~~~~~~
    插件基类

    :author: Fufu, 2021/6/9
"""
import json
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple, Union

from .metric import Metric


class BasePlugin(ABC):
    """插件基类"""

    module = ''
    name = ''

    def __init__(self, conf: Any) -> None:
        self.conf = conf

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

    @staticmethod
    def metrics_as_dict(metrics: List[Metric]) -> List[dict]:
        """指标数据列表转为字典"""
        return [m.as_dict for m in metrics] if metrics else []

    @staticmethod
    def metrics_as_json(metrics: List[Metric]) -> str:
        """指标数据列表转为 JSON"""
        return json.dumps(BasePlugin.metrics_as_dict(metrics)) if metrics else ''
