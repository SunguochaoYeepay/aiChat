#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
聊天系统与知识库集成测试脚本

此脚本用于验证聊天系统是否正确使用知识库和向量检索功能。
"""
import sys
import os
import json
import requests
import time
from pprint import pprint

# 设置项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# API地址
API_URL = "http://localhost:8000/api"  # 如果不是本地服务，请修改为实际API地址

def test_knowledge_base_search():
    """测试知识库搜索功能"""
    print("\n=== 测试知识库搜索 ===")
    
    # 定义测试查询
    test_queries = [
        "北京有哪些著名的旅游景点？",
        "上海的金融中心地位",
        "网页设计的基本原则"
    ]
    
    for query in test_queries:
        print(f"\n正在搜索: '{query}'")
        
        try:
            # 发送搜索请求
            response = requests.post(
                f"{API_URL}/search",
                json={
                    "query": query,
                    "top_k": 2
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"找到 {result['count']} 条结果:")
                
                for i, item in enumerate(result['results']):
                    print(f"  {i+1}. {item['name']} (相似度: {item['similarity']:.2f})")
                    print(f"     {item['content'][:100]}...")
                
                # 验证是否返回了结果
                assert result['count'] > 0, "搜索未返回任何结果"
                
                # 验证结果是否相关
                if "北京" in query:
                    found_beijing = any("北京" in item['content'] for item in result['results'])
                    assert found_beijing, "搜索北京但未找到相关内容"
                    
                elif "上海" in query:
                    found_shanghai = any("上海" in item['content'] for item in result['results'])
                    assert found_shanghai, "搜索上海但未找到相关内容"
                    
                elif "设计" in query:
                    found_design = any("设计" in item['content'] for item in result['results'])
                    assert found_design, "搜索设计但未找到相关内容"
                
                print("✓ 搜索测试通过")
                
            else:
                print(f"× 请求失败: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"× 测试出错: {str(e)}")

def test_chat_with_knowledge():
    """测试聊天系统是否使用知识库"""
    print("\n=== 测试聊天系统与知识库集成 ===")
    
    # 定义测试对话
    test_conversations = [
        [
            {"role": "user", "content": "北京有哪些著名的旅游景点？"}
        ],
        [
            {"role": "user", "content": "上海是一个什么样的城市？"}
        ],
        [
            {"role": "user", "content": "网页设计有哪些基本原则？"}
        ]
    ]
    
    for messages in test_conversations:
        query = messages[0]['content']
        print(f"\n测试对话: '{query}'")
        
        try:
            # 先获取知识库搜索结果
            kb_response = requests.post(
                f"{API_URL}/search",
                json={
                    "query": query,
                    "top_k": 2
                }
            )
            
            kb_result = kb_response.json() if kb_response.status_code == 200 else {"results": []}
            
            # 发送聊天请求
            chat_response = requests.post(
                f"{API_URL}/v1/chat/completions",
                json={
                    "messages": messages,
                    "stream": False
                }
            )
            
            if chat_response.status_code == 200:
                result = chat_response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0]['message']['content']
                    print("\n模型回复:")
                    print(content)
                    
                    # 检查回复是否包含知识库中的信息
                    knowledge_incorporated = False
                    
                    if kb_result['results']:
                        # 从知识库结果中提取关键词
                        key_phrases = []
                        for item in kb_result['results']:
                            # 简单拆分内容获取关键短语
                            phrases = [p.strip() for p in item['content'].split('。') if len(p.strip()) > 3]
                            key_phrases.extend(phrases[:2])  # 只取前两个短语
                        
                        # 检查回复中是否包含关键短语
                        for phrase in key_phrases:
                            if len(phrase) > 3 and phrase in content:
                                knowledge_incorporated = True
                                print(f"\n✓ 回复中包含知识库信息: '{phrase}'")
                                break
                    
                    if not knowledge_incorporated:
                        print("\n× 回复中未明确包含知识库信息")
                        
                        # 检查一些关键词
                        if "北京" in query:
                            landmarks = ["天安门", "故宫", "长城"]
                            found = any(landmark in content for landmark in landmarks)
                            if found:
                                print(f"✓ 但包含了相关地标信息")
                            
                        elif "上海" in query:
                            landmarks = ["外滩", "东方明珠", "豫园"]
                            found = any(landmark in content for landmark in landmarks)
                            if found:
                                print(f"✓ 但包含了相关地标信息")
                                
                        elif "设计" in query:
                            principles = ["简洁", "直观", "一致", "布局", "色彩"]
                            found = any(principle in content for principle in principles)
                            if found:
                                print(f"✓ 但包含了相关设计原则")
                else:
                    print("× 响应不包含有效回复")
            else:
                print(f"× 请求失败: {chat_response.status_code}")
                print(chat_response.text)
                
        except Exception as e:
            print(f"× 测试出错: {str(e)}")
        
        time.sleep(1)  # 避免频繁请求

def main():
    """主函数"""
    print("开始测试聊天系统与知识库集成...")
    
    # 测试服务是否在线
    try:
        status_response = requests.get(f"{API_URL}/status")
        if status_response.status_code != 200:
            print(f"× 服务状态检查失败: {status_response.status_code}")
            return
    except Exception as e:
        print(f"× 无法连接到API服务: {str(e)}")
        print(f"请确保服务已启动，并可通过 {API_URL} 访问")
        return
    
    # 运行测试
    test_knowledge_base_search()
    test_chat_with_knowledge()
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 