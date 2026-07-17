import os
import shutil
import tempfile
from fastapi import UploadFile, HTTPException
from services.scheduler import load_and_normalize_data, build_os_info, check_feasibility, create_solution

class SolveController:
    """
    Coordena a análise de arquivos, a invocação do solver heurístico,
    a formatação das métricas estruturadas para o frontend e a limpeza de arquivos temporários.
    """
    
    @staticmethod
    def process_scheduling(file: UploadFile):
        # 1. Validação do formato do arquivo
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Somente arquivos Excel (.xlsx, .xls) são suportados.")
            
        # 2. Salva o arquivo enviado em um diretório temporário de forma segura
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
                shutil.copyfileobj(file.file, temp_file)
                temp_path = temp_file.name
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo enviado: {str(e)}")
            
        # 3. Invoca o solver e extrai informações detalhadas para a UI
        try:
            # Execução principal do motor de otimização
            solution_res = create_solution(temp_path)
            
            # Simulação detalhada adicional para estruturar os dados do calendário semanal
            df_os, df_tasks, df_resources, df_paradas = load_and_normalize_data(temp_path)
            os_info = build_os_info(df_os, df_tasks)
            
            day_map = {f"Dia_{i}": i for i in range(1, 6)}
            capacity = {}
            for _, row in df_resources.iterrows():
                day_num = day_map.get(row['Dia'], 0)
                capacity[(row['Habilidade'], day_num)] = row['HH_Disponivel']
                
            parada_days = set(df_paradas[df_paradas['Parada'] == 'Sim']['Dia'].tolist())
            
            # Converte os dias agendados para inteiros
            scheduled = {os_id: int(day) for os_id, day in solution_res['solution'].items()}
            
            # Simulação horária detalhada de término das ordens
            _, consumed_final, os_ends = check_feasibility(
                scheduled, os_info, capacity, parada_days, strict_parada=True, strict_week=True
            )
            
            # Agrupa as ordens de serviço pelo dia de início alocado
            schedule_by_day = {str(d): [] for d in range(1, 6)}
            for os_id, start_day in scheduled.items():
                info = os_info[os_id]
                schedule_by_day[str(start_day)].append({
                    "os": os_id,
                    "priority": info['priority'],
                    "condition": info['condition'],
                    "predecessor": info['predecessor'],
                    "duration": info['duration'],
                    "end_hour": os_ends.get(os_id, 0),
                    "tasks": info['tasks']
                })
                
            # Ordena as ordens para melhor estética de exibição (Prioridade decrescente e duração crescente)
            priority_rank = {'Z': 4, 'A': 3, 'B': 2, 'C': 1}
            for day in schedule_by_day:
                schedule_by_day[day].sort(key=lambda item: (-priority_rank.get(item['priority'], 0), item['duration']))
                
            # Estrutura os vetores de utilização diária de recursos por dia (1 a 5)
            skills = {
                'mecanico': 'Mecânico',
                'eletrico': 'Elétrico',
                'lubrificador': 'Lubrificador',
                'soldador': 'Soldador'
            }
            
            daily_utilization = {key: [] for key in skills}
            for key, pt_name in skills.items():
                for day in range(1, 6):
                    cap = capacity.get((pt_name, day), 0)
                    cons = consumed_final.get((pt_name, day), 0)
                    util_pct = int(round(cons / cap * 100)) if cap > 0 else 0
                    daily_utilization[key].append(util_pct)
                    
            # Retorna o payload final formatado para consumo do dashboard
            return {
                "metrics": solution_res['metrics'],
                "schedule": schedule_by_day,
                "daily_utilization": daily_utilization,
                "extras": solution_res['extras']
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro interno no motor de otimização: {str(e)}")
            
        finally:
            # 4. Remove o arquivo Excel temporário para liberar memória e armazenamento
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
