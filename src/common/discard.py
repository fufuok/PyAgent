# -*- coding:utf-8 -*-
"""
    discard.py
    ~~~~~~~~
    数据项丢弃公共插件

    :author: Fufu, 2021/11/29
"""
from . import Common
from ..libs.helper import get_dict_value
from ..libs.metric import Metric


class Discard(Common):
    """类型转换处理"""

    async def run(self) -> Metric:
        """数据项丢弃"""
        if not self.plugin_conf:
            return self.metric

        metric_tag = self.metric.get('tag')

        # 优先使用指定 tag 项的配置
        discard_fields = get_dict_value(self.plugin_conf, metric_tag, [])

        if not discard_fields and metric_tag not in get_dict_value(self.plugin_conf, 'all_except', []):
            discard_fields = get_dict_value(self.plugin_conf, 'all', [])

        discard_fields and self.metric.delete(discard_fields)

        return self.metric
