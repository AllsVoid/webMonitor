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
from test_ai import AiClient

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
            time.sleep(self.interval * 60)

    def _check_changes(self):
        raise NotImplementedError

    def _save_snapshot(self, content, timestamp=None):
        if not timestamp:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}.html"
        filepath = os.path.join(self.snapshot_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath

    def _compare_content(self, old_content, new_content):
        if not old_content:
            return "首次获取，无法比较变化"
        
        diff = difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            lineterm=''
        )
        with open("diff.txt", "w", encoding="utf-8") as f:
            f.write('\n'.join(diff))
        return '\n'.join(diff)

    def _get_ai_response(self, diff):
        with open("diff.txt", "w", encoding="utf-8") as f:
            f.write(diff)
        ai_client = AiClient(
            model="gpt-4o-mini",
            diff=diff,
            base_url="https://ark.cn-beijing.volces.com/api/v3",
        )
        response = ai_client.get_response()
        return response

    def _notify_changes(self, changes):
        if self.send_mail and (self.email_addresses or self.cc_addresses):
            email_sender = EmailSender()
            subject = f"监控到变化 - {self.url}"
            email_sender.send_mail(
                subject=subject,
                content=changes,
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
                changes = self._compare_content(self.last_content, current_content)
                if changes:
                    print(f"检测到变化:\n{changes}")
                    self._notify_changes(changes)
            
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