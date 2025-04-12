#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:ping
# datetime:2025/4/2 14:43
import httpx
import aiohttp
import os
OPENWEATHER_API_BASE = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = "xxxxxx"  # 请替换为你自己的 OpenWeather API Key
USER_AGENT = "weather-app/1.0"
async def fetch_weather(city: str) :
    """
    从 OpenWeather API 获取天气信息。
    :param city: 城市名称（需使用英文，如 Beijing）
    :return: 天气数据字典；若出错返回包含 error 信息的字典
    """
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "zh_cn"
    }
    headers = {"User-Agent": USER_AGENT}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(OPENWEATHER_API_BASE, params=params, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()  # 返回字典类型
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP 错误: {e.response.status_code}"}
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}

#---------------关键词抽取-------------------
async def get_keyword(query):
    print("*************",query)
    params = {

        "sentence": query

    }
    print("params",params)
    url = "http://x/nlp/getTerms"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params) as res:
            result = await res.json()
    res = result.get("result")
    if res:
        term = res.get("terms")
    else:
        term = []
    return "".join(term)


    return "".join(result.get("result", []) ) # 直接返回 spoList，默认为空列表


#---------------摘要抽取-------------------
async def get_summery(data):

    url="http://xxxx/nlp/doc2title"
    params = {"docText": data}
    print("**************",params)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params) as res:
            result = await res.json()
    res = result.get("result")
    if res:
        term = res.get("title")
    else:
        term = []
    return "".join(term)
