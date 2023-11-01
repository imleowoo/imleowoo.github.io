---
title: "定期清理Airflow数据库"
description:
author: Leo
date: 2023-09-20 20:30:00
tags:
  - Airflow
  - apache-airflow
  - 调度
  - 数据库
  - crontab
categories:
  - 编程
---

# 运行环境

> - 操作系统：Darwin LEIdeMacBookPro.lan 23.0.0 Darwin Kernel Version 23.0.0: Fri Sep 15 14:41:43 PDT 2023; root:xnu-10002.1.13~1/RELEASE_ARM64_T6000 arm64
> - Python版本：Python 3.10.9 (main, Jan 31 2023, 16:44:05) [Clang 14.0.0 (clang-1400.0.29.202)] on darwin
> - Airflow版本：2.6.2
> - Airflow Database Backend: MySQL 5.7

# 背景

我所在的项目使用 airflow 作为任务调度器。
其中活跃的Active DAGs有400+，并且大部分DAGs的调度间隔都小于一小时。频繁的任务和大量的task使得运行一个月数据库就能产生超过10GB的数据。
数据库数据量增大后，出现了以下问题： 
1. 访问 airflow webserver 时页面响应缓慢；
2. 查询量过大，在极端情况下直接导致MySQL实例发生OOM。

所以为提高运行效率和稳定，计划定期清理 airflow 产生的数据。

# 清理 airflow 数据库

# airflow 数据表

```text
mysql> use airflow;
Database changed
mysql> show tables;
+--------------------------------+
| Tables_in_airflow              |
+--------------------------------+
| ab_permission                  |  > 存储与权限相关的信息，用于管理用户对 DAG 和其他资源的权限
| ab_permission_view             |  > 将权限与可视化视图相关联，用于管理用户对可视化视图的权限
| ab_permission_view_role        |  > 将权限、视图和角色关联在一起，用于管理用户在特定视图上的角色和权限
| ab_register_user               |  > 存储已注册用户的信息，通常与基于 Web 的用户身份验证相关
| ab_role                        |  > 存储定义的角色信息，用于将角色分配给用户和资源
| ab_user                        |  > 存储用户的信息，用于身份验证和授权
| ab_user_role                   |  > 将用户与角色关联，用于管理用户的角色和权限
| ab_view_menu                   |  > 存储可视化视图的信息，包括菜单和页面的层次结构
| alembic_version                |  > 存储 Alembic 数据库迁移的版本信息
| callback_request               |  > 存储回调请求信息，通常与外部系统的回调相关
| connection                     |  > 存储与外部系统的连接信息，例如数据库连接
| dag                            |  > 存储定义的 DAG（Directed Acyclic Graph）的信息，包括 DAG 的名称、描述等
| dag_code                       |  > 存储 DAG 的代码
| dag_owner_attributes           |  > 存储 DAG 所有者的属性
| dag_pickle                     |  > 存储 DAG 对象的序列化版本
| dag_run                        |  > 存储 DAG 运行的信息，每次 DAG 运行都会创建一个新的记录
| dag_run_note                   |  > 存储与 DAG 运行相关的注释
| dag_schedule_dataset_reference |  > 存储 DAG 的调度数据集引用
| dag_tag                        |  > 存储 DAG 的标签信息
| dag_warning                    |  > 存储 DAG 相关的警告信息
| dagrun_dataset_event           |  > 存储 DAG 运行数据集事件
| dataset                        |  > 存储数据集的信息
| dataset_dag_run_queue          |  > 存储数据集与 DAG 运行队列的关联信息
| dataset_event                  |  > 存储数据集事件的信息
| import_error                   |  > 存储 DAG 导入错误信息
| job                            |  > 存储作业信息，例如执行任务实例
| log                            |  > 存储日志信息
| log_template                   |  > 存储日志模板
| rendered_task_instance_fields  |  > 存储渲染的任务实例字段
| serialized_dag                 |  > 存储序列化的 DAG 对象
| session                        |  > 存储会话信息，用于数据库交互
| sla_miss                       |  > 存储 SLA（Service Level Agreement）错过的信息
| slot_pool                      |  > 存储任务槽池信息
| task_fail                      |  > 存储任务失败的信息
| task_instance                  |  > 存储任务实例的信息
| task_instance_note             |  > 存储任务实例的注释
| task_map                       |  > 存储任务映射信息
| task_outlet_dataset_reference  |  > 存储任务出口数据集引用
| task_reschedule                |  > 存储任务重新调度信息
| trigger                        |  > 存储触发器信息
| variable                       |  > 存储可变变量信息
| xcom                           |  > 存储 XCom（交流）数据，用于任务之间的数据传递
+--------------------------------+
42 rows in set (0.00 sec)
```

# 参考

> - [清理 Airflow 数据库](https://cloud.google.com/composer/docs/composer-2/cleanup-airflow-database?hl=zh-cn)
> - [Apache Airflow Documents](https://airflow.apache.org/docs/apache-airflow/stable/index.html)