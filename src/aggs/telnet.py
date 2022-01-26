# -*- coding:utf-8 -*-
"""
    telnet.py
    ~~~~~~~~
    Telnet 数据汇聚/报警插件

    :author: Fufu, 2021/6/16
"""
from . import AggsPlugin
from ..libs.metric import Metric


class Telnet(AggsPlugin):
    """Telnet 数据汇聚/报警"""

    name = 'telnet'

    async def alarm(self, metric: Metric) -> Metric:
        """报警"""
        if not self.get_plugin_conf_value('alarm'):
            return metric

        # 待报警标识
        tags = [] if self.get_plugin_conf_value('alarm|all') else self.get_plugin_conf_value('alarm|target', [])

        # 数据中的 tag
        tag = metric.get('tag')
        if tag and (not tags or tag in tags) and not metric.get('yes'):
            self.put_alarm_metric('{} - Telnet 端口不通'.format(tag), tag=tag, more=metric.get('address'))

        return metric
