from pyparsing import *


# 定义你的语法
entryType = Word("entry")
identifier = Word(alphas, alphanums + "_")
number = Combine(Optional('-') + Word(nums))
float_number = Combine(Optional(Literal("-") | "+") + Word(nums) + "." + Word(nums) + Literal("f"))
# float_number must be in the front of number !!!
# variable in the form of [12345]
squareVariable = Combine(Literal("[") + (float_number | number) + "]")

# entry: as a struct
assignment = identifier + Suppress(":") + (number | quotedString) + Suppress(Optional(","))
sprite_assignment = identifier + Suppress(":") + Suppress("{") + Dict(ZeroOrMore(Group(assignment))) + Suppress("}") + Suppress(Optional(","))
sprites_block = Literal("sprites") + Suppress(":") + Suppress("{") + Dict(ZeroOrMore(Group(sprite_assignment))) + Suppress("}")
entryBlock = Literal('entry') + identifier + Suppress("{") + Dict(ZeroOrMore(Group(assignment | sprites_block))) + Suppress("}")

# script: as C sentences
instruction = Combine("ins_" + Word(nums)) + Suppress("(") + Optional(delimitedList(float_number | number | identifier |squareVariable)) + Suppress(")") + Suppress(";")
offset = identifier + ":"
wait = "+" + number + ":" + "//" + number
scriptBlock = Literal("script") + identifier + Suppress("{") + ZeroOrMore(Group(instruction | offset | wait)) + Suppress("}")

def parseDDESscript(file):
    with open(file, 'r') as f:
        code = f.read()
    codeBlock = code.split("\n\n")
    blocks = []
    for i, block in enumerate(codeBlock):
        
        result = ZeroOrMore(scriptBlock | entryBlock).parse_string(block)
        # print(result)
        if 'script' in codeBlock[i]:
            blocks.append(result.as_list())
        elif 'entry' in codeBlock[i]:
            blocks.append(result.as_list()[:2]+[result.as_dict()])
            
    return blocks

from pprint import pprint
from pathlib import Path
if __name__ == '__main__':
    code = Path('E:\Documents\Coding\Python\zeGIFmaker\swy\source\player\pl00b.ddes')
        
    pprint(parseDDESscript(code)[-1], indent=2)

# 输出结果
# print(result)

# from pprint import pprint
# # 输出结果
# for item in result:
#     print(item)
#     print()
    

# # 解析你的代码
# results = entryBlock.searchString(my_code)

# # 输出结果
# for result in results:
#     print(result)

