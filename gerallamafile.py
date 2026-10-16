#!/usr/bin/env python3
"""
gerallamafile.py

Facilita a customização de modelos LLM locais usando o Mozilla AI Llamafile.
Detecta automaticamente o sistema operacional (Linux, macOS ou Windows 11),
lê o arquivo 'descricao.txt' presente no diretório atual e gera os inicializadores
executáveis (.sh para Linux/macOS e .bat para Windows) configurados com o
system prompt e o modo de processamento (CPU ou GPU).

Uso:
    python3 gerallamafile.py [--cpu | --gpu] [--chat | --web] [-o NOME_SCRIPT]
"""

import argparse
import json
import os
import stat
import sys
from pathlib import Path

DEFAULT_DESC_FILE = "descricao.txt"
DEFAULT_OUTPUT_SH = "iniciar_modelo.sh"
DEFAULT_OUTPUT_BAT = "iniciar_modelo.bat"
DEFAULT_UI_CONFIG = "ui_config.json"

EH_WINDOWS = sys.platform == "win32" or os.name == "nt"


def obter_modelos_llamafile(diretorio: Path):
    """Encontra todos os arquivos .llamafile e .llamafile.exe no diretório fornecido."""
    encontrados = list(diretorio.glob("*.llamafile")) + list(diretorio.glob("*.llamafile.exe"))
    # Remove duplicados preservando a ordem
    modelos_unicos = []
    nomes_vistos = set()
    for mod in encontrados:
        if mod.name not in nomes_vistos:
            nomes_vistos.add(mod.name)
            modelos_unicos.append(mod)
    return sorted(modelos_unicos, key=lambda p: p.name)


