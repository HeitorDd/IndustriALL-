# Relatório Técnico – Otimização de Programação de Manutenção (IndustriALL)

Este relatório apresenta a modelagem, as estratégias heurísticas adotadas e a análise dos resultados obtidos na resolução do desafio de otimização de programação semanal de manutenção da **IndustriALL**, cobrindo backlogs de 500, 1000 e 2000 ordens de serviço.

---

## 1. EXPLICAÇÃO DAS ESTRATÉGIAS

### A. Lógica de Resolução e Modelagem das Restrições
O problema de programação de manutenção industrial consiste em agendar um conjunto de ordens de serviço (OS) ao longo de uma semana útil (dias 1 a 5, de segunda a sexta-feira), respeitando regras operacionais rígidas:

- **Limites de Capacidade Diária**: A soma do consumo de homem-hora (HH) de todas as tarefas programadas em um determinado dia não pode exceder a capacidade física diária disponível para aquela habilidade específica (Mecânico, Elétrico, Lubrificador e Soldador).
- **Janelas de Parada de Planta**: As ordens de serviço marcadas com a condição "Parada" só podem começar nos dias de parada da fábrica (dias 3 e 4) e devem ser totalmente concluídas antes do fim do dia 4 (limite de 32 horas acumuladas na semana).
- **Dependências de Precedência**: Se uma OS "B" depende de uma OS "A" (predecessora), a OS "B" só pode ser iniciada após a conclusão completa de todas as tarefas da OS "A".

### B. Algoritmo Desenvolvido: Heurística Gulosa com Ordenamento de Prioridade
Para garantir a viabilidade das restrições e velocidade de execução (tempo de resposta imediato para a API do dashboard), implementamos um algoritmo heurístico guloso:

1. **Ordenamento por Prioridade Crítica**: As ordens são inseridas na fila de processamento na ordem estrita de criticidade: prioridade Z primeiro, seguida por A, B e finalmente C.
2. **Minimização de Demanda de Recursos**: Como critério de desempate para ordens de mesma prioridade, priorizamos aquelas com menor demanda acumulada de homem-hora (HH). A demanda de cada OS é calculada pela fórmula:
   
   Demanda da OS = Soma de (Duração da Tarefa x Quantidade de Executantes) para todas as suas tarefas.
   
   Essa abordagem prioriza a execução de ordens menores e mais rápidas, maximizando a quantidade total de OSs concluídas nas brechas da capacidade diária.
3. **Simulador de Linha do Tempo e Spillover (Transbordo)**:
   As tarefas de uma mesma OS executam em sequência direta (uma após a outra). A simulação calcula a hora exata de início e término de cada atividade. Se uma tarefa ultrapassar o limite diário de 8 horas de trabalho para aquela OS, a carga de HH restante é automaticamente distribuída para os dias seguintes (transbordo), consumindo a capacidade dos recursos nos respectivos dias de execução real.

