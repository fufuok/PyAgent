# -*- coding:utf-8 -*-
"""
    psutil.py
    ~~~~~~~~
    psutil 助手函数

    :author: Fufu, 2021/11/10
"""
from typing import Any


def to_dict(obj: Any) -> dict:
    """对象转字典"""
    if hasattr(obj, '_asdict'):
        return obj._asdict()

    if hasattr(obj, '_fields'):
        return dict(zip(obj._fields, obj))

    try:
        return dict(obj)
    except BaseException:
        pass

    return {}
