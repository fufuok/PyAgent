# -*- coding:utf-8 -*-
"""
    demo.py
    ~~~~~~~~
    示例数据汇聚/报警插件

    :author: Fufu, 2021/6/7
"""
from loguru import logger

from . import AggsPlugin
from ..libs.metric import Metric


class Demo(AggsPlugin):
    """示例数据汇聚/报警"""

    name = 'demo'

    async def alarm(self, metric: Metric) -> Metric:
        """报警"""
        if metric.get('x', 0) >= self.get_plugin_conf_value('alarm|limit', 0):
            return metric

        # 附加报警数据
        metric = metric.clone()
        metric.set(type='alarm~~~~~~~~~')
        metric.set(**{'a': True, 'b': 123})
        self.out_queue.put_nowait(metric)
        logger.debug('触发报警了: {}', metric.as_json)

        # 新生成报警数据
        self.put_alarm_metric('示例报警数据', tag="demo", flag="test", more='报警附加消息')

        return metric
