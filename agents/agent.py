# agents/agent.py
# agents/agent.py
"""
Root agent exposure for ADK compatibility
"""

try:
    from .architect_agent import advanced_architect_agent

    # Expor como root_agent (padrão ADK)
    root_agent = advanced_architect_agent

    # Expor também como 'agent' para compatibilidade
    agent = advanced_architect_agent

    # Verificação de integridade
    if root_agent is None:
        raise ValueError("advanced_architect_agent is None")

    print("✅ agents/agent.py loaded successfully - agent disponível!")

except Exception as e:
    print(f"❌ Error in agents/agent.py: {e}")
    # Fallback seguro
    root_agent = None
    agent = None

def test_agent():
    """Função de teste para verificar se o agente está funcionando"""
    if root_agent is None:
        return {"status": "error", "error": "root_agent is None"}
    try:
        # Teste simples de invocação
        response = root_agent.invoke({
            "messages": [{"role": "user", "content": "Hello, test message"}]
        })
        return {"status": "ok", "response": str(response)}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Disponibilizar função de teste e agentes para import
__all__ = ['root_agent', 'agent', 'test_agent']
