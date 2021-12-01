# -*- coding:utf-8 -*-
"""
    discard.py
    ~~~~~~~~
    数据项丢弃公共插件

    :author: Fufu, 2021/11/29
"""
from . import Common
from ..libs.metric import Metric


class Discard(Common):
    """类型转换处理"""

    async def run(self) -> Metric:
        """数据项丢弃"""
        for tag, fields in self.plugin_conf.items():
            if fields and isinstance(fields, list) and (tag == 'all' or tag == self.metric.get('tag')):
                self.metric.delete(fields)

        return self.metric
