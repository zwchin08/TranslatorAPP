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

document.addEventListener('DOMContentLoaded', function () {

    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = document.getElementById('inputLanguage').value;

        document.getElementById('inputLanguage').addEventListener('change', function () {
            recognition.lang = this.value;
        });

        let isListening = false;

        document.getElementById('voiceButton').addEventListener('click', function (event) {
            event.preventDefault(); // 阻止默认的提交行为
            isListening = !isListening;

            if (isListening) {
                recognition.start();
            } else {
                recognition.stop();
            }
        });

        recognition.onresult = function (event) {
            const transcript = event.results[0][0].transcript;
            if (isListening) {
                document.getElementById('textToTranslate').value += transcript;
            }
        };

        recognition.onend = function () {
            if (isListening) {
                recognition.start();
            }
        };
    } else {
        document.getElementById('textToTranslate').value = '抱歉，你的浏览器不支持语音识别功能。';
    }


    // 获取页面元素
    const imageInput = document.getElementById('imageInput');
    const textToTranslate = document.getElementById('textToTranslate');
    const imageButton = document.getElementById('imageButton');

    // 监听图像按钮的点击事件
    imageButton.addEventListener('click', function () {
        // 获取用户选择的图像文件
        const file = imageInput.files[0];

        if (file) {
            // 使用 FileReader 读取图像文件
            const reader = new FileReader();

            reader.onload = function (e) {
                // 获取图像数据
                const imageData = e.target.result;

                // 使用 Tesseract.js 进行图像识别
                Tesseract.recognize(
                    imageData,
                    'eng+jpn+chi_sim+mya', // 语言设置，可以根据需要调整
                    {
                        logger: info => console.log(info)
                    }
                ).then(({data: {text}}) => {
                    // 将图像识别的文本添加到 textToTranslate 元素中
                    textToTranslate.value = text;
                }).catch(error => {
                    console.error(error);
                });
            };

            // 读取图像文件
            reader.readAsDataURL(file);
        }
    });
});