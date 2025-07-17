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
    const settings = {
        smtp_server: document.getElementById('smtp_server').value,
        smtp_port: document.getElementById('smtp_port').value,
        email_account: document.getElementById('email_account').value,
        email_password: document.getElementById('email_password').value,
        api_key: document.getElementById('api_key').value
    };
    
    console.log('保存邮件设置:', settings);
    // TODO: 发送到后端保存
}