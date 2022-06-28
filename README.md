# 简介
sql-maker可以通过字典配置来构造sql,通过这种方式可以实现sql代码的复用,并且可以模块化/并平化,让sql的逻辑更加清晰.其实它仅仅是通过替换字符串来达到代码生成的效果,因此其也可以被用来做其他的代码生成,类似宏处理器

# 安装
下载[sql-maker源码压缩包](https://github.com/tianliuxin/sql-maker/raw/master/dist/sql-maker-0.1.tar.gz),使用`pip install sql-maker-0.1.tar.gz`,或者解压后,运行`python setup.py install`来安装

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

# sql文件解析
通过@@name{body}这种语法可以在sql文件里定义语句块,再配合解析,可以更方便的编写代码
```sql
-- demo.sql

@@sumif{
    sum(case when score > #{score} then 1 else 0)
}

@@main{
    select
        @sumif(score=60) as `大于60分人数` 
        ,@sumif(score=80) as `大于80分人数`
    from t_score
}

```
通过sqlmaker解析`demo.sql`
```python
import sqlmaker

print(sqlmaker.parse_file("demo.sql"))
```

# 高级使用
对于一些常用的,有些其实可以被抽象到多个文件中,进行模块化,但当前并没有提供`import`的功能,那是否就不能分文件组织了呢?当前可用通过`FileParser`对象中的parse方法,将文件解析为字典,通过字典的操作,进行数据的整合,这样就将名称的作用域放到了同一个字典里,便可用解析了.
```python

import sqlmaker

file_parser = FileParser()
with open("module1.sql",'r',encoding="utf8") as module1,open("main.sql",'r',encoding='utf8') as main:
    module1_dict,main_dict = file_parser.parse(module1.read()),file_parser.parse(main.read())

main_dict.update(module1_dict)
```
备注:可以加入简易版的`import`,但使用较少,所以暂时使用组合字典的方式,更多的应该还是单文件处理

# 致谢
该工具是看到鱼皮大佬的sql-generator项目,觉得非常有趣+有用,所以造了一个自己常用的python版的轮子.

鱼皮大佬的网站:[sql-generator](http://sql.yupi.icu)
