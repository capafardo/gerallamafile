#!/usr/bin/env python3
"""
gerallamafile.py

Facilita a customização de modelos LLM locais usando o Mozilla AI Llamafile.
Lê o arquivo 'descricao.txt' presente no diretório atual e gera um inicializador
executável configurado com o system prompt e o modo de processamento (CPU ou GPU).

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
DEFAULT_OUTPUT_SCRIPT = "iniciar_modelo.sh"
DEFAULT_UI_CONFIG = "ui_config.json"


def obter_modelos_llamafile(diretorio: Path):
    """Encontra todos os arquivos .llamafile no diretório fornecido."""
    return sorted(list(diretorio.glob("*.llamafile")))


def configurar_permissoes_execucao(caminho: Path):
    """Garante permissão de execução (chmod +x) para o arquivo."""
    st = caminho.stat()
    caminho.chmod(st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


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
        default=DEFAULT_OUTPUT_SCRIPT,
        help=f"Nome do script inicializador a ser gerado (padrão: {DEFAULT_OUTPUT_SCRIPT}).",
    )

    args = parser.parse_args()

    diretorio_atual = Path.cwd()
    arquivo_descricao = diretorio_atual / args.descricao
    arquivo_saida = diretorio_atual / args.output
    arquivo_ui_config = diretorio_atual / DEFAULT_UI_CONFIG

    print("=" * 60)
    print("  Customizador de Modelo Llamafile (Mozilla AI)")
    print("=" * 60)

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
            print(f"\n[ERRO] Nenhum arquivo '.llamafile' foi encontrado no diretório: {diretorio_atual}")
            print("       Certifique-se de que o modelo baixado está nesta pasta.")
            sys.exit(1)
        elif len(modelos_encontrados) == 1:
            caminho_modelo = modelos_encontrados[0]
        else:
            print("\nForam encontrados múltiplos arquivos .llamafile no diretório:")
            for idx, mod in enumerate(modelos_encontrados, start=1):
                print(f"  [{idx}] {mod.name}")
            try:
                escolha = input(f"\nSelecione o modelo desejado (1-{len(modelos_encontrados)}) [1]: ").strip()
                idx_escolhido = int(escolha) - 1 if escolha else 0
                caminho_modelo = modelos_encontrados[idx_escolhido]
            except (ValueError, IndexError):
                print("[ERRO] Opção inválida.")
                sys.exit(1)

    # Garante permissão de execução no modelo base
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

    # 4. Geração do arquivo de configuração para a Web UI
    dados_ui = {
        "systemMessage": conteudo_descricao,
        "showSystemMessage": True,
    }
    arquivo_ui_config.write_text(json.dumps(dados_ui, ensure_ascii=False, indent=2), encoding="utf-8")

    # 5. Geração do script inicializador shell
    conteudo_script = f"""#!/usr/bin/env bash
# ==============================================================================
# Script inicializador gerado por gerallamafile.py
# Modelo Base: {caminho_modelo.name}
# Aceleração:  {descricao_aceleracao}
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
MODELO="$SCRIPT_DIR/{caminho_modelo.name}"
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

# Verificação se o usuário passou --web ou --chat na linha de comando
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
    echo "  Modelo:     {caminho_modelo.name}"
    echo "  Aceleração: {descricao_aceleracao}"
    echo "  Acesse:     http://127.0.0.1:8080"
    echo "  (Para abrir no Terminal, execute: $0 --chat)"
    echo "--------------------------------------------------------------"
    exec "$MODELO" {modo_gpu_flag} --server --ui-config-file "$ARQ_UI_CONFIG" "$@"
else
    echo "--------------------------------------------------------------"
    echo "  Iniciando Modelo no Modo Chat (Terminal)"
    echo "  Modelo:     {caminho_modelo.name}"
    echo "  Aceleração: {descricao_aceleracao}"
    echo "  (Para abrir na Web UI, execute: $0 --web)"
    echo "--------------------------------------------------------------"
    exec "$MODELO" {modo_gpu_flag} --chat -p "$PROMPT_SISTEMA" "$@"
fi
"""

    arquivo_saida.write_text(conteudo_script, encoding="utf-8")
    configurar_permissoes_execucao(arquivo_saida)

    # 6. Feedback final
    linhas_prompt = conteudo_descricao.splitlines()
    resumo_prompt = linhas_prompt[0] if linhas_prompt else ""
    if len(linhas_prompt) > 1 or len(resumo_prompt) > 80:
        resumo_prompt = resumo_prompt[:77] + "..."

    print(f"\n[OK] Modelo configurado com sucesso!")
    print(f"  • Modelo base:     {caminho_modelo.name}")
    print(f"  • Aceleração:      {descricao_aceleracao}")
    print(f"  • Modo padrão:     {'Web UI (http://127.0.0.1:8080)' if modo_padrao_script == 'web' else 'Terminal Chat (TUI)'}")
    print(f"  • Descrição ativa: \"{resumo_prompt}\"")
    print(f"  • Inicializador:   ./{arquivo_saida.name}")
    print(f"\nComo rodar:")
    print(f"  ./{arquivo_saida.name}         # Inicia no modo padrão")
    print(f"  ./{arquivo_saida.name} --chat  # Força modo Chat no Terminal")
    print(f"  ./{arquivo_saida.name} --web   # Força modo Web UI no navegador")
    print("=" * 60)


if __name__ == "__main__":
    main()