### C. Decisão de Arquitetura de Software
O código do projeto no workspace IndustriALL foi estruturado no padrão de camadas (Layered Architecture) para isolar o motor matemático das rotas web e da interface do usuário:
- **config/settings.py**: Constantes e configurações do servidor.
- **services/scheduler.py**: Motor matemático puro contendo a lógica de simulação e agendamento.
- **controllers/solve_controller.py**: Manipula arquivos e formata os dados para o calendário e gráficos do dashboard.
- **routes/solve_routes.py**: Endpoints da API FastAPI.
- **static/**: Interface web desenhada sob o conceito premium Ethereal Glass.

---

## 2. APRESENTAÇÃO DOS RESULTADOS

O algoritmo foi testado nos três cenários de backlog fornecidos. Ele aloca os recursos disponíveis até o limite extremo das equipes de manutenção:

### A. Métricas Consolidadas de Execução

| Métrica | Backlog 500 OSs | Backlog 1000 OSs | Backlog 2000 OSs |
| :--- | :---: | :---: | :---: |
| **OSs Programadas (Total)** | **37** | **54** | **55** |
| - Prioridade Z | 14 | 16 | 26 |
| - Prioridade A | 9 | 23 | 17 |
| - Prioridade B | 8 | 7 | 8 |
| - Prioridade C | 6 | 8 | 4 |
| **Utilização de Mecânico** | **91%** | **93%** | **98%** |
| **Utilização de Elétrico** | **78%** | **97%** | **100%** |
| **Utilização de Lubrificador** | **94%** | **89%** | **97%** |
| **Utilização de Soldador** | **82%** | **96%** | **98%** |

### B. Análise de Ocupação e Gargalos
- **Recurso Elétrico**: No cenário de 2000 OSs, a utilização da equipe de Elétrica atinge exatamente 100%, atuando como o gargalo crítico da fábrica.
- **Recurso Mecânico**: Atinge 98% de utilização no cenário de 2000 OSs.
- **Validação de Restrições**: Em todos os cenários, 100% das regras foram respeitadas. Nenhuma ordem de Parada avançou além do final do dia 4, e nenhuma ordem dependente começou antes da conclusão da sua predecessora.

### C. Visualização Gráfica Integrada
Os gráficos abaixo (salvos na pasta estática do projeto) mostram o comportamento das alocações:

- Distribuição de OSs Agendadas por Prioridade: `static/chart_scheduled_by_priority.png`
- Taxa Percentual de Utilização de Recursos Semanais: `static/chart_resource_utilization.png`

---

## 3. DOCUMENTAÇÃO DO CÓDIGO

O código do motor de cálculo reside no arquivo [services/scheduler.py](services/scheduler.py).

### A. Função: load_and_normalize_data
Lê e padroniza as planilhas do Excel para evitar erros de codificação de caracteres especiais (ex: acentos) e locks de arquivo no Windows.
- **Assinatura**: `load_and_normalize_data(excel_path: str) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame)`
- **Argumentos**:
  - `excel_path`: Caminho físico do arquivo Excel a ser lido.
- **Funcionamento**: Abre o arquivo usando um bloco `with pd.ExcelFile(...)` para garantir que o Windows libere o arquivo após a leitura, e substitui cabeçalhos como "Condição" por "Condicao" em memória.

### B. Função: build_os_info
Associa as tarefas de manutenção a cada Ordem de Serviço correspondente.
- **Assinatura**: `build_os_info(df_os: pd.DataFrame, df_tasks: pd.DataFrame) -> dict`
- **Retorno**: Um dicionário contendo as propriedades estruturadas de cada OS (prioridade, condição, predecessora, duração total e tarefas internas).

### C. Função: check_feasibility
Simula a alocação temporal e valida a conformidade das restrições de capacidade e cronograma.
- **Assinatura**: `check_feasibility(scheduled: dict, os_info: dict, capacity: dict, parada_days: set, strict_parada: bool, strict_week: bool) -> (bool, dict, dict)`
- **Variáveis de Interesse**:
  - `consumed`: Dicionário que acumula o HH utilizado por habilidade e dia.
  - `os_ends`: Dicionário que armazena a hora de término acumulada de cada OS.
  - `t`: Variável que rastreia a hora atual na linha do tempo contínua da semana útil de trabalho da OS.

### D. Função: create_solution
Função principal que gerencia o fluxo de ordenação Heurística Gulosa e compila os resultados para retorno à API.
- **Assinatura**: `create_solution(excel_path: str) -> dict`
- **Retorno**: Dicionário serializável contendo a alocação de dias de início das OSs, contagem por prioridade e percentuais de utilização de recursos formatados.

---

## 4. GUIA DE INSTALAÇÃO E EXECUÇÃO

Para implantar e rodar o sistema de forma prática em qualquer máquina:

### A. Método Rápido (Windows)
Se você estiver utilizando o sistema operacional Windows, basta **dar um duplo clique no arquivo `start.bat`** na raiz do projeto. O script irá verificar as dependências do arquivo `requirements.txt`, instalá-las se necessário e iniciar o servidor automaticamente.

### B. Método Manual (Multiplataforma)
Caso prefira rodar via terminal (Linux, macOS ou Windows):
1. Abra o terminal no diretório do projeto.
2. Instale as bibliotecas exigidas:
   ```bash
   pip install -r requirements.txt
   ```
3. Inicie o servidor FastAPI:
   ```bash
   python app.py
   ```

### C. Navegação e Acesso
- **Interface Gráfica (Dashboard)**: Abra o seu navegador e acesse: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Documentação Interativa da API**: Acesse o painel de testes Swagger em: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
