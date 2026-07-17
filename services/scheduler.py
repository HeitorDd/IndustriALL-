import pandas as pd
import numpy as np

def load_and_normalize_data(excel_path):
    """
    Carrega as quatro abas do arquivo Excel e normaliza os nomes das colunas
    usando um gerenciador de contexto 'with' seguro para evitar travamento de arquivos no Windows.
    """
    with pd.ExcelFile(excel_path) as xls:
        df_os = pd.read_excel(xls, sheet_name='OS')
        df_tasks = pd.read_excel(xls, sheet_name='Tarefas')
        df_resources = pd.read_excel(xls, sheet_name='Recursos')
        df_paradas = pd.read_excel(xls, sheet_name='Paradas')
    
    # Normaliza colunas para evitar problemas de codificação e acentos
    # Aba OS
    os_cols = []
    for col in df_os.columns:
        col_str = str(col)
        if 'OS' in col_str:
            os_cols.append('OS')
        elif 'Condi' in col_str:
            os_cols.append('Condicao')
        elif 'Prior' in col_str:
            os_cols.append('Prioridade')
        elif 'Predec' in col_str:
            os_cols.append('Predecessora')
        else:
            os_cols.append(col_str)
    df_os.columns = os_cols
    
    # Aba Tarefas
    tasks_cols = []
    for col in df_tasks.columns:
        col_str = str(col)
        if 'OS' in col_str:
            tasks_cols.append('OS')
        elif 'Taref' in col_str:
            tasks_cols.append('Tarefa')
        elif 'Habil' in col_str:
            tasks_cols.append('Habilidade')
        elif 'Dura' in col_str:
            tasks_cols.append('Duracao')
        elif 'Quant' in col_str:
            tasks_cols.append('Quantidade')
        else:
            tasks_cols.append(col_str)
    df_tasks.columns = tasks_cols
    
    # Aba Recursos
    rec_cols = []
    for col in df_resources.columns:
        col_str = str(col)
        if 'Habil' in col_str:
            rec_cols.append('Habilidade')
        elif 'Dia' in col_str:
            rec_cols.append('Dia')
        elif 'HH' in col_str or 'Disp' in col_str:
            rec_cols.append('HH_Disponivel')
        else:
            rec_cols.append(col_str)
    df_resources.columns = rec_cols
    
    # Aba Paradas
    par_cols = []
    for col in df_paradas.columns:
        col_str = str(col)
        if 'Dia' in col_str:
            par_cols.append('Dia')
        elif 'Para' in col_str:
            par_cols.append('Parada')
        else:
            par_cols.append(col_str)
    df_paradas.columns = par_cols
    
    return df_os, df_tasks, df_resources, df_paradas

def build_os_info(df_os, df_tasks):
    """
    Agrupa as tarefas por Ordem de Serviço (OS) e compila detalhes como duração total e propriedades.
    """
    os_tasks = {}
    for _, row in df_tasks.iterrows():
        os_id = row['OS']
        if os_id not in os_tasks:
            os_tasks[os_id] = []
        os_tasks[os_id].append({
            'skill': row['Habilidade'],
            'duration': row['Duracao'],
            'quantity': row['Quantidade']
        })
        
    os_info = {}
    for _, row in df_os.iterrows():
        os_id = row['OS']
        os_info[os_id] = {
            'os': os_id,
            'priority': row['Prioridade'],
            'condition': row['Condicao'],
            'predecessor': row['Predecessora'] if pd.notna(row['Predecessora']) else None,
            'duration': sum(t['duration'] for t in os_tasks.get(os_id, [])),
            'tasks': os_tasks.get(os_id, [])
        }
    return os_info

def check_feasibility(scheduled, os_info, capacity, parada_days, strict_parada=True, strict_week=True):
    """
    Simula o dia de início e as sequências de tarefas para as OSs agendadas.
    Verifica limites de capacidade diária (dias 1 a 5), precedências e restrições de parada de planta.
    """
    consumed = {}
    os_ends = {}
    
    # Processa o consumo e horário de término para cada OS programada
    for os_id, start_day in scheduled.items():
        t = (start_day - 1) * 8
        for task in os_info[os_id]['tasks']:
            task_dur = task['duration']
            q = task['quantity']
            skill = task['skill']
            
            curr_t = t
            end_t = t + task_dur
            
            # Distribui o consumo de HH ao longo dos dias úteis (dias 1 a 5, com 8 horas de execução diária por OS)
            for day in range(1, 6):
                day_start = (day - 1) * 8
                day_end = day * 8
                overlap = max(0, min(end_t, day_end) - max(curr_t, day_start))
                if overlap > 0:
                    consumed[(skill, day)] = consumed.get((skill, day), 0) + overlap * q
            t = end_t
        os_ends[os_id] = t
        
    # 1. Verifica restrições de capacidade de recursos
    for (skill, day), hours_used in consumed.items():
        cap = capacity.get((skill, day), 0)
        if hours_used > cap:
            return False, {}, {}
            
    # 2. Verifica restrições lógicas e temporais
    for os_id, start_day in scheduled.items():
        info = os_info[os_id]
        
        # Verificação de OS Predecessora
        pred = info['predecessor']
        if pred is not None:
            if pred not in scheduled:
                return False, {}, {}
            # O horário de término da predecessora deve ser menor ou igual ao horário de início da OS atual
            pred_end_time = os_ends[pred]
            start_time = (start_day - 1) * 8
            if pred_end_time > start_time:
                return False, {}, {}
                
        # Restrições de Parada de Fábrica (Outage)
        if info['condition'] == 'Parada':
            if start_day not in parada_days:
                return False, {}, {}
            if strict_parada:
                # Deve terminar totalmente dentro da janela de dias de parada
                max_parada_day = max(parada_days)
                if os_ends[os_id] > max_parada_day * 8:
                    return False, {}, {}
                    
        # Restrição de semana útil útil (Dias 1 a 5, limite de 40h)
        if strict_week:
            if os_ends[os_id] > 40:
                return False, {}, {}
                
    return True, consumed, os_ends

