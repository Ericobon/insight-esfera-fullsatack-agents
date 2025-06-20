import os
from agents.architect_agent import architect_agent
from agents.registry import list_agents

def main():
    print("==== MVP ArchitectAgent - Teste Local ====")

    # Teste: Criar um novo agente genérico (pode ser TechLead ou um DummyAgent)
    response = architect_agent.tools[0](
        agent_name="DummyAgent",
        agent_description="Agente de teste criado pelo ArchitectAgent.",
        agent_instructions="Apenas um agente para testar persistência.",
        tools_list=["consult_rag_knowledge", "list_available_tools"]
    )
    print("Retorno da criação:", response["message"])
    print("Configuração do agente criado:")
    print(response["agent_config"])

    # Teste: Listar todos os agentes criados
    print("\nAgentes registrados no disco:")
    agents = list_agents()
    for agent in agents:
        print(f"- {agent['name']}: {agent['description']}")

    # Teste: Consultar as ferramentas disponíveis do ArchitectAgent
    print("\nFerramentas do ArchitectAgent:")
    tool_list = architect_agent.tools[2]()  # list_available_tools deve ser o terceiro
    for tool in tool_list["tools"]:
        print("-", tool)

if __name__ == "__main__":
    main()
