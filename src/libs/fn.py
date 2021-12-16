# -*- coding:utf-8 -*-
"""
    fn.py
    ~~~~~~~~
    导入数据生成相关函数

    :author: Fufu, 2021/12/9
"""
from .sign import sign_charge


def gen_data_fn() -> dict:
    """返回可用的数据生成函数"""
    return {
        'sign_charge': sign_charge,
    }
