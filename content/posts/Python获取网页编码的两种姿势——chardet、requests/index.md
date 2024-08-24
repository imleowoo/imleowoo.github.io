---
title: Python获取网页编码的两种姿势——chardet、requests
summary: Python开发中通常使用自带的urllib模块和第三方requests模块来发起HTTP请求。请求响应结果输出可能会出现页面乱码的情况，通常是因为编码格式不匹配造成的，一般匹配好HTML文件的编码格式就可解决乱码问题。urllib和requests都提供了获取页面编码格式的函数，看看其分别如何使用。
author: Leo
date: 2017-12-12 16:57:22
tags:
  - Python
  - 爬虫
  - HTML
categories:
  - Tips
---

## 运行环境

> - `Python 3.6`
> - `requests==2.18.4`

## `chardet`模块

```python
In[2]: import requests
In[3]: resp = requests.get('http://baidu.com')
In[4]: resp
Out[4]: <Response [200]>
In[5]: resp.encoding
Out[5]: 'ISO-8859-1'
```

## `requests`模块

```python
In[2]: import chardet
In[3]: from urllib.request import urlopen
In[4]: url = 'http://www.baidu.com'
In[5]: html = urlopen(url).read()
In[6]: print(chardet.detect(html))
{'encoding': 'utf-8', 'confidence': 0.99, 'language': ''}
```
