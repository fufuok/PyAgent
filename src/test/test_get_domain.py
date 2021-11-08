# -*- coding:utf-8 -*-
"""
    test_get_domain.py
    ~~~~~~~~

    :author: Fufu, 2021/9/15
"""
import unittest
from ..libs.helper import get_domain, get_extend_domain, get_domain_host


class TestGetDomain(unittest.TestCase):

    def test_get_domain(self):
        for a, b in {
            (None, 'f'),
            ('f.cn', 'f.cn'),
            ('7.cn', '7.cn'),
            ('f.cn', "\t f.cn \n "),
            (None, 'f .cn'),
            ('f-f.com.cn', 'f-f.com.cn'),
            (None, 'f--f.cn'),
            (None, '-f.cn'),
            (None, 'f-.cn'),
            (None, 'f_.cn'),
            (None, 'f_f.cn'),
            (None, 'f.f'),
            (None, 'f.77'),
            ('f.{}'.format('f' * 63), 'f.{}'.format('f' * 63)),
            ('f.{}.cn'.format('f' * 63), 'f.{}.cn'.format('f' * 63)),
            (None, 'f.{}'.format('f' * 64)),
            (None, 'f.{}.cn'.format('f' * 64)),
            (None, '_.f.cn'),
            (None, '*.f.cn'),
            (None, 'xn--fiq06l2rdsvs.xn--vuq861b.xn--fiqs8s'),
        }:
            self.assertEqual(a, get_domain(b))

    def test_get_domain_extend(self):
        for a, b in {
            (None, 'f'),
            ('f.cn', 'f.cn'),
            ('7.cn', '7.cn'),
            ('f.cn', "\t f.cn \n "),
            (None, 'f .cn'),
            ('f-f.com.cn', 'f-f.com.cn'),
            ('f--f.cn', 'f--f.cn'),
            ('-f.cn', '-f.cn'),
            ('f-.cn', 'f-.cn'),
            ('f_.cn', 'f_.cn'),
            ('f_f.cn', 'f_f.cn'),
            ('f.f', 'f.f'),
            ('f.77', 'f.77'),
            ('f.{}'.format('f' * 63), 'f.{}'.format('f' * 63)),
            ('f.{}.cn'.format('f' * 63), 'f.{}.cn'.format('f' * 63)),
            (None, 'f.{}'.format('f' * 64)),
            (None, 'f.{}.cn'.format('f' * 64)),
            ('_.f.cn', '_.f.cn'),
            ('*.f.cn', '*.f.cn'),
            ('xn--fiq06l2rdsvs.xn--vuq861b.xn--fiqs8s', 'xn--fiq06l2rdsvs.xn--vuq861b.xn--fiqs8s'),
        }:
            self.assertEqual(a, get_extend_domain(b))

    def test_get_domain_host(self):
        for a, b in {
            ('f', 'f'),
            ('f' * 63, 'f' * 63),
            (None, 'f' * 64),
            ('f.cn', 'f.cn'),
            ('7.cn', '7.cn'),
            ('f.cn', "\t f.cn \n "),
            (None, 'f .cn'),
            ('f-f.com.cn', 'f-f.com.cn'),
            ('f--f.cn', 'f--f.cn'),
            ('-f.cn', '-f.cn'),
            ('f-.cn', 'f-.cn'),
            ('f_.cn', 'f_.cn'),
            ('f_f.cn', 'f_f.cn'),
            ('f.f', 'f.f'),
            ('f.77', 'f.77'),
            ('f.{}'.format('f' * 63), 'f.{}'.format('f' * 63)),
            ('f.{}.cn'.format('f' * 63), 'f.{}.cn'.format('f' * 63)),
            (None, 'f.{}'.format('f' * 64)),
            (None, 'f.{}.cn'.format('f' * 64)),
            ('_.f.cn', '_.f.cn'),
            ('*.f.cn', '*.f.cn'),
            ('xn--fiq06l2rdsvs.xn--vuq861b.xn--fiqs8s', 'xn--fiq06l2rdsvs.xn--vuq861b.xn--fiqs8s'),
        }:
            self.assertEqual(a, get_domain_host(b))


if __name__ == '__main__':
    unittest.main()
