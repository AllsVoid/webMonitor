 // 加载邮件设置
function loadEmailSettings() {
    fetch('/api/settings/email')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.settings) {
                const settings = data.settings;
                
                // 设置服务类型
                const serviceType = settings.service_type || 'sendcloud';
                document.getElementById('email_service_type').value = serviceType;
                handleEmailServiceChange();
                
                if (serviceType === 'sendcloud') {
                    document.getElementById('api_user').value = settings.api_user || '';
                    document.getElementById('api_key').value = settings.api_key || '';
                    document.getElementById('from_email').value = settings.from_email || '';
                    document.getElementById('from_name').value = settings.from_name || '';
                } else {
                    document.getElementById('smtp_server').value = settings.smtp_server || '';
                    document.getElementById('smtp_port').value = settings.smtp_port || '587';
                    document.getElementById('email_account').value = settings.email_account || '';
                    document.getElementById('email_password').value = settings.email_password || '';
                }
            }
        })
        .catch(error => {
            console.error('加载邮件设置失败:', error);
        });
}

// 页面加载完成后自动加载设置
document.addEventListener('DOMContentLoaded', function() {
    loadEmailSettings();
});

// 邮件字段处理
function handleCompareMode() {
    const sendMailGroup = document.getElementById('send_mail_group');
    const compareMode = document.querySelector('input[name="compare_mode"]:checked').value;
    sendMailGroup.style.display = compareMode === '1' ? 'flex' : 'none';
    if (compareMode === '0') {
        document.getElementById('mail_group').style.display = 'none';
        document.querySelectorAll('input[name="send_mail"]').forEach(radio => {
            radio.checked = false;
        });
    }
}

function handleSendMail() {
    const mailGroup = document.getElementById('mail_group');
    const sendMail = document.querySelector('input[name="send_mail"]:checked').value;
    mailGroup.style.display = sendMail === '1' ? 'flex' : 'none';
}

// 邮件服务类型切换
function handleEmailServiceChange() {
    const serviceType = document.getElementById('email_service_type').value;
    const sendcloudSettings = document.getElementById('sendcloud_settings');
    const smtpSettings = document.getElementById('smtp_settings');
    
    if (serviceType === 'sendcloud') {
        sendcloudSettings.style.display = 'block';
        smtpSettings.style.display = 'none';
    } else {
        sendcloudSettings.style.display = 'none';
        smtpSettings.style.display = 'block';
    }
}

// 邮件地址字段管理
function addEmailField(containerId) {
    const container = document.getElementById(containerId);
    const newRow = document.createElement('div');
    newRow.className = 'email-input-row';
    
    const input = document.createElement('input');
    input.type = 'email';
    input.placeholder = containerId === 'email_addresses' ? '请输入邮件地址...' : '请输入抄送地址...';
    
    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.className = 'btn-small remove';
    removeBtn.textContent = '-';
    removeBtn.onclick = function() {
        container.removeChild(newRow);
    };
    
    newRow.appendChild(input);
    newRow.appendChild(removeBtn);
    container.appendChild(newRow);
}

// 获取邮件地址
function getEmailAddresses() {
    const addresses = [];
    document.querySelectorAll('#email_addresses input').forEach(input => {
        if (input.value.trim()) {
            addresses.push(input.value.trim());
        }
    });
    return addresses;
}

// 获取抄送地址
function getCCAddresses() {
    const addresses = [];
    document.querySelectorAll('#email_cc input').forEach(input => {
        if (input.value.trim()) {
            addresses.push(input.value.trim());
        }
    });
    return addresses;
}

// 保存邮件设置
function saveEmailSettings() {
    const serviceType = document.getElementById('email_service_type').value;
    
    const settings = {
        service_type: serviceType
    };
    
    if (serviceType === 'sendcloud') {
        settings.flag = "1";
        settings.api_user = document.getElementById('api_user').value;
        settings.api_key = document.getElementById('api_key').value;
        settings.from_email = document.getElementById('from_email').value;
        settings.from_name = document.getElementById('from_name').value;
    } else {
        settings.flag = "0";
        settings.smtp_server = document.getElementById('smtp_server').value;
        settings.smtp_port = document.getElementById('smtp_port').value;
        settings.email_account = document.getElementById('email_account').value;
        settings.email_password = document.getElementById('email_password').value;
    }
    
    console.log('保存邮件设置:', settings);
      // 发送到后端保存
    fetch('/api/settings/email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('邮件设置保存成功');
        } else {
            alert('邮件设置保存失败：' + (data.message || '未知错误'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('保存失败: ' + error.message);
    });
}