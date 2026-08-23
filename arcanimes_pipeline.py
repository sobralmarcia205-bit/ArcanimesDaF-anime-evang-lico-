"""
arcanimes_pipeline.py
Pipeline autocontido do canal ArcanimesDaFé — roda via GitHub Actions.

Faz tudo em um único arquivo (sem depender de módulos que só existiam
no Colab): escolhe tema -> gera roteiro via Claude API -> gera áudio
(edge-tts) -> gera legenda .srt -> salva prompt Creaty -> salva pacote
de publicação pronto.

Requer no requirements.txt: anthropic, edge-tts, python-dotenv
Requer no repo (Settings > Secrets > Actions): ANTHROPIC_API_KEY
"""

import asyncio
import json
import os
from datetime import datetime, timezone

import anthropic
import edge_tts

CATEGORIAS = {
    "oracao": {
        "titulo_base": "Antes do Dia Começar",
        "gancho": "Ore antes que o mundo fale com você",
        "prompt_creaty_en": (
            "Dark gospel anime style, cinematic 2D anime, divine golden light, "
            "dramatic shadows, celestial glowing particles, figure kneeling in prayer "
            "at dawn, golden light breaking through window, quiet dark room, "
            "vertical 9:16, intimate low angle, highly detailed, smooth animation, "
            "4K, no text"
        ),
        "hashtags": ["#oracao", "#gospel", "#fe", "#evangelico", "#animegospel"],
        "voz": "pt-BR-FranciscaNeural",
    },
    "consagracao": {
        "titulo_base": "Selado Pelo Sangue",
        "gancho": "Você já foi selado. O inimigo só finge que não sabe",
        "prompt_creaty_en": (
            "Dark gospel anime style, cinematic 2D anime, divine golden light, "
            "dramatic shadows, celestial glowing particles, figure with raised hands, "
            "glowing cross symbol emerging from chest, dark sacred temple, "
            "vertical 9:16, dramatic close-up, highly detailed, smooth animation, "
            "4K, no text"
        ),
        "hashtags": ["#consagracao", "#gospel", "#fe", "#jesus", "#animegospel"],
        "voz": "pt-BR-AntonioNeural",
    },
    "motivacao": {
        "titulo_base": "Levanta e Anda",
        "gancho": "38 anos esperando... e ninguém vem",
        "prompt_creaty_en": (
            "Dark gospel anime style, cinematic 2D anime, divine golden light, "
            "dramatic shadows, celestial glowing particles, figure lying weak by "
            "ancient pool, golden light touching them as they rise, dark stone "
            "architecture, vertical 9:16, rising low angle shot, highly detailed, "
            "smooth animation, 4K, no text"
        ),
        "hashtags": ["#motivacaocrista", "#fe", "#gospel", "#forca", "#animegospel"],
        "voz": "pt-BR-AntonioNeural",
    },
    "louvor": {
        "titulo_base": "Grande é o Senhor",
        "gancho": None,
        "prompt_creaty_en": (
            "Dark gospel anime style, cinematic 2D anime, divine golden light, "
            "dramatic shadows, celestial glowing particles, crowd silhouettes "
            "raising hands, radiant light breaking through parted sky, vast dark "
            "landscape, vertical 9:16, dramatic wide low angle, highly detailed, "
            "smooth animation, 4K, no text"
        ),
        "hashtags": ["#louvor", "#gospel", "#adoracao", "#deus", "#animegospel"],
        "voz": None,
    },
    "guerra_espiritual": {
        "titulo_base": "Vestido de Armadura",
        "gancho": "Você não está lutando sozinho",
        "prompt_creaty_en": (
            "Dark gospel anime style, cinematic 2D anime, divine golden light, "
            "dramatic shadows, celestial glowing particles, warrior putting on "
            "glowing armor piece by piece, dark spiritual battlefield behind, "
            "vertical 9:16, dynamic mid shot, highly detailed, smooth animation, "
            "4K, no text"
        ),
        "hashtags": ["#guerraespiritual", "#armaduradedeus", "#fe", "#animegospel"],
        "voz": "pt-BR-AntonioNeural",
    },
    "restauracao": {
        "titulo_base": "Deus Devolve em Dobro",
        "gancho": "Ele viu tudo o que você perdeu",
        "prompt_creaty_en": (
            "Dark gospel anime style, cinematic 2D anime, divine golden light, "
            "dramatic shadows, celestial glowing particles, figure standing in ruins "
            "transforming into golden abundant light, before and after contrast, "
            "vertical 9:16, epic wide transition shot, highly detailed, smooth "
            "animation, 4K, no text"
        ),
        "hashtags": ["#restauracao", "#fe", "#gospel", "#prosperidade", "#animegospel"],
        "voz": "pt-BR-FranciscaNeural",
    },
}

