# -*- coding:utf-8 -*-
"""
    es.py
    ~~~~~~~~
    数据发布插件 - ES

    :author: Fufu, 2021/6/7
"""
import asyncio
from typing import List

from loguru import logger

from . import OutputPlugin
from ..libs.metric import Metric
from ..libs.net import request


class Es(OutputPlugin):
    """数据发布到 ES"""

    name = 'es'

    # 缺省的 ES 接口和索引名
    es_api = 'http://data-router.demo.com:6600/v1/monitor_metric/bulk'
    es_index = 'monitor_metric'

    async def run(self) -> None:
        """数据打包并提交发布"""
        while True:
            # 定时推送
            await asyncio.sleep(self.get_interval(default=30))

            # 取队列数据
            metrics = []
            while not self.in_queue.empty():
                metric = self.in_queue.get_nowait()
                metrics.append(metric)
                # 数据传递
                self.out_queue and self.out_queue.put_nowait(metric)
                self.in_queue.task_done()

            # 执行推送
            metrics and asyncio.create_task(self.write(metrics))

    async def write(self, metrics: List[Metric]) -> None:
        """写入数据"""
        # 根据 tag 对应接口和数据
        post_data = {}
        for x in metrics:
            k = f'{x.tag}.{x.name}'
            if k not in post_data:
                post_data[k] = {
                    'api_url': self.get_es_api(x.tag),
                    'data': [],
                }
            post_data[k]['data'].append(x)

        for k, d in post_data.items():
            resp = await request(d['api_url'], json=self.metrics_as_dict(d['data']))
            logger.debug('es.post: {}, api_url: {}, resp: {}', k, d['api_url'], resp)

    def get_es_api(self, tag: str) -> str:
        """获取 ES 上报接口"""
        es_index = self.get_plugin_conf_ab_value([f'index_{tag}', 'index'], self.es_index)
        es_api = self.get_plugin_conf_value('url', self.es_api).replace('{es_index}', es_index)

        return es_api
