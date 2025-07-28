import requests
from bs4 import BeautifulSoup
import feedparser
import time
import threading
import os
from datetime import datetime
import difflib
import json
from email_sender import EmailSender
from ai import AiClient

class BaseMonitor:
    def __init__(self, url, interval, compare_mode=False, send_mail=False, 
                 email_addresses=None, cc_addresses=None):
        self.url = url
        self.interval = interval
        self.compare_mode = compare_mode
        self.send_mail = send_mail
        self.email_addresses = email_addresses or []
        self.cc_addresses = cc_addresses or []
        self.running = False
        self.thread = None
        self.last_content = None
        self.snapshot_dir = 'website_snapshots'

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop)
            self.thread.daemon = True
            self.thread.start()

    def pause(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _monitor_loop(self):
        while self.running:
            try:
                self._check_changes()
            except Exception as e:
                print(f"监控出错: {str(e)}")
            time.sleep(self.interval * 10)

    def _check_changes(self):
        raise NotImplementedError

    def _save_snapshot(self, content, timestamp=None):
        if not timestamp:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}.html"
        filepath = os.path.join(self.snapshot_dir, filename)
        
        os.makedirs(self.snapshot_dir, exist_ok=True)

        if isinstance(content, bytes):
            content = content.decode('utf-8')
            
        with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(content)
        return filepath

    def _compare_content(self, old_content, new_content):
        if not old_content:
            return "首次获取，无法比较变化"
        
        diff_lines = list(difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            lineterm=''
        ))
        
        diff_text = '\n'.join(diff_lines)
        
        with open("diff.txt", "w", encoding="utf-8") as f:
            f.write(diff_text)
        if diff_lines:
            try:
                ai_result = self._get_ai_response(diff_text)
                return diff_text, ai_result
            except Exception as e:
                print(f"AI分析出错: {str(e)}")
                return diff_text, None
                
        return diff_text, None

    def _get_ai_response(self, diff):
        with open("config/ai_settings.json", "r", encoding="utf-8") as f:
            ai_settings = json.load(f)
        print("DBG, ai_settings", ai_settings)
        ai_client = AiClient(
            model=ai_settings['model'],
            diff=diff,
            base_url=ai_settings['api_url'],
            api_token=ai_settings['api_token']
        )
        print("DBG, ai_client", ai_client)
        return ai_client.get_response()

    def _notify_changes(self, changes, ai_result=None):
        if self.send_mail and (self.email_addresses or self.cc_addresses):
            email_sender = EmailSender()
            
            # 提取网站名称（简单处理，可以进一步优化）
            website_name = self.url.split('//')[-1].split('/')[0]
            
            email_sender.send_mail(
                website_name=website_name,
                url=self.url,
                changes=changes,
                ai_result=ai_result,
                recipients=self.email_addresses,
                cc_recipients=self.cc_addresses
            )

class WebsiteMonitor(BaseMonitor):
    def _check_changes(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        current_content = soup.prettify()
        
        if self.compare_mode:
            if self.last_content:
                diff_text, ai_result = self._compare_content(self.last_content, current_content)
                if diff_text:
                    print(f"检测到变化:\n{diff_text}")
                    
                    try:
                        if ai_result:
                            ai_result_dict = json.loads(ai_result)
                            print(f"AI 分析结果:\n{json.dumps(ai_result_dict, indent=2, ensure_ascii=False)}")
                            
                            if ai_result_dict.get('review_needed', True):
                                print("AI 建议需要人工审查，发送通知...")
                                self._notify_changes(diff_text, ai_result)
                            else:
                                print("AI 判断不需要review，跳过邮件通知")
                        else:
                            print("未获得AI分析结果，按默认方式处理...")
                            self._notify_changes(diff_text)
                    except json.JSONDecodeError as e:
                        print(f"AI返回结果解析失败: {e}，按默认方式处理...")
                        self._notify_changes(diff_text)
                    except Exception as e:
                        print(f"处理AI分析结果时出错: {e}，按默认方式处理...")
                        self._notify_changes(diff_text)
            
            self.last_content = current_content
        
        self._save_snapshot(current_content)

class RSSMonitor(BaseMonitor):
    def _check_changes(self):
        feed = feedparser.parse(self.url)
        current_content = json.dumps(feed.entries, indent=2, ensure_ascii=False)
        
        if self.compare_mode:
            if self.last_content:
                changes = self._compare_content(self.last_content, current_content)
                if changes:
                    print(f"检测到RSS更新:\n{changes}")
                    self._notify_changes(changes)
            
            self.last_content = current_content
        
        self._save_snapshot(current_content)

class GitHubMonitor(BaseMonitor):
    def _check_changes(self):
        # 添加releases.atom后缀
        if not self.url.endswith('/releases.atom'):
            self.url = f"{self.url.rstrip('/')}/releases.atom"
        
        response = requests.get(self.url)
        feed = feedparser.parse(response.text)
        current_content = json.dumps(feed.entries, indent=2, ensure_ascii=False)
        
        if self.compare_mode:
            if self.last_content:
                changes = self._compare_content(self.last_content, current_content)
                if changes:
                    print(f"检测到GitHub更新:\n{changes}")
                    self._notify_changes(changes)
            
            self.last_content = current_content
        
        self._save_snapshot(current_content)