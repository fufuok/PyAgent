# -*- coding:utf-8 -*-
"""
    demo.py
    ~~~~~~~~
    示例数据处理插件
    可以删除该文件, processor.demo.yaml 配置依然生效

    :author: Fufu, 2021/6/7
"""
from . import ProcessorPlugin


class Demo(ProcessorPlugin):
    """示例数据处理"""

    name = 'demo'
