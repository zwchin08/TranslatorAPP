var clipboard = new ClipboardJS('#copy-button');

clipboard.on('success', function (e) {
    var copyButton = document.getElementById('copy-button');
    copyButton.textContent = 'Copied!';
    copyButton.classList.add('clicked');
    var copyBar = document.querySelector('.copy-bar');
    copyBar.style.display = 'block';
    setTimeout(function () {
        copyButton.textContent = 'Copy code';
        copyButton.classList.remove('clicked');
        copyBar.style.display = 'none';
    }, 2000); // 2秒后恢复按钮文本和隐藏条形框
});

clipboard.on('error', function (e) {
    alert('复制失败，请手动复制文本');
});

