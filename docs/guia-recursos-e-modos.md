# Guia de Recursos e Modos de Execução do Llamafile

Este guia descreve os modos de operação, opções de aceleração e melhores práticas para tirar o máximo proveito dos modelos executados via Llamafile.

---

## 1. Modos de Operação

O Llamafile (em especial a versão 0.10+) suporta diferentes formas de interação com o modelo:

### A. Modo Chat no Terminal (TUI — Terminal User Interface)
Permite conversar com o modelo diretamente no terminal, sem abrir o navegador e sem iniciar serviços de rede adicionais.

* **Como ativar:** `--chat`
* **Customização de Persona:** `-p "Seu system prompt aqui"`
* **Recursos internos durante a conversa:**
  - `/clear`: Reinicia a conversa limpando o contexto da sessão;
  - `/context`: Exibe o consumo atual de tokens da janela de contexto;
  - `/stats`: Apresenta métricas de desempenho (tokens gerados por segundo, latência de preenchimento de prompt);
  - `/dump [arquivo]`: Salva todo o histórico da conversa em um arquivo de texto;
  - `/upload [arquivo]`: Envia o conteúdo de um arquivo para análise pelo modelo;
  - `/exit`: Encerra o chat.

---

### B. Modo Servidor e Web UI (Navegador)
Inicia um servidor HTTP local que disponibiliza uma interface gráfica amigável de chat acessível pelo navegador (por padrão em `http://127.0.0.1:8080`) e uma API REST compatível com o padrão OpenAI.

* **Como ativar:** `--server`
* **Configurações adicionais:**
  - `--port 8085`: Altera a porta do servidor web;
  - `--host 0.0.0.0`: Permite acesso de outras máquinas na rede local (padrão é apenas `127.0.0.1`);
  - `--ui-config-file config.json`: Injeta preferências padrão de interface (como o `systemMessage` inicial para novos chats);
  - `--api-key [chave]`: Exige autenticação para acesso via API.

---

### C. Modo CLI (Linha de Comando de Pergunta Única)
Ideal para automações, scripts em lote e pipelines de dados onde você deseja apenas enviar uma pergunta e obter a resposta no stdout.

* **Exemplo:**
  ```bash
  ./seu-modelo.llamafile --gpu disable --cli -p "Explique a diferença entre lematização e stemming."
  ```

---

## 2. Aceleração por Hardware: CPU vs GPU

O Llamafile possui suporte integrado a múltiplos backends gráficos compilados dentro do próprio arquivo.

| Flag | Modo de Aceleração | Quando usar |
| :--- | :--- | :--- |
| `--gpu disable` | **Exclusivo CPU** | Recomendado para máquinas sem placa de vídeo dedicada, servidores genéricos ou para garantir compatibilidade máxima sem consumo de VRAM. |
| `--gpu auto` | **Auto-detecção de GPU** | O Llamafile detecta automaticamente se há drivers NVIDIA (CUDA), AMD (Vulkan/ROCm) ou Apple Silicon (Metal) e acelera as camadas do modelo. |
| `--gpu nvidia` | **Força CUDA** | Força a utilização de aceleração via placas NVIDIA compatíveis. |
| `--gpu amd` | **Força Vulkan / AMD** | Força aceleração via Vulkan para placas de vídeo AMD ou Intel. |

> [!TIP]
> Caso a sua GPU não tenha memória VRAM suficiente para carregar todas as camadas do modelo, o Llamafile realiza o "offload" automático: parte do modelo roda na GPU e o restante continua sendo executado na memória RAM convencional via CPU.

---

## 3. Onde Encontrar e Baixar Mais Modelos Llamafile

Você pode utilizar este projeto com qualquer modelo Llamafile oficial ou da comunidade. Alguns dos principais locais para download são:

1. **Repositório Oficial do Mozilla AI no Hugging Face:**
   - [Hugging Face: Mozilla-Ocho / llamafile-models](https://huggingface.co/models?search=llamafile)
   - Exemplos de modelos populares:
     - `Qwen2.5` e `Qwen3.5` (excelentes em raciocínio, programação e múltiplos idiomas);
     - `Llama-3.1` e `Llama-3.2` (versáteis, rápidos e com grande base de conhecimento);
     - `Mistral-7B` (ótimo desempenho para processamento de texto e sumarização).

2. **Como usar um novo modelo com o nosso projeto:**
   - Basta baixar o novo arquivo `.llamafile` e colocá-lo na mesma pasta do projeto;
   - No Linux/macOS, dê permissão de execução: `chmod +x novo-modelo.llamafile`;
   - No Windows, se o arquivo não terminar em `.exe`, renomeie para `novo-modelo.llamafile.exe` (ou o próprio script `gerallamafile.py` fará isso automaticamente);
   - Execute `python3 gerallamafile.py` (Linux) ou `python gerallamafile.py` (Windows) para gerar os inicializadores.

---

## 4. Execução Nativa no Windows 11 (Sem WSL)

O projeto é 100% compatível com o Windows 11 sem necessidade de WSL, Docker ou máquinas virtuais:

1. **Extensão Executável:** O Windows exige que arquivos executáveis terminem com `.exe`. O `gerallamafile.py` detecta isso e ajusta o nome do arquivo criando um *hard-link* (não consome espaço extra no disco).
2. **Inicializador Batch (`iniciar_modelo.bat`):**
   - Suporta **duplo-clique** direto no Windows Explorer;
   - Suporta argumentos via Prompt de Comando:
     ```cmd
     iniciar_modelo.bat         REM Inicia o chat no terminal
     iniciar_modelo.bat --web   REM Inicia o servidor e abre a Web UI no navegador
     ```
3. **Tratamento de UTF-8 no Windows:** O `iniciar_modelo.bat` utiliza a página de código UTF-8 (`chcp 65001`) e o PowerShell nativo do Windows 11 para garantir que caracteres com acentuação sejam preservados corretamente.

