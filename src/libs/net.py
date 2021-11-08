# -*- coding:utf-8 -*-
"""
    net.py
    ~~~~~~~~
    网络相关助手函数

    :author: Fufu, 2021/6/9
"""
import math
import os
import re
from asyncio import create_subprocess_shell, subprocess
from socket import AF_INET, AF_INET6, SOCK_STREAM, socket
from typing import Any, Optional, Tuple, Union

from aiohttp import ClientSession, TCPConnector
from icmplib import async_ping
from loguru import logger

from .helper import get_int, get_json_loads, get_round


async def request(
        url: str,
        method: str = 'POST',
        *,
        as_json: bool = True,
        throw: bool = False,
        **kwargs: Any,
) -> Union[dict, Tuple[Any]]:
    """发起 HTTP 请求(异步)"""
    async with ClientSession(connector=TCPConnector(ssl=False)) as client:
        try:
            async with client.request(method, url, **kwargs) as resp:
                res = await resp.text()
                return get_json_loads(res) if as_json else (res, resp.status, dict(resp.headers))
        except Exception as e:
            logger.opt(exception=True).debug('Exception: {}, {}: {}', e, method, url)
            if throw:
                raise e
            return {} if as_json else ('', 504, {})


async def ping(target: str, count: int = 3, timeout: int = 1000, interval: float = 1.0):
    """
    PING 目标网络, 获取延迟丢包 (备用)
    调用 Windows/Linux 系统 PING 命令, 支持 IPv6

    :param target: 目标地址
    :param count: 发送的回显请求数
    :param timeout: 超时时间, Windows 有效
    :param interval: Linux 每次 PING 的时隔
    :return:
    """
    err_value = 5000
    windows = os.name == 'nt'
    ret = {
        'loss': err_value,
        'minimum': err_value,
        'maximum': err_value,
        'average': err_value,
    }

    if windows:
        cmd = f'ping -w {timeout} -n {count} {target}'
    else:
        timeout = math.ceil(count * interval)
        cmd = f'ping -i {interval} -c {count} -w {timeout} {target}'

    process = await create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 等待该子进程运行结束
    stdout, errout = await process.communicate()

    if len(errout) > 0:
        return ret

    # 运行结果
    res = stdout.decode('gbk', 'ignore').strip()

    # 丢包率 %
    loss = re.findall(r'(\d+)%', res)
    if loss:
        ret['loss'] = get_round(loss[0], err_value)

    # 延迟
    patt = r'(\d+)ms.*? (\d+)ms.*? (\d+)ms' if windows else r'([\d.]+)/([\d.]+)/([\d.]+)'
    delay = re.findall(patt, res)
    if delay and len(delay[0]) == 3:
        delay = [get_round(x, err_value) for x in delay[0]]
        ret['minimum'] = delay[0]
        if windows:
            ret['maximum'] = delay[1]
            ret['average'] = delay[2]
        else:
            ret['maximum'] = delay[2]
            ret['average'] = delay[1]

    return ret


async def pyping(target: str, count: int = 3, timeout: float = 0.7, interval: float = 0.1):
    """
    PING 目标网络, 获取延迟丢包
    基于 icmplib, 支持 IPv6

    :param target: 目标地址
    :param count: 发送的回显请求数
    :param timeout: 超时时间
    :param interval: Linux 每次 PING 的时隔
    :return:
    """
    host = await async_ping(target, count=count, timeout=timeout, interval=interval)
    if host.is_alive:
        return {
            'loss': get_round(host.packet_loss * 100),
            'minimum': host.min_rtt,
            'maximum': host.max_rtt,
            'average': host.avg_rtt,
        }

    return {
        'loss': 100,
        'minimum': 5000,
        'maximum': 5000,
        'average': 5000,
    }


def chk_port(
        ip: Union[str, tuple, list],
        port: Optional[int] = None,
        as_ipv6: bool = False,
        timeout: int = 5,
) -> Tuple[bool, int]:
    """
    检查 TCP 端口连通性

    e.g.::

        chk_port('baidu.com', 443)
        chk_port('baidu.com:443')
        chk_port(('baidu.com', 443))
        chk_port('baidu.com')
        chk_port('[::1]:443', as_ipv6=True)

    :param ip:
    :param port: 默认 80
    :param as_ipv6:
    :param timeout: 超时秒数
    :return:
    """
    if not port:
        ip_port = ip if isinstance(ip, (list, tuple)) else str(ip).rsplit(':', 1)
        ip, port = ip_port if len(ip_port) > 1 else (ip_port, None)

    try:
        with socket(AF_INET6 if as_ipv6 else AF_INET, SOCK_STREAM) as s:
            s.settimeout(get_int(timeout, 5))
            x = s.connect_ex((str(ip), get_int(port, 80)))
            s.settimeout(None)
            return x == 0, x
    except Exception:
        pass

    return False, -1
