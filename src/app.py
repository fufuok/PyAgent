# -*- coding:utf-8 -*-
"""
    app.py
    ~~~~~~~~

    :author: Fufu, 2021/6/7
"""
from asyncio import Queue, create_task, sleep
from typing import Callable, Optional

from loguru import logger

from .conf.settings import CONF


class Worker:
    """插件工作单元"""

    def __init__(self, name: str) -> None:
        # 插件名称
        self.name = name

        # 数据通道
        self.q_input = Queue()
        self.q_processor = Queue()
        self.q_aggs = Queue()

    async def run(self, cls_input: Callable) -> None:
        """启动插件"""
        # 数据收集
        create_task(cls_input(CONF, None, self.q_input).run())

        # 数据处理
        self.create_tasks('processor', self.q_input, self.q_processor)

        # 汇聚/报警
        self.create_tasks('aggs', self.q_processor, self.q_aggs)

        # 数据发布
        self.create_tasks('output', self.q_aggs, None)

    def create_tasks(self, module: str, in_queue: Queue, out_queue: Optional[Queue]) -> None:
        """启动插件"""
        # 启动系统配置的公共插件, 比如多个公共输出插件
        for cls_name in CONF.get_conf_value(f'main|common_{module}', []):
            cls = CONF.get_plugin_obj(module, cls_name)
            if cls:
                out_queue_next = Queue()
                cls_obj = cls(CONF, in_queue, out_queue_next)
                cls_obj.alias = self.name
                create_task(cls_obj.run())
                in_queue = out_queue_next

        # 启动插件本身
        cls = CONF.get_plugin_obj(module, self.name)
        if cls:
            cls_obj = cls(CONF, in_queue, out_queue)
            cls_obj.alias = self.name
            coro = cls_obj.run()
        else:
            # 克隆 default 插件
            cls_obj = CONF.get_plugin_obj(module, 'default')(CONF, in_queue, out_queue)
            cls_obj.alias = self.name
            coro = cls_obj.run()

        create_task(coro)


async def main() -> None:
    """程序入口"""
    logger.info('PyAgent(v0.2.5.21122417) start working')

    while True:
        await CONF.update()
        CONF.reload()
        await start_plugins()
        await sleep(CONF.reload_sec)


async def start_plugins():
    """启动插件"""
    plugins = CONF.plugins_open - CONF.plugins_working
    for name in plugins:
        # 数据采集插件
        cls_input = CONF.get_plugin_obj('input', name)
        if not cls_input:
            logger.error(f'Plugin {name} does not exist')
            continue

        # 启动插件
        create_task(Worker(name).run(cls_input))
        CONF.plugins_working.add(name)
        logger.info(f'Plugin {name} start working')

    CONF.plugins_working or logger.warning('No plugins are working')
