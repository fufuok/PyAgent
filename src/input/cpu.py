# -*- coding:utf-8 -*-
"""
    cpu.py
    ~~~~~~~~
    CPU 信息收集插件

    :author: kerrygao, Fufu, 2021/6/10
"""
from asyncio import create_task, get_running_loop, sleep

import psutil

from . import InputPlugin
from ..libs.psutil import to_dict


class Cpu(InputPlugin):
    """CPU收集插件"""

    # 模块名称
    name = 'cpu'

    async def run(self):
        """定时执行收集"""
        while True:
            create_task(self.gather())
            await sleep(self.get_interval(60))

    async def gather(self):
        """获取数据"""
        metric = await get_running_loop().run_in_executor(None, self.get_cpu_info)
        self.out_queue.put_nowait(metric)

    def get_cpu_info(self):
        """获取 CPU 信息"""
        # CPU 逻辑个数
        cpu_logical_count = psutil.cpu_count()
        # CPU 物理个数
        cpu_count = psutil.cpu_count(logical=False)
        # CPU 占用率
        cpu_percent = psutil.cpu_percent(interval=0.1)
        # CPU 运行时间
        cpu_times = psutil.cpu_times()
        # CPU 统计信息
        cpu_stats = psutil.cpu_stats()
        # CPU 频率
        cpu_freq = psutil.cpu_freq()

        metric = self.metric({
            'cpu_logical_count': cpu_logical_count,
            'cpu_count': cpu_count,
            'cpu_percent': cpu_percent,
            'cpu_times': to_dict(cpu_times),
            'cpu_stats': to_dict(cpu_stats),
            'cpu_freq': to_dict(cpu_freq)
        })

        return metric
