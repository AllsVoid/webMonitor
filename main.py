import requests
import hashlib
import os
from datetime import datetime
import time
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class WebsiteMonitor:
    def __init__(self, url, save_dir='website_snapshots'):
        self.url = url
        self.save_dir = save_dir
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 创建保存目录
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
    def get_website_content(self):
        """获取网站内容"""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"获取网站内容时出错: {e}")
            return None
            
    def save_content(self, content):
        """保存网站内容到文件"""
        if content is None:
            return None
            
        # 生成文件名（使用时间戳）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}.html"
        filepath = os.path.join(self.save_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info(f"内容已保存到: {filepath}")
            return filepath
        except IOError as e:
            logging.error(f"保存文件时出错: {e}")
            return None
            
    def get_content_hash(self, content):
        """计算内容的哈希值"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
        
    def check_for_changes(self, previous_hash, current_content):
        """检查内容是否发生变化"""
        if current_content is None:
            return False
        current_hash = self.get_content_hash(current_content)
        return previous_hash != current_hash

def main():
    # 配置参数
    url = "http://192.168.16.65/wafi/"  # 替换为要监控的网站URL
    check_interval = 300  # 检查间隔（秒）
    
    monitor = WebsiteMonitor(url)
    previous_content = monitor.get_website_content()
    
    if previous_content is None:
        logging.error("初始化失败，无法获取网站内容")
        return
        
    previous_hash = monitor.get_content_hash(previous_content)
    monitor.save_content(previous_content)
    
    logging.info(f"开始监控网站: {url}")
    logging.info(f"检查间隔: {check_interval}秒")
    
    try:
        while True:
            time.sleep(check_interval)
            current_content = monitor.get_website_content()
            
            if monitor.check_for_changes(previous_hash, current_content):
                logging.info("检测到网站内容发生变化！")
                monitor.save_content(current_content)
                previous_hash = monitor.get_content_hash(current_content)
            else:
                logging.info("网站内容未发生变化")
                
    except KeyboardInterrupt:
        logging.info("监控程序已停止")

if __name__ == "__main__":
    main()
