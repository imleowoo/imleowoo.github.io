---
title: （译）在Python中如何使用生成器和yield
date: 2022-09-28 18:00:00
tags:
---

> 原文地址：[How to Use Generators and yield in Python - Real Python](https://realpython.com/introduction-to-python-generators/#creating-data-pipelines-with-generators)

# 前言

你是否有过处理大量的数据集，以至于它的大小超过了处理机的内存？或者说你有一个复杂的函数，每次调用的时候都需要维护一个内部的状态，但是这个函数太小，小到没有必要创建一个类。在这样一系列情况下，生成器Generators和 Python `yield` 语句可以派上用场。

阅读完这篇文章，你可以了解以下：

- 什么是生成器Generators，以及如何使用它；
- 如何写生成器函数和表达式；
- Python `yield` 语句是如何工作的；
- 在一个生成器函数中如何使用多个Python `yield` 语句；
- 如何使用高级的生成器方法；
- 如何使用多个生成器来构建数据管道Pipelines。

如果你是一个初学者或着中级的Python使用者，并且对使用更加Pythonic的方式处理大型数据集感兴趣，这个教程会很适合你。

> 下载数据集：[单击此处下载教程中用到的数据集](https://realpython.com/bonus/generators-yield/)来学习使用生成器 generators 和 Python `yield`。或者直接访问 [github 地址](https://github.com/realpython/materials/blob/master/generators/techcrunch.csv)。

# 使用生成器

在 [PEP 255](https://peps.python.org/pep-0255/) 中提出，生成器函数是一种特殊的函数，它会返回一个[惰性迭代器](https://en.wikipedia.org/wiki/Lazy_evaluation)。这些惰性迭代器对象可以像列表一样循环。然而和列表不同的事，惰性迭代器不会将其内容存储在内存中。有关Python迭代器的概述，可以看看这篇博客《**[Python "for" Loops (Definite Iteration)](https://realpython.com/python-for-loop/)**》。

大致了解了生成器的作用后，现在通过两个简单的例子来看看他是如何使用的。首先大致地了解生成器的工作原理，再认真剖析每一个示例。

## 示例1：读取大文件

生成器时常会用于处理大型的数据流或文件。比如CSV这种文本文件，使用逗号`,`将数据分隔为列。这种格式经常用来共享传播数据。假如现在需要计算CSV文件中的行数应该怎么办？

就类似于下面代码块这样

```python
csv_gen = csv_reader("some_csv.txt")
row_count = 0

for row in csv_gen:
    row_count += 1

print(f"Row count is {row_count}")
```

从这个示例中看到，可能期望对象`csv_gen`是一个列表。若要填充该列表，函数`csv_reader()`内应该打开这个csv文件，并将其内容加载到`csv_gen`中。然后遍历列表元素，并每次为计数对象 `row_count` 递增`+1`。

上面的例子已经解决了问题。但是如果文件很大，这样的实现方式是否还是有效的？当文件大于可用的内存应该怎么办？在上面提到的`csv_gen`是一个列表，假设`csv_reader()` 只是打开文件并将其读入数组：

```python
def csv_reader(file_name):
    file = open(file_name)
    result = file.read().split("\n")
    return result
```

在 函数 `csv_reader()` 中打开了一个给定的文件，并使用 `file.read().split("\n")`将每一行作为一个单独的元素添加到了列表中。当文件大于了可用内存时，会出现以下现象输出：

```bash
Traceback (most recent call last):
  File "ex1_naive.py", line 22, in <module>
    main()
  File "ex1_naive.py", line 13, in main
    csv_gen = csv_reader("file.txt")
  File "ex1_naive.py", line 6, in csv_reader
    result = file.read().split("\n")
MemoryError
```

在这种情况下，虽然 open() 返回一个~~生成器对象~~迭代器对象，可以逐行的惰性迭代它。但是在`file.read().split("\n")`会一次性将所有数据加载到内存中，引起`MemoryError`。

程序运行过程中，发生`MemoryError`之前，可能会留意到计算机运行变得缓慢，甚至需要使用`KeyboardInterrupt` 来终止它。那应该怎么处理大量的数据？把函数`csv_reader()`改造一下：

```python
def csv_reader(file_name):
    for row in open(file_name, "r"):
        yield row
```

使用改造后的`csv_reader()` 后，重新运行程序时，会打开文件并遍历它，生成一行数据，并不会出现内存错误，并且输出了结果：

```bash
Row count is 64186394
```

改造后的函数变化在于，将 `csv_reader()`变成了一个生成器函数。遍历文件的每一行时，会返回改行的数据，并不会产生所有行的数据后再一并返回。

另外可以利用生成器推导式，可以在不调用函数的情况下使用生成器。

```python
csv_gen = (row for row in open(file_name))
```

使用推导式看起来是很简洁的，接下来会开始了解Python `yield` 语句的更多信息。使用`yield` 时有这两个关键区别：

- 使用 `yield` 会把普通函数变成一个生成器函数；
- 如果将函数中的关键词`yield` 换成 `return` 只会返回文件的第一行。

## 示例2：生成无限的序列

换个角度来看看无限序列如何生成。在Python中，可以使用 `range()` 来获得一个有限的序列，并且可以在该对象作用域上下文中使用它：

```python
>>> a = range(5)
>>> list(a)
[0, 1, 2, 3, 4]
```

计算机内存是有限的，如果需要生成无限序列则需要使用生成器。

```python
def infinite_sequence():
    num = 0
    while True:
        yield num
        num += 1
```

如上代码块所示，初始化变量 `num=0` 并开始一个无限循环，执行到 `yield num` 时得到了`num`的初始状态。

在 `yield` 之后，会将 `num` 执行加1操作。如果使用 `for` 循环遍历这个函数，会发现是无限产生的。

```python
>>> for i in infinite_sequence():
...     print(i, end=" ")
...
0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29
30 31 32 33 34 35 36 37 38 39 40 41 42
[...]
6157818 6157819 6157820 6157821 6157822 6157823 6157824 6157825 6157826 6157827
6157828 6157829 6157830 6157831 6157832 6157833 6157834 6157835 6157836 6157837
6157838 6157839 6157840 6157841 6157842
KeyboardInterrupt
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
```

程序会持续执行，直到手动去终止它（如使用 ctrl+C）。

除了使用`for`循环外，还可以使用`next()` 直接调用生成器对象。在控制台中这样测试生成器特别方便有用：

```python
>>> gen = infinite_sequence()
>>> next(gen)
0
>>> next(gen)
1
>>> next(gen)
2
>>> next(gen)
3
```

上面代码块中，得到了一个生成器对象 gen，使用next(gen) 重复调用手动迭代它。这种方法可以很好的检查得到的生成器对象，是否符合预期输出。

> 注意：当使用`next()`时，Python会调用 `.__next__()` 函数

## 示例3：检测回文

将产生的无限序列用于构建回文检测器。回文检测器将判定所有属于回文的字母和数字序列。这样的回文字符串 <u>从左往后</u> 和 <u>从右往左</u> 读起来都是相同的单词或数字，例如 <u>121</u>、<u>abba</u>。

首先定义一个数字的回文检测器，具体的实现如下：

```python
def is_palindrome(num):
    # Skip single-digit inputs
    if num // 10 == 0:
        return False
    temp = num
    reversed_num = 0

    while temp != 0:
        reversed_num = (reversed_num * 10) + (temp % 10)
        temp = temp // 10

    if num == reversed_num:
        return num
    else:
        return False
```

先不用急着去理解函数`is_palindrome(num)`的处理逻辑。简单来讲，该函数接手一个传入的数字后将其反转，然后检查反转后的数字是否与输入的原始数字相同。

现在整合一下无限序列生成器和回文检测函数，用于获取所有回文数字。

```python
>>> for i in infinite_sequence():
...     pal = is_palindrome(i)
...     if pal:
...         print(i)
...
11
22
33
[...]
99799
99899
99999
100001
101101
102201
KeyboardInterrupt
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
  File "<stdin>", line 5, in is_palindrome
```

> 注意：在实际应用中，不大可能或者说没必要自己实现一个无限序列生成器。在内置模块`itertools`中提供了一个高效的无限序列生成器 `itertools.count()`。

上面了解了无限序列生成器的简单用例，接下来深入了解生成器的工作原理。

# 了解生成器

到目前为止，已经了解了创建生成器的两种主要方法：

- 生成器函数
- 生成器表达式

或许你对生成器的工作方式已经有了个直观了解，现在再花点时间更让理解更深入些。

生成器函数的外观和行为看起来普通函数差别不大，但是生成器函数有一个特征，就是生成器函数使用 Python `yield` 关键词，而不是 `return` 来返回结果。

回想一下上面编写的生成无限数字序列的生成器函数。

```python
def infinite_sequence():
    num = 0
    while True:
        yield num
        num += 1
```

除了Python `yield` 语句和它后面的代码外，看起来就是一个典型的函数定义。`yield` 语句会将其后面的值发送回调用者的位置，与`return`不同的是，它并不会结束退出函数。

相反它会记住函数中上下文**状态**。当`next()` 在生成器对象上调用时（显式或在`for`循环中隐式），先前的变量 `num` 会递增，然后再次通过 `yield` 产出。由于生成器函数看起来和其它函数外观和行为上都很相似，可以假设生成器表达式和Python中的其它推导式会比较相似…

> 注意：如果对Python的列表、集合和字典的推导式感到生疏了，可以参考这篇教程[Using List Comprehensions Effectively](https://realpython.com/courses/using-list-comprehensions-effectively/)

## 使用生成器表达式构建生成器

和列表推导式类似，生成器表达式也可以在几行代码中快速创建一个生成器对象。和使用到列表推导式的地方是相似，除此之外还有一个额外的好处：可以在迭代之前，无需在内存中创建和保存整个对象。换句话说，使用生成器表达式时，不会带来多余的内存消耗。

以下面这个数字的平方为例：

```python
>>> nums_squared_lc = [num**2 for num in range(5)]
>>> nums_squared_gc = (num**2 for num in range(5))
```

两者看起来基本相同，当我们检查每个对象时，就会发现`nums_squared_lc` 和 `nums_squared_gc` 它们之间的不同

```python
>>> nums_squared_lc
[0, 1, 4, 9, 16]
>>> nums_squared_gc
<generator object <genexpr> at 0x107fbbc78>
```

第一个对象`nums_squared_lc`使用方括号构建了一个列表，而第二个对象`nums_squared_gc`使用圆括号构成了一个生成器表达式，创建了一个生成器对象。

## 分析生成器性能

从一开始了解到，生成器是优化内存的好方法。上面提到的无限序列生成器是这种优化内存的一种极端例子。现在来仔细看看刚刚示例的平方数示例，并检查产生的对象占用内存大小。

使用 `sys.getsizeof(obj)` 来获取占用空间大小。

```python
>>> import sys
>>> nums_squared_lc = [i ** 2 for i in range(10000)]
>>> sys.getsizeof(nums_squared_lc)
87624
>>> nums_squared_gc = (i ** 2 for i in range(10000))
>>> print(sys.getsizeof(nums_squared_gc))
120
```

这种情况下可以看到，通过列表推导式得到的列表为87624 Bytes，而生成器对象只有 120 Bytes。产生的列表比生成器对象大 **700+** 倍！

不过需要记得的是，如果列表大小小于机器的可用内存，列表推导式的计算速度可能比等效的生成器表达式更快（**[List comprehension vs generator expression's weird timeit results?](https://stackoverflow.com/questions/11964130/list-comprehension-vs-generator-expressions-weird-timeit-results)**）。为了搞清楚这一点，我们把上面的两个推导式结果相加求和，使用`cProfile.run()`输出运行情况。

```python
>>> import cProfile
>>> cProfile.run('sum([i * 2 for i in range(10000)])')
         5 function calls in 0.001 seconds

   Ordered by: standard name

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.001    0.001    0.001    0.001 <string>:1(<listcomp>)
        1    0.000    0.000    0.001    0.001 <string>:1(<module>)
        1    0.000    0.000    0.001    0.001 {built-in method builtins.exec}
        1    0.000    0.000    0.000    0.000 {built-in method builtins.sum}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}

>>> cProfile.run('sum((i * 2 for i in range(10000)))')
         10005 function calls in 0.003 seconds

   Ordered by: standard name

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    10001    0.002    0.000    0.002    0.000 <string>:1(<genexpr>)
        1    0.000    0.000    0.003    0.003 <string>:1(<module>)
        1    0.000    0.000    0.003    0.003 {built-in method builtins.exec}
        1    0.001    0.001    0.003    0.003 {built-in method builtins.sum}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```

从输出结果中可以看到，对列表推导式中的值求和用时 0.001 seconds，相比于生成器推导式求和用时0.003 seconds，只使用了**1/3**的时间。如果更加看重速度而内存不是一个限制的话，列表推导器或许会是更好的实现方式。

> 注意：这些测试不仅对使用生成器推导式创建的生成器对象有效，对于生成器函数创建的生成器对象，也是一样的。因为生成的生成器是等效的。

请记住，列表推导式返回完整列表，而生成器推导式返回生成器。无论生成器是从推导式还是生成器函数构建的，生成器的工作方式都是一样的。使用表达式只是允许在一行代码中实现一个简单的生成器，在内部每个迭代都有一个`yield`产生结果。

Python `yield` 语句无疑是实现生成器功能的关键，所以现在深入了解下Python `yield` 的工作原理。

# 理解 Python Yield 语句

总的来说，`yield`是一个很简单的语句，它主要提供了类似于`return`的控制生成器函数的工作流程。不过正如上面提到的，使用Python `yield` 语句有一些技巧。

当调用生成器函数或生成器推导式时，会返回一个称为生成器（或生成器对象）的特殊迭代器，可以将此生成器作为一个变量来使用。当在生成器调用特殊方法，例如`next()` 时，生成器函数内部代码会执行到 `yield` 处。

当执行到`yield`语句处时，程序会暂停函数的执行并将`yield`产生的值返回给调用者（相反 `return`语句会直接终止函数的执行）。当函数被挂起时，函数的状态被保存，保存的状态包括生成器本地的任何变量、指令指针、内部堆栈和异常处理。

这使得在调用生成器的方法时重新恢复函数的执行。这样，函数的计算会在`yield`之后理解恢复执行。可以通过使用多个`yield`语句来看到这一点：

```python
>>> def multi_yield():
...     yield_str = "This will print the first string"
...     yield yield_str
...     yield_str = "This will print the second string"
...     yield yield_str
...
>>> multi_obj = multi_yield()
>>> print(next(multi_obj))
This will print the first string
>>> print(next(multi_obj))
This will print the second string
>>> print(next(multi_obj))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

最后一次调用`next()`时可以看到，执行过程中抛出了 [traceback](https://realpython.com/python-traceback/) 异常信息。这是因为和所有的迭代器一样（生成器也是迭代器），生成器可能会耗尽。除非生成器对象是无限的（如上面提到的无限序列生成器），否则只能遍历它一次。一旦所有的值都迭代完成后，迭代将会停止并退出循环。如果使用的是`next()`，将会得到一个明确的`StopIteration` 异常。

> 注意：`Stopteration`是一个自然异常，旨在用于引发迭代器结束。对于循环，他们都是围绕`StopIteration`来构建的。你甚至也可以使用`while`循环来自行实现一个循环：
>
>
> ```python
> >>> letters = ["a", "b", "c", "y"]
> >>> it = iter(letters)
> >>> while True:
> ...     try:
> ...         letter = next(it)
> ...     except StopIteration:
> ...         break
> ...     print(letter)
> ...
> a
> b
> c
> y
> ```
>
> 在Python官方文档 [exception](https://docs.python.org/zh-cn/3.10/library/exceptions.html) 中可以了解更多关于`StopIteration` 的说明。关于常规迭代的更多信息，可以参考教程 **[Python "for" Loops (Definite Iteration)](https://realpython.com/python-for-loop/) 和 [Python "while" Loops (Indefinite Iteration)](https://realpython.com/python-while-loop/)**

`yield` 有多种方式来控制生成器的执行流程。取决于你的创造力，可以多个 Python `yield` 一起使用。

# 使用高级生成器方法

上面看过了生成器最常见的用途和构造，另外还有一些技巧需要介绍下。除了 `yield` 关键词，生成器对象还可以使用以下这些方法（[PEP 342 – Coroutines via Enhanced Generators](https://peps.python.org/pep-0342/)）：

- `.send()`
- `.throw()`
- `.close()`

## 如何使用 `.send()`

在接下来的章节中，将构建一个会使用到这三种生成器的高级方法的程序。这个程序会像之前一样打印回文数字，但是会有一些调整。

1. 遇到回文时，新程序将添加一个数字，并从那个位置开始搜索下一个数字；
2. 同时还将使用`.throw()` 来处理异常；
3. 并且在给定数量的数字后使用`.close()`停止生成器；

首先我们回顾一下回文数字检测器的代码：

```python
def is_palindrome(num):
    # Skip single-digit inputs
    if num // 10 == 0:
        return False
    temp = num
    reversed_num = 0

    while temp != 0:
        reversed_num = (reversed_num * 10) + (temp % 10)
        temp = temp // 10

    if num == reversed_num:
        return True
    else:
        return False
```

这和上面的代码类似的，唯一的不同是原来的程序在满足情况下会返回传入的参数`num`，而现在严格要求返回 `True` 或 `False`。除此之外，还需要修改原始的无限序列生成器，如下所示：

```python
def infinite_palindromes():
    num = 0
    while True:
        if is_palindrome(num):
            i = (yield num)
            if i is not None:
                num = i
        num += 1
```

这里有许多变化！在第5行`i = (yield num)`在之前说到 yield 是一个语句，但现在并非仅仅如此了。

从 Python 2.5 开始（[参考PEP342](https://peps.python.org/pep-0342/)），`yield` 从语句升级为一个表达式。当然，依旧可以将其作为一个语句使用。但是现在允许我们像上面代码块第5行那样使用它，其中 `i` 用于获取 `yield` 表达式的值，使得我们可以利用这个对象 `i` 。更重要的是，它允许使用方法 `.send()` 来将一个值传递给生成器。在生成器恢复执行之后，对象 `i`可以获取到传入的值。

`infinite_palindromes()` 方法中还新增了一个判定检查逻辑 `if i is not None`，因为`i`可能是为`None`值（如果使用`next()` 或使用`for` 循环迭代时就会发生`i is None` 的情况）。如果`i`有得到一个非`None`的值，那么`num`将会被重新赋值为传入的`i`，另外无论如何`num`都会递增`+1`。

现在回来看一下入口主函数代码的功能，他将得到的回文数字的位数`digits`用来产生一个10的`digits`次方的新数字，并发送给生成器。例如，如果回文数字是121，则其数字位数为3，则将 `send(1000)`。

```python
pal_gen = infinite_palindromes()
for i in pal_gen:
    digits = len(str(i))
    pal_gen.send(10 ** (digits))
```

这块代码功能，他可以创建生成器对象并对其进行迭代。该程序在找到一个回文数字后才会产生一个值。使用`len()` 函数获取产生的回文数字的位数`digits`，然后将其 `10**digits` 发送至生成器。将重新回到生成器逻辑中，并将 `10**digits`赋值给`i`。现在`i`得到了一个新的值，程序会更新增加`num`和检查回文数字。

一旦在代码流程中找到并产出了一个新的回文，将会通过`for`循环迭代得到，这和使用`next()` 迭代是相同的。生成器一样会运行到第5行`i = (yield num)`给i赋值，但是`i` 的值为`None`，因为没有发送明确的值（相当于 `.send(None)`）。

在这里把它视为协程函数或生成器函数，你可以向内部传递数据。这样可以方便的构建数据管道，但是很快就会看到，他们并不是构建数据管道所必需的。（如果想有更深入地研究，可以参考[A Curious Course on Coroutines and Concurrency](http://www.dabeaz.com/coroutines/)。Tips：里面使用Python版本2.5，比较陈旧，但提供了多种协程并发示例，能不错地递进实现并解释协程的流程）

目前已经了解了`.send()`，再来看看 `.throw()`。

## 如何使用`.throw()`

`.throw()` 方法允许使用生成对象向生成器函数内抛出异常。下面示例的第6行代码中将使用throw()来引发异常。

当位数`digits`达到`5`时，代码中生成器对象将抛出一个 `ValueError` 异常。

```python
pal_gen = infinite_palindromes()
for i in pal_gen:
    print(i)
    digits = len(str(i))
    if digits == 5:
        pal_gen.throw(ValueError("We don't like large palindromes"))
    pal_gen.send(10 ** (digits))
```

与之前的代码相同，唯一就是现在需要判断 `digits` 是否等于`5`。如果等于`5`时将使用 `.throw()` 抛出`ValueError`。

运行一下看看代码是否按照预期运行，代码的运行结果如下：

```python
11
111
1111
10101
Traceback (most recent call last):
  File "advanced_gen.py", line 47, in <module>
    main()
  File "advanced_gen.py", line 41, in main
    pal_gen.throw(ValueError("We don't like large palindromes"))
  File "advanced_gen.py", line 26, in infinite_palindromes
    i = (yield num)
ValueError: We don't like large palindromes
```

`.throw()`在任何需要捕获异常的地方都很有用。在本例子中，使用了 `.throw()` 来控制了生成器在何时停止迭代，除此之外使用`.close()` 可以更优雅的完成这个操作。

## 如何使用`.close()`

顾名思义，我们可以使用 `.close()` 来停止生成器。该方法使得在控制无限序列生成器时特别方便。现在我们通过将 `.throw()` 更改为 `.close()` 来实现上面停止迭代的功能。

```python
pal_gen = infinite_palindromes()
for i in pal_gen:
    print(i)
    digits = len(str(i))
    if digits == 5:
        pal_gen.close()
    pal_gen.send(10 ** (digits))
```

在代码第6行中，使用了`.close()`，而不是 `.throw()`。使用`.close()` 的好处在于它会引发一个`StopIteration`异常，这是一个用来表示**有限迭代器**结束的异常。

```python
11
111
1111
10101
Traceback (most recent call last):
  File "advanced_gen.py", line 46, in <module>
    main()
  File "advanced_gen.py", line 42, in main
    pal_gen.send(10 ** (digits))
StopIteration
```

现在已经了解了生成器所提供的特殊方法，现在来讨论下如何使用生成器构建数据管道。

# 使用生成器创建数据管道

数据管道允许你将代码串在一起以处理大型数据集或数据流，避免因计算机可用内存不足而发生**OOM**（Out Of Memory 内存溢出）。

假设你有一个很大的CSV文件:

```
permalink,company,numEmps,category,city,state,fundedDate,raisedAmt,raisedCurrency,round
digg,Digg,60,web,San Francisco,CA,1-Dec-06,8500000,USD,b
digg,Digg,60,web,San Francisco,CA,1-Oct-05,2800000,USD,a
facebook,Facebook,450,web,Palo Alto,CA,1-Sep-04,500000,USD,angel
facebook,Facebook,450,web,Palo Alto,CA,1-May-05,12700000,USD,a
photobucket,Photobucket,60,web,Palo Alto,CA,1-Mar-05,3000000,USD,a
```

这个数据集例子来自于TechCrunch Continental USA，它记录了美国各种初创公司的融资轮次和金额。可以点击下面的链接下载示例数据集：

> 下载数据集：[Github](https://github.com/realpython/materials/blob/master/generators/techcrunch.csv) or [Blog](./techcrunch.csv)

现在来演示如何使用Python生成器构建管道，用来分析这个文件以获取数据集中所有A轮融资的金额总数和平均数。

让我们思考一个策略：

1. 读取这个文件的每一行；
2. 将每一行拆分成一系列值的列表；
3. 提取列名；
4. 使用列名和列表映射来创建字典；
5. 过滤掉不感兴趣的数据列；
6. 计算感兴趣的数据列总值和平均值；

通常情况下，我们可以使用像[pandas](https://realpython.com/pandas-python-explore-dataset/)这类包来实现这些策略，但现在也可以使用几个生成器表达式来实现这些策略。

首先，使用生成器表达式读取数据集文件中的每一行：

```python
file_name = "techcrunch.csv"
lines = (line for line in open(file_name))
```

然后，使用另外一个生成器表达式来配合前面的表达式将每一行数据分割成一个列表：

```python
list_line = (s.rstrip().split(",") for s in lines)
```

在这里，创建了一个生成器 `list_line`，它将遍历第一个生成器`lines`。这是设计生成器管道时常见的模式。接下来将从`techcrunch.csv`文件中提取列名，CSV文件的列名通常是在文件第一行，因此可以简单方便的使用首次 `next()` 来获取列名：

```python
cols = next(list_line)
```

调用 next() 可以使迭代器在list_line生成器上推进一次。把上面的步骤代码整合到一起：

```python
file_name = "techcrunch.csv"
lines = (line for line in open(file_name))
list_line = (s.rstrip().split(",") for s in lines)
cols = next(list_line)
```

总结一下，我们首先创建了一个生成器表达式`lines`来生成器文件中的每一行。接下来，在另一个生成器表达式`list_line`中遍历该生成器，该表达式会将每一行数据转换为值的列表。然后使用`next()` 将list_line 提前迭代一次，以从CSV文件中获取列名列表。

> 注意：注意每一行尾的换行符！所以在 `list_line` 生成器中使用了`.rstrip()` 来确保每一行尾没有出现换行符。

为了方便过滤数据和对数据进行操作，将创建字典，其中 `key` 是 CSV 中的列名：

```python
company_dicts = (dict(zip(cols, data)) for data in list_line)
```

此生成器表达式将遍历`list_line`生成的列表。然后使用`zip()`建立映射关系，再使用`dict()` 将映射关系转换成字典。现在可以用第4个生成器表达式来过滤期望得到的融资，并将`raisedAmt`处理成正确的数值类型。

```python
funding = (
    int(company_dict["raisedAmt"])
    for company_dict in company_dicts
    if company_dict["round"] == "a"
)
```

在这个代码片段中，生成器表达式会遍历`company_dicts`的结果，并且将筛选每一个属于A轮融资的 `company_dict`，并将原始的融资金额`raisedAmt`字符串值转换成数值类型。

需要知道的是，并不是在生成器表达式中一次性完成所有这些遍历。实际上在使用 `for` 循环或其它用于迭代的函数（如`sum()`）之前，并不会迭代任何内容。

现在，调用 `sum()` 来遍历生成器：

```python
total_series_a = sum(funding)
```

将上述流程整合到一起，这些脚本将每个生成器组合在一起，它们都作为一个大数据管道运行。得到以下脚本：

```python
file_name = "techcrunch.csv"
# 读取文件的每一行
lines = (line for line in open(file_name))
# 将每一行拆分为值并将这些值放入一个列表中
list_line = (s.rstrip().split(",") for s in lines)
# 获取文件首行的字段当作列名
cols = next(list_line)
# 创建字典来将列名与值结合起来
company_dicts = (dict(zip(cols, data)) for data in list_line)
# 获取每家公司A轮的融资金额，过滤了其它筹集的金额
funding = (
    int(company_dict["raisedAmt"])
    for company_dict in company_dicts
    if company_dict["round"] == "a"
)
# 通过调用 sum() 来获取CSV文件中所有公司A轮融资的总金额
total_series_a = sum(funding)
print(f"Total series A fundraising: ${total_series_a}")
```

当读取文件techcrunch.csv运行上面的代码，得到的了在A轮融资中总共获得了$4376015000。

> 注意：本教程中开发的用于处理CSV文件的方法对于理解使用生成器和Python `yield`很重要。然而，当你在Python中处理CSV文件时，应该改用Python标准库内置的[csv](https://docs.python.org/3/library/csv.html)模块。该模块对处理CSV文件做了更有效的优化。

为了更好的深入发掘，可以尝试计算每家公司在A轮融资中的平均融资额。这会有点棘手，有一些提示：

- 生成器在完全迭代后会自行耗尽；
- 仍然会使用到 `sum()`。

# 结论

在本教程中，探讨了生成器函数和生成器表达式。

现在可以知道的是：

1. 如何使用和编写生成器函数和生成器表达式；
2. `yield` 语句是如何启用生成器；
3. 如何在生成器函数中使用多个`yield` 语句；
4. 如何使用`.send()` 向生成器发送数据；
5. 如何使用`.throw()` 引发生成器的异常；
6. 如何使用`.close()` 停止生成器的迭代；
7. 如何构建生成器管道来高效处理大型CSV数据集；

# 参考

- **[PEP 342 – Coroutines via Enhanced Generators](https://peps.python.org/pep-0342/)**
- **[PEP 255 – Simple Generators](https://peps.python.org/pep-0255/)**
- **[Working With Files in Python](https://realpython.com/working-with-files-in-python/)**
- **[A Curious Course on Coroutines and Concurrency](http://www.dabeaz.com/coroutines/)**