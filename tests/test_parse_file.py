import sqlmaker


def test_parse():
    ctx = {
        "main":"select (@总人数(tbl=@筛选成绩大于(score=80))) as `大于80分的人数`,(@总人数(tbl=@筛选成绩大于(score=70))) as `大于70分的人数`",
        "筛选成绩大于":"select * from t_student where score>#{score}",
        "总人数":"select count(*) cnt from (#{tbl}) t"
    }
    sql = sqlmaker.parse(ctx)
    print(sql)

def test_parse_file():
    f = "demo.sql"
    print(sqlmaker.parse_file(f))