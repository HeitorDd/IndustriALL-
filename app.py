import uvicorn
from fastapi import FastAPI
from routes import solve_routes
from config import settings

app = FastAPI(
    title="IndustriALL - Sistema de Otimização de Manutenção",
    description="Interface de planejamento e escalonamento semanal de manutenção industrial."
)

# Register routes
app.include_router(solve_routes.router)

if __name__ == "__main__":
    print(f"Starting IndustriALL scheduling system server at http://{settings.HOST}:{settings.PORT}")
    uvicorn.run("app:app", host=settings.HOST, port=settings.PORT, reload=True)
