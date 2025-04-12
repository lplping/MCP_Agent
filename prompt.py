#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ping
# datetime:2025/4/8 15:07
instruction = """
你现在是一个agent规划师，你需要根据目前现有的工具，生成一段think过程，思考的过程要和工具相关,问题是否需要拆解，不要对问题进行回复解释，你只需要输出思考的过程，不用回答问题。

请结合以下工具：

tools:
1. check_weather(city: str): 查询城市天气
2. keywords_extract(sentence: str): 抽取关键词
3. summary_extract(docText: str): 生成摘要
4. calculate(expression: str): 数学计算
5. lyric_generate(query: str): 生成歌词


【示例】
用户：计算1+1的结果，并基于结果生成一段歌词
思考：完成这个任务需要两个步骤，首先我需要计算 1+1 的结果，然后基于该结果生成一段歌词。分别调用 calculate 和 lyric_generate 工具。
━━━━━━━━━━━━━━━━━━
[AI]:
用户：{query}
思考：
"""


rewrite_query="""
## 目标
你现在Agent规划专家，根据上一个问题和结果，生成当前问题

## 约束
1）如果当前问题和上一个问题结果相关的，你需要根据上一个问题的结果生成问题
2）生成的问题不要偏离原始用户问题

## 示例
原始用户问题：计算1+1的结果，并基于结果生成一段歌词
上一个问题：{{expression: 1 + 1}}
上一个工具：{{calculator}}
工具返回结果：{{result=2}}
当前问题：以结果为2生成一段歌词

━━━━━━━━━━━━━━━━━━
[AI]:

原始用户问题：{original_query}
上一个问题：{last_question}
上一个工具：{last_tool_name}
工具返回结果：{last_result}
当前问题：

"""
prompts={"prompt_plan":instruction,"rewrite_query": rewrite_query}
