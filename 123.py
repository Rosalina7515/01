from flask import Flask, jsonify
from gevent import pywsgi  
from JtPythonBCPToHardware import *
from time import sleep
import threading
import logging

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 缓存数据结构保持不变，但现在只在请求时使用
latest_data = {
    "temperature": 0,
    "humidity": 0,
    "illumination": 0,
    "infrared": 0
}

# define COM
serial_tool = None
serial_lock = threading.Lock()  # 用于线程安全的锁

def init_serial(port="com3"):
    """初始化串口连接"""
    global serial_tool
    try:
        serial_tool = SerialTool(port)
        logger.info(f"串口 {port} 初始化成功")
        return True
    except Exception as e:
        logger.error(f"串口初始化失败: {str(e)}")
        return False
def emo(emotype):
    """获取表情符号(emoticon)的API端点
    
    参数:
        emotype: 表情类型，如happy、sad等
    
    返回:
        JSON格式的表情符号数据
    """
    try:
        with serial_lock:
            if serial_tool is None:
                if not init_serial():
                    return jsonify({"success": False, "message": "串口连接失败"})
        match emotype:
            case "happy":
                expression = """   /^v^v^v^\\    
  |  ^   ^  |   
  \\___v___/     """
            case "wink":
                expression = """   /^v^v^v^\\   
  |  -   o  |  
   \\___^___/   """
            case "surprised":
                expression = """   /^v^v^v^\\   
  |  O   O  |  
   \\___o___/   """
            case "angry":
                expression = """   /^v^v^v^\\   
  |  >   <  |  
   \\___-___/   """
            case "sleepy":
                expression = """   /^v^v^v^\\   
  |  -   -  |  
   \\___~___/   """
            case "crying":
                expression = """   /^v^v^v^\\   
  |  Q   Q  |  
   \\__TT___/   """
            case "playful":
                expression = """   /^v^v^v^\\   
  |  ^   -  |  
   \\___P___/   """
            case "cute":
                expression = """   /^v^v^v^\\   
  |  *   *  |  
   \\___w___/   """
            case "thinking":
                expression = """   /^v^v^v^\\   
  |  ?   ?  |  
   \\___o___/   """
            case "love":
                expression = """   /^v^v^v^\\   
  |  <   >  |  
   \\__{3}__/   """
            case _:
                expression = "Unknown emoticon type"
        serial_tool.hardwareSend(HardwareType.lcd, HardwareCommand.control, expression)
        return jsonify({
            "success": True,
            "data": {
                "emoticon": expression,
                "type": emotype
            }
        })
    except Exception as e:
        logger.error(f"获取表情符号时出错: {str(e)}")
        return jsonify({
            "success": False, 
            "message": f"获取表情符号失败: {str(e)}"
        })

def get_sensor_data(sensor_type):
    """按需获取传感器数据"""
    global serial_tool
    
    try:
        with serial_lock:
            if serial_tool is None:
                if not init_serial():
                    logger.error("获取传感器数据时串口初始化失败")
                    return False
            
            if sensor_type == "temp-humidity" or sensor_type == "temperature" or sensor_type == "humidity" or sensor_type == "all":
                serial_tool.hardwareSend(HardwareType.tempHumidity, HardwareCommand.get, "")
                sleep(2)
                latest_data["temperature"] = serial_tool.tempData
                latest_data["humidity"] = serial_tool.humidityData
            
            if sensor_type == "illumination" or sensor_type == "all" or sensor_type == "temp-humidity":
                serial_tool.hardwareSend(HardwareType.illumination, HardwareCommand.get, "")
                sleep(2)
                latest_data["illumination"] = serial_tool.illuminationData
            
            if sensor_type == "infrared" or sensor_type == "all":
                serial_tool.hardwareSend(HardwareType.infrared, HardwareCommand.get, "")
                sleep(2)
                latest_data["infrared"] = serial_tool.infraredData
            
            
            return True
    except Exception as e:
        
        serial_tool = None  # 发生错误时重置串口
        return False

@app.route('/api/sensor/temperature', methods=['GET'])
def get_temperature():
    """获取温度数据的API端点"""
    get_sensor_data("temperature")
    return jsonify({
        "success": True,
        "data": {
            "temperature": latest_data["temperature"]
        }
    })

@app.route('/api/sensor/humidity', methods=['GET'])
def get_humidity():
    """获取湿度数据的API端点"""
    get_sensor_data("humidity")
    return jsonify({
        "success": True,
        "data": {
            "humidity": latest_data["humidity"]
        }
    })

@app.route('/api/sensor/temp-humidity', methods=['GET'])
def get_temp_humidity():
    """获取温湿度数据的API端点"""
    get_sensor_data("temp-humidity")
    return jsonify({
        "success": True,
        "data": {
            "temperature": latest_data["temperature"],
            "humidity": latest_data["humidity"]
        }
    })

@app.route('/api/sensor/all', methods=['GET'])
def get_all_data():
    
    get_sensor_data("all")
    return jsonify({
        "success": True,
        "data": latest_data
    })

@app.route('/api/control/led/<status>', methods=['GET'])
def control_led(status):
    
    try:
        with serial_lock:
            if serial_tool is None:
                if not init_serial():
                    return jsonify({"success": False, "message": "串口连接失败"})
            
            if status == "on":
                serial_tool.hardwareSend(HardwareType.led, HardwareCommand.control, HardwareOperate.LEDALLON)
                message = "LED已打开"
            elif status == "off":
                serial_tool.hardwareSend(HardwareType.led, HardwareCommand.control, HardwareOperate.LEDALLOFF)
                message = "LED已关闭"
            else:
                return jsonify({"success": False, "message": "无效的状态参数，使用 'on' 或 'off'"})
            
            sleep(1)
            return jsonify({"success": True, "message": message, "status": serial_tool.ledData})
    except Exception as e:
        logger.error(f"控制LED时出错: {str(e)}")
        return jsonify({"success": False, "message": f"操作失败: {str(e)}"})

@app.route('/api/control/lcdtext/<content>', methods=['GET'])
def control_lcd(content):
    """控制LCD显示内容的API端点"""
    try:
        with serial_lock:
            if serial_tool is None:
                if not init_serial():
                    return jsonify({"success": False, "message": "串口连接失败"})
            
            try:
                # 尝试使用GBK编码验证内容是否可以被编码
                content_encoded = content.encode('gbk')
                serial_tool.hardwareSend(HardwareType.lcd, HardwareCommand.control, content)
                sleep(1)
                return jsonify({"success": True, "message": f"LCD显示内容已设置为: {content}"})
            except UnicodeEncodeError as ue:
                logger.error(f"LCD内容编码错误: {str(ue)}，正在将内容转换为GBK编码后再显示")
                converted_content = content.encode('gbk', errors='replace').decode('gbk')
                serial_tool.hardwareSend(HardwareType.lcd, HardwareCommand.control, converted_content)
                sleep(1)
                return jsonify({"success": True, "message": f"LCD显示内容已设置为: {converted_content}"})
    except Exception as e:
        logger.error(f"控制LCD时出错: {str(e)}")
        return jsonify({"success": False, "message": f"操作失败: {str(e)}"})

@app.route('/api/emo/<emotype>', methods=['GET'])
def change_emo(emotype):
    return emo(emotype)
if __name__ == '__main__':
    #server = pywsgi.WSGIServer(('127.0.0.1', 5000), app)  
    #server.serve_forever()
    # start server
    app.run(host='127.0.0.1', port=5000, debug=True)