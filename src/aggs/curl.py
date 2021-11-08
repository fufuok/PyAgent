# -*- coding:utf-8 -*-
"""
    curl.py
    ~~~~~~~~
    CURL 数据汇聚/报警插件

    :author: Fufu, 2021/6/15
"""
from typing import List, Tuple

from . import AggsPlugin
from ..libs.helper import get_json_loads
from ..libs.metric import Metric


class Curl(AggsPlugin):
    """CURL 数据汇聚/报警"""

    name = 'curl'

    async def alarm(self, metric: Metric) -> None:
        """报警"""
        # 公共报警规则
        for name, conf in self.get_plugin_conf_value('alarm|all', {}).items():
            fn_name = f'chk_{name}'
            if not hasattr(self, fn_name):
                continue

            ok, info = getattr(self, fn_name)(metric, conf)
            if not ok:
                info = '{} - {}'.format(metric.get('tag'), info)
                return self.put_alarm_metric(info, more=metric.get('url', ''))

        # 标识指定报警规则
        for tag, tag_conf in self.get_plugin_conf_value('alarm|target', {}).items():
            if metric.get('tag', '') != tag or not isinstance(tag_conf, dict):
                continue

            for name, conf in tag_conf.items():
                fn_name = f'chk_{name}'
                if not hasattr(self, fn_name):
                    continue

                ok, info = getattr(self, fn_name)(metric, conf)
                if not ok:
                    info = '{} - {}'.format(metric.get('tag'), info)
                    return self.put_alarm_metric(info, more=metric.get('url', ''))

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
                if str(js.get(k)) != str(v):
                    return False, f'返回值: {k} != {v}'

        return True, ''

    @staticmethod
    def chk_header(metric: Metric, conf: dict) -> Tuple[bool, str]:
        """检查响应头是否包含相应键值"""
        header = metric.get('header')
        if not header or not isinstance(header, dict):
            return False, '响应头为空或不正确'

        if conf and isinstance(conf, dict):
            for k, v in conf.items():
                if str(header.get(k)) != str(v):
                    return False, f'响应头: {k} != {v}'

        return True, ''
