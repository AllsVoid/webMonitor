import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

class EmailSender:
    def __init__(self):
        self.settings = self._load_settings()

    def _load_settings(self):
        settings_file = 'config/email_settings.json'
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                return json.load(f)
        return {}

    def send_mail(self, subject, content, recipients, cc_recipients=None):
        if not self.settings:
            print("邮件设置未配置")
            return False

        msg = MIMEMultipart()
        msg['From'] = self.settings['email_account']
        msg['To'] = ', '.join(recipients)
        if cc_recipients:
            msg['Cc'] = ', '.join(cc_recipients)
        msg['Subject'] = subject

        msg.attach(MIMEText(content, 'plain', 'utf-8'))

        try:
            server = smtplib.SMTP(self.settings['smtp_server'], 
                                int(self.settings['smtp_port']))
            server.starttls()
            server.login(self.settings['email_account'], 
                        self.settings['email_password'])
            
            all_recipients = recipients + (cc_recipients or [])
            server.sendmail(self.settings['email_account'], 
                          all_recipients, 
                          msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"发送邮件失败: {str(e)}")
            return False