ORDEM_ROTACAO = [
    "motivacao", "oracao", "guerra_espiritual",
    "louvor", "consagracao", "restauracao",
]

HISTORICO_PATH = "historico_temas.json"
ROTEIROS_DIR = "ROTEIROS_PRONTOS"
AUDIOS_DIR = "AUDIOS_PRONTOS"
PROMPTS_DIR = "PROMPTS_CREATY"
LEGENDAS_DIR = "LEGENDAS_PRONTAS"
DADOS_PUBLICACAO_DIR = "DADOS_PUBLICACAO"


def _garantir_pastas():
    for pasta in [ROTEIROS_DIR, AUDIOS_DIR, PROMPTS_DIR, LEGENDAS_DIR, DADOS_PUBLICACAO_DIR]:
        os.makedirs(pasta, exist_ok=True)


def _carregar_historico() -> dict:
    if os.path.exists(HISTORICO_PATH):
        with open(HISTORICO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _salvar_historico(historico: dict) -> None:
    with open(HISTORICO_PATH, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)


def _slugify(titulo: str) -> str:
    slug = titulo.lower()
    trocas = [("á", "a"), ("ã", "a"), ("â", "a"), ("é", "e"), ("ê", "e"),
              ("í", "i"), ("ó", "o"), ("õ", "o"), ("ô", "o"), ("ú", "u"), ("ç", "c")]
    for de, para in trocas:
        slug = slug.replace(de, para)
    slug = "".join(c if c.isalnum() else "-" for c in slug)
    while "--" in slug:
        slug = slug.replace("--", "-")
    data = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"{data}-{slug.strip('-')}"


def _formatar_tempo_srt(segundos: float) -> str:
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    ms = int((segundos - int(segundos)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def escolher_categoria(historico: dict) -> str:
    usados_recentes = set(historico.get("ultimas_categorias", [])[-2:])
    desempenho = historico.get("desempenho_por_categoria", {})

    def score(cat):
        dados = desempenho.get(cat)
        if not dados:
            return 0.7
        return (dados.get("views_medio", 0) / 10000) * 0.5 + dados.get("retencao_media", 0) * 0.5

    candidatos = [c for c in ORDEM_ROTACAO if c not in usados_recentes]
    if not candidatos:
        candidatos = ORDEM_ROTACAO
    return max(candidatos, key=score)


def gerar_roteiro(categoria: str, pacote: dict) -> dict:
    client = anthropic.Anthropic()

    gancho = pacote.get("gancho") or "Louvor instrumental — sem narração"
    system_prompt = (
        "Você escreve roteiros curtos (15-30s) para Shorts evangélicos em "
        "estilo dark gospel anime, em português do Brasil. Estrutura: gancho "
        "nos 3 primeiros segundos, tensão, virada com luz/esperança, e CTA "
        "final. Responda SOMENTE em JSON, sem markdown, com os campos: "
        "titulo (string), texto_narracao (string, o texto que será narrado, "
        "sem marcações de tempo), descricao (string curta para o YouTube)."
    )
    user_prompt = (
        f"Categoria: {categoria}\n"
        f"Tema base: {pacote['titulo_base']}\n"
        f"Gancho: {gancho}\n"
        "Gere o roteiro completo seguindo a estrutura."
    )

    resposta = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    texto = resposta.content[0].text.strip()
    texto = texto.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return {
            "titulo": pacote["titulo_base"],
            "texto_narracao": texto,
            "descricao": f"{pacote['titulo_base']} — ArcanimesDaFé",
        }


async def gerar_audio(texto: str, voz: str, slug: str) -> str:
    caminho = os.path.join(AUDIOS_DIR, f"{slug}.mp3")
    comunicador = edge_tts.Communicate(texto, voz)
    await comunicador.save(caminho)
    return caminho


def gerar_srt(texto: str, slug: str) -> str:
    caminho = os.path.join(LEGENDAS_DIR, f"{slug}.srt")
    frases = [f.strip() for f in texto.split(".") if f.strip()]
    linhas = []
    t = 0.0
    duracao = 3.0
    for i, frase in enumerate(frases, start=1):
        linhas += [str(i), f"{_formatar_tempo_srt(t)} --> {_formatar_tempo_srt(t + duracao)}", frase + ".", ""]
        t += duracao
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    return caminho


def salvar_prompt_creaty(prompt: str, slug: str) -> str:
    caminho = os.path.join(PROMPTS_DIR, f"{slug}.txt")
    prompt_final = prompt[:800]
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(prompt_final)
    return caminho


async def executar() -> dict:
    _garantir_pastas()
    historico = _carregar_historico()

    categoria = escolher_categoria(historico)
    pacote = CATEGORIAS[categoria]

    roteiro = gerar_roteiro(categoria, pacote)
    slug = _slugify(roteiro.get("titulo", pacote["titulo_base"]))

    caminho_roteiro = os.path.join(ROTEIROS_DIR, f"{slug}.json")
    with open(caminho_roteiro, "w", encoding="utf-8") as f:
        json.dump(roteiro, f, ensure_ascii=False, indent=2)

    caminho_audio = None
    caminho_srt = None
    if pacote["voz"]:
        caminho_audio = await gerar_audio(roteiro["texto_narracao"], pacote["voz"], slug)
        caminho_srt = gerar_srt(roteiro["texto_narracao"], slug)

    caminho_prompt = salvar_prompt_creaty(pacote["prompt_creaty_en"], slug)

    dados_publicacao = {
        "categoria": categoria,
        "titulo": roteiro.get("titulo", pacote["titulo_base"]),
        "descricao": roteiro.get("descricao", ""),
        "hashtags": pacote["hashtags"],
        "roteiro_path": caminho_roteiro,
        "audio_path": caminho_audio,
        "srt_path": caminho_srt,
        "prompt_creaty_path": caminho_prompt,
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "status": "pronto_para_publicacao",
    }
    caminho_dados = os.path.join(DADOS_PUBLICACAO_DIR, f"{slug}.json")
    with open(caminho_dados, "w", encoding="utf-8") as f:
        json.dump(dados_publicacao, f, ensure_ascii=False, indent=2)

    historico.setdefault("ultimas_categorias", []).append(categoria)
    historico["ultimas_categorias"] = historico["ultimas_categorias"][-30:]
    historico.setdefault("log_execucoes", []).append({
        "categoria": categoria, "titulo": dados_publicacao["titulo"],
        "data": dados_publicacao["gerado_em"],
    })
    historico["log_execucoes"] = historico["log_execucoes"][-30:]
    _salvar_historico(historico)

    print(f"[OK] Conteúdo pronto: {slug}")
    print(json.dumps(dados_publicacao, ensure_ascii=False, indent=2))
    return dados_publicacao


if __name__ == "__main__":
  
    asyncio.run(executar())
