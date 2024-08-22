document.getElementById('upload-button').addEventListener('click', function() {
    document.getElementById('video-upload').click();
});
//=================================================================
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
                document.getElementById('upload-status').innerHTML = `<p>업로드 완료</p>`;
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
//=================================================================

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

//=================================================================
let audio;  // 전역 변수로 오디오 객체 선언

// 공통 TTS 요청 함수
function requestTTS(text) {
    fetch('/speak', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => response.blob())
    .then(blob => {
        const audioUrl = URL.createObjectURL(blob);

        // 이전 오디오가 재생 중이면 정지하고 제거
        if (audio) {
            audio.pause();
            audio.currentTime = 0;  // 오디오를 처음으로 되돌림
            URL.revokeObjectURL(audio.src);  // 이전 오디오 URL 해제
        }

        audio = new Audio(audioUrl);  // 새로운 오디오 객체 생성
        audio.play();  // 새로운 오디오 재생

        // 멈추기 버튼 표시
        document.getElementById('stop-button').style.display = 'inline-block';

        // 오디오가 끝나면 멈추기 버튼 숨기기
        audio.addEventListener('ended', function() {
            document.getElementById('stop-button').style.display = 'none';
        });
    })
    .catch(error => {
        console.error('TTS 요청 오류:', error);
    });
}

// 오디오 멈추기 버튼 이벤트 핸들러
document.getElementById('stop-button').addEventListener('click', function() {
    if (audio) {
        audio.pause();
        audio.currentTime = 0;  // 오디오를 처음으로 되돌림
        document.getElementById('stop-button').style.display = 'none';  // 멈추기 버튼 숨기기
    }
});

// 비디오와 관련된 TTS 요청 처리
document.getElementById('tts-button').addEventListener('click', function() {
    const predictedText = document.getElementById('result').innerText.replace('Received predicted class: ', '');
    requestTTS(predictedText); // 공통 함수 호출
});

// 동화 읽기 버튼 클릭 이벤트 핸들러
function readStory() {
    const storyText = document.querySelector('.FairyTail').dataset.story;  // 데이터 속성에서 story 읽기
    requestTTS(storyText); // 공통 함수 호출
}



