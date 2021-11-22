# -*- coding:utf-8 -*-
"""
    cpu.py
    ~~~~~~~~
    CPU 数据汇聚/报警插件

    :author: kerrygao, Fufu, 2021/6/10
    :update: Fufu, 2021/11/17 报警优先级: 系统 1 分钟内负载 > CPU 总使用率 > CPU 单核使用率
"""
from . import AggsPlugin


class Cpu(AggsPlugin):
    """CPU 数据汇聚/报警"""

    name = 'cpu'

    async def alarm(self, metric):
        """CPU 报警"""
        alarm_conf = self.get_plugin_conf_value('alarm', {})
        if not alarm_conf:
            return

        loadavg_precent_1 = metric.get('loadavg_precent_1', -0.1)
        conf_loadavg_precent_1 = self.get_plugin_conf_value('alarm|loadavg_precent_1', -0.1)
        if loadavg_precent_1 >= conf_loadavg_precent_1 >= 0.0:
            self.put_alarm_metric(f'系统平均负载过高(%): {loadavg_precent_1}>={conf_loadavg_precent_1}')
            return

        percent = metric.get('percent', -0.1)
        conf_percent = self.get_plugin_conf_value('alarm|percent', -0.1)
        if percent >= conf_percent >= 0.0:
            self.put_alarm_metric(f'CPU 总使用率过高(%): {percent}>={conf_percent}')
            return

        max_percent = metric.get('max_percent', -0.1)
        conf_max_percent = self.get_plugin_conf_value('alarm|max_percent', -0.1)
        if max_percent >= conf_max_percent >= 0.0:
            self.put_alarm_metric(f'CPU 单核使用率过高(%): {max_percent}>={conf_max_percent}')
            return
