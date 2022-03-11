---
title: 浅谈Python线程安全
date: 2022-03-10 00:00:00
tags:
  - Python
  - 线程安全
  - 编程
  - 并发
  - 多线程
categories:
  - 编程
---

## 全局解释器锁GIL

Python中通过`GIL（Global Interpreter Lock）`这种互斥锁（`mutual-exclusion lock, mutex`）来防止CPython的多线程环境中受到干扰。

因为在这种环境下，一条线程有可能突然打断另一条线路抢占程序的控制权。如果这种抢占行为来得不是时候，那么解释器的状态（如垃圾回收的引用计数）就会遭到破坏。

> 我们可以通过如下方式来获取Python程序中对象`obj`的引用数
>
> ```python
> import sys
> 
> sys.getrefcount(obj)
> ```

以下面为例，假如没有GIL的情况下，有线程A和线程B两个线程，都引用了同一个对象`obj`。由于没有GIL的存在，A和B两个线程甚至可以在多核CPU上并行执行，忽略其它对`obj`的引用，起始情况下`obj.refcount==2`。

![python-without-gil](python-without-gil.png)



