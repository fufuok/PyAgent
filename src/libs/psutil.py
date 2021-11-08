# -*- coding:utf-8 -*-
"""
    psutil.py
    ~~~~~~~~
    psutil 助手函数

    :author: kerrygao 2021/6/23
"""


def to_dict(obj):
    """对象转字典"""
    tmp_dict = dict()
    for field in obj._fields:
        v = getattr(obj, field)
        tmp_dict.update({field: v})
    return tmp_dict
