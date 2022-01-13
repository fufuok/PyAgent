# -*- coding:utf-8 -*-
"""
    telnet.py
    ~~~~~~~~
    数据收集插件 - 端口检测

    :author: Fufu, 2021/6/16
"""
from asyncio import ensure_future
from typing import Union

from . import InputPlugin
from ..libs.helper import get_dict_value
from ..libs.metric import Metric
from ..libs.net import chk_port


class Telnet(InputPlugin):
    """端口检测数据收集插件"""

    # 模块名称
    name = 'telnet'

    async def gather(self) -> None:
        """获取数据(允许堆叠)"""
        await self.perf_gather()

    async def run_gather(self) -> None:
        """获取数据"""
        tasks = []
        for tag, conf in self.get_plugin_conf_value('target', {}).items():
            address = get_dict_value(conf, 'address', '').strip()
            if address:
                as_ipv6 = get_dict_value(conf, 'ipv6', False)
                timeout = get_dict_value(conf, 'timeout', 5)
                tasks.append(ensure_future(self.run_telnet(tag, address, as_ipv6, timeout)))

        # 等待任务执行
        tasks and await self.run_tasks(tasks)

    async def run_telnet(
            self,
            tag: str,
            address: Union[str, tuple, list],
            as_ipv6: bool = False,
            timeout: int = 5,
    ) -> Metric:
        """执行检测并发送结果"""
        yes, errcode = await self.to_thread(chk_port, address, None, as_ipv6, timeout)
        metric = self.metric({
            'tag': tag,
            'address': address,
            'as_ipv6': as_ipv6,
            'timeout': timeout,
            'yes': yes,
            'errcode': errcode,
        })
        return metric
