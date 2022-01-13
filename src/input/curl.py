# -*- coding:utf-8 -*-
"""
    curl.py
    ~~~~~~~~
    CURL 数据收集插件

    :author: Fufu, 2021/6/15
"""
from asyncio import ensure_future, sleep
from typing import Any

from aiohttp import ClientSession, TCPConnector
from loguru import logger

from . import InputPlugin
from ..libs.helper import get_dict_value, get_int, get_json_loads
from ..libs.metric import Metric


class Curl(InputPlugin):
    """CURL 数据收集插件"""

    # 模块名称
    name = 'curl'

    async def gather(self) -> None:
        """获取数据(允许堆叠)"""
        await self.perf_gather()

    async def run_gather(self) -> None:
        """按配置发起请求任务"""
        # 并发限制(到同主机)
        limit = self.get_plugin_conf_value('worker_limit', 30)
        # 创建请求任务
        async with ClientSession(connector=TCPConnector(ssl=False, limit_per_host=limit)) as sess:
            tasks = []
            for tag, conf in self.get_plugin_conf_value('target', {}).items():
                url = get_dict_value(conf, 'url')
                if not url:
                    continue

                # 是否重试, 及重试状态码
                retry = self.get_retry_conf(conf)

                # 是否将响应内容(请求失败时忽略)合并到指标数据
                as_merge_resp = get_dict_value(conf, 'merge_response', False)

                # 请求参数集
                req = self.get_request_conf(conf, url)

                tasks.append(ensure_future(self.get_request(sess, tag, req, as_merge_resp, retry)))

            # 等待任务执行
            tasks and await self.run_tasks(tasks)

    async def get_request(self, sess: Any, tag: str, req: dict, as_merge_resp: bool, retry: dict) -> Metric:
        """获取请求结果"""
        exception = ''
        url = req['url']
        status = 504
        metric = self.metric({
            'tag': tag,
            'url': url,
            'method': req['method'],
            'host': req['headers'].get('Host', ''),
            'response': '',
            'status': status,
            'headers': {},
        })

        for i in range(-1, retry['attempts']):
            try:
                async with sess.request(**req) as resp:
                    metric = await self.get_response(resp, metric, as_merge_resp)
                    status = resp.status
                    if self.conf.debug and not resp.ok:
                        logger.warning(f'curl {status}, req_info={resp.request_info}, metric={metric.as_text}')
                    if status not in retry['statuses']:
                        break
            except Exception as e:
                exception = str(e)
                self.conf.debug and logger.error(f'curl exception, req={req} err={e}')
            # 1 秒后重试
            await sleep(1)
            i >= 0 and logger.warning(f'retry({i + 1}) curl {status}, url={url}')

        # 附加异常报警
        exception and metric.set(exception=exception)

        return metric

    @staticmethod
    def get_retry_conf(conf: dict) -> dict:
        """初始化重试配置"""
        retry = get_dict_value(conf, 'retry', {})

        attempts = retry.get('attempts')
        attempts = get_int(attempts, 0)
        retry['attempts'] = 0 if attempts < 0 else attempts

        statuses = retry.get('statuses')
        if not statuses or not isinstance(statuses, list):
            statuses = [500, 502, 504]
        retry['statuses'] = statuses

        return retry

    def get_request_conf(self, conf: dict, url: str) -> dict:
        """初始化请求参数配置"""
        headers = get_dict_value(conf, 'headers', {})
        method = get_dict_value(conf, 'method', 'get').upper()
        req = {
            'url': url,
            'method': method,
            'headers': headers,
        }

        if method == 'POST':
            # 请求数据项
            data = get_dict_value(conf, 'data', {})
            # 附加函数返回值
            conf_func = get_dict_value(conf, 'use_func_data', [])
            conf_func and data.update(self.use_func_data(conf_func, data))
            if data:
                if get_dict_value(conf, 'type', 'data').lower() == 'json':
                    req['json'] = data
                else:
                    req['data'] = data

        return req

    @staticmethod
    async def get_response(resp: Any, metric: Metric, as_merge_resp: bool) -> Metric:
        """整理响应到指标数据"""
        res = await resp.text()
        data = {
            'response': res,
            'status': resp.status,
            'host': resp.request_info.headers.get('Host', metric.get('host')),
            'headers': dict(resp.headers),
        }
        as_merge_resp and data.update(get_json_loads(res))
        metric.set(**data)
        return metric
