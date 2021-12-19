# -*- coding:utf-8 -*-
"""
    process.py
    ~~~~~~~~
    磁盘/报警插件

    :author: Fufu, 2012/12/18
"""
from . import AggsPlugin
from ..libs.helper import get_dict_value, get_round
from ..libs.metric import Metric


class Process(AggsPlugin):
    """进程报警"""

    name = 'process'

    async def alarm(self, metric: Metric) -> Metric:
        """进程报警"""
        alarm_conf = self.get_plugin_conf_value('alarm', {})
        if not alarm_conf:
            return metric

        target_conf = get_dict_value(alarm_conf, 'target', {})
        if not target_conf:
            return metric

        self.alarm_target(metric, target_conf)

        return metric

    def alarm_target(self, metric: Metric, target_conf: dict) -> None:
        """按进程名称报警"""
        pinfo_list = metric.get('pinfo_list', [])
        if not pinfo_list:
            return

        # {'python.exe': [{'count': 12, 'cpu_percent': 77, ...},{...}]}
        proc_info = {}

        # 统计需要检查报警的进程 CPU 和内存占用率
        for pinfo in pinfo_list:
            proc_name = pinfo.get('name', '')
            if proc_name in target_conf:
                count = get_dict_value(proc_info, f'{proc_name}|count', 0) + 1
                cpu_pct = get_dict_value(proc_info, f'{proc_name}|cpu_percent', 0.0) + pinfo.get('cpu_percent', 0)
                mem_pct = get_dict_value(proc_info, f'{proc_name}|memory_percent', 0.0) + pinfo.get('memory_percent', 0)
                proc_info[proc_name] = {
                    'count': count,
                    'cpu_percent': cpu_pct,
                    'memory_percent': mem_pct,
                }

        for proc_name, item in proc_info.items():
            min_process_num = get_dict_value(target_conf, f'{proc_name}|min_process_num', -1)
            max_process_num = get_dict_value(target_conf, f'{proc_name}|max_process_num', -1)
            cpu_percent = get_dict_value(target_conf, f'{proc_name}|cpu_percent', -0.1)
            memory_percent = get_dict_value(target_conf, f'{proc_name}|memory_percent', -0.1)
            comment = get_dict_value(target_conf, f'{proc_name}|comment', '')

            # 进程数检查
            if min_process_num >= 0 and item['count'] < min_process_num:
                self.put_alarm_metric(f'{proc_name} 进程数小于配置: {item["count"]}<{min_process_num}', more=comment)
                continue
            if 0 <= max_process_num < item['count']:
                self.put_alarm_metric(f'{proc_name} 进程数大于配置: {item["count"]}>{max_process_num}', more=comment)
                continue

            # CPU 占用
            if 0 <= cpu_percent <= item['cpu_percent']:
                cpu_pct = item["cpu_percent"]
                self.put_alarm_metric(f'{proc_name} CPU占用过高(%): {cpu_pct}>={cpu_percent}', more=comment)
                continue

            # 内存占用
            if 0 <= memory_percent <= item['memory_percent']:
                mem_pct = get_round(item["memory_percent"])
                self.put_alarm_metric(f'{proc_name} 内存占用过高(%): {mem_pct}>={memory_percent}', more=comment)
