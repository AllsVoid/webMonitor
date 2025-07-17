 // 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化监听模式
    handleModeChange();
});

// 监控模式切换处理
function handleModeChange() {
    const mode = document.getElementById('monitor_mode').value;
    // 隐藏所有输入框
    document.getElementById('website_input').style.display = 'none';
    document.getElementById('github_input').style.display = 'none';
    document.getElementById('rss_input').style.display = 'none';
    
    // 显示选中的输入框
    document.getElementById(`${mode}_input`).style.display = 'flex';
}

// 标签页切换
function switchTab(tabId) {
    // 移除所有标签页和按钮的active类
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });

    // 激活选中的标签页和按钮
    document.getElementById(tabId).classList.add('active');
    document.querySelector(`button[onclick="switchTab('${tabId}')"]`).classList.add('active');
}