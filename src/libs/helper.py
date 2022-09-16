"""
    helper.py
    ~~~~~~~~
    助手函数集

    :author: Fufu, 2019/9/9
"""
import calendar
import hashlib
import json
import re
import socket
import time
from copy import deepcopy
from datetime import date, datetime, timedelta
from decimal import Decimal
from functools import wraps
from inspect import isfunction
from itertools import chain
from typing import Any, Callable, Optional, Union

from loguru import logger


def try_logger(depth=1, *, as_logger=True, log_tag=''):
    """
    带 Logger 的 try

    e.g.::

        @try_logger()
        def foo():
            1/0

    :param depth: int, 日志记录调用器深度
    :param as_logger: bool, 是否记录日志
    :param log_tag: str, 日志标识文本
    :return:
    """

    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            msg = '{} - {}'.format(log_tag, fn.__name__) if log_tag else fn.__name__
            try:
                if as_logger:
                    logger.opt(depth=depth).debug('try {} start'.format(msg))
                    start = time.perf_counter()
                    res = fn(*args, **kwargs)
                    cost = time.perf_counter() - start
                    logger.opt(depth=depth).debug('try {} end, cost: {:.6f}'.format(msg, cost))
                else:
                    res = fn(*args, **kwargs)
                return res
            except Exception as e:
                as_logger and logger.opt(exception=True).error('try {} error: {}'.format(msg, e))

        return wrapper

    return decorate


def get_plain_text(s):
    """
    获取纯文本内容
    清除 html 标签, 空白字符替换为一个空格, 去除首尾空白

    :param s: str
    :return: str
    """
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip()


def get_uniq_list(data):
    """
    列表去重并保持顺序(数据量大时效率不高)

    :param data: list
    :return: list
    """
    ret = list(set(data))
    ret.sort(key=data.index)
    return ret


def list2dict(key, *value):
    """
    列表转换列表.字典(用于数据记录转字典列表)

    e.g.::

        list2dict(('a', 'b'), [(1, 2), (3, 4)], [('x', 22)])

    :param key: tuple, list, 元组或列表, 与每行数据元素个数相同
    :param value: list.tuple, 一组元组数据
    :return: list.dict
    """
    try:
        return [dict(zip(key, x)) for x in chain(*value)]
    except Exception:
        return []


def data2list(data, sep=','):
    """
    字符串转列表

    :param data: 非字符串和列表外, 其他类型返回空列表
    :param sep: 字符串分隔符
    :return: list
    """
    if isinstance(data, list):
        return data
    elif data and isinstance(data, str):
        return data.split(sep)
    else:
        return []


def get_round(s=None, default=None, precision=2, sep=None):
    """
    检查是否为浮点数, 转换(四舍六入五成双)并返回 float 或 列表

    e.g.::

        # None
        get_round('1a')

        # 0
        get_round('1a', 0)

        # 123.0
        get_round(' 123   ')

        # [123.0, 456.34, 7.0]
        get_round('123, 456.336,, 7,, ,', sep=',')

    :param s: str, 整数值或字符串
    :param default: 转换整数失败时的默认值(列表转换时无效)
    :param precision: 小数位置, 默认 2 位
    :param sep: str, 指定分隔符时返回 list, e.g. [1, 7]
    :return: int / list / default
    """
    if isinstance(s, (float, int, Decimal)):
        return round(float(s), precision)
    elif isinstance(s, str):
        s = s.strip()
        try:
            if sep:
                ret = [round(float(x), precision) for x in s.split(sep) if x.strip() != '']
                ret = get_uniq_list(ret)
            else:
                ret = round(float(s), precision)
        except ValueError:
            ret = [] if sep else default
    else:
        ret = [] if sep else default

    return ret


