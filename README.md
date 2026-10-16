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

1. **Linux**, **macOS** ou **Windows** (via WSL2);
2. **Python 3.8+**;
3. Um modelo em formato `.llamafile` baixado na pasta do projeto (ex: `Qwen3.5-2B-Q8_0.llamafile`).

> Caso ainda não possua um modelo baixado, consulte o [Guia de Recursos e Modelos](docs/guia-recursos-e-modos.md#3-onde-encontrar-e-baixar-mais-modelos-llamafile).

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
python3 gerallamafile.py

# Ou explicitando o uso de CPU:
python3 gerallamafile.py --cpu

# Ou habilitando aceleração por GPU (se disponível):
python3 gerallamafile.py --gpu
```

### 3. Inicie o Seu Modelo
O comando anterior gera o script executável [iniciar_modelo.sh](file:///home/marcelo/projetos/pln/llamafile/iniciar_modelo.sh). Para utilizá-lo:

```bash
# Iniciar no modo padrão (Chat interativo no terminal):
./iniciar_modelo.sh

# Ou iniciar no modo Web UI (abrindo servidor no navegador):
./iniciar_modelo.sh --web
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
