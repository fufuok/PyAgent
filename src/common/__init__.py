# -*- coding:utf-8 -*-
"""
    __init__.py
    ~~~~~~~~

    :author: Fufu, 2021/11/29
"""
from abc import ABC
from typing import Optional

from ..libs.metric import Metric
from ..libs.plugin import RootPlugin


class Common(RootPlugin, ABC):
    """公共插件"""

    def __init__(
            self,
            conf,
            module: str,
            name: str,
            metric: Metric,
            plugin_conf: Optional[dict] = None,
    ) -> None:
        super().__init__(conf)

        # 调用时传入数据, 模块, 名称, 对应公共插件的配置
        self.metric = metric
        self.module = module
        self.name = name
        self.plugin_conf = plugin_conf if plugin_conf and isinstance(plugin_conf, dict) else {}
