import os
import shutil
import tempfile
from fastapi import UploadFile, HTTPException
from services.scheduler import load_and_normalize_data, build_os_info, check_feasibility, create_solution

class SolveController:
    """
    Coordinates file parsing, solver invocation, formatting UI-ready metrics,
    and handling temporary cleanup operations.
    """
    
    @staticmethod
    def process_scheduling(file: UploadFile):
        # 1. Validation
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Somente arquivos Excel (.xlsx, .xls) são suportados.")
            
        # 2. Save temporary upload file
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
                shutil.copyfileobj(file.file, temp_file)
                temp_path = temp_file.name
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo enviado: {str(e)}")
            
        # 3. Invoke Solver & Extract Info
        try:
            # Core solver run
            solution_res = create_solution(temp_path)
            
            # Additional detailed simulation for UI calendar rendering
            df_os, df_tasks, df_resources, df_paradas = load_and_normalize_data(temp_path)
            os_info = build_os_info(df_os, df_tasks)
            
            day_map = {f"Dia_{i}": i for i in range(1, 6)}
            capacity = {}
            for _, row in df_resources.iterrows():
                day_num = day_map.get(row['Dia'], 0)
                capacity[(row['Habilidade'], day_num)] = row['HH_Disponivel']
                
            parada_days = set(df_paradas[df_paradas['Parada'] == 'Sim']['Dia'].tolist())
            
            # Parse days as integers
            scheduled = {os_id: int(day) for os_id, day in solution_res['solution'].items()}
            
            # Simulate detailed hours
            _, consumed_final, os_ends = check_feasibility(
                scheduled, os_info, capacity, parada_days, strict_parada=True, strict_week=True
            )
            
            # Group by start day
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
                
            # Sort for display aesthetics
            priority_rank = {'Z': 4, 'A': 3, 'B': 2, 'C': 1}
            for day in schedule_by_day:
                schedule_by_day[day].sort(key=lambda item: (-priority_rank.get(item['priority'], 0), item['duration']))
                
            # Daily resources utilization arrays
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
                    
            # Return final UI payload
            return {
                "metrics": solution_res['metrics'],
                "schedule": schedule_by_day,
                "daily_utilization": daily_utilization,
                "extras": solution_res['extras']
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro interno no motor de otimização: {str(e)}")
            
        finally:
            # 4. Cleanup temp file
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
