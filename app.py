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
    
    # 创建监控器实例
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

    # 保存任务到数据库
    task_id = db.add_task(monitor)
    
    # 启动监控
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

@app.route('/api/settings/email', methods=['POST'])
def save_email_settings():
    data = request.get_json()
    settings = {
        'smtp_server': data['smtp_server'],
        'smtp_port': data['smtp_port'],
        'email_account': data['email_account'],
        'email_password': data['email_password'],
        'api_key': data['api_key']
    }
    
    # 保存设置到配置文件
    with open('config/email_settings.json', 'w') as f:
        json.dump(settings, f)
    
    return jsonify({'message': '设置保存成功'})

if __name__ == '__main__':
    # 确保必要的目录存在
    os.makedirs('website_snapshots', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    
    app.run(debug=True)