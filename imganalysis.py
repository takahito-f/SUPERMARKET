import os
from openai import AzureOpenAI
from azure.storage.blob import BlobServiceClient, generate_container_sas, ContainerSasPermissions
from datetime import datetime, timedelta, timezone
# from dotenv import load_dotenv # (LOCAL)

def analyze_image(img_name):
    # 環境変数読み込み(LOCAL)
    # load_dotenv()

    # AzureOpenAIのインスタンスを生成　
    client = AzureOpenAI(
        api_version=os.getenv("OPENAI_API_VERSION"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    model_name = "oomaeai-gpt-4o"

    # Azure Storageの接続文字列
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
    connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
    container_url = os.getenv("AZURE_STORAGE_CONTAINER_URL")

    # Blobサービスクライアントを作成
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # SASトークンを生成
    sas_token = generate_container_sas(
        account_name = account_name,
        account_key = account_key,
        container_name = container_name,
        permission = ContainerSasPermissions(read=True),
        expiry = datetime.now(timezone.utc) + timedelta(hours=1)  # 有効期限を1時間に設定（必要な時間に短縮するのが望ましい）
    )
    sas_para=f"?{sas_token}"

    # 画像URL
    blob_url = f"{container_url}/" + img_name + sas_para
    img_url = blob_url

    # LLMタスク
    prompt = "URLの画像を見て、簡潔に説明してください。"
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": img_url
                        },
                    },
                ],
            }
        ],
        max_tokens=1200,
    )
    return response.choices[0].message.content 