import requests
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailSender:
    def __init__(self):
        self.email_settings = self._load_email_settings()
        self.template_settings = self._load_template_settings()
        self.sendcloud_api_url = "https://api.sendcloud.net/apiv2/mail/send"

    def _load_email_settings(self):
        settings_file = 'config/email_settings.json'
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_template_settings(self):
        template_file = 'config/email_template.json'
        if os.path.exists(template_file):
            with open(template_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'subject_template': '[{{website_name}}] 网站更新通知',
            'body_template': '''
网站: {{website_name}}
URL: {{url}}
检测时间: {{change_time}}

变化内容:
{{changes}}

{{ai_analysis}}
            ''',
            'ai_analysis_template': '''
AI分析结果:
{{ai_result}}
            '''
        }

    def _render_template(self, template, **kwargs):
        """渲染邮件模板"""
        rendered = template
        for key, value in kwargs.items():
            rendered = rendered.replace(f'{{{{{key}}}}}', str(value))
        return rendered

    def send_mail(self, subject=None, content=None, recipients=[], cc_recipients=None, 
                  website_name="", url="", changes="", ai_result=None):
        if not self.email_settings:
            print("邮件设置未配置")
            return False

        # 准备模板变量
        template_vars = {
            'website_name': website_name,
            'url': url,
            'change_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'changes': changes,
            'ai_analysis': ''
        }

        # 处理AI分析结果
        if ai_result:
            ai_analysis = self._render_template(
                self.template_settings.get('ai_analysis_template', '{{ai_result}}'),
                ai_result=ai_result
            )
            template_vars['ai_analysis'] = ai_analysis

        # 使用模板或直接使用传入的内容
        if not subject:
            subject = self._render_template(
                self.template_settings.get('subject_template', '[{{website_name}}] 网站更新通知'),
                **template_vars
            )
        
        if not content:
            content = self._render_template(
                self.template_settings.get('body_template', '{{changes}}'),
                **template_vars
            )

        # 根据配置的服务类型发送邮件
        service_type = self.email_settings.get('service_type', 'sendcloud')
        
        if service_type == 'sendcloud':
            return self._send_via_sendcloud(subject, content, recipients, cc_recipients)
        elif service_type == 'smtp':
            return self._send_via_smtp(subject, content, recipients, cc_recipients)
        else:
            print(f"不支持的邮件服务类型: {service_type}")
            return False

    def _send_via_sendcloud(self, subject, content, recipients, cc_recipients=None):
        """通过 SendCloud API 发送邮件"""
        params = {
            "apiUser": self.email_settings.get('api_user'),
            "apiKey": self.email_settings.get('api_key'),
            "from": self.email_settings.get('from_email', 'service@sendcloud.im'),
            "fromName": self.email_settings.get('from_name', 'Web Change Notify'),
            "to": ', '.join(recipients),
            "subject": subject,
            "html": content.replace('\n', '<br>')
        }
        
        print(f"SendCloud 发送参数: {params}")
        
        # 添加抄送收件人
        if cc_recipients:
            params["cc"] = ', '.join(cc_recipients)

        try:
            response = requests.post(self.sendcloud_api_url, files={}, data=params)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result') == True:
                    print("邮件发送成功")
                    return True
                else:
                    print(f"邮件发送失败: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"API 请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"SendCloud 发送邮件失败: {str(e)}")
            return False

    def _send_via_smtp(self, subject, content, recipients, cc_recipients=None):
        """通过 SMTP 发送邮件"""
        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = self.email_settings.get('email_account')
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            if cc_recipients:
                msg['Cc'] = ', '.join(cc_recipients)
            
            # 添加邮件正文
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 连接SMTP服务器
            server = smtplib.SMTP(
                self.email_settings.get('smtp_server'),
                int(self.email_settings.get('smtp_port', 587))
            )
            server.starttls()
            server.login(
                self.email_settings.get('email_account'),
                self.email_settings.get('email_password')
            )
            
            # 发送邮件
            all_recipients = recipients + (cc_recipients or [])
            server.sendmail(
                self.email_settings.get('email_account'),
                all_recipients,
                msg.as_string()
            )
            server.quit()
            
            print("SMTP 邮件发送成功")
            return True
            
        except Exception as e:
            print(f"SMTP 发送邮件失败: {str(e)}")
            return False

# if __name__ == "__main__":
#     email_sender = EmailSender()
#     email_sender.send_mail("测试邮件", "这是一封测试邮件", ["Wafi_Wang@asus.com"])