def get_int(s=None, default=None, sep=None):
    """
    检查是否为整数, 转换并返回 int 或 列表

    e.g.::

        # None
        get_int('1a')

        # 0
        get_int('1a', 0)

        # 123
        get_int(' 123   ')

        # [123, 456, 7]
        get_int('123, 456,, 7,, ,', sep=',')

    :param s: str, 整数值或字符串
    :param default: 转换整数失败时的默认值(列表转换时无效)
    :param sep: str, 指定分隔符时返回 list, e.g. [1, 7]
    :return: int / list / default
    """
    if isinstance(s, int):
        return int(s)
    elif isinstance(s, (float, Decimal)):
        return int(float(s))
    elif isinstance(s, str):
        s = s.strip()
        try:
            if sep:
                ret = [int(x) for x in s.split(sep) if x.strip() != '']
                ret = get_uniq_list(ret)
            else:
                ret = int(s)
        except ValueError:
            ret = [] if sep else default
    else:
        ret = [] if sep else default

    return ret


def get_domain(domain: Optional[str] = None):
    """
    检查是否为标准域名, 清除域名前后空白后返回

    1. 域名长度不超过 255
    2. 每个标签(主机记录)不超过 63 个字符
    3. 只允许字母数字和连字符, 连字符(-)不能连续出现, 也不能出现在头和尾

    :param domain: str
    :return: str|None
    """
    domain = domain.strip()
    patt = r'^(?=^.{3,255}$)(?!^.*?-{2,}.*$)([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$'
    return domain if re.match(patt, domain) else None


def get_extend_domain(domain: Optional[str] = None):
    """
    检查是否为域名, 宽松模式, 清除域名前后空白后返回

    1. 允许使用泛域名 *.fufuok.com
    2. 标签(主机记录)允许使用下划线
    3. 允许中文域名 Punycode 编码 RFC 3492: xn--fiq06l2rdsvs.xn--vuq861b.xn--fiqs8s

    :param domain: str
    :return: str|None
    """
    std_domain = get_domain(domain)
    if std_domain:
        return std_domain

    domain = domain.strip()
    if len(domain) < 3 or len(domain) > 255:
        return None

    # 处理泛域名
    extend_domain = domain[2:] if domain[:2] == '*.' else domain

    patt = r'^([-\w]{1,63}\.)+[-\w]{1,63}$'
    return domain if re.match(patt, extend_domain, re.A) else None


def get_domain_host(host: Optional[str] = None):
    """
    检查主机记录是否正确, 宽松模式, 清除前后空白后返回

    :param host: str
    :return: str|None
    """
    host = host.strip()
    return host if get_extend_domain('{}.f'.format(host)) else None


