# -*- coding:utf-8 -*-
"""
    network.py
    ~~~~~~~~
    网络信息收集插件

    :author: kerrygao, 2021/6/10
    :update: Fufu, 2021/11/8 代码重构, 支持网卡前缀配置和多 IP
"""
import time
from asyncio import create_task, get_running_loop, sleep

import psutil

from . import InputPlugin
from ..libs.helper import get_round, get_comma, get_int
from ..libs.humanize import human_bps
from ..libs.psutil import to_dict


class Network(InputPlugin):
    """网络收集插件"""

    # 模块名称
    name = 'network'

    # 存储上一时间的网卡数据
    last_data = {}

    async def run(self):
        """定时执行收集"""
        while True:
            create_task(self.gather())
            await sleep(self.get_interval(60))

    async def gather(self):
        """获取数据"""
        return await get_running_loop().run_in_executor(None, self.get_network_info)

    def get_network_info(self):
        """获取网络信息"""
        # 获取网口的流量
        net_io_counters = psutil.net_io_counters(pernic=True)
        if not self.last_data:
            self.last_data = {nic: to_dict(data) for nic, data in net_io_counters.items()}
            self.last_data['last_time'] = time.time()
            return

        # 获取待采集的网卡列表
        nic_list = self.get_nic_list(net_io_counters.keys())

        # 时间间隔
        now = time.time()
        interval = now - self.last_data['last_time']
        self.last_data['last_time'] = time.time()
        if interval < 0:
            return

        # 获取网卡的信息
        net_if_addrs = psutil.net_if_addrs()
        # 获取网络接口的状态
        net_if_stats = psutil.net_if_stats()

        for nic in nic_list:
            now_nic_data = to_dict(net_io_counters[nic])
            last_nic_data = self.last_data.get(nic, {})
            self.last_data[nic] = now_nic_data
            if not last_nic_data:
                # 新网卡
                continue
            self.gen_metric(interval, nic, now_nic_data, last_nic_data, net_if_addrs, net_if_stats)

    def get_nic_list(self, all_nic: list) -> set:
        """获取待采集的网卡列表"""
        nic_list = set()

        # 配置中指定的要采集的网卡
        conf_nic_list = self.get_plugin_conf_value('network_card', [])
        if conf_nic_list:
            nic_list = set(conf_nic_list).intersection(set(all_nic))

        # 配置中指定的要采集的网卡前缀
        nic_prefix_list = self.get_plugin_conf_value('network_card_prefix', [])
        for prefix in nic_prefix_list:
            nic_list.update([x for x in all_nic if str(x).startswith(prefix)])

        return nic_list

    def gen_metric(
            self,
            interval,
            nic: str,
            now_nic_data: dict,
            last_nic_data: dict,
            net_if_addrs: dict,
            net_if_stats: dict
    ) -> None:
        """生成指标数据"""
        metric = {
            'nic': nic,
            'interval': interval,
        }
        metric.update(to_dict(net_if_stats[nic]))
        for snic in net_if_addrs[nic]:
            if snic.family.name in ('AF_LINK', 'AF_PACKET'):
                metric['mac'] = snic.address
            elif snic.family.name == 'AF_INET':
                metric['ipv4'] = f'{metric["ipv4"]},{snic.address}' if 'ipv4' in metric else snic.address
            elif snic.family.name == 'AF_INET6':
                metric['ipv6'] = f'{metric["ipv6"]},{snic.address}' if 'ipv6' in metric else snic.address

        metric.update(now_nic_data)
        metric['bps_in'] = get_round((now_nic_data['bytes_recv'] - last_nic_data['bytes_recv']) * 8 / interval)
        metric['bps_out'] = get_round((now_nic_data['bytes_sent'] - last_nic_data['bytes_sent']) * 8 / interval)
        metric['pps_in'] = get_int((now_nic_data['packets_recv'] - last_nic_data['packets_recv']) / interval)
        metric['pps_out'] = get_int((now_nic_data['packets_sent'] - last_nic_data['packets_sent']) / interval)

        metric['kbps_in'] = get_round(metric['bps_in'] / 1000)
        metric['kbps_out'] = get_round(metric['bps_out'] / 1000)
        metric['human_kbps_in'] = human_bps(metric['bps_in'])
        metric['human_kbps_out'] = human_bps(metric['bps_out'])
        metric['comma_pps_in'] = get_comma(metric['pps_in'])
        metric['comma_pps_out'] = get_comma(metric['pps_out'])

        self.out_queue.put_nowait(self.metric(metric))
