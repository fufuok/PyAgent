# -*- coding:utf-8 -*-
"""
    test_extend_dict.py
    ~~~~~~~~

    :author: Fufu, 2021/11/10
"""
from ..libs.helper import extend_dict


def test_extend_dict():
    a = {'a': {'a1': 1, 'a2': 2}, 'b': 3, 'e': 7}
    b = {'a': {'a1': 'f', 'a3': 3}, 'b': {'b1': 5}, 0: 6}

    c = extend_dict(a, b)
    assert isinstance(c, dict)
    assert c['a']['a1'] == 'f'
    assert c['a']['a2'] == 2
    assert c['b']['b1'] == 5
    assert c['e'] == 7
    assert c[0] == 6

    d = extend_dict(a, b, False)
    assert isinstance(d, dict)
    assert d['a']['a1'] == 'f'
    assert d['a'].get('a2') is None
    assert c['b']['b1'] == 5
    assert d['e'] == 7
    assert d[0] == 6

    e = 1
    f = extend_dict(a, e)
    assert isinstance(f, dict)
    assert not f