def get_date(any_dt=None, in_fmt='%Y-%m-%d', out_fmt='', default=True, add_days=0, add_hours=0, add_seconds=0):
    """
    检查日期是否正确并返回日期

    e.g.::

        get_date('2018-10-10')
        get_date('2018-10-10 12:00:00', '%Y-%m-%d %H:%M:%S')
        get_date('1599444062')
        get_date(out_fmt='timestamp000')
        get_date(out_fmt='date')
        get_date(out_fmt='datetime')
        get_date(date(year=2020, month=1, day=1))
        get_date(date(year=2020, month=1, day=1), out_fmt='datetime')

        # '2021-11-05T14:00:00+08:00'
        get_date('2021-11-05T14:00:00.283+08:00', in_fmt='iso', out_fmt='iso')
        get_date('2021-11-05T14:00:00.000Z', in_fmt='iso', out_fmt='iso')


    :param any_dt: mixed, 输入的日期, 空/日期字符串/日期对象/时间戳
    :param in_fmt: str, 源日期格式
    :param out_fmt: str, 返回的日期格式, 默认返回日期对象, 特殊: timestamp 时返回时间戳, timestamp000 毫秒时间戳
    :param default: bool, True 源日期格式不正确时返回今天
    :param add_days: int, 正负数, 与输入日期相差的天数
    :param add_hours: int, 正负数, 与输入日期相差的小时数
    :param add_seconds: int, 正负数, 与输入日期相差的秒数
    :return: datetime|None|str
    """
    dt = None
    if isinstance(any_dt, (datetime, date)):
        dt = any_dt
    else:
        try:
            if in_fmt == 'iso':
                any_dt = str(any_dt).strip()
                in_fmt = '%Y-%m-%dT%H:%M:%S'
                if '.' in any_dt:
                    in_fmt += '.%f'
                if 'Z' in any_dt:
                    in_fmt += 'Z'
                elif '+' in any_dt:
                    tmp = any_dt.split('+')
                    if len(tmp) < 2:
                        any_dt = tmp[0]
                    else:
                        any_dt = tmp[0] + '+' + tmp[1].replace(':', '')
                        in_fmt += '%z'
            dt = datetime.strptime(any_dt, in_fmt)
        except Exception:
            timestamp = get_int(any_dt)
            if timestamp:
                try:
                    dt = datetime.fromtimestamp(timestamp)
                except Exception:
                    pass

    if not dt:
        if default:
            dt = datetime.now()
        else:
            return None

    if add_days and isinstance(add_days, int):
        dt = dt + timedelta(days=add_days)

    if add_hours and isinstance(add_hours, int):
        dt = dt + timedelta(hours=add_hours)

    if add_seconds and isinstance(add_seconds, int):
        dt = dt + timedelta(seconds=add_seconds)

    if not out_fmt:
        return dt
    if out_fmt == 'iso':
        return get_iso_date(dt)
    if out_fmt == 'timestamp000':
        return int(dt.timestamp() * 1000)
    if out_fmt == 'timestamp':
        return int(dt.timestamp())
    if out_fmt == 'datetime':
        if not getattr(dt, 'date', None):
            dt = datetime(dt.year, dt.month, dt.day)
        return dt
    if out_fmt == 'date':
        return dt.date() if getattr(dt, 'date', None) else dt

    return datetime.strftime(dt, out_fmt)


def get_iso_date(any_dt=None, in_fmt='%Y-%m-%d', zone='+08:00'):
    """
    世界时间格式, 默认当前时间
    注: 忽略输入的时区, 结果强制为指定的时区

    e.g.::

        get_iso_date()
        get_iso_date('2020-01-01')
        get_iso_date(date(year=2020, month=1, day=1))
        get_iso_date('2020-01-01 01:02:03', in_fmt='%Y-%m-%d %H:%M:%S')

        # '2021-11-05T14:00:00Z'
        get_iso_date('2021-11-05T14:00:00.000Z', in_fmt='iso', zone='Z')
        get_iso_date('2021-11-05T14:00:00.283+08:00', in_fmt='iso', zone='Z')

    :param any_dt: mixed, 输入的日期, 空/日期字符串/日期对象/时间戳
    :param in_fmt: str, 源日期格式
    :param zone:
    :return:
    """
    return get_date(any_dt, in_fmt=in_fmt, out_fmt='datetime').isoformat(timespec='seconds').split('+')[0] + zone


def get_ymd(dt=None, in_fmt='%Y-%m-%d', out_fmt='%Y-%m-%d', default=True, add_days=0):
    """方便获取年月日格式的日期"""
    return get_date(dt, in_fmt=in_fmt, default=default, add_days=add_days, out_fmt=out_fmt)


def get_next_month_first(dt=None, in_fmt='%Y-%m-%d', out_fmt=''):
    """
    获取日期的下月第一天

    e.g.::

        # 2020-07-01
        get_next_month_first('2020-06-28', out_fmt='%Y-%m-%d')

    :param dt: mixed, 输入的日期, 空/日期字符串/日期对象
    :param in_fmt: str, 源日期格式
    :param out_fmt: str, 返回的日期格式, 默认返回日期对象
    :return: datetime|None|str
    """
    dt = get_date(dt, in_fmt=in_fmt)
    return get_date(datetime(dt.year, dt.month, 1) + timedelta(days=calendar.monthrange(dt.year, dt.month)[1]),
                    out_fmt=out_fmt)