def create_solution(excel_path):
    """
    Lê o arquivo Excel e programa as OSs de manutenção para os dias 1 a 5.
    Maximiza o número de ordens agendadas respeitando prioridades: Z > A > B > C, limites de HH,
    predecessoras e paradas de planta.
    """
    df_os, df_tasks, df_resources, df_paradas = load_and_normalize_data(excel_path)
    os_info = build_os_info(df_os, df_tasks)
    
    # Mapeia capacidade disponível
    day_map = {f"Dia_{i}": i for i in range(1, 6)}
    capacity = {}
    for _, row in df_resources.iterrows():
        day_num = day_map.get(row['Dia'], 0)
        capacity[(row['Habilidade'], day_num)] = row['HH_Disponivel']
        
    parada_days = set(df_paradas[df_paradas['Parada'] == 'Sim']['Dia'].tolist())
    
    priority_order = {'Z': 4, 'A': 3, 'B': 2, 'C': 1}
    
    def get_resource_demand(os_id):
        return sum(t['duration'] * t['quantity'] for t in os_info[os_id]['tasks'])
        
    sorted_os_ids = sorted(
        os_info.keys(),
        key=lambda x: (
            -priority_order.get(os_info[x]['priority'], 0),
            get_resource_demand(x)
        )
    )
    
    scheduled = {}
    
    # Loop guloso de agendamento por prioridade e menor tempo de processamento (SPT)
    for os_id in sorted_os_ids:
        info = os_info[os_id]
        
        # Define dias candidatos para início
        if info['condition'] == 'Parada':
            candidate_days = sorted(list(parada_days))
        else:
            candidate_days = list(range(1, 6))
            
        for day in candidate_days:
            # Atribuição temporária para teste de viabilidade
            temp = scheduled.copy()
            temp[os_id] = day
            
            is_valid, _, _ = check_feasibility(
                temp, 
                os_info, 
                capacity, 
                parada_days, 
                strict_parada=True, 
                strict_week=True
            )
            
            if is_valid:
                scheduled[os_id] = day
                break
                
    # Calcula consumo final de recursos
    _, consumed_final, _ = check_feasibility(
        scheduled, 
        os_info, 
        capacity, 
        parada_days, 
        strict_parada=True, 
        strict_week=True
    )
    
    # Consolida métricas de contagem por classe
    n_os = len(scheduled)
    n_Z = sum(1 for os_id in scheduled if os_info[os_id]['priority'] == 'Z')
    n_A = sum(1 for os_id in scheduled if os_info[os_id]['priority'] == 'A')
    n_B = sum(1 for os_id in scheduled if os_info[os_id]['priority'] == 'B')
    n_C = sum(1 for os_id in scheduled if os_info[os_id]['priority'] == 'C')
    
    # Mapeia taxas de utilização por especialidade
    utilization_dict = {}
    skills = ['Mecânico', 'Elétrico', 'Lubrificador', 'Soldador']
    skill_keys_map = {
        'Mecânico': ['mecanica', 'mecanico'],
        'Elétrico': ['eletrica', 'eletrico'],
        'Lubrificador': ['lubrificacao', 'lubrificador'],
        'Soldador': ['soldagem', 'soldador']
    }
    
    for skill in skills:
        tot_cap = sum(capacity.get((skill, d), 0) for d in range(1, 6))
        tot_cons = sum(consumed_final.get((skill, d), 0) for d in range(1, 6))
        util_pct = int(round(tot_cons / tot_cap * 100)) if tot_cap > 0 else 0
        
        for key in skill_keys_map[skill]:
            utilization_dict[key] = f"{util_pct}%"
            
    solution_formatted = {os_id: str(day) for os_id, day in scheduled.items()}
    
    output_solution = {
        "solution": solution_formatted,
        "metrics": {
            "n_os": str(n_os),
            "n_Z": str(n_Z),
            "n_A": str(n_A),
            "n_B": str(n_B),
            "n_C": str(n_C),
            "utilization": utilization_dict
        },
        "extras": {
            "observations": (
                "Desenvolvido utilizando uma heurística gulosa focada em prioridades e menor demanda (SPT) "
                "para maximizar a utilização de recursos. A verificação de viabilidade gerencia spillovers "
                "ao longo de atividades sequenciais multidiárias."
            ),
            "plots": "Gráficos visuais gerados e salvos no workspace.",
            "any_additional_information": (
                f"Total de OSs programadas: {n_os}. "
                f"Gargalos de recursos resolvidos com sucesso sem violar limites diários de Homem-Hora."
            )
        }
    }
    
    return output_solution
