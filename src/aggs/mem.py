# -*- coding:utf-8 -*-
"""
    mem.py
    ~~~~~~~~
    内存/报警插件

    :author: kerrygao, Fufu, 2021/6/7
"""
from . import AggsPlugin


class Mem(AggsPlugin):
    """内存报警"""

    name = 'mem'

    async def alarm(self, metric):
        """内存报警"""
        conf_percent = self.get_plugin_conf_value('alarm|percent', 0.0)
        mem_percent = metric.get('percent')
        mem_percent >= conf_percent and self.put_alarm_metric(f'内存占用率过高(%): {mem_percent}>={conf_percent}')
