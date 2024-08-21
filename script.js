document.getElementById('upload-button').addEventListener('click', function() {
    document.getElementById('video-upload').click();
});

document.getElementById('video-upload').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('file', file);

        // 업로드 상태 업데이트
        document.getElementById('upload-status').textContent = '동영상 업로드 중...';

        // 서버로 파일 전송
        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.videoUrl) {
                console.log("Video URL:", data.videoUrl);
                document.getElementById('uploaded-video').src = data.videoUrl;
                document.getElementById('uploaded-video').style.display = 'block';
                document.getElementById('upload-status').innerHTML = `<p>업로드 완료: <a href="${data.videoUrl}" target="_blank">${data.videoUrl}</a></p>`;
            } else {
                throw new Error('파일 업로드에 실패했습니다.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('upload-status').textContent = error.message || '파일 업로드 중 오류가 발생했습니다.';
            document.getElementById('result').innerText = ''; // 오류 시 결과를 표시하지 않음
        });
    }
});


// 주기적으로 예측 결과 확인
setInterval(function() {
    fetch('/callback')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && data.predicted_class) {
                document.getElementById('result').innerText = `Received predicted class: ${data.predicted_class}`;
            }
        })
        .catch(error => {
            console.error('Error fetching predicted class:', error);
        });
}, 5000); // 5초마다 요청

document.getElementById('tts-button').addEventListener('click', function() {
    const predictedText = document.getElementById('result').innerText.replace('Received predicted class: ', '');

    fetch('/speak', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: predictedText })
    })
    .then(response => response.blob())
    .then(blob => {
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);
        audio.play();
    })
    .catch(error => {
        console.error('TTS 요청 오류:', error);
    });
});
