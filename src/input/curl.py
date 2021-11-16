# -*- coding:utf-8 -*-
"""
    curl.py
    ~~~~~~~~
    CURL 数据收集插件

    :author: Fufu, 2021/6/15
"""
from asyncio import as_completed, ensure_future
from typing import Any

from aiohttp import ClientSession, TCPConnector
from loguru import logger

from . import InputPlugin
from ..libs.helper import get_dict_value
from ..libs.metric import Metric


class Curl(InputPlugin):
    """CURL 数据收集插件"""

    # 模块名称
    name = 'curl'

    async def gather(self) -> None:
        """按配置发起请求任务"""
        # 并发限制(到同主机)
        limit = self.get_conf_value('worker_limit', 30)
        # 创建请求任务
        async with ClientSession(connector=TCPConnector(ssl=False, limit_per_host=limit)) as sess:
            tasks = []
            for tag, conf in self.get_plugin_conf_value('target', {}).items():
                url = get_dict_value(conf, 'url')
                if not url:
                    continue

                # 请求参数集
                method = get_dict_value(conf, 'method', 'get').upper()
                req = {
                    'url': url,
                    'method': method,
                }

                if method == 'POST':
                    # 请求数据项
                    data = get_dict_value(conf, 'data', {})
                    if data:
                        if get_dict_value(conf, 'type', 'data').lower() == 'json':
                            req['json'] = data
                        else:
                            req['data'] = data

                tasks.append(ensure_future(self.get_request(sess, tag, req)))

            # 等待任务执行
            tasks and await self.run_tasks(tasks)

    async def get_request(self, sess: Any, tag: str, req: dict) -> Metric:
        """获取请求结果"""
        metric = self.metric({
            'tag': tag,
            'url': req['url'],
            'method': req['method'],
            'response': '',
            'status': 504,
            'header': {},
        })
        try:
            async with sess.request(**req) as resp:
                res = await resp.text()
                metric.set(**{
                    'response': res,
                    'status': resp.status,
                    'header': dict(resp.headers),
                })
                if self.conf.debug and not resp.ok:
                    logger.warning(f'curl {resp.status}, req_info={resp.request_info}, metric={metric.as_text}')
        except Exception as e:
            self.conf.debug and logger.error(f'curl exception, req={req} err={e}')

        return metric

    async def run_tasks(self, tasks: list) -> None:
        """接收请求结果并推送"""
        for task in as_completed(tasks):
            metric = await task
            self.out_queue.put_nowait(metric)
