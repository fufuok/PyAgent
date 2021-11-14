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
        conf_percent = self.get_plugin_conf_value('alarm|percent', -0.1)
        if n <= 0 or m <= 0 or conf_percent < 0:
            return

        # CPU 占用率
        self.n_minute_data.append(metric.get('cpu_percent'))
        if len(self.n_minute_data) < n:
            return

        data = self.n_minute_data[-n:]
        alarm_data = list(filter(lambda x: x >= conf_percent, data))

        # n 分钟内有 m 次 cpu 占用率达到 percent% 报警
        len(alarm_data) >= m and self.put_alarm_metric(f'CPU 占用率过高(%): {max(alarm_data)}>={conf_percent}')
