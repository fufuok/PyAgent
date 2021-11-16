# -*- coding:utf-8 -*-
"""
    metric.py
    ~~~~~~~~
    指标数据

    :author: Fufu, 2021/6/7
"""
import json
import time
from typing import Any, Optional, Union, List, Tuple

from .helper import get_iso_date, get_same_type


class Metric:
    """指标数据"""

    def __init__(
            self,
            name: str,
            data: Optional[dict] = None,
            *,
            info: Optional[dict] = None,
            tag: str = 'metric',
    ) -> None:
        # 数据标识: `metric` 采集的指标数据; `alarm` 报警数据
        self.tag = str(tag)
        # 数据名称: `cpu` 采集的 CPU 指标数据, 一般是插件名称
        self.name = str(name)
        # 基础数据项
        self.metric = {
            'name': self.name,
            'time': get_iso_date(),
            'timestamp': int(time.time())
        }
        # 服务器标识信息
        isinstance(info, dict) and self.metric.update(info)
        # 指标数据
        isinstance(data, dict) and self.metric.update(data)

    def get(
            self,
            key: str,
            default: Any = None,
            *,
            fix_type: bool = True
    ) -> Optional[str]:
        """获取数据"""
        value = self.metric.get(key, default)
        return get_same_type(default, value) if fix_type else value

    def set(self, **data: Any) -> None:
        """添加数据"""
        self.metric.update(data)

    def add(self, key: str, value: Any) -> None:
        """添加数据"""
        self.metric[key] = value

    def delete(self, key: Union[str, List[str], Tuple[str]]) -> None:
        """删除数据项"""
        for x in (key if isinstance(key, (list, tuple)) else [key]):
            x in self.metric and self.metric.pop(x)

    def has_key(self, key: str):
        """是否存在相应的键"""
        return key in self.metric

    def get_name(self) -> str:
        """获取数据项名称"""
        return self.name

    def set_name(self, name: str) -> None:
        """设置数据项名称"""
        self.name = name
        self.metric['name'] = name

    def get_tag(self) -> str:
        """获取数据项标识"""
        return self.tag

    def set_tag(self, tag: str) -> None:
        """设置数据项标识"""
        self.tag = tag

    def clone(self) -> Any:
        """克隆数据"""
        return Metric(self.name, self.as_dict, tag=self.tag)

    def keys(self, scope: Optional[Union[list, tuple, set]] = None) -> list:
        """获取数据键名列表"""
        return list(set(self.metric.keys()) & set(scope)) if scope else self.metric.keys()

    @property
    def as_dict(self) -> dict:
        """转换为字典(浅拷贝)"""
        return self.metric.copy()

    @property
    def as_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.metric)

    @property
    def as_text(self) -> str:
        """转换为字符串"""
        return '{}, {}'.format(self.tag.upper(), ' '.join([f'{k}={v}' for k, v in self.metric.items()]))

    @property
    def is_closed(self) -> bool:
        """检查是否为关闭信号(退出插件)"""
        return self.tag == '__CLOSE_SIGNAL__'

    def __contains__(self, key: str):
        return key in self.metric
