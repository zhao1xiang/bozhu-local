#!/usr/bin/env python3
"""
医院切换工具
"""
import yaml
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logger import logger

CONFIG_FILE = "config/config.yaml"


def load_config():
    """加载配置文件"""
    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)


def save_config(config):
    """保存配置文件"""
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def list_hospitals():
    """列出所有可用的医院"""
    config = load_config()
    current = config.get("active_hospital")
    
    print("\n可用的医院配置:")
    print("-" * 50)
    
    for hospital_id, hospital_config in config["hospitals"].items():
        status = " (当前)" if hospital_id == current else ""
        print(f"  {hospital_id}: {hospital_config['name']}{status}")
    
    print("-" * 50)


def switch_hospital(hospital_id):
    """切换到指定医院"""
    config = load_config()
    
    if hospital_id not in config["hospitals"]:
        print(f"错误: 医院 '{hospital_id}' 不存在")
        list_hospitals()
        return False
    
    old_hospital = config.get("active_hospital")
    config["active_hospital"] = hospital_id
    
    try:
        save_config(config)
        hospital_name = config["hospitals"][hospital_id]["name"]
        print(f"成功切换到: {hospital_name} ({hospital_id})")
        
        if old_hospital:
            old_name = config["hospitals"][old_hospital]["name"]
            print(f"之前的医院: {old_name} ({old_hospital})")
        
        return True
        
    except Exception as e:
        print(f"切换失败: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python tools/switch_hospital.py list          # 列出所有医院")
        print("  python tools/switch_hospital.py <hospital_id> # 切换到指定医院")
        print("\n示例:")
        print("  python tools/switch_hospital.py hospital1")
        print("  python tools/switch_hospital.py hospital2")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_hospitals()
    elif command in ["help", "-h", "--help"]:
        main()
    else:
        # 尝试切换到指定医院
        if switch_hospital(command):
            print("\n提示: 请重启同步服务以使配置生效")


if __name__ == "__main__":
    main()