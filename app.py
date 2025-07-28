from flask import Flask, render_template, request, jsonify
from monitor import WebsiteMonitor, RSSMonitor, GitHubMonitor
from database import Database
import json
import os

app = Flask(__name__)
db = Database()

@app.route('/')
def index():
    tasks = db.get_all_tasks()
    return render_template('index.html', tasks=tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    
    if data['mode'] == 'website':
        monitor = WebsiteMonitor(
            url=data['url'],
            interval=int(data['interval']),
            compare_mode=data['compareMode'],
            send_mail=data['sendMail'],
            email_addresses=data['emailAddresses'],
            cc_addresses=data['ccAddresses']
        )
    elif data['mode'] == 'github':
        monitor = GitHubMonitor(
            url=data['url'],
            interval=int(data['interval']),
            compare_mode=data['compareMode'],
            send_mail=data['sendMail'],
            email_addresses=data['emailAddresses'],
            cc_addresses=data['ccAddresses']
        )
    elif data['mode'] == 'rss':
        monitor = RSSMonitor(
            url=data['url'],
            interval=int(data['interval']),
            compare_mode=data['compareMode'],
            send_mail=data['sendMail'],
            email_addresses=data['emailAddresses'],
            cc_addresses=data['ccAddresses']
        )
    else:
        return jsonify({'error': '不支持的监控模式'}), 400

    task_id = db.add_task(monitor)
    
    monitor.start()
    
    return jsonify({
        'id': task_id,
        'message': '任务添加成功'
    })

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    db.delete_task(task_id)
    return jsonify({'message': '任务删除成功'})

@app.route('/api/tasks/<task_id>/pause', methods=['POST'])
def pause_task(task_id):
    task = db.get_task(task_id)
    if task:
        task.pause()
        return jsonify({'message': '任务已暂停'})
    return jsonify({'error': '任务不存在'}), 404

@app.route('/api/settings/ai', methods=['POST'])
def save_ai_settings():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        settings = {
            'model': data.get('model'),
            'api_token': data.get('api_token'),
            'api_url': data.get('api_url')
        }
        
        os.makedirs('config', exist_ok=True)
        
        with open('config/ai_settings.json', 'w') as f:
            json.dump(settings, f)
        
        return jsonify({'message': 'AI设置保存成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/email', methods=['POST'])
def save_email_settings():
    try:
        data = request.get_json()
        print(data)
        
        if not data:
            return jsonify({'success': False, 'message': '无效的请求数据'}), 400
        
        # 确保目录存在
        os.makedirs('config', exist_ok=True)
        
        if data.get('flag') == '0':
            # SMTP 设置
            settings = {
                'service_type': 'smtp',
                'smtp_server': data.get('smtp_server'),
                'smtp_port': data.get('smtp_port'),
                'email_account': data.get('email_account'),
                'email_password': data.get('email_password')
            }
        elif data.get('flag') == '1':
            # SendCloud 设置
            settings = {
                'service_type': 'sendcloud',
                'api_user': data.get('api_user'),
                'api_key': data.get('api_key'),
                'from_email': data.get('from_email'),
                'from_name': data.get('from_name')
            }
        else:
            return jsonify({'success': False, 'message': '无效的服务类型标识'}), 400
        
        with open('config/email_settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True, 'message': '邮件设置保存成功'})
        
    except Exception as e:
        print(f"保存邮件设置时出错: {e}")
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'}), 500

if __name__ == '__main__':
    import webbrowser
    import threading
    import time
    
    # 创建必要的目录
    os.makedirs('website_snapshots', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    
    print("🚀 启动网站变化监控系统...")
    print("📋 正在启动 Web 服务器...")
    
    # 在单独线程中启动浏览器
    def open_browser():
        time.sleep(1.5)  # 等待服务器启动
        url = "http://127.0.0.1:5000"
        print(f"🌐 正在打开浏览器: {url}")
        webbrowser.open(url)
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    print("✅ 服务器已启动，访问地址: http://127.0.0.1:5000")
    print("💡 提示: 关闭此窗口将停止服务")
    print("-" * 50)
    
    try:
        app.run(host='127.0.0.1', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"\n❌ 服务启动失败: {e}")
        input("按任意键退出...")