# Customizador de Modelos Llamafile (Mozilla AI)

Este projeto oferece uma ferramenta simples e eficiente em **Python** para customizar e inicializar modelos de linguagem locais baseados no projeto **[Mozilla AI Llamafile](https://github.com/mozilla-ai/llamafile)**.

Com ele, basta escrever em um arquivo de texto simples ([descricao.txt](file:///home/marcelo/projetos/pln/llamafile/descricao.txt)) a persona ou comportamento que você deseja que o modelo assuma (ex: *"Você é um especialista em Processamento de Linguagem Natural..."*). O script gera automaticamente um inicializador executável configurado, **sem duplicar arquivos pesados de gigabytes**.

---

## 🚀 Principais Recursos

- **Zero Duplicação de Disco:** Cria um inicializador leve reutilizando os pesos do modelo original existente no diretório.
- **Configuração Simples de Persona:** Define o *system prompt* do modelo diretamente a partir de um arquivo de texto comum.
- **Escolha de Hardware Flexível:** Suporte a execução em **CPU** (modo padrão, sem exigir GPU) ou **GPU** (detecção automática de CUDA/Vulkan/Metal).
- **Múltiplos Modos de Interação:**
  - **Terminal Chat (TUI):** Conversa interativa com cores e comandos diretamente no terminal.
  - **Web UI:** Interface visual completa no navegador (acessível em `http://127.0.0.1:8080`).
- **Detecção Automática:** Localiza automaticamente qualquer arquivo `.llamafile` presente na pasta de trabalho.

---

## 📋 Pré-requisitos

1. **Linux**, **macOS** ou **Windows 11** (nativamente sem WSL, ou via WSL2);
2. **Python 3.8+**;
3. Um modelo em formato `.llamafile` colocado na pasta do projeto (ex: `Qwen3.5-2B-Q8_0.llamafile`).

---

## 📥 Onde e Como Baixar Modelos Llamafile

Os arquivos `.llamafile` são executáveis completos que contêm tanto os pesos da rede neural quanto o código de inferência. Por pesarem entre **1.5 GB e 8 GB**, **eles são estritamente ignorados pelo Git** (via [`.gitignore`](.gitignore)) e não devem ser enviados ao repositório.

Você pode baixar modelos prontos gratuitamente nas seguintes fontes oficiais:

### 1. Repositórios Oficiais
- **Mozilla Ocho no Hugging Face (Recomendado):**  
  [https://huggingface.co/Mozilla-Ocho](https://huggingface.co/Mozilla-Ocho)  
  Repositório oficial mantido pela Mozilla AI com os modelos mais populares já empacotados.
- **Busca Geral de Llamafiles no Hugging Face:**  
  [https://huggingface.co/models?search=llamafile](https://huggingface.co/models?search=llamafile)
- **Releases Oficiais no GitHub:**  
  [https://github.com/mozilla-ai/llamafile/releases](https://github.com/mozilla-ai/llamafile/releases)

### 2. Modelos Populares Sugeridos

| Modelo | Tamanho | Perfil / Uso Recomendado | Link direto |
| :--- | :--- | :--- | :--- |
| **Qwen 2.5 / 3.5 (2B/3B)** | ~2.2 GB - 2.8 GB | Leve, excelente em português, código e raciocínio. Ideal para CPU. | [Hugging Face Qwen](https://huggingface.co/models?search=qwen+llamafile) |
| **Llama 3.2 (1B / 3B)** | ~1.3 GB - 2.4 GB | Muito rápido, consome pouca memória RAM. | [Hugging Face Llama-3.2](https://huggingface.co/models?search=llama-3.2+llamafile) |
| **Mistral 7B Instruct** | ~4.5 GB | Excelente capacidade de escrita, redação e análise textual. | [Hugging Face Mistral](https://huggingface.co/models?search=mistral+llamafile) |

### 3. Exemplo de Download via Terminal

Você pode baixar um modelo diretamente para a pasta do projeto via linha de comando:

**No Linux ou macOS:**
```bash
wget https://huggingface.co/Mozilla-Ocho/Qwen2.5-3B-Instruct-llamafile/resolve/main/Qwen2.5-3B-Instruct.Q8_0.llamafile
chmod +x Qwen2.5-3B-Instruct.Q8_0.llamafile
```

**No Windows 11 (Prompt de Comando ou PowerShell):**
```cmd
curl.exe -L -o Qwen2.5-3B-Instruct.Q8_0.llamafile.exe https://huggingface.co/Mozilla-Ocho/Qwen2.5-3B-Instruct-llamafile/resolve/main/Qwen2.5-3B-Instruct.Q8_0.llamafile
```

---

## 🛠️ Passo a Passo de Uso

### 1. Defina o Comportamento do Modelo
Edite ou crie o arquivo [descricao.txt](file:///home/marcelo/projetos/pln/llamafile/descricao.txt) na mesma pasta do projeto com a instrução desejada:

```text
Você é um especialista em Processamento de Linguagem Natural (PLN). 
Responda sempre em português do Brasil, de forma clara, didática e com exemplos práticos.
```

### 2. Gere o Inicializador Customizado
Execute o script [gerallamafile.py](file:///home/marcelo/projetos/pln/llamafile/gerallamafile.py) escolhendo o modo de aceleração desejado:

```bash
# Execução padrão utilizando CPU:
python3 gerallamafile.py      # No Linux / macOS
python gerallamafile.py       # No Windows 11

# Ou habilitando aceleração por GPU (se disponível):
python3 gerallamafile.py --gpu
```

> **Nota sobre o Windows 11:** O script detecta o Windows automaticamente e, se o seu modelo ainda não tiver a extensão `.exe`, ele cria um hard-link ou renomeia para `modelo.llamafile.exe` de forma transparente, permitindo execução nativa imediata sem WSL.

### 3. Inicie o Seu Modelo

O comando anterior gera os inicializadores para o seu sistema:

#### No Linux / macOS:
```bash
./iniciar_modelo.sh         # Modo Chat interativo no terminal
./iniciar_modelo.sh --web   # Modo Web UI no navegador (http://127.0.0.1:8080)
```

#### No Windows 11 (Nativo, sem WSL):
- **Opção 1:** Dê **dois cliques** no arquivo `iniciar_modelo.bat` no Windows Explorer.
- **Opção 2:** Pelo Prompt de Comando (CMD) ou PowerShell:
  ```cmd
  iniciar_modelo.bat         REM Modo Chat interativo no terminal
  iniciar_modelo.bat --web   REM Modo Web UI no navegador (abre automaticamente)
  ```

---

## ⚙️ Opções da Linha de Comando de `gerallamafile.py`

| Parâmetro | Tipo | Descrição |
| :--- | :--- | :--- |
| `--cpu` | Flag | Força o modelo a executar exclusivamente na CPU (padrão). |
| `--gpu` | Flag | Habilita a detecção e uso automático de GPU (CUDA/Vulkan/Metal). |
| `--web` | Flag | Define a interface Web como o modo de inicialização padrão do script gerado. |
| `--chat` | Flag | Define o chat no terminal como o modo de inicialização padrão (padrão). |
| `--modelo ARQUIVO` | String | Especifica um arquivo `.llamafile` caso haja múltiplos modelos na pasta. |
| `--descricao ARQUIVO` | String | Caminho alternativo para o arquivo de descrição (padrão: `descricao.txt`). |
| `-o`, `--output NOME` | String | Nome do script inicializador gerado (padrão: `iniciar_modelo.sh`). |

---

## 📁 Estrutura do Repositório

```text
.
├── gerallamafile.py          # Script principal de customização
├── descricao.txt             # Arquivo com a persona/system prompt configurada
├── .gitignore                # Regras de exclusão do git (ignora modelos e logs)
├── README.md                 # Documentação principal do projeto
└── docs/                     # Documentação complementar e didática
    ├── o-que-e-llamafile.md  # Arquitetura do Llamafile, Cosmopolitan e APE
    └── guia-recursos-e-modos.md # Modos de execução, aceleração e download de modelos
```

---

## 📚 Documentação Complementar

- [O que é o Llamafile e como ele funciona internamente](docs/o-que-e-llamafile.md)
- [Guia completo de recursos, atalhos de chat e aceleração de hardware](docs/guia-recursos-e-modos.md)

---

## 📄 Licença e Créditos

Este projeto é desenvolvido para fins educacionais e de pesquisa em Processamento de Linguagem Natural. Baseado na tecnologia aberta desenvolvida pela equipe da **Mozilla AI** e do projeto **llama.cpp / Cosmopolitan Libc**.
