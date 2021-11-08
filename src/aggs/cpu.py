# -*- coding:utf-8 -*-
"""
    cpu.py
    ~~~~~~~~
    CPU 数据汇聚/报警插件

    :author: kerrygao, Fufu, 2021/6/10
"""
from . import AggsPlugin


class Cpu(AggsPlugin):
    """CPU 数据汇聚/报警"""

    name = 'cpu'

    # N分钟内的数据
    n_minute_data = []

    async def alarm(self, metric):
        """报警"""
        n = self.get_plugin_conf_value('alarm|n', 0)
        m = self.get_plugin_conf_value('alarm|m', 0)
        percent = self.get_plugin_conf_value('alarm|percent', 0.0)
        if n <= 0 or m <= 0 or percent <= 0:
            return

        # CPU 占用率
        self.n_minute_data.append(metric.get('cpu_percent'))
        if len(self.n_minute_data) < n:
            return

        data = self.n_minute_data[-n:]
        new_data = list(filter(lambda x: x >= percent, data))

        # n 分钟内有 m 次 cpu 占用率达到 percent% 报警
        len(new_data) >= m and self.put_alarm_metric(f'CPU 占用率过高(%): >={percent}')
