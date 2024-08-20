import os
from flask import Flask, render_template, jsonify, request
from google.cloud import storage, texttospeech
from flask_cors import CORS

# 전역 변수로 예측 결과 저장
predicted_class = None

# GCP 서비스 계정 키 파일 설정
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'andong-24-team-103-b64ebb4e3719.json'

app = Flask(__name__)
CORS(app)

# Google Cloud Storage 클라이언트 설정
bucket_name = 'forcloudfuntions'
predictions_store = []

# 기본 경로 라우트 (index.html)
@app.route('/', methods=['GET', 'POST'], endpoint='index')
def upload_video():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400
        if file:
            gcs_url = upload_to_gcs(file, bucket_name, file.filename)
            return jsonify({'videoUrl': gcs_url})
    return render_template('index.html')




# 추가된 HTML 파일에 대한 라우트 정의
@app.route('/education')
def education():
    return render_template('education.html')

@app.route('/community')
def community():
    return render_template('community.html')

@app.route('/learning')
def learning():
    return render_template('learning.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

# GCS에 파일 업로드하는 함수
def upload_to_gcs(file, bucket_name, destination_blob_name):
    """파일을 GCS에 업로드합니다."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)  # Blob 객체 생성
    blob.upload_from_file(file)  # 파일을 업로드
    return blob.public_url  # 파일의 공개 URL 반환



@app.route('/callback', methods=['POST'])
def callback():
    global predicted_class
    data = request.json  # JSON 데이터를 파싱합니다.
    if not data or 'predicted_class' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid data'}), 400
    
    predicted_class = data['predicted_class']
    print(f"Received predicted class: {predicted_class}")
    
    # 받은 데이터를 HTML에서 사용할 수 있도록 저장
    return jsonify({'status': 'success', 'received_class': predicted_class})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

