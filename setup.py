from setuptools import setup

setup(
    name = "sql-maker",
    version="0.1",
    description="通过字典构建sql查询",
    author="liuxin",
    author_email="1627094964@qq.com",
    py_modules=['sqlmaker'],
    test_requires = [
        'pytest'
    ],
    install_requires=[
        'sqlparse'
    ]
)

