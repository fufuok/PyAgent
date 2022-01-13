# -*- coding:utf-8 -*-
"""
    mem.py
    ~~~~~~~~
    内存 信息收集插件

    :author: kerrygao, Fufu, 2021/6/10
"""
import psutil

from . import InputPlugin
from ..libs.helper import get_fn_fields, try_logger
from ..libs.humanize import human_bytes
from ..libs.psutil import to_dict


class Mem(InputPlugin):
    """内存收集插件"""

    # 模块名称
    name = 'mem'

    async def run_gather(self):
        """获取数据"""
        await self.to_thread(self.get_mem_info)

    @try_logger()
    def get_mem_info(self):
        """内存占用情况"""
        info = to_dict(psutil.virtual_memory())
        info = get_fn_fields(info, human_bytes, name_prefix='human_', ban_keys=['percent'])
        self.out_queue.put_nowait(self.metric(info))
