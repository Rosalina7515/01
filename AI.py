import os
import json
import requests
from typing import Dict, Any
from openai import OpenAI

class IoTAgent:
   
    
    def __init__(self, api_key: str, api_base_url: str = "http://localhost:5000", 
                 base_url: str = "https://api.siliconflow.cn/v1", 
                 primary_model: str = "Qwen/QwQ-32B-Preview",
                 secondary_model: str = "Qwen/QwQ-32B-Preview"):
        """
        Args:
            api_key: OpenAI API key
            api_base_url: Base URL for IoT API
            base_url: Base URL for OpenAI API
            primary_model: 用于初始查询的主模型
            secondary_model: 用于后续响应的次要模型
        """
        self.client = OpenAI(api_key=api_key,
                             base_url=base_url
                             )
        self.api_base_url = api_base_url
        self.primary_model = primary_model
        self.secondary_model = secondary_model
        
        # API endpoints
        self.endpoints = {
            "temperature": "/api/sensor/temperature",
            "humidity": "/api/sensor/humidity",
            "temp_humidity": "/api/sensor/temp-humidity",
            "all_sensors": "/api/sensor/all",
            "led_on": "/api/control/led/on",
            "led_off": "/api/control/led/off",
            "emo_happy": "/api/emo/happy",
            "emo_wink": "/api/emo/wink",
            "emo_surprised": "/api/emo/surprised",
            "emo_angry": "/api/emo/angry",
            "emo_sleepy": "/api/emo/sleepy",
            "emo_crying": "/api/emo/crying",
            "emo_playful": "/api/emo/playful",
            "emo_cute": "/api/emo/cute",
            "emo_thinking": "/api/emo/thinking",
            "emo_love": "/api/emo/love"
        }
        
    def _call_api(self, endpoint: str) -> Dict[str, Any]:
        url = f"{self.api_base_url}{endpoint}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
            
    def _execute_function(self, function_name: str) -> Dict[str, Any]:
        function_mapping = {
            "get_temperature": self.endpoints["temperature"],
            "get_humidity": self.endpoints["humidity"],
            "get_temp_humidity": self.endpoints["temp_humidity"],
            "get_all_sensor_data": self.endpoints["all_sensors"],
            "turn_led_on": self.endpoints["led_on"],
            "turn_led_off": self.endpoints["led_off"],
            "emo_happy": self.endpoints["emo_happy"],
            "emo_wink": self.endpoints["emo_wink"],
            "emo_surprised": self.endpoints["emo_surprised"],
            "emo_angry": self.endpoints["emo_angry"],
            "emo_sleepy": self.endpoints["emo_sleepy"],
            "emo_crying": self.endpoints["emo_crying"],
            "emo_playful": self.endpoints["emo_playful"],
            "emo_cute": self.endpoints["emo_cute"],
            "emo_thinking": self.endpoints["emo_thinking"],
            "emo_love": self.endpoints["emo_love"]

        }
        
        if function_name in function_mapping:
            return self._call_api(function_mapping[function_name])
        else:
            return {"success": False, "error": f"未知功能: {function_name}"}
    
    def process_query(self, user_query: str) -> str:
        # 定义系统消息
        messages = [
            {"role": "system", "content": """
            你是一个物联网传感器监控和控制系统的助手。
             你可以提供关于温度、湿度、光照和红外传感器的信息，
             并且可以控制LED灯（开启或关闭）。
             你还可以显示各种表情：快乐、眨眼、惊讶、愤怒、困倦、哭泣、调皮、可爱、思考和爱心。
             如果被要求提供传感器数据，请调用适当的函数获取实时数据。
             根据用户的情感和交流内容，适时展示合适的表情。
             以简洁明了的方式回应用户请求。
             """},
            {"role": "user", "content": user_query}
        ]
        
        # 定义可用的函数
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_temperature",
                    "description": "获取当前温度传感器读数",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_humidity",
                    "description": "获取当前湿度传感器读数",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_temp_humidity",
                    "description": "同时获取温度和湿度读数",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_sensor_data",
                    "description": "获取所有传感器读数（温度、湿度、光照、红外）",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "turn_led_on",
                    "description": "打开LED灯",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "turn_led_off",
                    "description": "关闭LED灯",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "emo_happy",
                    "description": "做快乐的表情",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "emo_wink",
                    "description": "显示眨眼的表情",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "emo_surprised",
                    "description": "显示惊讶的表情",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "emo_angry",
                    "description": "显示愤怒的表情",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "emo_sleepy",
                    "description": "显示困倦的表情",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "emo_crying",
                    "description": "显示哭泣的表情",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "emo_playful",
                    "description": "显示调皮的表情",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "emo_cute",
                    "description": "显示可爱的表情",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "emo_thinking",
                    "description": "显示思考的表情",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "emo_love",
                    "description": "显示爱心的表情",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
            
        ]
        
        try:
            # 获取OpenAI响应
            response = self.client.chat.completions.create(
                model=self.primary_model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
                
            )
            
            message = response.choices[0].message
            
            # 检查是否需要调用函数
            if message.tool_calls:
                function_name = message.tool_calls[0].function.name
                function_response = self._execute_function(function_name)
                
                # 将函数结果发回给OpenAI
                messages.append(message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": message.tool_calls[0].id,
                    "name": function_name,
                    "content": json.dumps(function_response)
                })

                # 如果是表情相关功能且API调用成功，添加额外的提示
                if function_name.startswith("emo_") and function_response.get("success", False):
                    emotion_type = function_name.replace("emo_", "")
                    messages.append({
                        "role": "system", 
                        "content": f"表情'{emotion_type}'已成功显示。请确保在回复中使用自然语言，不要直接返回API响应。"
                    })
                
                # 获取最终响应
                second_response = self.client.chat.completions.create(
                    model=self.secondary_model,
                    messages=messages
                )
                return second_response.choices[0].message.content
            else:
                return message.content
                
        except Exception as e:
            return f"处理请求时出错: {str(e)}"


def main():
    """主函数，用于测试IoT Agent"""
    # 设置openai baseurl
    os.environ["OPENAI_API_BASE"] = "https://api.siliconflow.cn/v1"
    # 从环境变量获取API密钥
    api_key = os.environ.get("OPENAI_API_KEY")
    # dev
    api_key = 'sk-pkspmxtdjjeinufxmvnymdeaqznwzgkxijgwyjlynoqpjsph'
    # 获取模型配置（如果有）
    primary_model = os.environ.get("PRIMARY_MODEL", "Qwen/Qwen2.5-7B-Instruct")
    secondary_model = os.environ.get("SECONDARY_MODEL", "Qwen/Qwen2.5-7B-Instruct")

    if not api_key:
        # //用户设置API密钥
        print("请设置OpenAI API密钥。")
        os.environ["OPENAI_API_KEY"] = input("请输入API密钥: ")
        api_key = os.environ.get("OPENAI_API_KEY")
        
    
    # 创建代理
    agent = IoTAgent(api_key, primary_model=primary_model, secondary_model=secondary_model)
    
    print("物联网代理已初始化。输入'quit'退出。")

    while True:
        query = input("\n输入您的查询: ")
        if query.lower() in ["quit", "exit", "退出"]:
            break
        
        response = agent.process_query(query)
        print("\n响应:", response)


if __name__ == "__main__":
    main()
