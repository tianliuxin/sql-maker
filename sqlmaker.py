'''
整体思路
给定一个main sql,解析main sql中的node,找到node代表的sql和参数,
先替换sql中的参数(参数中的node也要替换),再替换sql中的node
'''
import re
import sqlparse
import json
from typing import List, Union
from abc import ABC,abstractmethod


class InvokeNode:
    def __init__(self, text, key, params):
        self.key = key
        self.params = params
        self.text = text
        self.parse_text = ""  # 待解析/解析后文本
        self.children = []  # 子节点

    def __repr__(self):
        return '{"key":"%s","params":"%s","text":"%s","parse_text":"%s","children":%s}' % (
            self.key, self.params, self.text, self.parse_text, self.children
        )


class SqlGenerator:
    def __init__(self, ctx: dict):
        self.ctx = ctx
        self.pattern = re.compile("@(.+?)\(.*?\)")

    def extract_invoke_node(self, text: str, match: re.Match) -> InvokeNode:
        '''根据待解析的text和匹到配的match对象,解析出完整的InvokeNode

        解析的算法是获取match中最左边的左括号,向右移动,直到左括号计数器值为0,
        此时匹配到了完整node中的最右的右节点,提取完整node,设置待解析文本为key查到的值,
        递归的先解析文本中的参数值,再解析文本中的node
        '''
        match_node_text = match.group(0)  # 匹配的部分节点值
        node_key = match.group(1)  # 匹配到的key值
        node_start = match.start()  # 匹配的起始点
        first_left_parenthes_index = node_start + match_node_text.index("(")
        left_parenthes_count = 1  # 左括号计数,模仿栈,维护状态
        i = first_left_parenthes_index
        while left_parenthes_count > 0:
            i += 1
            current_char = text[i]
            # 匹配到),计数减1,匹配到(,计数加1
            if current_char == ")":
                left_parenthes_count -= 1
            elif current_char == "(":
                left_parenthes_count += 1
        last_right_parenthes_index = i  # 最右右括号位置
        # 完整的replace_text
        node_text = text[node_start:last_right_parenthes_index+1]
        params = text[first_left_parenthes_index+1:last_right_parenthes_index]

        invoke_node = InvokeNode(node_text, node_key, params)
        invoke_node.parse_text = self.ctx[invoke_node.key]
        invoke_node = self.replace_params(invoke_node)
        invoke_node = self.replace_invoke_nodes(invoke_node)
        return invoke_node

    def replace_invoke_nodes(self, invoke_node: InvokeNode) -> InvokeNode:
        '''解析node中的parse_text,将其中的@xxx(xxx)替换为解析后的文本

        invoke_node:父节点,用来传递待解析的文本,收集其解析出的子节点
        '''
        text = invoke_node.parse_text
        invoke_nodes: List[InvokeNode] = [
            self.extract_invoke_node(text, m) for m in re.finditer(self.pattern, text)
        ]
        # 替换解析的node,若存在node则替换,不存在node则返回自己
        invoke_node.children += invoke_nodes
        for node in invoke_nodes:
            text = text.replace(node.text, node.parse_text)
        invoke_node.parse_text = text
        return invoke_node

    def replace_params(self, invoke_node: InvokeNode, sep="|||") -> InvokeNode:
        '''替换node中的参数值'''
        text, params = invoke_node.parse_text, invoke_node.params
        params = params.split(sep)
        # 没有参数,返回节点本身
        if not params[0].strip():
            return invoke_node
        for p in params:
            p_name, p_value = p.split("=",maxsplit=1)
            p_name, p_value = p_name.strip(), p_value.strip()  # 清除空格
            invoke_node.parse_text = p_value  # 将待解析的parse_text设置为p_value
            p_value_node = self.replace_invoke_nodes(
                invoke_node)  # 传递invoke_node解析参数值,收集参数中的子节点
            text = text.replace(f"#{{{p_name}}}", p_value_node.parse_text)
        invoke_node.parse_text = text
        return invoke_node

    def parse(self, text:str, key="") -> InvokeNode:
        '''解析text,返回解析后的节点'''
        root_node = InvokeNode(text, key, "")
        root_node.parse_text = text  # 设置待解析文本为text
        root_node = self.replace_invoke_nodes(root_node)
        return root_node

class BaseFileParser(ABC):
    '''文件解析的抽象基类'''
    @abstractmethod
    def parse(self,text):
        '''parse接口'''
        pass
    
    def read_file(self,file,encoding="utf-8"):
        '''读取文件并解析'''
        with open(file,encoding=encoding) as f:
            text = f.read()
        return self.parse(text)
    
class FileParser(BaseFileParser):
    '''解析文件中的内容为字典
    
    文件需要使用@@name{body}来定义代码块,会将这部分解析为字典{"name1":"body1","name2":"body2"}
    当前为了实现简单,使用@@来标识定义开始,其实也可以改成def,@等,另外实现可以改成SqlGenerator中的正则方式,这样会更加灵活
    '''
    def __init__(self):
        self.fn_pattern = re.compile("(.*?)\{(.*)\}",flags=re.DOTALL)

    def parse(self,text)->dict:
        '''str解析为dict
        
        解析方法,重载这个方法可以解析不同形式的文件
        '''
        sep="@@"
        def parse_fn(fn:str)->tuple:
            fn_match = self.fn_pattern.search(fn)
            fn_name,fn_body = fn_match.group(1).strip(),fn_match.group(2).strip()
            return fn_name,fn_body

        fns = [ parse_fn(fn) for fn in text.split(sep) if fn.strip() != "" ]
        fns = dict(fns)
        return fns


class Formatter:
    def sql_format(self, data: Union[str, InvokeNode]):
        if isinstance(data, InvokeNode):
            data = data.parse_text  # 获取解析后的文本,转为字符串
            return sqlparse.format(data, reindent=True, keyword_case='upper')

    def json_format(self, data: Union[str, InvokeNode]):
        if isinstance(data, InvokeNode):
            data = str(data)  # 转为字符串
            return json.dumps(
                json.loads(data), indent=2, ensure_ascii=False
            )


def parse(ctx:dict)->str:
    '''从main节点开始解析,返回解析后的文本,若要使用解析后的节点值,则应使用SqlGenerator类中的parse'''
    sql_generator = SqlGenerator(ctx)
    return sql_generator.parse(ctx['main'], "main").parse_text

def parse_file(file,encoding="utf-8")->str:
    file_parser = FileParser()
    ctx = file_parser.read_file(file,encoding)
    return parse(ctx)

formatter = Formatter()  # formatter接口

if __name__ == "__main__":


    ctx = {
        "main":"Hello, @name()",
        "name":"liuxin"
    }
    sql = parse(ctx)
    print(sql)