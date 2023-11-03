function validateForm() {
    var username = document.querySelector('input[name="username"]').value;
    var email = document.querySelector('input[name="email"]').value;
    var password = document.querySelector('#password').value;
    var confirmPassword = document.querySelector('#confirm-password').value;

    // 检查密码是否匹配
    if (password !== confirmPassword) {
        var errorMessagesDiv = document.getElementById('error-password');
        errorMessagesDiv.textContent = "パスワードが一致しません.";
        return false;
    } else {
        var errorMessagesDiv = document.getElementById('error-password');
        errorMessagesDiv.textContent = "";
    }

    // 检查其他字段是否符合要求，根据需要添加更多验证

    // 如果所有验证通过，清空错误消息
    var errorMessagesDiv = document.getElementById('error-messages');
    errorMessagesDiv.textContent = "";

    // 如果验证通过，返回true允许表单提交
    return true;
}