def configurar_permissoes_execucao(caminho: Path):
    """Garante permissão de execução (chmod +x) em sistemas POSIX (Linux/macOS)."""
    if not EH_WINDOWS:
        try:
            st = caminho.stat()
            caminho.chmod(st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        except OSError:
            pass


def ajustar_extensao_windows(caminho_modelo: Path) -> Path:
    """
    No Windows 11 nativo (sem WSL), executáveis precisam da extensão .exe.
    Se o arquivo terminar em .llamafile sem .exe, cria um hard-link ou renomeia.
    """
    if not caminho_modelo.name.lower().endswith(".exe"):
        nome_exe = f"{caminho_modelo.name}.exe"
        caminho_exe = caminho_modelo.with_name(nome_exe)
        if not caminho_exe.exists():
            print(f"\n[AJUSTE WINDOWS] No Windows 11, executáveis exigem a extensão .exe.")
            print(f"                 Ajustando: {caminho_modelo.name} -> {nome_exe}")
            try:
                # Tenta criar hard-link (0 bytes extras de disco)
                os.link(caminho_modelo, caminho_exe)
                print(f"                 [OK] Hard-link criado com sucesso (sem consumo extra de disco).")
            except (OSError, AttributeError):
                try:
                    caminho_modelo.rename(caminho_exe)
                    print(f"                 [OK] Arquivo renomeado com sucesso.")
                except Exception as e:
                    print(f"                 [AVISO] Não foi possível renomear automaticamente: {e}")
                    print(f"                 Por favor, renomeie '{caminho_modelo.name}' para '{nome_exe}'.")
            caminho_modelo = caminho_exe
        else:
            caminho_modelo = caminho_exe
    return caminho_modelo


def main():
    parser = argparse.ArgumentParser(
        description="Gera um inicializador customizado para modelos Llamafile com base em descricao.txt.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Exemplos de uso:
  python3 gerallamafile.py                # CPU por padrão, modo Chat no terminal
  python3 gerallamafile.py --cpu          # CPU explicitamente
  python3 gerallamafile.py --gpu          # Habilita aceleração por GPU
  python3 gerallamafile.py --web          # Define a Web UI (navegador) como modo padrão
  python3 gerallamafile.py --gpu --web    # GPU + Web UI como padrão
""",
    )

    grupo_proc = parser.add_mutually_exclusive_group()
    grupo_proc.add_argument(
        "--cpu",
        action="store_true",
        help="Executa o modelo utilizando apenas CPU (padrão).",
    )
    grupo_proc.add_argument(
        "--gpu",
        action="store_true",
        help="Habilita aceleração por GPU (auto-detecção CUDA/Vulkan/Metal).",
    )

    grupo_modo = parser.add_mutually_exclusive_group()
    grupo_modo.add_argument(
        "--chat",
        action="store_true",
        help="Define o modo Chat no Terminal (TUI) como inicialização padrão.",
    )
    grupo_modo.add_argument(
        "--web",
        action="store_true",
        help="Define o modo Web UI / Servidor (navegador em http://127.0.0.1:8080) como inicialização padrão.",
    )

    parser.add_argument(
        "--modelo",
        type=str,
        default=None,
        help="Nome específico do arquivo .llamafile (caso haja mais de um na pasta).",
    )

    parser.add_argument(
        "--descricao",
        type=str,
        default=DEFAULT_DESC_FILE,
        help=f"Arquivo contendo a descrição/personalidade do modelo (padrão: {DEFAULT_DESC_FILE}).",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Nome customizado do script inicializador a ser gerado.",
    )

    args = parser.parse_args()

    diretorio_atual = Path.cwd()
    arquivo_descricao = diretorio_atual / args.descricao
    arquivo_ui_config = diretorio_atual / DEFAULT_UI_CONFIG

    sistema_operacional = "Windows 11 / Windows" if EH_WINDOWS else ("macOS" if sys.platform == "darwin" else "Linux")

    print("=" * 65)
    print("  Customizador de Modelo Llamafile (Mozilla AI)")
    print(f"  Sistema Operacional detectado: {sistema_operacional}")
    print("=" * 65)

    # 1. Validação do arquivo de descrição
    if not arquivo_descricao.is_file():
        print(f"\n[ERRO] O arquivo '{args.descricao}' não foi encontrado neste diretório.")
        print(f"       Crie o arquivo '{args.descricao}' contendo o comportamento esperado do modelo.")
        print("       Exemplo de conteúdo:")
        print("       'Você é um especialista em Processamento de Linguagem Natural...'")
        sys.exit(1)

    conteudo_descricao = arquivo_descricao.read_text(encoding="utf-8").strip()
    if not conteudo_descricao:
        print(f"\n[ERRO] O arquivo '{args.descricao}' está vazio.")
        print("       Escreva o comportamento esperado do modelo no arquivo antes de continuar.")
        sys.exit(1)

    # 2. Localização do arquivo .llamafile
    if args.modelo:
        caminho_modelo = diretorio_atual / args.modelo
        if not caminho_modelo.is_file():
            print(f"\n[ERRO] O modelo especificado '{args.modelo}' não foi encontrado.")
            sys.exit(1)
    else:
        modelos_encontrados = obter_modelos_llamafile(diretorio_atual)
        if not modelos_encontrados:
            print(f"\n[ERRO] Nenhum arquivo '.llamafile' ou '.llamafile.exe' foi encontrado em: {diretorio_atual}")
            print("       Certifique-se de que o modelo baixado está nesta pasta.")
            sys.exit(1)
        elif len(modelos_encontrados) == 1:
            caminho_modelo = modelos_encontrados[0]
        else:
            print("\nForam encontrados múltiplos arquivos de modelo no diretório:")
            for idx, mod in enumerate(modelos_encontrados, start=1):
                print(f"  [{idx}] {mod.name}")
            try:
                escolha = input(f"\nSelecione o modelo desejado (1-{len(modelos_encontrados)}) [1]: ").strip()
                idx_escolhido = int(escolha) - 1 if escolha else 0
                caminho_modelo = modelos_encontrados[idx_escolhido]
            except (ValueError, IndexError):
                print("[ERRO] Opção inválida.")
                sys.exit(1)

    # Se estiver rodando no Windows, ajusta a extensão se necessário
    if EH_WINDOWS:
        caminho_modelo = ajustar_extensao_windows(caminho_modelo)
    else:
        configurar_permissoes_execucao(caminho_modelo)

    # 3. Definição do modo de aceleração (CPU vs GPU)
    if args.gpu:
        modo_gpu_flag = "--gpu auto"
        descricao_aceleracao = "GPU (Aceleração ativada - auto detecção)"
    else:
        modo_gpu_flag = "--gpu disable"
        descricao_aceleracao = "CPU (Processamento exclusivo por CPU)"

    # Modo padrão do script gerado: 'web' se --web foi passado, caso contrário 'chat'
    modo_padrao_script = "web" if args.web else "chat"

    # 4. Geração do arquivo de configuração para a Web UI (UTF-8)
    dados_ui = {
        "systemMessage": conteudo_descricao,
        "showSystemMessage": True,
    }
    arquivo_ui_config.write_text(json.dumps(dados_ui, ensure_ascii=False, indent=2), encoding="utf-8")

    # Nome do binário no script para Windows (assegura .exe para Windows)
    nome_binario_windows = caminho_modelo.name if caminho_modelo.name.lower().endswith(".exe") else f"{caminho_modelo.name}.exe"
    nome_binario_posix = caminho_modelo.name

    # 5. Geração do script Shell (Linux / macOS)
    conteudo_sh = f"""#!/usr/bin/env bash
# ==============================================================================
# Script inicializador gerado por gerallamafile.py (Linux / macOS)
# Modelo Base: {nome_binario_posix}
# Aceleração:  {descricao_aceleracao}
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
MODELO="$SCRIPT_DIR/{nome_binario_posix}"
ARQ_DESC="$SCRIPT_DIR/{args.descricao}"
ARQ_UI_CONFIG="$SCRIPT_DIR/{DEFAULT_UI_CONFIG}"

if [ ! -f "$MODELO" ]; then
    echo "[ERRO] Arquivo do modelo não encontrado: $MODELO"
    exit 1
fi

if [ ! -f "$ARQ_DESC" ]; then
    echo "[ERRO] Arquivo de descrição não encontrado: $ARQ_DESC"
    exit 1
fi

PROMPT_SISTEMA="$(cat "$ARQ_DESC")"
MODO_EXECUCAO="{modo_padrao_script}"

if [ "$1" = "--web" ] || [ "$1" = "--server" ]; then
    MODO_EXECUCAO="web"
    shift
elif [ "$1" = "--chat" ]; then
    MODO_EXECUCAO="chat"
    shift
fi

if [ "$MODO_EXECUCAO" = "web" ]; then
    echo "--------------------------------------------------------------"
    echo "  Iniciando Modelo no Modo Web UI"
    echo "  Modelo:     {nome_binario_posix}"
    echo "  Aceleração: {descricao_aceleracao}"
    echo "  Acesse:     http://127.0.0.1:8080"
    echo "  (Para abrir no Terminal, execute: $0 --chat)"
    echo "--------------------------------------------------------------"
    exec "$MODELO" {modo_gpu_flag} --server --ui-config-file "$ARQ_UI_CONFIG" "$@"
else
    echo "--------------------------------------------------------------"
    echo "  Iniciando Modelo no Modo Chat (Terminal)"
    echo "  Modelo:     {nome_binario_posix}"
    echo "  Aceleração: {descricao_aceleracao}"
    echo "  (Para abrir na Web UI, execute: $0 --web)"
    echo "--------------------------------------------------------------"
    exec "$MODELO" {modo_gpu_flag} --chat -p "$PROMPT_SISTEMA" "$@"
fi
"""

    # 6. Geração do script Batch nativo para Windows 11 (CMD / Dois cliques)
    conteudo_bat = f"""@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM ==============================================================================
REM Script inicializador nativo para Windows 11 (CMD / PowerShell / Dois Cliques)
REM Gerado por gerallamafile.py
REM Modelo Base: {nome_binario_windows}
REM Aceleração:  {descricao_aceleracao}
REM ==============================================================================

set "SCRIPT_DIR=%~dp0"
set "MODELO=%SCRIPT_DIR%{nome_binario_windows}"
set "ARQ_DESC=%SCRIPT_DIR%{args.descricao}"
set "ARQ_UI_CONFIG=%SCRIPT_DIR%{DEFAULT_UI_CONFIG}"

if not exist "%MODELO%" (
    echo [ERRO] Arquivo do modelo nao encontrado: %MODELO%
    echo No Windows, verifique se o modelo termina com .exe (ex: {nome_binario_windows})
    pause
    exit /b 1
)

if not exist "%ARQ_DESC%" (
    echo [ERRO] Arquivo de descricao nao encontrado: %ARQ_DESC%
    pause
    exit /b 1
)

set "MODO_EXECUCAO={modo_padrao_script}"

if "%~1"=="--web" (
    set "MODO_EXECUCAO=web"
    shift
) else if "%~1"=="--server" (
    set "MODO_EXECUCAO=web"
    shift
) else if "%~1"=="--chat" (
    set "MODO_EXECUCAO=chat"
    shift
)

if "%MODO_EXECUCAO%"=="web" (
    echo --------------------------------------------------------------
    echo   Iniciando Modelo no Modo Web UI (Windows)
    echo   Modelo:     {nome_binario_windows}
    echo   Aceleracao: {descricao_aceleracao}
    echo   Acesse:     http://127.0.0.1:8080
    echo   (Para abrir no Terminal, execute: %~nx0 --chat)
    echo --------------------------------------------------------------
    start "" http://127.0.0.1:8080
    "%MODELO%" {modo_gpu_flag} --server --ui-config-file "%ARQ_UI_CONFIG%" %*
) else (
    echo --------------------------------------------------------------
    echo   Iniciando Modelo no Modo Chat - Terminal (Windows)
    echo   Modelo:     {nome_binario_windows}
    echo   Aceleracao: {descricao_aceleracao}
    echo   (Para abrir na Web UI, execute: %~nx0 --web)
    echo --------------------------------------------------------------
    powershell -NoProfile -ExecutionPolicy Bypass -Command "& {{ [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; $desc = Get-Content -Raw -Encoding UTF8 '%ARQ_DESC%'; & '%MODELO%' {modo_gpu_flag} --chat -p $desc $args }}" %*
)
"""

    # Determinação dos caminhos de saída
    if args.output:
        caminho_saida_principal = diretorio_atual / args.output
        caminho_saida_principal.write_text(conteudo_bat if args.output.lower().endswith(".bat") else conteudo_sh, encoding="utf-8")
        configurar_permissoes_execucao(caminho_saida_principal)
        arquivos_gerados = [caminho_saida_principal.name]
    else:
        # Gera ambos os inicializadores para que a pasta funcione em qualquer sistema
        arq_sh = diretorio_atual / DEFAULT_OUTPUT_SH
        arq_bat = diretorio_atual / DEFAULT_OUTPUT_BAT
        arq_sh.write_text(conteudo_sh, encoding="utf-8")
        configurar_permissoes_execucao(arq_sh)
        arq_bat.write_text(conteudo_bat, encoding="utf-8")
        arquivos_gerados = [arq_sh.name, arq_bat.name]

    # 7. Feedback final personalizado por sistema operacional
    linhas_prompt = conteudo_descricao.splitlines()
    resumo_prompt = linhas_prompt[0] if linhas_prompt else ""
    if len(linhas_prompt) > 1 or len(resumo_prompt) > 80:
        resumo_prompt = resumo_prompt[:77] + "..."

    print(f"\n[OK] Modelo configurado com sucesso!")
    print(f"  • Modelo base:     {caminho_modelo.name}")
    print(f"  • Aceleração:      {descricao_aceleracao}")
    print(f"  • Modo padrão:     {'Web UI (http://127.0.0.1:8080)' if modo_padrao_script == 'web' else 'Terminal Chat (TUI)'}")
    print(f"  • Descrição ativa: \"{resumo_prompt}\"")
    print(f"  • Scripts gerados: {', '.join(arquivos_gerados)}")

    print(f"\nComo rodar no seu sistema ({sistema_operacional}):")
    if EH_WINDOWS:
        print(f"  Prompt / PowerShell:  .\\{DEFAULT_OUTPUT_BAT}")
        print(f"  Ou dê dois cliques no arquivo '{DEFAULT_OUTPUT_BAT}' no Windows Explorer.")
        print(f"  Para Web UI:          .\\{DEFAULT_OUTPUT_BAT} --web")
        print(f"  Para Chat Terminal:   .\\{DEFAULT_OUTPUT_BAT} --chat")
    else:
        print(f"  ./{DEFAULT_OUTPUT_SH}         # Inicia no modo padrão")
        print(f"  ./{DEFAULT_OUTPUT_SH} --chat  # Força modo Chat no Terminal")
        print(f"  ./{DEFAULT_OUTPUT_SH} --web   # Força modo Web UI no navegador")
        print(f"  (Dica: '{DEFAULT_OUTPUT_BAT}' também foi gerado caso queira rodar no Windows 11)")
    print("=" * 65)


if __name__ == "__main__":
    main()
