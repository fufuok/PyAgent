# -*- coding:utf-8 -*-
"""
    human.py
    ~~~~~~~~
    数字的数量级表示

    e.g.::

        # 1 KB
        human_bytes(1024)

        # 1 KB
        human_1k_bytes(1000)

        # 1KiB
        human_kib(1024)

        # 1Kb
        human_bit(1000)

        # 1Kbps
        human_bps(1000)

    :author: Fufu, 2021/6/12
"""
from math import floor, log, pow
from typing import Optional, Iterable


def human_bytes(
        n: int,
        *,
        prec=1,
        sep: str = ' ',
) -> str:
    """1 KB = 1024 B 字节转为二进制字节单位"""
    return human_base(n, prec=prec, base=1024, sep=sep)


def human_1k_bytes(
        n: int,
        *,
        prec=1,
        sep: str = ' ',
) -> str:
    """1 KB = 1000 B 字节转为千字节单位, 如: KB(kilobyte) 千字节"""
    return human_base(n, prec=prec, base=1000, sep=sep,
                      sizes=['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'])


def human_kib(
        n: int,
        *,
        prec=1,
        sep: str = ' ',
) -> str:
    """1 KiB = 1024 B 字节转为二进制字节单位, 如: KiB(kilo binary byte) 千位二进制字节"""
    return human_base(n, prec=prec, base=1024, sep=sep,
                      sizes=['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'])


def human_bit(
        n: int,
        *,
        prec=1,
        sep: str = ' ',
) -> str:
    """1 Kbit = 1000 bit 位"""
    return human_base(n, prec=prec, base=1000, sep=sep,
                      sizes=['b', 'Kb', 'Mb', 'Gb', 'Tb', 'Pb', 'Eb', 'Zb', 'Yb'])


def human_bps(
        n: int,
        *,
        prec=1,
        sep: str = ' ',
) -> str:
    """1 Kbps = 1000 bit, 传输速率(bit per second, 位/每秒)"""
    return human_base(n, prec=prec, base=1000, sep=sep,
                      sizes=['bps', 'Kbps', 'Mbps', 'Gbps', 'Tbps', 'Pbps', 'Ebps', 'Zbps', 'Ybps'])


def human_base(
        n: int,
        *,
        prec=1,
        base: int = 1024,
        sep: str = ' ',
        sizes: Optional[Iterable[str]] = None,
) -> str:
    """数字转为合适的数量级单位"""
    if sizes is None:
        sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    if n < base:
        return f'{n}{sep}{sizes[0]}'

    i = int(floor(log(n, base)))
    m = round(n / pow(base, i), prec)
    if m >= base:
        m = round(m / base, prec)
        i += 1

    if i >= len(sizes):
        i = len(sizes) - 1
        m = round(n / pow(base, i), prec)

    return f'{m}{sep}{sizes[i]}'
