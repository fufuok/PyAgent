# -*- coding:utf-8 -*-
"""
    converter.py
    ~~~~~~~~
    数据类型转换处理公共插件

    :author: Fufu, 2021/6/13
"""
import re
from inspect import isfunction

from ..libs.converter import *
from ..libs.helper import get_dict_value, get_fn_value
from ..libs.metric import Metric
from ..libs.plugin import RootPlugin


class Converter(RootPlugin):
    """类型转换处理"""

    # 转换函数集
    fn = {}

    def __init__(
            self,
            conf,
            module: str,
            name: str,
            metric: Metric,
    ) -> None:
        super().__init__(conf)

        # 调用时传入数据, 模块和名称
        self.metric = metric
        self.module = module
        self.name = name

        if not self.fn:
            for x, obj in globals().items():
                if isfunction(obj) and obj.__code__.co_argcount > 0:
                    self.fn[x] = obj

    async def run(self) -> Metric:
        """转换数据并增加到新字段"""
        # 加载调用公共插件的固定名称对应配置
        for fn_name, fn_conf in self.get_plugin_conf_value('use_plugin_converter', {}).items():
            fn = self.fn.get(fn_name)
            if not fn or not fn_conf or not isinstance(fn_conf, dict):
                continue

            fields_conf = get_dict_value(fn_conf, 'fields_conf', {})
            name_prefix = get_dict_value(fn_conf, 'name_prefix', '')
            name_suffix = get_dict_value(fn_conf, 'name_suffix', '')
            delete_old = fn_conf.get('delete_old', False)
            default_value = fn_conf.get('default_value', None)

            for field in self.get_fields_items(fn_conf):
                if field not in self.metric:
                    continue

                # 处理结果值非真时是否使用默认值, 默认值 None 时不启用
                as_true = False if default_value is None else True

                # 执行函数, 参数为字段值, 如: human_bps(1000)
                value = get_fn_value(
                    fn,
                    self.metric.get(field),
                    default=get_dict_value(fields_conf, f'{field}|default_value', default_value, as_true=as_true),
                    as_true=as_true,
                )

                # 是否删除原字段, 字段单独配置项优先
                get_dict_value(fields_conf, f'{field}|delete_old', delete_old) and self.metric.delete(field)

                # 指标数据增加新值字段, 字段单独配置的 name_override 优先
                key = get_dict_value(fields_conf, f'{field}|name_override', f'{name_prefix}{field}{name_suffix}')
                self.metric.add(key, value)

        return self.metric

    def get_fields_items(self, fn_conf: dict) -> set:
        """根据配置获取待处理字段集合"""
        fields_items = get_dict_value(fn_conf, 'fields_items', set())
        fields_prefix = get_dict_value(fn_conf, 'fields_prefix', [])
        fields_suffix = get_dict_value(fn_conf, 'fields_suffix', [])
        fields_regex = get_dict_value(fn_conf, 'fields_regex', [])

        metric_keys = self.metric.keys()
        if fields_prefix:
            for x in fields_prefix:
                fields_items.update([f for f in metric_keys if str(f).startswith(x)])
        if fields_suffix:
            for x in fields_suffix:
                fields_items.update([f for f in metric_keys if str(f).endswith(x)])
        if fields_regex:
            s = []
            for x in fields_regex:
                for f in metric_keys:
                    try:
                        s.append([f, bool(re.search(x, str(f), re.I)), re.search(x, str(f), re.I)])
                        re.search(x, str(f), re.I) and fields_items.add(f)
                    except Exception:
                        continue

        return fields_items
