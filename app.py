from flask import Flask, request
from azure.storage.blob import BlobServiceClient
from imganalysis import analyze_image
import os
# from dotenv import load_dotenv

# 環境変数読み込み
# load_dotenv()
app = Flask(__name__)

# アップロード可能ファイル
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    name, extension = os.path.splitext(filename)
    extension = extension.lstrip('.')
    return extension in ALLOWED_EXTENSIONS

# BLOBに画像ファイルをアップロード
def upload_file():
    file = request.files['file']
    if allowed_file(file.filename):
        # Azure Blob Storageの接続文字列とコンテナ名を設定
        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

        # BlobServiceClientを作成
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_client = blob_service_client.get_container_client(container_name)

        # コンテナが存在しない場合は作成
        if not container_client.exists():
            container_client.create_container()
        # 重複を避けるためにファイル名を生成する必要があるかも？
        filename = file.filename
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
        blob_client.upload_blob(file, overwrite=True)
        return file.filename, 200
    return "Invalid file type.", 400

@app.route('/', methods=['POST'])
def main():
    # 画像をBLOBに保存
    result, status_code = upload_file()
    if status_code == 200:
        evaluation = analyze_image(result)
        return evaluation
        # return result, status_code
    else:
        return result, status_code

@app.route('/', methods=['GET'])
def not_found():
    text = "oomaeai ver 0.01"
    return text

if __name__ == '__main__':
    app.run(debug=True)