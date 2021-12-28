# -*- coding:utf-8 -*-
"""
    network.py
    ~~~~~~~~
    网络信息汇聚/报警插件

    :author: Fufu, 2021/12/24 重构代码, 增加集群 IP 报警
"""
from . import AggsPlugin
from ..libs.helper import get_dict_value
from ..libs.metric import Metric


class Network(AggsPlugin):
    """网络/报警"""

    name = 'network'

    # 存储上一时间的网卡 IP
    last_ips = {}

    async def alarm(self, metric: Metric) -> Metric:
        """报警"""
        nic = metric.get('nic')
        alarm_conf = self.get_plugin_conf_value(f'alarm|{nic}', {})
        if not alarm_conf:
            return metric

        nic = metric.get('nic')
        more = get_dict_value(alarm_conf, 'comment', '')

        self.alarm_in_out(metric, alarm_conf, nic, more)
        self.alarm_vip(metric, alarm_conf, nic, more)

        return metric

    def alarm_in_out(self, metric: Metric, alarm_conf: dict, nic: str, more: str = '') -> None:
        """流入流出带宽报警"""
        # 流入带宽报警
        kbps_in_limit = get_dict_value(alarm_conf, 'kbps_in', -0.1)
        if kbps_in_limit >= 0:
            kbps_in = metric.get('kbps_in', 0.0)
            if kbps_in >= kbps_in_limit:
                self.put_alarm_metric(f'{nic} 流入带宽(kbps): {kbps_in}>{kbps_in_limit}', more=more)

        # 流出带宽报警
        kbps_out_limit = get_dict_value(alarm_conf, 'kbps_out', -0.1)
        if kbps_out_limit >= 0:
            kbps_out = metric.get('kbps_out', 0.0)
            if kbps_out >= kbps_out_limit:
                self.put_alarm_metric(f'{nic} 流出带宽(kbps): {kbps_out}>{kbps_out_limit}', more=more)

    def alarm_vip(self, metric: Metric, alarm_conf: dict, nic: str, more: str = '') -> None:
        """集群漂移 IP 报警"""
        vip = get_dict_value(alarm_conf, 'vip', {})
        if vip:
            nic_ips = {}
            for v, ip in vip.items():
                now_ips = metric.get(v, '').split(',')
                last_ips = get_dict_value(self.last_ips, f'{nic}|{v}', [])
                if last_ips:
                    in_last = ip in last_ips
                    in_now = ip in now_ips
                    flag = metric.get('timestamp')
                    if in_last and not in_now:
                        self.put_alarm_metric(f'{nic} 减少 IP: {ip}', data={'alarm_flag': f'vip_dec_{flag}'}, more=more)
                    elif in_now and not in_last:
                        self.put_alarm_metric(f'{nic} 增加 IP: {ip}', data={'alarm_flag': f'vip_inc_{flag}'}, more=more)
                nic_ips[v] = now_ips
            self.last_ips[nic] = nic_ips
