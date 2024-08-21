import os
from flask import Flask, render_template, jsonify, request
from google.cloud import storage, translate_v2 as translate
from flask_cors import CORS
from google.cloud import texttospeech
from flask import send_file
from gemini_api import generate_story_with_gemini


# GCP 서비스 계정 키 파일 설정
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'andong-24-team-103-b64ebb4e3719.json'

app = Flask(__name__)
CORS(app)

# Google Cloud Storage 클라이언트 설정
bucket_name = 'forcloudfuntions'
predictions_store = []

# Google Cloud Translation 클라이언트 설정
translate_client = translate.Client()

# Google Cloud Text-to-Speech 클라이언트 설정
tts_client = texttospeech.TextToSpeechClient()



# 전역 변수로 예측 결과 저장
predicted_class_name = None

#===========================================================================================
@app.route('/', methods=['GET', 'POST'], endpoint='index')
def upload_video():
    global predicted_class_name
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400
        if file:
            # GCS에 파일 업로드 (구현)
            gcs_url = upload_to_gcs(file, bucket_name, file.filename)

            # GCS URL 반환
            return jsonify({'videoUrl': gcs_url})
    
    # GET 요청 시 predicted_class_name을 템플릿으로 전달
    return render_template('index.html', predicted_class_name=predicted_class_name)

#===========================================================================================
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

#===========================================================================================

# GCS에 파일 업로드하는 함수
def upload_to_gcs(file, bucket_name, destination_blob_name):
    """파일을 GCS에 업로드합니다."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)  # Blob 객체 생성
    blob.upload_from_file(file)  # 파일을 업로드
    return blob.public_url  # 파일의 공개 URL 반환

#===========================================================================================
@app.route('/callback', methods=['POST', 'GET'])
def callback():
    global predicted_class_name
    if request.method == 'POST':
        data = request.json
        if not data or 'predicted_class' not in data:
            return jsonify({'status': 'error', 'message': 'Invalid data'}), 400
        
        predicted_class_name = data['predicted_class']
        print(f"APP.PY Received predicted class: {predicted_class_name}")

        # 예측된 클래스를 한글로 번역
        translated_class_name = translate_to_korean(predicted_class_name)
        print(f"Translated class: {translated_class_name}")

        return jsonify({'status': 'success', 'predicted_class': translated_class_name})
    
    # GET 요청 시 저장된 예측 결과 반환
    elif request.method == 'GET':
        translated_class_name = translate_to_korean(predicted_class_name)
        return jsonify({'status': 'success', 'predicted_class': translated_class_name})


def translate_to_korean(text):
    """텍스트를 한국어로 번역합니다."""
    if not text:
        return "No text provided"

    translation = translate_client.translate(text, target_language="ko")
    return translation['translatedText']


#===========================================================================================
def text_to_speech(text):
    """텍스트를 한국어 음성으로 변환"""
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    
    return response.audio_content

@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({'status': 'error', 'message': 'Text not provided'}), 400
    
    # 텍스트를 음성으로 변환
    audio_content = text_to_speech(text)

    # 오디오 데이터를 MP3 파일로 저장
    audio_filename = "output.mp3"
    with open(audio_filename, "wb") as audio_file:
        audio_file.write(audio_content)

    # 파일을 클라이언트로 전송
    return send_file(audio_filename, as_attachment=True)
#===========================================================================================
@app.route('/favicon.ico')
def favicon():
    return '', 204
#===========================================================================================


@app.route('/generate_story', methods=['POST'])
def create_story():
    data = request.json
    keywords = data.get('keywords', '')

    if not keywords:
        return jsonify({'status': 'error', 'message': 'No keywords provided'}), 400

    story = generate_story_with_gemini(keywords)
    if story:
        return jsonify({'status': 'success', 'story': story})
    else:
        return jsonify({'status': 'error', 'message': 'Story generation failed'}), 500

#===========================================================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