def get_month_last(dt=None, in_fmt='%Y-%m-%d', out_fmt=''):
    """
    获取当月最后一天

    e.g.::

        # 200630 235959
        get_month_last('2020-06-12', out_fmt='%y%m%d %H%M%S')

    :param dt: mixed, 输入的日期, 空/日期字符串/日期对象
    :param in_fmt: str, 源日期格式
    :param out_fmt: str, 返回的日期格式, 默认返回日期对象
    :return: datetime|None|str
    """
    dt = get_next_month_first(dt, in_fmt=in_fmt) + timedelta(seconds=-1)
    return get_date(dt, out_fmt=out_fmt)


def get_last_month_last(dt=None, in_fmt='%Y-%m-%d', out_fmt=''):
    """
    获取上月最后一天

    e.g.::

        # 200531 235959
        get_last_month_last('2020-06-12', out_fmt='%y%m%d %H%M%S')

    :param dt: mixed, 输入的日期, 空/日期字符串/日期对象
    :param in_fmt: str, 源日期格式
    :param out_fmt: str, 返回的日期格式, 默认返回日期对象
    :return: datetime|None|str
    """
    dt = get_date(dt, in_fmt=in_fmt)
    return get_date(datetime(dt.year, dt.month, 1) + timedelta(seconds=-1), out_fmt=out_fmt)


def get_hash(data=None, hash_name='md5', salt=''):
    """
    获取数据的摘要信息

    :param data: str, list, dict...
    :param hash_name: str, e.g. 'md5', 'sha1', 'sha224', 'sha256'...
    :param salt: str
    :return:
    """
    try:
        m = getattr(hashlib, hash_name)(salt if isinstance(salt, bytes) else bytes(str(salt), 'utf-8'))
        m.update(data if isinstance(data, bytes) else bytes(str(data), 'utf-8'))
        return m.hexdigest()
    except Exception:
        return ''


def get_json_loads(s: Any, default: bool = False, *, as_file=False) -> dict:
    """屏蔽错误, 加载 JSON 字符串或文件"""
    if isinstance(s, dict):
        return s
    try:
        if as_file:
            with open(s, 'r') as f:
                return json.load(f)
        else:
            return json.loads(s)
    except Exception:
        return {} if default is False else default


