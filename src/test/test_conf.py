# -*- coding:utf-8 -*-
"""
    test_conf.py
    ~~~~~~~~

    :author: Fufu, 2021/6/7
"""
from ..conf.config import Config


def test_get_yaml():
    txt_conf = '''# 启用的插件
open:
  - demo
  - mem
  - cpu

# 采集时间间隔(公共的)
interval: 1000'''
    res = Config.load_yaml(txt_conf)
    assert isinstance(res, dict)
    assert len(res) == 2
    assert isinstance(res.get('open'), list)
    assert 'cpu' in res.get('open', [])
