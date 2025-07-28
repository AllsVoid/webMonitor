 // 添加新任务
function addTask() {
    const mode = document.getElementById('monitor_mode').value;
    let url;
    
    switch(mode) {
        case 'website':
            url = document.getElementById('monitor_website').value;
            break;
        case 'github':
            url = document.getElementById('monitor_github').value;
            break;
        case 'rss':
            url = document.getElementById('monitor_rss').value;
            break;
    }

    // 验证必填字段
    if (!url) {
        alert('请输入监控地址！');
        return;
    }
    if (!document.getElementById('time').value) {
        alert('请输入监控时间间隔！');
        return;
    }
    
    const task = {
        mode: mode,
        url: url,
        interval: document.getElementById('time').value,
        compareMode: document.querySelector('input[name="compare_mode"]:checked')?.value === '1',
        sendMail: document.querySelector('input[name="send_mail"]:checked')?.value === '1',
        emailAddresses: getEmailAddresses(),
        ccAddresses: getCCAddresses()
    };
    
    // 发送到后端保存
    fetch('/api/tasks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(task)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('添加任务失败：' + data.error);
        } else {
            alert('任务添加成功！');
            // 刷新页面以显示新任务
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('添加任务失败，请检查网络连接！');
    });
}

// 暂停任务
function pauseTask(taskId) {
    fetch(`/api/tasks/${taskId}/pause`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('暂停任务失败：' + data.error);
        } else {
            alert('任务已暂停');
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('暂停任务失败，请检查网络连接！');
    });
}

// 删除任务
function deleteTask(taskId) {
    if (!confirm('确定要删除这个任务吗？')) {
        return;
    }
    
    fetch(`/api/tasks/${taskId}`, {
        method: 'DELETE',
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('删除任务失败：' + data.error);
        } else {
            alert('任务已删除');
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('删除任务失败，请检查网络连接！');
    });
}

// AI模型切换处理
function handleAIModelChange() {
    const model = document.getElementById('ai_choice').value;
    const apiUrlInput = document.getElementById('ai_api_url');
    
    // 根据不同的AI模型设置默认API URL
    switch(model) {
        case 'chatgpt':
            apiUrlInput.value = 'https://api.openai.com/v1/chat/completions';
            break;
        case 'gemini':
            apiUrlInput.value = 'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent';
            break;
        case 'volcano':
            apiUrlInput.value = 'https://ark.cn-beijing.volces.com/api/v3';
            break;
        case 'deepseek':
            apiUrlInput.value = 'https://api.deepseek.com/v1/chat/completions';
            break;
    }
}

// 保存AI设置
function saveAISettings() {
    const settings = {
        'model': document.getElementById('ai_model').value,
        'api_token': document.getElementById('ai_api_token').value,
        'api_url': document.getElementById('ai_api_url').value
    };

    fetch('/api/settings/ai', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(result => {
        if (result.message) {
            alert('AI设置保存成功！');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('保存AI设置时发生错误');
    });
}

// 保存邮件模板设置
function saveEmailTemplate() {
    const template = {
        subject: document.getElementById('email_subject_template').value,
        body: document.getElementById('email_body_template').value,
        aiAnalysis: document.getElementById('ai_analysis_template').value
    };

    fetch('/api/settings/email-template', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(template)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('邮件模板保存成功！');
        } else {
            alert('保存失败：' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('保存失败，请检查网络连接');
    });
}

// 页面加载时加载设置
document.addEventListener('DOMContentLoaded', function() {
    // 加载AI设置
    fetch('/api/settings/ai')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('ai_model').value = data.settings.model;
                document.getElementById('ai_api_token').value = data.settings.apiToken;
                document.getElementById('ai_api_url').value = data.settings.apiUrl;
            }
        });

    // 加载邮件模板设置
    fetch('/api/settings/email-template')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('email_subject_template').value = data.template.subject;
                document.getElementById('email_body_template').value = data.template.body;
                document.getElementById('ai_analysis_template').value = data.template.aiAnalysis;
            }
        });
});