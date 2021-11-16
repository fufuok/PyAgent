# -*- coding:utf-8 -*-
"""
    __init__.py
    ~~~~~~~~
    数据聚合/报警插件 aggs

    :author: Fufu, 2021/6/7
"""
from asyncio import create_task
from typing import Any

from loguru import logger

from ..libs.metric import Metric
from ..libs.plugin import BasePlugin


class AggsPlugin(BasePlugin):
    """数据聚合/报警插件基类"""

    module = 'aggs'

    async def run(self) -> None:
        """数据汇聚/报警"""
        logger.debug(f'{self.module}.{self.name}({self.alias}) is working')
        is_closed = False
        while not is_closed:
            # 取队列数据
            metric = await self.in_queue.get()
            is_closed = metric.is_closed

            # 数据分发
            create_task(self.alarm(metric))

            # 传递数据
            self.out_queue.put_nowait(metric)
            self.in_queue.task_done()

        logger.debug(f'{self.module}.{self.name}({self.alias}) is closed')

    async def alarm(self, metric: Metric) -> Any:
        """报警器"""
        pass

    def put_alarm_metric(
            self,
            info: str,
            *,
            code: str = '',
            more: str = '',
            tag: str = '',
    ) -> None:
        """生成并推送报警数据"""
        alarm_metric = self.metric(
            {
                'code': self.get_conf_value('alarm|code', 'alarm') if code == '' else str(code),
                'info': str(info),
                'more': str(more) if more else self.get_plugin_conf_value('alarm|comment', ''),
            },
            tag='alarm' if tag == '' else str(tag),
        )
        self.out_queue.put_nowait(alarm_metric)
        logger.debug('alarm_metric: {}', alarm_metric.as_json)
