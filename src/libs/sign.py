# -*- coding:utf-8 -*-
"""
    data.py
    ~~~~~~~~
    数据项生成函数

    :author: Fufu, 2021/12/9
"""
import time

from envcrypto import decrypt

from .helper import get_hash
from ..env import COMMON_KEY


def sign_charge(token: str = '') -> dict:
    """DemoCharge 监控签名生成"""
    timestamp = int(time.time())
    key = decrypt(token, COMMON_KEY)
    sign = get_hash(f'DemoCharge+{timestamp}~~{key}')

    return {
        'timestamp': timestamp,
        'sign': sign,
    }
