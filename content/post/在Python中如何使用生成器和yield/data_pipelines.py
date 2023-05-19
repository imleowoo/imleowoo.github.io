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
