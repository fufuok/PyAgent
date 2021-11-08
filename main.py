#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
    main.py
    ~~~~~~~~

    :author: Fufu, 2021/6/7
"""
from asyncio import run
from icmplib import async_ping

from src.app import main

if __name__ == '__main__':
    run(main())
