# -*- coding:utf-8 -*-
"""
    disk.py
    ~~~~~~~~
    磁盘 信息收集插件

    :author: kerrygao, Fufu, 2021/6/10
"""
import psutil

from . import InputPlugin
from ..libs.humanize import human_bytes
from ..libs.psutil import to_dict


class Disk(InputPlugin):
    """磁盘收集插件"""

    # 模块名称
    name = 'disk'

    async def gather(self):
        """磁盘占用情况"""
        return await self.to_thread(self.get_disk_info)

    def get_disk_info(self):
        """磁盘占用情况"""
        for disk in psutil.disk_partitions():
            if not str(disk.opts).startswith('rw,'):
                continue
            data = to_dict(disk)
            disk_usage = psutil.disk_usage(disk.mountpoint)
            data.update(to_dict(disk_usage))
            data.update({
                'human_total': human_bytes(disk_usage.total),
                'human_used': human_bytes(disk_usage.used),
                'human_free': human_bytes(disk_usage.free),
            })
            self.out_queue.put_nowait(self.metric(data))
