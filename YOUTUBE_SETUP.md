# 📺 Configuração de Automação YouTube - Arcanos da Fé

Guia completo para automatizar a publicação de vídeos no canal YouTube "Arcanos da Fé".

## 🔧 Requisitos

- Conta Google/YouTube
- Acesso de desenvolvedor (Google Cloud Console)
- Credenciais de serviço (Service Account)

## 📋 Passo a Passo

### 1. Criar Projeto no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto: `ArcanosDA-YouTube`
3. Ative a API YouTube Data API v3

### 2. Criar Service Account

1. No Console, vá para "APIs e Serviços" > "Credenciais"
2. Clique em "Criar Credenciais" > "Conta de Serviço"
3. Nome: `arcanos-youtube-bot`
4. Crie uma chave JSON
5. Baixe o arquivo JSON

### 3. Configurar Secrets no GitHub

1. Vá para seu repositório > Settings > Secrets and variables > Actions
2. Clique em "New repository secret"
3. Adicione os seguintes secrets:

```
YOUTUBE_CREDENTIALS = [conteúdo do arquivo JSON em base64]
YOUTUBE_CHANNEL_ID = [ID do seu canal YouTube]
```

Para converter o JSON em base64:
```bash
cat credentials.json | base64 | tr -d '\n'
```

### 4. Estrutura de Pastas

```
videos/
├── episodio-01/
│   ├── video.mp4
│   └── metadata.json
├── episodio-02/
│   ├── video.mp4
│   └── metadata.json
```

### 5. Formato do metadata.json

```json
{
  "title": "Episódio 01 - Arcanos da Fé",
  "description": "Bem-vindo ao canal evangélico anime Dark. Conheça os mistérios de Arcanos da Fé.",
  "tags": ["anime", "evangélico", "fé", "arcanosodafe"],
  "privacy": "public"
}
```

## 🚀 Como Usar

### Publicar Automaticamente (via Git)

```bash
# Adicione seu vídeo e metadata
git add videos/episodio-01/
git commit -m "feat: add episodio 01"
git push origin feature/youtube-automation

# O workflow será acionado automaticamente!
```

### Publicar Manualmente

1. Vá para Actions
2. Selecione "YouTube Automation - Publish Videos"
3. Clique em "Run workflow"
4. Insira o video_id (opcional)

## 📊 Monitoramento

- Acesse a aba "Actions" do repositório
- Veja logs de cada publicação
- Verifique erros e status

## 🔐 Segurança

- ✅ Credenciais armazenadas como GitHub Secrets
- ✅ Nunca comite credentials.json no repositório
- ✅ Use .gitignore para credenciais

```gitignore
credentials.json
*.key
.env
```

## 📧 Troubleshooting

| Erro | Solução |
|------|---------|
| `Invalid credentials` | Verifique se a chave JSON está correta e em base64 |
| `Channel not found` | Confirme o YOUTUBE_CHANNEL_ID |
| `Video upload failed` | Verifique se o arquivo de vídeo existe e é válido |

## 📚 Recursos Úteis

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [Google Cloud Console](https://console.cloud.google.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Canal:** Arcanos da Fé  
**Tipo:** Evangélico Anime Dark  
**Status:** 🟢 Pronto para automação
