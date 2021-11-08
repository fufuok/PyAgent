# -*- coding:utf-8 -*-
"""
    network.py
    ~~~~~~~~
    网络信息收集插件

    :author: kerrygao 2021/6/10
"""
from asyncio import create_task, get_running_loop, sleep

import psutil

from . import InputPlugin
from ..libs.converter import get_comma
from ..libs.helper import get_int, get_round
from ..libs.humanize import human_bps


class Network(InputPlugin):
    """网络收集插件"""

    # 模块名称
    name = 'network'

    # 存储上一分钟 网卡数据
    before_one_minute = dict()

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
        # 获取网卡的信息
        net_if_addrs = psutil.net_if_addrs()
        # 获取网络接口的状态
        net_if_stats = psutil.net_if_stats()
        network_card_list = self.get_plugin_conf_value('network_card', [])
        interval = self.get_interval(60)
        for item in net_io_counters.items():
            network_card_name = item[0]
            net_if_addrs_item = net_if_addrs.get(item[0])
            net_if_stats_item = net_if_stats.get(item[0])
            duplex = net_if_stats_item.duplex
            isup = net_if_stats_item.isup
            mtu = net_if_stats_item.mtu
            speed = net_if_stats_item.speed

            ipv4 = ''
            ipv6 = ''
            mac = ''

            for addr in net_if_addrs_item:
                family = str(addr.family)
                if family == 'AddressFamily.AF_LINK':
                    mac = addr.address
                elif family == 'AddressFamily.AF_INET':
                    ipv4 = addr.address
                elif family == 'AddressFamily.AF_INET6':
                    ipv6 = addr.address

            network_card_info = self.before_one_minute.get(network_card_name)

            if network_card_info:
                if not network_card_list or network_card_name in network_card_list:
                    bps_in = get_round((item[1].bytes_recv - network_card_info["bytes_recv"]) * 8 / interval)
                    bps_out = get_round((item[1].bytes_sent - network_card_info["bytes_sent"]) * 8 / interval)
                    pps_in = get_int((item[1].packets_recv - network_card_info["packets_recv"]) / interval)
                    pps_out = get_int((item[1].packets_sent - network_card_info["packets_sent"]) / interval)

                    net_info = {
                        "network_card_name": network_card_name,
                        "duplex": duplex,
                        "isup": isup,
                        "mtu": mtu,
                        "speed": speed,
                        "ipv4": ipv4,
                        "ipv6": ipv6,
                        "mac": mac,
                        "bytes_recv": item[1].bytes_recv,
                        "bytes_sent": item[1].bytes_sent,
                        "kbps_in": get_round(bps_in / 1000),
                        "kbps_out": get_round(bps_out / 1000),
                        "human_kbps_in": human_bps(bps_in),
                        "human_kbps_out": human_bps(bps_out),
                        "dropin": item[1].dropin,
                        "dropout": item[1].dropout,
                        "errin": item[1].errin,
                        "errout": item[1].errout,
                        "packets_recv": item[1].packets_recv,
                        "packets_sent": item[1].packets_sent,
                        "pps_in": pps_in,
                        "pps_out": pps_out,
                        "comma_pps_in": get_comma(pps_in),
                        "comma_pps_out": get_comma(pps_out)
                    }
                    self.out_queue.put_nowait(self.metric(net_info))

            before_one_minute_info = {
                "bytes_recv": item[1].bytes_recv,
                "bytes_sent": item[1].bytes_sent,
                "packets_recv": item[1].packets_recv,
                "packets_sent": item[1].packets_sent
            }
            self.before_one_minute.update({
                network_card_name: before_one_minute_info
            })
