# -*- coding:utf-8 -*-
"""
    psutil.py
    ~~~~~~~~
    psutil 助手函数

    :author: Fufu, 2021/11/10
"""
import time
from operator import itemgetter
from typing import Any, List, Optional, Union

import psutil

from ..libs.helper import get_int, get_round


def get_process_info(
        target: Optional[list] = None,
        fields: Optional[list] = None,
        *,
        orderby: Optional[Union[str, List[str]]] = None,
        reverse=True,
) -> list:
    """获取进程列表信息"""
    fields = fields if fields and isinstance(fields, list) \
        else ['pid', 'ppid', 'name', 'username', 'cpu_percent', 'memory_percent', 'exe', 'num_threads', 'create_time']

    chk_names = target and isinstance(target, list)
    as_ctime = 'create_time' in fields
    as_mem = 'memory_percent' in fields
    as_cpu = 'cpu_percent' in fields
    logical_count = 1
    if as_cpu:
        logical_count = psutil.cpu_count()
        list(psutil.process_iter(['cpu_percent']))
        time.sleep(0.5)

    pinfo_list = []
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=fields)
        except psutil.Error:
            pass
        else:
            # 指定进程名(默认采集所有进程)
            proc_name = proc.name()
            if not proc_name or chk_names and proc_name not in target:
                continue
            # 核算 CPU 占用
            if as_cpu:
                pinfo['cpu_percent'] = get_round(pinfo.get('cpu_percent', 0) / logical_count, default=0)
            # 处理默认字段格式
            if as_mem:
                pinfo['memory_percent'] = get_round(pinfo.get('memory_percent', 0), default=0)
            if as_ctime:
                pinfo['create_time'] = get_int(pinfo.get('create_time', 0), default=0)
            pinfo_list.append(pinfo)

    if not orderby:
        return pinfo_list

    orderby_list = orderby if isinstance(orderby, list) else [orderby]
    orderby = list(set(orderby_list) & set(fields))
    if not orderby:
        return pinfo_list

    orderby.sort(key=orderby_list.index)
    pinfo_list = sorted(pinfo_list, key=itemgetter(*orderby), reverse=reverse)

    return pinfo_list


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
