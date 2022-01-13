# -*- coding:utf-8 -*-
"""
    ping.py
    ~~~~~~~~
    ping - 数据包

    :author: kerrygao, Fufu, 2021/6/21
"""
from asyncio import ensure_future

from . import InputPlugin
from ..libs.helper import get_dict_value
from ..libs.metric import Metric
from ..libs.net import pyping


class Ping(InputPlugin):
    """Ping 网络检测"""

    # 模块名称
    name = 'ping'

    async def gather(self) -> None:
        """获取数据(允许堆叠)"""
        await self.perf_gather()

    async def run_gather(self) -> None:
        """获取数据"""
        # 注意: 以下 3 个参数要尽量确定在一个时间间隔内执行完毕, 否则会堆叠任务
        # PING 多少次
        count = self.get_plugin_conf_value('count', 60)
        # 每次 PING 多少时间超时 (秒)
        timeout = self.get_plugin_conf_value('timeout', 0.7)
        # 每次 PING 时间间隔 (秒)
        interval_ping = self.get_plugin_conf_value('interval_ping', 0.1)

        tasks = []
        for tag, conf in self.get_plugin_conf_value('target', {}).items():
            address = get_dict_value(conf, 'address', '').strip()
            tasks.append(ensure_future(self.run_ping(address, tag, count, timeout, interval_ping)))

        # 等待任务执行
        tasks and await self.run_tasks(tasks)

    async def run_ping(
            self,
            address: str,
            tag: str,
            count: int,
            timeout: int,
            interval: float,
    ) -> Metric:
        """执行检测并发送结果"""
        ret = await pyping(address, count, timeout, interval)
        ret.update({
            "tag": tag,
            "address": address
        })
        metric = self.metric(ret)
        return metric
