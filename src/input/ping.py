# -*- coding:utf-8 -*-
"""
    ping.py
    ~~~~~~~~
    ping - 数据包

    :author: kerrygao, Fufu, 2021/6/21
"""
from asyncio import create_task

from . import InputPlugin
from ..libs.helper import get_dict_value
from ..libs.net import pyping


class Ping(InputPlugin):
    """Ping 网络检测"""

    # 模块名称
    name = 'ping'

    async def gather(self) -> None:
        """获取数据"""
        # PING 多少次
        count = self.get_plugin_conf_value('count', 60)
        # 每次 PING 多少时间超时 (秒)
        timeout = self.get_plugin_conf_value('timeout', 0.7)
        # 每次 PING 时间间隔 (秒)
        interval_ping = self.get_plugin_conf_value('interval_ping', 0.1)

        for tag, conf in self.get_plugin_conf_value('target', {}).items():
            address = get_dict_value(conf, 'address', '').strip()
            address and create_task(self.put_metric(address, tag, count, timeout, interval_ping))

    async def put_metric(
            self,
            address: str,
            tag: str,
            count: int,
            timeout: int,
            interval: float,
    ) -> None:
        """执行检测并发送结果"""
        ret = await pyping(address, count, timeout, interval)
        ret.update({
            "tag": tag,
            "address": address
        })
        metric = self.metric(ret)
        self.out_queue.put_nowait(metric)
