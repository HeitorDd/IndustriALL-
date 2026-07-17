# IndustriALL – Otimizador de Cronograma Semanal de Manutenção

Este projeto consiste em uma ferramenta de otimização de programação semanal de manutenção industrial (PCM) projetada para a **IndustriALL**. O sistema consome dados de ordens de serviço (OS) e recursos de planilhas Excel, executa uma heurística gulosa de alta performance para resolver as restrições operacionais e apresenta o cronograma final através de um dashboard web moderno e responsivo.

---

## 🚀 Guia de Clonagem, Instalação e Execução

Siga os passos abaixo para baixar o código e rodar a aplicação em sua máquina local.

### 1. Clonando o Repositório
Abra o terminal (Prompt de Comando, PowerShell ou Terminal do Git) na pasta onde deseja salvar o projeto e execute o comando abaixo:
```bash
git clone https://github.com/HeitorDd/IndustriALL-.git
```

Em seguida, acesse a pasta criada:
```bash
cd IndustriALL-
```

---

### 2. Executando o Projeto

Você pode iniciar o servidor de duas maneiras:

#### Método Rápido (Windows)
Se você estiver utilizando o sistema operacional Windows:
- Basta **dar um duplo clique no arquivo `start.bat`** na raiz da pasta do projeto.
- O script automatizado irá baixar/atualizar as dependências e iniciar o servidor FastAPI sem necessidade de comandos adicionais.

#### Método Manual (Qualquer Sistema Operacional)
1. Certifique-se de ter o Python instalado.
2. Instale as bibliotecas necessárias listadas no `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicialize o servidor executando:
   ```bash
   python app.py
   ```

---

### 3. Acessando a Aplicação
Com o servidor ativo:
- **Dashboard de PCM (Interface Web)**: Abra o navegador e acesse [http://127.0.0.1:8000/](http://127.0.0.1:8000/) para interagir com o planejador.
- **Documentação da API**: Acesse o painel do Swagger em [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) para validar os endpoints.

---

## 🛠️ Tecnologias Utilizadas
- **Backend**: FastAPI (Python) - Servidor web assíncrono de alto desempenho.
- **Otimização**: Algoritmo Heurístico Guloso desenvolvido com Pandas e NumPy para manipulação rápida de matrizes.
- **Frontend**: HTML5, Vanilla CSS3 (Visual Ethereal Glass com paleta de cores corporativa) e JavaScript ES6.
- **Gráficos**: Chart.js para visualização diária de utilização das equipes de manutenção.
- **Execução**: Uvicorn.
