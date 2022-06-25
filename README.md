# 简介
sql-maker可以通过字典配置来构造sql,通过这种方式可以实现sql代码的复用,并且可以模块化/并平化,让sql的逻辑更加清晰.其实它仅仅是通过替换字符串来达到代码生成的效果,因此其也可以被用来做其他的代码生成,类似宏处理器

# 安装
下载sql-maker源码压缩包,使用`pip install sql-maker-0.1.tar.gz`,或者解压后,运行`python setup.py install`来安装

# 基本使用
```python
import sqlmaker
sql1 = {
    "main":"Hello, @name()!",
    "name":"World"
}
print(sqlmaker.parse(sql))

sql2 = {
    "main":"select (@总人数(tbl=@筛选成绩大于(score=80))) as `大于80分的人数`,(@总人数(tbl=@筛选成绩大于(score=70))) as `大于70分的人数`",
    "筛选成绩大于":"select * from t_student where score>#{score}",
    "总人数":"select count(*) cnt from (#{tbl}) t"
}
print(sqlmaker.parse(sql2))
print(sqlmaker.formatter.sql_format(sqlmaker.parse(sql2))) # 格式化sql
```

# 致谢
该工具是看到鱼皮大佬的sql-generator项目,觉得非常有趣+有用,所以造了一个自己常用的python版的轮子.

鱼皮大佬的网站:[sql-generator](http://sql.yupi.icu)