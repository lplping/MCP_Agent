#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ping
# datetime:2025/4/9 13:44
from openai import AsyncOpenAI
from prompt import prompts
import requests
import logging
import re
import json
import logging
from typing import List
def get_http_tools(tool_name,tool_args):


    url = "http://xxxx:18475/call_tools"
    res = requests.post(url,json={"tool_name":tool_name,"tool_args":tool_args})
    result = res.json()

    return result

logger=logging.getLogger("agent.log")

def get_tools_num(A):
    # 工具列表
    tools = [
        "check_weather",
        "keywords_extract",
        "summary_extract",
        "query_spo",
        "ocr_recognition",
        "calculate",
        "music_store",
        "lyric_generate",
        "extract_entity",
        "generate_image"
    ]

    # 输入文本

    # 匹配出出现在A中的工具名
    used_tools = [tool for tool in tools if re.search(r'\b' + re.escape(tool) + r'\b', A)]

    return used_tools
logger = logging.getLogger(__name__)

class AgentAI:
    def __init__(self):
        self.openai_api_key = "xxxxxc"
        self.base_url = "xxxxx"
        self.model = "Qwen/Qwen2.5-32B-Instruct"  # 读取 model
        self.openai = AsyncOpenAI(api_key=self.openai_api_key, base_url=self.base_url)

    async def query_thinks(self,prompt):

        querys = await self.openai.chat.completions.create(
            model=self.model,
            max_tokens=1000,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ])
        thinks = querys.choices[0].message.content
        return thinks

    async def get_ocr_res(self, base64):
        """
        识别到OCR的逻辑
        :param base64:
        :return:
        """
        tool_name = "ocr_recognition"
        tool_args = base64
        res = get_http_tools(tool_name, tool_args)
        return res

    async def process_query(self, query: str,image=None):


        available_tools =    [{'type': 'function', 'function': {'name': 'check_weather', 'description': '\n    输入指定城市的英文名称，返回今日天气查询结果。\n    :param city: 城市名称（需使用英文）\n    :return: 格式化后的天气信息\n    ', 'parameters': {'properties': {'city': {'title': 'City', 'type': 'string'}}, 'required': ['city'], 'title': 'check_weatherArguments', 'type': 'object'}}}, {'type': 'function', 'function': {'name': 'keywords_extract', 'description': '\n    抽取句子中的关键词,包括术语等\n    输入的是句子，返回的关键词抽取结果\n    :param sentence: 需要抽取关键词的文本\n    :return: 关键词抽取结果\n    ', 'parameters': {'properties': {'sentence': {'title': 'Sentence', 'type': 'string'}}, 'required': ['sentence'], 'title': 'keywords_extractArguments', 'type': 'object'}}}, {'type': 'function', 'function': {'name': 'summary_extract', 'description': '\n    生成摘要，根据一段描述，生成这段描述的摘要\n    输入的是一段描述，返回的是该描述对应的摘要\n    :param docText: 需要抽取摘要的文本\n    :return: 根据该文本生成的描述\n    ', 'parameters': {'properties': {'docText': {'title': 'Doctext', 'type': 'string'}}, 'required': ['docText'], 'title': 'summary_extractArguments', 'type': 'object'}}}]

        # =======生成一段thingk==============================
        inputs = prompts["prompt_plan"].format(query=query)
        think = await self.query_thinks(inputs)
        print("----------think", think)
        tools_=get_tools_num(think)#确定工具总数
        history=[]
        MAX_TOOL_CALLS=len(tools_)
        
        if MAX_TOOL_CALLS==0:
            MAX_TOOL_CALLS=2



        messages = [
            {
                "role": "system",
                "content": "你是一个智能助手，能够根据任务自动规划多个工具调用步骤。"
            },
            {
                "role": "user",
                "content": query
            }
        ]
        history.extend( [
            {
                "role": "system",
                "content": "你需要根据历史调用工具的结果，进行总结回复"
            },
            {
                "role": "user",
                "content": query
            }
        ])

        tool_results = []
        steps = []
        current_query = query
        for step_idx in range(MAX_TOOL_CALLS):
            # history.extend(messages)
            # 用当前对话 + 当前query 生成一个工具调用
            completion = await self.openai.chat.completions.create(
                model=self.model,
                max_tokens=1000,
                messages=messages,
                tools=available_tools
            )

            assistant_message = completion.choices[0].message

            if not assistant_message.tool_calls:
                break  # 没有新的工具调用，终止

            tool_call = assistant_message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = tool_call.function.arguments
            result = get_http_tools(tool_name, tool_args)
            print(f"==> 执行第{step_idx + 1}个工具: {tool_name}")
            print("参数:", tool_args)
            print("返回结果:", result)
            # 补充对话上下文
            history.extend([
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call]
                },
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result.get("result")
                }
            ])



            # 记录调用步骤
            steps.append({
                "original_query": current_query,
                "tool_call": {
                    "tool_name": tool_name,
                    "tool_args": tool_args,
                    "tool_result": result
                },
                "final_response": None
            })

            # 重写下一个查询（准备下一轮工具调用）
            rewrite_prompt = prompts["rewrite_query"].format(
                last_question=tool_args,
                original_query=query,
                last_tool_name=tool_name,
                last_result=result
            )
            # print("rewrite_prompt",rewrite_prompt)
            rewritten_resp = await self.openai.chat.completions.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {"role": "system", "content": "你是一个任务重写助手"},
                    {"role": "user", "content": rewrite_prompt}
                ]
            )
            current_query = rewritten_resp.choices[0].message.content
            print("current_query",current_query)
            messages=[{"role": "user", "content": current_query}]


        
        final_completion = await self.openai.chat.completions.create(
            model=self.model,
            max_tokens=1000,
            messages=history
        )
        final_text = final_completion.choices[0].message.content

        return {
            "think": think,
            "steps": steps,
            "final_summary": final_text
        }


