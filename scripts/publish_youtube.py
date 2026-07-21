#!/usr/bin/env python3
"""
YouTube Video Publishing Script
Automatiza o processo de publicação de vídeos no canal Arcanos da Fé
"""

import os
import json
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def authenticate_youtube():
    """Autentica com a API do YouTube usando credenciais de serviço"""
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    
    try:
        credentials = Credentials.from_service_account_file(
            'credentials.json', scopes=SCOPES)
        return build('youtube', 'v3', credentials=credentials)
    except Exception as e:
        print(f"Erro ao autenticar: {e}")
        return None

def publish_video(youtube, video_file, title, description, tags):
    """
    Publica um vídeo no YouTube
    
    Args:
        youtube: Cliente autenticado da API YouTube
        video_file: Caminho do arquivo de vídeo
        title: Título do vídeo
        description: Descrição do vídeo
        tags: Lista de tags
    """
    try:
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "categoryId": "24",  # Categoria: Entertainment
                    "description": description,
                    "tags": tags,
                    "title": title,
                    "defaultLanguage": "pt",
                    "defaultAudioLanguage": "pt"
                },
                "status": {
                    "privacyStatus": "public",  # public, private, unlisted
                    "madeForKids": False
                }
            },
            media_body=open(video_file, 'rb')
        )
        
        response = request.execute()
        print(f"✅ Vídeo publicado com sucesso! ID: {response['id']}")
        return response
    except HttpError as e:
        print(f"❌ Erro ao publicar vídeo: {e}")
        return None

def main():
    """Fun��ão principal"""
    youtube = authenticate_youtube()
    if not youtube:
        return
    
    # Exemplo de uso
    video_metadata = {
        "title": "Episódio Arcanos da Fé",
        "description": "Bem-vindo ao canal evangélico anime Dark - Arcanos da Fé",
        "tags": ["anime", "evangélico", "fé", "arcanosodafe"]
    }
    
    print("🚀 Iniciando automação do YouTube...")
    print(f"Canal: Arcanos da Fé")
    print(f"Título: {video_metadata['title']}")

if __name__ == "__main__":
    main()
