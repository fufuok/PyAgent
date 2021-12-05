# -*- coding:utf-8 -*-
"""
    cpu.py
    ~~~~~~~~
    CPU 信息收集插件

    :author: kerrygao, Fufu, 2021/6/10
"""
import psutil

from . import InputPlugin
from ..libs.helper import get_round, try_logger
from ..libs.psutil import to_dict


class Cpu(InputPlugin):
    """CPU收集插件"""

    # 模块名称
    name = 'cpu'

    async def gather(self):
        """获取数据"""
        await self.to_thread(self.get_cpu_info)

    @try_logger()
    def get_cpu_info(self):
        """获取 CPU 信息"""
        # CPU 逻辑个数
        logical_count = psutil.cpu_count()
        # CPU 物理个数
        count = psutil.cpu_count(logical=False)
        # CPU 总使用率
        percent = psutil.cpu_percent(interval=None)
        # CPU 单核使用率
        percent_percpu = psutil.cpu_percent(interval=None, percpu=True)
        max_percent = max(percent_percpu) if percent_percpu else percent
        # CPU 运行时间
        times = psutil.cpu_times()
        # CPU 运行时间比例
        times_percent = psutil.cpu_times_percent()
        # CPU 统计信息
        stats = psutil.cpu_stats()
        # 1, 5, 15 分钟系统平均负载
        try:
            loadavg = psutil.getloadavg()
        except Exception:
            loadavg = [0]
        loadavg_precent = [get_round(x / logical_count * 100) for x in loadavg]
        loadavg_precent_1 = loadavg_precent[0]

        metric = self.metric({
            'logical_count': logical_count,
            'count': count,
            'percent': percent,
            'percent_percpu': percent_percpu,
            'max_percent': max_percent,
            'times': to_dict(times),
            'times_percent': to_dict(times_percent),
            'stats': to_dict(stats),
            'loadavg': loadavg,
            'loadavg_precent': loadavg_precent,
            'loadavg_precent_1': loadavg_precent_1,
        })
        self.out_queue.put_nowait(metric)
