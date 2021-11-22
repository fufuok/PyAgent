# PyAgent (运维监控和指标采集客户端框架)

## 功能

基于 asyncio 的高性能/插件式 Python Agent, 跨平台的运维监控和指标采集框架. 兼容 Windows/Linux, 灵感来自于: `Telegraf`

- 配置远程管理, 自动拉取更新, 动态加载插件和配置
- 插件式, 易扩展, 插件自动扫描/静态注册(默认)
- 轻量协程, 资源占用低, 若有阻塞类代码请放入线程执行
- 脚手架, 请根据业务需要编写插件即可
  - 基础插件: `demo`, `cpu`, `mem`, `disk`, `curl`, `network`, `ping`, `telnet`

## 依赖

兼容 `Python-3.8.5+`, 依赖见: [requirements.txt](requirements.txt)

## 配置

若要使用自动拉取配置, 请参考 `src/conf/config.py` 中的 `update()` 方法接入自己的配置中心接口.

配置文档采用 YAML 格式, 系统有 3 重可选配置, 优先级为:

```
各插件本地目录(input/processor/aggs/output)
  > host.yaml(适配在线管理的基于主机 IP 的配置)
    > main.yaml(适配在线管理的全局默认配置, 针对所有主机)
```

## 使用

直接源码运行:

```shell
pip3 install -r requirements.txt
python3 main.py
# nohup ./main.py >./log/run.log 2>&1 &
```

```shell
root@DevBeta:~/py/pyagent# python3 main.py 
2021-11-15 10:20:39.680 | DEBUG | src.conf.config.init_logger:288 | 日志初始化完成
2021-11-15 10:20:39.681 | INFO | src.app.main:71 | PyAgent(v0.1.0) start working
2021-11-15 10:20:39.695 | INFO | src.app.start_plugins:93 | Plugin cpu start working
2021-11-15 10:20:39.696 | INFO | src.app.start_plugins:93 | Plugin mem start working
2021-11-15 10:20:39.697 | INFO | src.app.start_plugins:93 | Plugin disk start working
2021-11-15 10:20:39.699 | DEBUG | src.input.run:25 | input.cpu is working
2021-11-15 10:20:39.699 | DEBUG | src.processor.run:25 | processor.default(cpu) is working
2021-11-15 10:20:39.700 | DEBUG | src.aggs.run:26 | aggs.cpu(cpu) is working
2021-11-15 10:20:39.701 | DEBUG | src.output.run:25 | output.console(cpu) is working
2021-11-15 10:20:39.701 | DEBUG | src.output.es.run:30 | output.es(cpu) is working
2021-11-15 10:20:39.702 | DEBUG | src.output.default.run:21 | output.default(cpu) is working
2021-11-15 10:20:39.702 | DEBUG | src.input.run:25 | input.mem is working
2021-11-15 10:20:39.702 | DEBUG | src.processor.run:25 | processor.default(mem) is working
2021-11-15 10:20:39.703 | DEBUG | src.aggs.run:26 | aggs.mem(mem) is working
2021-11-15 10:20:39.703 | DEBUG | src.output.run:25 | output.console(mem) is working
2021-11-15 10:20:39.703 | DEBUG | src.output.es.run:30 | output.es(mem) is working
2021-11-15 10:20:39.704 | DEBUG | src.output.default.run:21 | output.default(mem) is working
2021-11-15 10:20:39.704 | DEBUG | src.input.run:25 | input.disk is working
2021-11-15 10:20:39.704 | DEBUG | src.processor.run:25 | processor.default(disk) is working
2021-11-15 10:20:39.705 | DEBUG | src.aggs.run:26 | aggs.disk(disk) is working
2021-11-15 10:20:39.705 | DEBUG | src.output.run:25 | output.console(disk) is working
2021-11-15 10:20:39.705 | DEBUG | src.output.es.run:30 | output.es(disk) is working
2021-11-15 10:20:39.706 | DEBUG | src.output.default.run:21 | output.default(disk) is working
>>> METRIC, name=mem time=2021-11-15T10:20:39+08:00 timestamp=1636942839 node_ip=0.0.0.0 host=WebServer total=8348397568 available=5567897600 percent=33.3 used=2422042624 free=433340416 active=3699130368 inactive=3444563968 buffers=349544448 cached=5143470080 shared=46780416 slab=621330432 human_total=7.8 GB human_available=5.2 GB human_used=2.3 GB human_free=413.3 MB human_active=3.4 GB human_inactive=3.2 GB human_buffers=333.4 MB human_cached=4.8 GB human_shared=44.6 MB human_slab=592.5 MB
>>> METRIC, name=disk time=2021-11-15T10:20:39+08:00 timestamp=1636942839 node_ip=0.0.0.0 host=WebServer device=/dev/sda2 mountpoint=/ fstype=ext4 opts=rw,relatime maxfile=255 maxpath=4096 total=42004086784 used=22808981504 free=17031004160 percent=57.3 human_total=39.1 GB human_used=21.2 GB human_free=15.9 GB
>>> METRIC, name=cpu time=2021-11-15T10:20:39+08:00 timestamp=1636942839 node_ip=0.0.0.0 host=WebServer cpu_logical_count=4 cpu_count=4 cpu_percent=2.4 cpu_times={'user': 1803486.75, 'nice': 4242.65, 'system': 437369.76, 'idle': 62342010.14, 'iowait': 3763.82, 'irq': 0.0, 'softirq': 97654.76, 'steal': 0.0, 'guest': 0.0, 'guest_nice': 0.0} cpu_stats={'ctx_switches': 17157214700, 'interrupts': 14394108423, 'soft_interrupts': 18238331768, 'syscalls': 0} cpu_freq={'current': 3300.0, 'min': 0.0, 'max': 0.0}
```

或用 `pyinstaller` 打包后运行, 配置文件目录 `etc` 与 `main.exe` 放在同一目录.

(注: 若要打包请看: `src/conf/config.py` 中 `self.plugins = PLUGINS` 处的注释, 如果要在 Windows 7 或 2008 上运行, 最好使用 Python-3.8)

`dist` 是单配置文件示例.

打包命令参考:

```shell
pyinstaller -p E:\Python\github\PyAgent\venvw\Lib\site-packages -F main.py -i doc\f.ico
```

![windows-demo](doc/windows-demo.png)

## 结构

`etc/main.yaml` 必须, 主配置文件, 可以包含所有子配置内容, 也可以将插件配置分别写到下面的目录(优先使用).

```
.
├── doc               设计文档
├── etc               配置文件目录
│   ├── aggs          数据聚合(报警)插件的配置项
│   ├── input         输入(数据采集)插件的配置项
│   ├── output        输出插件的配置项
│   └── processor     数据处理插件的配置项
├── log               日志文件
├── src               代码
│   ├── aggs          插件: 数据聚合(报警)
│   ├── common        公共插件
│   ├── conf          配置处理
│   ├── input         插件: 输入
│   ├── libs          公共类库
│   ├── output        插件: 输出
│   ├── processor     插件: 数据处理
│   └── test          单元测试
└── venvw
```

## 设计

![PyAgent](doc/pyagent.png)







*ff*