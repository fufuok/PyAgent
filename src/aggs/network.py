# -*- coding:utf-8 -*-
"""
    cpu.py
    ~~~~~~~~
    CPU 数据汇聚/报警插件

    :author: kerrygao, Fufu, 2021/6/10
"""
from . import AggsPlugin
from ..libs.metric import Metric


class Network(AggsPlugin):
    """网络/报警"""

    name = 'network'

    async def alarm(self, metric: Metric) -> Metric:
        """报警"""
        # 网卡名
        nic = metric.get('nic')

        # 流入带宽报警
        kbps_in_limit = self.get_plugin_conf_value(f'alarm|{nic}|kbps_in', -0.1)
        if kbps_in_limit >= 0:
            kbps_in = metric.get('kbps_in', 0.0)
            if kbps_in >= kbps_in_limit:
                more = self.get_plugin_conf_value(f'alarm|{nic}|comment', '')
                self.put_alarm_metric(f'{nic} 流入带宽(kbps): {kbps_in}>{kbps_in_limit}', more=more)

        # 流出带宽报警
        kbps_out_limit = self.get_plugin_conf_value(f'alarm|{nic}|kbps_out', -0.1)
        if kbps_out_limit >= 0:
            kbps_out = metric.get('kbps_out', 0.0)
            if kbps_out >= kbps_out_limit:
                more = self.get_plugin_conf_value(f'alarm|{nic}|comment', '')
                self.put_alarm_metric(f'{nic} 流出带宽(kbps): {kbps_out}>{kbps_out_limit}', more=more)

        return metric
