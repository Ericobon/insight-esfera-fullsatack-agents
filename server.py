from fastapi import FastAPI, Request
from pydantic import BaseModel
from agents.architect_agent import architect_agent
import uvicorn

app = FastAPI()

class AgentPrompt(BaseModel):
    prompt: str

@app.post("/create-agent")
async def create_agent(prompt_input: AgentPrompt):
    prompt = prompt_input.prompt
    # Aqui simulamos o uso do ArchitectAgent recebendo o prompt do usuário
    # O método pode variar dependendo do Agent, adapte se necessário
    try:
        # Supondo que o Agent aceite .run(prompt) ou equivalente
        # Se precisar ajustar o método (ex: .act, .process, etc), me fale!
        result = architect_agent.run(
            prompt,
            tools=["create_agent_tool", "consult_rag_knowledge", "list_available_tools"]
        )
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"msg": "InsightEsfera ArchitectAgent API running!"}

if __name__ == "__main__":
    # Rodar localmente na porta 8000
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
