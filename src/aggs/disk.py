# -*- coding:utf-8 -*-
"""
    disk.py
    ~~~~~~~~
    磁盘/报警插件

    :author: kerrygao, Fufu, 2021/6/7
"""
from . import AggsPlugin
from ..libs.metric import Metric


class Disk(AggsPlugin):
    """磁盘报警"""

    name = 'disk'

    async def alarm(self, metric: Metric) -> Metric:
        """磁盘报警"""
        alarm_conf = self.get_plugin_conf_value('alarm', {})
        if not alarm_conf:
            return metric

        disk_percent = metric.get('percent', 0)
        if disk_percent == 0:
            return metric

        # 报警盘符
        disk_symbol = alarm_conf.get('disk_symbol', {})
        mountpoint = metric.get('mountpoint').replace(':\\', '').lower()

        # 磁盘使用率报警阈值, 没有配置则取默认阈值
        conf_percent = self.get_plugin_conf_ab_value([f'alarm|disk_symbol|{mountpoint}|percent', 'alarm|percent'], -0.1)
        if conf_percent < 0:
            return metric

        # 无指定盘符配置时, 针对所有盘符报警
        if (not disk_symbol or mountpoint in [disk.lower() for disk in disk_symbol]) \
                and disk_percent >= conf_percent:
            self.put_alarm_metric(f'磁盘 {mountpoint} 占用率高(%): {disk_percent}>={conf_percent}')

        return metric
