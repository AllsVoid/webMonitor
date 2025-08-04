// AI 模型切换处理
function handleAIModelChange() {
    const aiChoice = document.getElementById('ai_choice').value;
    const aiModel = document.getElementById('ai_model');
    const aiApiUrl = document.getElementById('ai_api_url');
    
    // 根据选择的 AI 设置默认值
    switch(aiChoice) {
        case 'chatgpt':
            aiModel.value = aiModel.value || 'gpt-4';
            aiApiUrl.value = aiApiUrl.value || 'https://api.openai.com/v1/chat/completions';
            break;
        case 'gemini':
            aiModel.value = aiModel.value || 'gemini-pro';
            aiApiUrl.value = aiApiUrl.value || 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';
            break;
        case 'volcano':
            aiModel.value = aiModel.value || 'chatglm3-6b';
            aiApiUrl.value = aiApiUrl.value || 'https://api.volcengine.com/ml-platform/v1/model/invoke';
            break;
        case 'deepseek':
            aiModel.value = aiModel.value || 'deepseek-chat';
            aiApiUrl.value = aiApiUrl.value || 'https://api.deepseek.com/v1/chat/completions';
            break;
    }
}

// 加载 AI 设置
function loadAISettings() {
    fetch('/api/settings/ai')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.settings) {
                const settings = data.settings;
                
                // 设置 AI 选择
                if (settings.model) {
                    // 根据模型名称推断 AI 类型
                    let aiChoice = 'chatgpt';
                    if (settings.model.includes('gemini')) {
                        aiChoice = 'gemini';
                    } else if (settings.model.includes('chatglm')) {
                        aiChoice = 'volcano';
                    } else if (settings.model.includes('deepseek')) {
                        aiChoice = 'deepseek';
                    }
                    
                    document.getElementById('ai_choice').value = aiChoice;
                }
                
                // 填充其他字段
                document.getElementById('ai_model').value = settings.model || '';
                document.getElementById('ai_api_token').value = settings.api_token || '';
                document.getElementById('ai_api_url').value = settings.api_url || '';
                
                // 触发模型变更处理
                handleAIModelChange();
            }
        })
        .catch(error => {
            console.error('加载 AI 设置失败:', error);
        });
}

// 保存 AI 设置
function saveAISettings() {
    const settings = {
        model: document.getElementById('ai_model').value,
        api_token: document.getElementById('ai_api_token').value,
        api_url: document.getElementById('ai_api_url').value
    };
    
    fetch('/api/settings/ai', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success || data.message === 'AI设置保存成功') {
            alert('AI 设置保存成功');
        } else {
            alert('AI 设置保存失败：' + (data.message || '未知错误'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('保存失败: ' + error.message);
    });
}

// 页面加载完成后自动加载设置
document.addEventListener('DOMContentLoaded', function() {
    loadAISettings();
});