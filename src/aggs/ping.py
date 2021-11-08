# -*- coding:utf-8 -*-
"""
    ping.py
    ~~~~~~~~
    网络延迟报警

    :author: kerrygao, Fufu, 2021/6/21
"""
from . import AggsPlugin


class Ping(AggsPlugin):
    """ping 网络延迟报警"""

    name = 'ping'

    async def alarm(self, metric):
        """ping 网络延迟报警"""
        alarm_conf = self.get_plugin_conf_value('alarm', {})
        if not alarm_conf:
            return

        target = metric.get('address')
        tag = metric.get('tag')

        average = self.get_plugin_conf_ab_value([f'alarm|target|{tag}|average', 'alarm|average'], -0.1)
        loss = self.get_plugin_conf_ab_value([f'alarm|target|{tag}|loss', 'alarm|loss'], -0.1)
        maximum = self.get_plugin_conf_ab_value([f'alarm|target|{tag}|maximum', 'alarm|maximum'], -0.1)

        if metric.get('loss', -1.1) >= loss >= 0:
            self.put_alarm_metric(f'{tag} 丢包比例过高(%): {metric.get("loss")}>={loss}', more=target)

        elif metric.get('average', -1.1) >= average >= 0:
            self.put_alarm_metric(f'{tag} 平均延迟过高(ms): {metric.get("average")}>={average}', more=target)

        elif metric.get('maximum', -1.1) >= maximum >= 0:
            self.put_alarm_metric(f'{tag} 最大延迟过高(ms): {metric.get("maximum")}>={maximum}', more=target)
