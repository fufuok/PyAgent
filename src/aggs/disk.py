# -*- coding:utf-8 -*-
"""
    disk.py
    ~~~~~~~~
    磁盘/报警插件

    :author: kerrygao, Fufu, 2021/6/7
"""
from . import AggsPlugin


class Disk(AggsPlugin):
    """磁盘报警"""

    name = 'disk'

    async def alarm(self, metric):
        """磁盘报警"""
        alarm_conf = self.get_plugin_conf_value('alarm', {})
        if not alarm_conf:
            return

        percent_disk = metric.get('percent', 0)
        if percent_disk == 0:
            return

        # 报警盘符
        disk_symbol = alarm_conf.get('disk_symbol', {})
        device = metric.get('device').replace(':\\', '').lower()

        # 磁盘使用率报警阈值, 没有配置则取默认阈值
        percent_conf = self.get_plugin_conf_ab_value([f'alarm|disk_symbol|{device}|percent', 'alarm|percent'], -0.1)

        # 无指定盘符配置时, 针对所有盘符报警
        if (not disk_symbol or device in [disk.lower() for disk in disk_symbol]) \
                and percent_disk >= percent_conf:
            self.put_alarm_metric(f'磁盘 {device} 占用率高(%): {percent_disk}>={percent_conf}')
