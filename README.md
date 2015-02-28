wb -- 微博命令行工具
==========

## 简介：
基于 [lxyu/weibo](https://github.com/lxyu/weibo) 项目作为SDK开发的应用. 安装使用前请**确保**本机安装有[Python 2.7.x](https://www.python.org/downloads/), 而不是Python 3.x.x.

能够支持**Linux/Mac/Windows**平台. 运行中若报错, 缺少相应的Python模块, 请使用`pip`命令安装.

关于`pip`的安装, 请移步[这里](https://github.com/zhanglintc/tools-lite/tree/master/misc/pip_install).

**2015.01.08** `setup.py`已经添加依靠`./bin/pip.exe`以及`./requirements.txt`自动下载依赖模块的功能, 以期实现全自动安装.

## 下载：
- 下载最新v0.2版, 点击[这里](https://zhanglintc.github.io/download/wb.zip)
- 查看历史版本：点击[这里](https://github.com/zhanglintc/xiaobawang/releases)

## 安装：

#### Linux/Mac/Windows：
克隆本项目到本地, 或者获取zip文件解压到本地后, 使用命令`python setup.py`即可安装, 然后在命令行中输入`wb`, 若出现相应提示即表明安装成功.

## 使用：

```
    wb -a               # 登录微博账户
    wb -d               # 删除登录信息
    wb -c N             # 获取最新的N条微博, 默认5条
    wb -g N             # 获取最新的N条微博, 默认5条
    wb -p "微博内容"     # 发表新微博, 也可以使用-t参数
    wb -r N "回复内容"   # 回复屏幕显示的第N条微博(或评论), 使用该命令前请务必先使用 -g 或 -c 功能
    wb -h               # 获取帮助信息
```

## 说明：
- **bin**: 一些可能会用到的可执行文件.
- **linux/mac/win**: 各平台安装程序.
- **src**: 程序代码, 入口请查看`wb.py`.
- **setup.py**: 通用安装程序, 会调用相应平台对应文件夹下的安装程序.
- **uninst.py**: 通用卸载程序, 同样调用对应平台的卸载程序进行卸载.


## 其他:
如发现bug, 请邮件联系我或者发issues给我.

其他功能开发中, 敬请关注更新.


