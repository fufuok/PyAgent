# -*- coding:utf-8 -*-
"""
    plugins.py
    ~~~~~~~~
    插件集, 静态注册(方便打包)

    :author: Fufu, 2021/6/13
"""
from ..common import converter
from ..input import (demo as input_demo, cpu as input_cpu, mem as input_mem, disk as input_disk,
                     network as input_network, curl as input_curl, telnet as input_telnet, ping as input_ping)
from ..processor import default as processor_default, demo as processor_demo
from ..aggs import (default as aggs_default, demo as aggs_demo, cpu as aggs_cpu, curl as aggs_curl,
                    telnet as aggs_telnet, disk as aggs_disk, mem as aggs_mem, network as aggs_network,
                    ping as aggs_ping)
from ..output import default as output_default, console as output_console, es as output_es

PLUGINS = {
    'common': {
        'converter': converter.Converter,
    },
    'input': {
        'demo': input_demo.Demo,
        'cpu': input_cpu.Cpu,
        'mem': input_mem.Mem,
        'disk': input_disk.Disk,
        'network': input_network.Network,
        'curl': input_curl.Curl,
        'telnet': input_telnet.Telnet,
        'ping': input_ping.Ping
    },
    'processor': {
        'default': processor_default.Default,
        'demo': processor_demo.Demo,
    },
    'aggs': {
        'default': aggs_default.Default,
        'demo': aggs_demo.Demo,
        'cpu': aggs_cpu.Cpu,
        'curl': aggs_curl.Curl,
        'telnet': aggs_telnet.Telnet,
        'disk': aggs_disk.Disk,
        'mem': aggs_mem.Mem,
        'network': aggs_network.Network,
        'ping': aggs_ping.Ping,
    },
    'output': {
        'default': output_default.Default,
        'console': output_console.Console,
        'es': output_es.Es,
    }
}
