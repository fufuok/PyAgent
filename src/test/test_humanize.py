# -*- coding:utf-8 -*-
"""
    test_humanize.py
    ~~~~~~~~

    :author: Fufu, 2021/6/12
"""
import unittest
from ..libs.humanize import *


class HumanTestCase(unittest.TestCase):
    def test_human_bytes(self):
        for a, b in {
            ('0 B', 0),
            ('1 B', 1),
            ('999 B', 999),
            ('1023 B', 1023),
            ('1.0 KB', 1024),
            ('1.0 MB', 1024 * 1024),
            ('1.0 GB', 1024 * 1024 * 1024),
            ('1.0 TB', 1 << 4 * 10),
            ('1.0 PB', 1 << 5 * 10),
            ('1.0 EB', 1 << 6 * 10),
            ('2.0 ZB', 2 << 7 * 10),
            ('3.0 YB', 3 << 8 * 10),

            ('1.0 MB', 1024 * 1024 - 1),
            ('11.8 MB', 12345678),
            ('11.5 GB', 12345678900),
        }:
            self.assertEqual(a, human_bytes(b))

    def test_human_1k_bytes(self):
        for a, b in {
            ('0 B', 0),
            ('1 B', 1),
            ('999 B', 999),
            ('1.0 KB', 1000),
            ('1.0 MB', 1000 ** 2),
            ('1.0 GB', 1000 ** 3),
            ('1.0 TB', 1000 ** 4),
            ('1.0 PB', 1000 ** 5),
            ('1.0 EB', 1000 ** 6),
            ('1.0 ZB', 1000 ** 7),
            ('1.0 YB', 1000 ** 8),

            ('1.0 MB', 1000 * 1000 - 1),
            ('12.3 MB', 12345678),
            ('12.3 GB', 12345678900),
        }:
            self.assertEqual(a, human_1k_bytes(b))

    def test_human_kib(self):
        for a, b in {
            ('0 B', 0),
            ('1 B', 1),
            ('999 B', 999),
            ('1023 B', 1023),
            ('1.0 KiB', 1024),
            ('1.0 MiB', 1024 * 1024),
            ('1.0 GiB', 1024 * 1024 * 1024),
            ('1.0 TiB', 1 << 4 * 10),
            ('1.0 PiB', 1 << 5 * 10),
            ('1.0 EiB', 1 << 6 * 10),
            ('2.0 ZiB', 2 << 7 * 10),
            ('3.0 YiB', 3 << 8 * 10),

            ('1.0 MiB', 1024 * 1024 - 1),
            ('11.8 MiB', 12345678),
            ('11.5 GiB', 12345678900),
        }:
            self.assertEqual(a, human_kib(b))

    def test_human_bit(self):
        for a, b in {
            ('0 b', 0),
            ('1 b', 1),
            ('999 b', 999),
            ('1.0 Kb', 1000),
            ('1.0 Mb', 1000 ** 2),
            ('1.0 Gb', 1000 ** 3),
            ('1.0 Tb', 1000 ** 4),
            ('1.0 Pb', 1000 ** 5),
            ('1.0 Eb', 1000 ** 6),
            ('1.0 Zb', 1000 ** 7),
            ('1.0 Yb', 1000 ** 8),

            ('1.0 Mb', 1000 * 1000 - 1),
            ('12.3 Mb', 12345678),
            ('12.3 Gb', 12345678900),
        }:
            self.assertEqual(a, human_bit(b))

    def test_human_bps(self):
        for a, b in {
            ('0 bps', 0),
            ('1 bps', 1),
            ('999 bps', 999),
            ('1.0 Kbps', 1000),
            ('1.0 Mbps', 1000 ** 2),
            ('1.0 Gbps', 1000 ** 3),
            ('1.0 Tbps', 1000 ** 4),
            ('1.0 Pbps', 1000 ** 5),
            ('1.0 Ebps', 1000 ** 6),
            ('1.0 Zbps', 1000 ** 7),
            ('1.0 Ybps', 1000 ** 8),

            ('1.0 Mbps', 1000 * 1000 - 1),
            ('12.3 Mbps', 12345678),
            ('12.3 Gbps', 12345678900),
        }:
            self.assertEqual(a, human_bps(b))

    def test_human_base(self):
        self.assertEqual('12345.68 千字节', human_base(12345678, prec=2, base=1000, sizes=['byte', '千字节']))
        self.assertEqual('12345.68 千位/秒', human_base(12345678, prec=2, base=1000, sizes=['bit/s', '千位/秒']))
        self.assertEqual('12056.33 KB.1024进制', human_base(12345678, prec=2, base=1024, sizes=['B', 'KB.1024进制']))
        self.assertEqual(human_bytes(12345678), human_base(12345678))


if __name__ == '__main__':
    unittest.main()
