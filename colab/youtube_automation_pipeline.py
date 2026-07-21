#!/usr/bin/env python3
"""
Integração Colab + YouTube Automático
Pipeline completo de processamento e publicação de vídeos
Canal: Arcanos da Fé - Evangélico Anime Dark
"""

import os
import json
import subprocess
from pathlib import Path
from google.colab import files
from google.colab import drive
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Montar Google Drive
drive.mount('/content/drive')

class ColabYouTubeAutomation:
    """Classe para automação completa Colab + YouTube"""
    
    def __init__(self):
        self.drive_path = '/content/drive/MyDrive/ArcanosDAFe'
        self.videos_path = f'{self.drive_path}/videos'
        self.processed_path = f'{self.drive_path}/processed'
        self.youtube = None
        
    def setup_directories(self):
        """Cria estrutura de diretórios"""
        print("📁 Criando estrutura de diretórios...")
        Path(self.videos_path).mkdir(parents=True, exist_ok=True)
        Path(self.processed_path).mkdir(parents=True, exist_ok=True)
        print("✅ Diretórios prontos!")
    
    def authenticate_youtube(self):
        """Autentica com YouTube API"""
        print("🔐 Autenticando com YouTube...")
        SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
        
        try:
            # Obter credenciais do Drive
            creds_path = f'{self.drive_path}/credentials.json'
            credentials = Credentials.from_service_account_file(
                creds_path, scopes=SCOPES)
            self.youtube = build('youtube', 'v3', credentials=credentials)
            print("✅ Autenticado com YouTube!")
            return True
        except Exception as e:
            print(f"❌ Erro na autenticação: {e}")
            return False
    
    def process_video(self, video_path):
        """Processa vídeo com FFmpeg"""
        print(f"⚙️ Processando vídeo: {video_path}")
        
        try:
            # Instalar FFmpeg
            subprocess.run(['apt-get', 'update', '-qq'], check=True)
            subprocess.run(['apt-get', 'install', '-y', 'ffmpeg', '-qq'], check=True)
            
            # Procesar vídeo (redimensionar, codec, qualidade)
            output_path = video_path.replace('.mp4', '_processed.mp4')
            
            cmd = [
                'ffmpeg', '-i', video_path,
                '-c:v', 'libx264',      # Codec de vídeo
                '-crf', '23',            # Qualidade (0-51, menor=melhor)
                '-preset', 'medium',     # Velocidade de encoding
                '-c:a', 'aac',          # Codec de áudio
                '-b:a', '128k',         # Bitrate de áudio
                '-y',                    # Sobrescrever arquivo
                output_path
            ]
            
            subprocess.run(cmd, check=True)
            print(f"✅ Vídeo processado: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Erro ao processar: {e}")
            return None
    
    def generate_thumbnail(self, video_path):
        """Gera thumbnail do vídeo"""
        print(f"🖼️ Gerando thumbnail...")
        
        try:
            output_path = video_path.replace('.mp4', '_thumb.jpg')
            
            # Extrair frame no meio do vídeo
            cmd = [
                'ffmpeg', '-i', video_path,
                '-ss', '00:00:05',      # 5 segundos
                '-vframes', '1',         # 1 frame
                '-vf', 'scale=1280:720', # Resolução
                '-y',
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Thumbnail gerada: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Erro ao gerar thumbnail: {e}")
            return None
    
    def add_subtitles(self, video_path):
        """Adiciona legendas automáticas (com Speech-to-Text)"""
        print("🎤 Processando áudio para legendas...")
        
        try:
            # Instalar dependências
            subprocess.run(['pip', 'install', 'openai-whisper', '-q'], check=True)
            
            import whisper
            
            # Carregar modelo Whisper
            model = whisper.load_model("base")
            
            # Transcrever áudio
            result = model.transcribe(video_path, language="pt")
            
            # Salvar SRT (legenda)
            srt_path = video_path.replace('.mp4', '.srt')
            
            with open(srt_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(result['segments'], 1):
                    start = self._format_timestamp(segment['start'])
                    end = self._format_timestamp(segment['end'])
                    text = segment['text']
                    f.write(f"{i}\n{start} --> {end}\n{text}\n\n")
            
            print(f"✅ Legendas geradas: {srt_path}")
            return srt_path
            
        except Exception as e:
            print(f"⚠️ Legendas não geradas: {e}")
            return None
    
    def _format_timestamp(self, seconds):
        """Formata timestamp para SRT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def publish_to_youtube(self, video_path, metadata):
        """Publica vídeo no YouTube"""
        print(f"📤 Publicando no YouTube...")
        
        try:
            request = self.youtube.videos().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "categoryId": "24",
                        "description": metadata.get('description', ''),
                        "tags": metadata.get('tags', []),
                        "title": metadata.get('title', ''),
                        "defaultLanguage": "pt",
                        "defaultAudioLanguage": "pt"
                    },
                    "status": {
                        "privacyStatus": metadata.get('privacy', 'public'),
                        "madeForKids": False
                    }
                },
                media_body=open(video_path, 'rb')
            )
            
            response = request.execute()
            video_id = response['id']
            print(f"✅ Vídeo publicado! ID: {video_id}")
            print(f"📺 Link: https://youtube.com/watch?v={video_id}")
            
            return video_id
            
        except HttpError as e:
            print(f"❌ Erro ao publicar: {e}")
            return None
    
    def run_pipeline(self, video_file, metadata_file):
        """Executa pipeline completo"""
        print("\n" + "="*60)
        print("🚀 INICIANDO PIPELINE ARCANOS DA FÉ")
        print("="*60 + "\n")
        
        # 1. Setup
        self.setup_directories()
        
        # 2. Autenticar
        if not self.authenticate_youtube():
            return False
        
        # 3. Carregar metadata
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # 4. Processar vídeo
        processed_video = self.process_video(video_file)
        if not processed_video:
            return False
        
        # 5. Gerar thumbnail
        self.generate_thumbnail(processed_video)
        
        # 6. Adicionar legendas
        self.add_subtitles(processed_video)
        
        # 7. Publicar
        video_id = self.publish_to_youtube(processed_video, metadata)
        
        print("\n" + "="*60)
        print("✅ PIPELINE CONCLUÍDO COM SUCESSO!")
        print("="*60 + "\n")
        
        return video_id is not None

# Executar automação
if __name__ == "__main__":
    # Inicializar
    automation = ColabYouTubeAutomation()
    
    # Exemplo de uso
    print("📺 Automação Colab + YouTube - Arcanos da Fé\n")
    
    # Fazer upload de vídeo
    print("Faça upload do seu vídeo:")
    uploaded_files = files.upload()
    
    video_file = list(uploaded_files.keys())[0]
    
    # Criar metadata
    metadata = {
        "title": "Episódio Arcanos da Fé",
        "description": "Bem-vindo ao canal evangélico anime Dark - Arcanos da Fé",
        "tags": ["anime", "evangélico", "fé", "arcanosodafe"],
        "privacy": "public"
    }
    
    metadata_file = "/tmp/metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # Executar pipeline
    automation.run_pipeline(video_file, metadata_file)
