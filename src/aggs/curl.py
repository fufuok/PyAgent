# -*- coding:utf-8 -*-
"""
    curl.py
    ~~~~~~~~
    CURL 数据汇聚/报警插件

    :author: Fufu, 2021/6/15
"""
from typing import List, Tuple

from . import AggsPlugin
from ..libs.helper import get_dict_value, get_json_loads
from ..libs.metric import Metric


class Curl(AggsPlugin):
    """CURL 数据汇聚/报警"""

    name = 'curl'

    async def alarm(self, metric: Metric) -> Metric:
        """报警"""
        alarm_conf = self.get_plugin_conf_value('alarm', {})
        if not alarm_conf:
            return metric

        # 获取报警时使用的指标字段
        metric_tag = metric.get('tag')
        msg_fields = self.get_msg_fields(alarm_conf, metric_tag)

        # 优先使用指定 tag 报警
        self.alarm_target(metric, alarm_conf, msg_fields) or self.alarm_all(metric, alarm_conf, msg_fields)

        return metric

    @staticmethod
    def get_msg_fields(alarm_conf: dict, metric_tag: str) -> List[str]:
        msg_conf = get_dict_value(alarm_conf, 'use_msg_fields', {})
        if not msg_conf:
            return []

        # 优先使用指定 tag 项的配置
        msg_fields = get_dict_value(msg_conf, metric_tag, [])

        if not msg_fields and metric_tag not in get_dict_value(msg_conf, 'all_except', []):
            msg_fields = get_dict_value(msg_conf, 'all', [])

        return msg_fields

    def alarm_all(self, metric: Metric, alarm_conf: dict, msg_fields: list) -> bool:
        """检查全局报警"""
        all_conf = get_dict_value(alarm_conf, 'all', {})
        if not all_conf:
            return False

        for name, conf in all_conf.items():
            fn_name = f'chk_{name}'
            if not hasattr(self, fn_name):
                continue

            ok, info = getattr(self, fn_name)(metric, conf)
            if not ok:
                info = '{} - {} {}'.format(metric.get('tag'), info, metric.msg(msg_fields))
                self.put_alarm_metric(info, tag=metric.get('tag'), more=metric.get('url', ''))
                return True

        return False

    def alarm_target(self, metric: Metric, alarm_conf: dict, msg_fields: list) -> bool:
        """标识指定报警规则"""
        target_conf = get_dict_value(alarm_conf, 'target', {})
        if not target_conf:
            return False

        for tag, tag_conf in target_conf.items():
            if metric.get('tag', '') != tag or not isinstance(tag_conf, dict):
                continue

            for name, conf in tag_conf.items():
                fn_name = f'chk_{name}'
                if not hasattr(self, fn_name):
                    continue

                ok, info = getattr(self, fn_name)(metric, conf)
                if not ok:
                    info = '{} - {} {}'.format(metric.get('tag'), info, metric.msg(msg_fields))
                    self.put_alarm_metric(info, tag=tag, more=metric.get('url', ''))
                    return True

        return False

    @staticmethod
    def chk_status(metric: Metric, conf: List[int]) -> Tuple[bool, str]:
        """检查 HTTP 状态码是否正确"""
        status = metric.get('status', 0)
        if isinstance(conf, (list, tuple)) and status in conf:
            return True, ''

        return False, f'HTTP 状态码错误: {status}'

    @staticmethod
    def chk_contains(metric: Metric, conf: str) -> Tuple[bool, str]:
        """检查返回值是否包含指定字符串"""
        if str(conf) in metric.get('response', ''):
            return True, ''

        return False, f'返回值不包含: {conf}'

    @staticmethod
    def chk_json(metric: Metric, conf: dict) -> Tuple[bool, str]:
        """检查返回值是否为 JSON 字符串, 检查是否包含相应键值"""
        js = get_json_loads(metric.get('response'))
        if not js or not isinstance(js, dict):
            return False, '返回值不是有效JSON键值对'

        if conf and isinstance(conf, dict):
            for k, v in conf.items():
                v = '' if v is None else str(v)
                if str(js.get(k)) != v:
                    return False, f'返回值: {k} != {v}'

        return True, ''

    @staticmethod
    def chk_headers(metric: Metric, conf: dict) -> Tuple[bool, str]:
        """检查响应头是否包含相应键值"""
        headers = metric.get('headers')
        if not headers or not isinstance(headers, dict):
            return False, '响应头为空或不正确'

        if conf and isinstance(conf, dict):
            for k, v in conf.items():
                v = '' if v is None else str(v)
                if str(headers.get(k)) != v:
                    return False, f'响应头: {k} != {v}'

        return True, ''

    @staticmethod
    def chk_metric(metric: Metric, conf: dict) -> Tuple[bool, str]:
        """检查指标数据是否包含相应键值"""
        if conf and isinstance(conf, dict):
            for k, v in conf.items():
                v = '' if v is None else str(v)
                if str(metric.get(k)) != v:
                    return False, f'数据项: {k} != {v}'

        return True, ''
