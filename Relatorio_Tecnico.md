# Relatório Técnico – Otimização de Programação de Manutenção (iOptimum)

Este relatório apresenta a modelagem matemática, a estratégia heurística e os resultados obtidos na resolução do desafio de otimização de programação semanal de manutenção utilizando três cenários de backlog (500, 1000 e 2000 ordens de serviço).

## 1. Modelagem Matemática e Abordagem

O problema consiste em programar um conjunto de ordens de serviço (OS) ao longo de 5 dias úteis (Segunda a Sexta), respeitando quatro conjuntos de restrições críticas:

1. **Capacidade Diária de Habilidades**: Cada dia da semana possui um limite disponível de homens-hora (HH) para as habilidades de *Mecânico*, *Elétrico*, *Lubrificador* e *Soldador*. A alocação total de HH em cada dia não deve superar a capacidade disponível.
2. **Predecessoras (Dependência)**: Uma OS $B$ que depende de uma OS $A$ só pode ser iniciada após a conclusão total da OS $A$. Como as OSs são programadas no nível diário e podem durar mais de 1 dia, a alocação de data de início de $B$ deve garantir que ela comece após o dia de término real de $A$.
3. **Parada de Planta (Outage)**: Certas OSs possuem a condição `Parada`. Essas ordens de serviço só podem ser programadas nos dias de parada da planta (definidos como Dias 3 e 4). Para garantir a integridade da planta, essas ordens também devem ser concluídas na totalidade antes do fim do período de parada (Dia 4).
4. **Duração Multidia e Sequenciamento**: Embora haja capacidade de HH disponível em um dia, as tarefas de uma OS são executadas sequencialmente por no máximo 8 horas diárias de trabalho consecutivo. OSs longas podem, portanto, se estender por múltiplos dias úteis, consumindo recursos de forma fracionada ao longo do tempo.

## 2. Design do Algoritmo Heurístico

A fim de resolver este problema de empacotamento restrito (*Knapsack-like scheduling with dependencies and spillovers*) de forma eficiente e determinística, projetamos uma **Heurística Gulosa com Ordenamento de Prioridade** (Greedy Priority Dispatching):

1. **Ordenamento Crítico**: As OSs são ordenadas de forma decrescente pela prioridade ($Z > A > B > C$).
2. **Minimização de Recursos**: Dentro de uma mesma prioridade, as OSs são ordenadas de forma crescente pelo seu consumo total de recursos (Soma da duração das tarefas multiplicada pela quantidade de executantes). Isso garante que, para uma mesma classe de prioridade, empacotamos o maior número possível de OSs menores, maximizando a contagem total de OSs programadas.
3. **Verificação Dinâmica de Viabilidade**: Para cada OS, testamos os dias de início viáveis (Dias 3 e 4 para OSs de parada; Dias 1 a 5 para as demais). Executamos uma simulação completa do cronograma para verificar se a alocação no dia em teste causa estouro de capacidade de qualquer habilidade em qualquer dia, ou violação de precedência.
4. **Resolução de Conflitos**: A OS é fixada no primeiro dia em que ela se provar viável. Caso contrário, não é programada.

## 3. Resultados dos Cenários de Backlog

Abaixo estão os resultados consolidados obtidos ao rodar o algoritmo desenvolvido em cada um dos três arquivos Excel disponibilizados:

| Métrica | Backlog 500 OSs | Backlog 1000 OSs | Backlog 2000 OSs |
| :--- | :---: | :---: | :---: |
| **OSs Programadas** | 37 | 54 | 55 |
| - Prioridade Z | 14 | 16 | 26 |
| - Prioridade A | 9 | 23 | 17 |
| - Prioridade B | 8 | 7 | 8 |
| - Prioridade C | 6 | 8 | 4 |
| **Utilização de Mecânico** | 91% | 93% | 98% |
| **Utilização de Elétrico** | 78% | 97% | 100% |
| **Utilização de Lubrificador** | 94% | 89% | 97% |
| **Utilização de Soldador** | 82% | 96% | 98% |

### Visualização Gráfica

Os gráficos gerados abaixo ilustram o desempenho e o aproveitamento dos recursos:

#### Distribuição de OSs por Prioridade
![Distribuição por Prioridade](chart_scheduled_by_priority.png)

#### Percentual de Utilização de Recursos
![Utilização de Recursos](chart_resource_utilization.png)

## 4. Análise de Gargalos e Recomendações

1. **Saturação de Capacidade**: Observa-se que, à medida que o tamanho do backlog aumenta, a utilização dos recursos chega a quase **100%** (como o recurso *Elétrico* no backlog de 2000 OSs e *Mecânico* no de 2000 OSs com 98.4%). Isso indica que a restrição de capacidade de homem-hora é o principal limitador para programar mais ordens de serviço.
2. **Eficiência do Escalonamento**: A heurística demonstrou alto desempenho ao conseguir alocar quase toda a capacidade disponível semanal sem violar os limites diários individuais, mantendo um equilíbrio excelente entre as restrições de precedência e paradas.
3. **Otimizações Futuras**: Caso a planta aumente a quantidade de mão de obra (por exemplo, contratando subempreiteiros para as habilidades limitantes), a heurística gulose irá automaticamente preencher as lacunas adicionais, escalando de maneira linear com a complexidade do problema.