def get_host_ip():
    """
    查询本机 IP 地址

    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def get_dict_value(d, key_path, default=None, *, as_true=True, fix_type=True):
    """
    获取字典键值
    源字典类型错误时, 返回默认值
    获取的结果为假时, 返回默认值
    获取的结果类型自动转换为默认值相同类型, 转换失败返回默认值, 默认值为 None 时不转换

    e.g.::

        # 1
        get_dict_value({'a': {'b': 0}}, '', 1)

        # 1
        get_dict_value({'a': {'b': 0}}, 'a', 1)

        # {'b':0}
        get_dict_value({'a': {'b': 0}}, 'a', {})

        # 1
        get_dict_value({'a': {'b': 0}}, 'a|b', 1)

        # 0
        get_dict_value({'a': {'b': 0}}, 'a|b', 1, as_true=False)

        # 1
        get_dict_value({'a': {'b': 0}}, 'a|b|c', 1)

        # 1
        get_dict_value({'a':True}, 'a', 0)

        # True
        get_dict_value({'a':True}, 'a', False)

        # True
        get_dict_value({'a':True}, 'a', 0, fix_type=False)

        # 0
        get_dict_value({'a':False}, 'a', 0)

        # False
        get_dict_value({'a':False}, 'a',False)

        # False
        get_dict_value({'a':False}, 'a', 0, as_true=False, fix_type=False)

        # 0
        get_dict_value({'a':False}, 'b', 0)

        # 0
        get_dict_value(1, 'b', 0)

        # None
        get_dict_value({'a':False}, 'b')

    :param d: dict
    :param key_path: e.g. x|new_name
    :param default:
    :param as_true: bool, 字典值为假是返回默认值
    :param fix_type: 是否强制修正为 default 相同类型
    :return:
    """
    if not isinstance(d, dict):
        return default

    value = d
    for key in str(key_path).split('|'):
        try:
            value = value.get(key, None)
            if value is None:
                return default
        except Exception:
            return default

    if as_true and not value:
        return default

    if fix_type and default is not None:
        return get_same_type(default, value)

    return value


def get_same_type(src, dst):
    """将 dst 的类型转换为 src 相同的类型"""
    if src is None:
        return dst

    if isinstance(src, bool):
        return get_bool(dst)

    try:
        return type(src)(dst)
    except Exception:
        return src


def get_fn_value(fn, *args, default=None, as_true=True) -> Any:
    """
    获取函数处理后的值

    :param fn: 函数
    :param args: 函数参数
    :param default: 默认值
    :param as_true: bool, 函数返回值为假时返回默认值
    :return:
    """
    if not isfunction(fn):
        return default

    try:
        value = fn(*args)
    except Exception:
        return default

    if as_true and not value:
        return default

    return value


def get_fn_fields(
        src: dict, fn: Callable,
        *,
        name_prefix: str = '', name_suffix: str = '',
        default_value: Any = None, delete_old: bool = False,
        allow_keys: Optional[Union[list, tuple, set]] = None, ban_keys: Optional[Union[list, tuple, set]] = None,
) -> dict:
    """
    函数返回值生成新字段

    :param src:
    :param fn: 生成新值的函数
    :param name_prefix: 新字段前缀
    :param name_suffix: 新字段后缀
    :param default_value: 默认值
    :param delete_old: 是否删除原字段
    :param allow_keys: 只对某些键生成新字段
    :param ban_keys: 不对某些键生成新字段
    :return:
    """
    # 处理结果值非真时是否使用默认值, 默认值 None 时不启用
    as_true = False if default_value is None else True

    for k, v in list(src.items()):
        if k in ban_keys or allow_keys and k not in allow_keys:
            continue

        # 执行函数, 参数为字段值, 如: human_bps(1000)
        value = get_fn_value(fn, v, default=default_value, as_true=as_true)

        # 是否删除原字段
        delete_old and src.pop(k, None)

        # 增加新值字段
        key = f'{name_prefix}{k}{name_suffix}'
        src[key] = value

    return src


def get_str(v: Any) -> str:
    """转换为字符串"""
    return str(v)


def get_comma(n: Union[int, float]) -> str:
    """千分位分隔"""
    return '{:,}'.format(n)


def get_bool(v: Any) -> bool:
    """转换为布尔值"""
    return str(v) in ('1', 't', 'T', 'true', 'TRUE', 'True')


def merge_dicts(a: dict, b: dict, merge_sub_dict: bool = True) -> dict:
    """
    深拷贝, 扩展合并字典
    默认包含对下级字典合并, 保留只在 a 中存在的键值
    合并失败时, 返回空字典

    e.g.::

        a = {'a': {'a1': 1, 'a2': 2}, 'b': 3, 'e': 7}
        b = {'a': {'a1': 'f', 'a3': 3}, 'b': {'b1': 5}, 'd': 6}

        # {'a': {'a1': 'f', 'a3': 3, 'a2': 2}, 'b': {'b1': 5}, 'e': 7, 'd': 6}
        z = extend_dict(a, b)

        # {'a': {'a1': 'f', 'a3': 3}, 'b': {'b1': 5}, 'e': 7, 'd': 6}
        z = extend_dict(a, b, False)

    :param a:
    :param b:
    :param merge_sub_dict: True, 扩展合并下一级的字典
    :return:
    """
    try:
        c = deepcopy(a)
        c.update(deepcopy(b))
    except Exception:
        return {}

    if merge_sub_dict:
        for k in list(c.keys()):
            if isinstance(c[k], dict):
                d = get_dict_value(a, k, {})
                d and c[k].update({x: y for x, y in d.items() if x not in c[k]})

    return c
