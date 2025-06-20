# test_imports.py
"""Script para testar importações do projeto"""

def test_imports():
    results = {}
    
    # Teste 1: Importar o pacote agents
    try:
        import agents
        results['agents_import'] = "✅ OK"
        print("✅ agents importado com sucesso")
    except Exception as e:
        results['agents_import'] = f"❌ ERRO: {e}"
        print(f"❌ Erro ao importar agents: {e}")
        return results
    
    # Teste 2: Verificar se agents.agent existe
    try:
        agent = getattr(agents, 'agent', None)
        if agent:
            results['agents_agent'] = "✅ OK"
            print("✅ agents.agent encontrado")
        else:
            results['agents_agent'] = "❌ agents.agent não encontrado"
            print("❌ agents.agent não encontrado")
    except Exception as e:
        results['agents_agent'] = f"❌ ERRO: {e}"
        print(f"❌ Erro ao acessar agents.agent: {e}")
    
    # Teste 3: Verificar se agents.root_agent existe
    try:
        root_agent = getattr(agents, 'root_agent', None)
        if root_agent:
            results['agents_root_agent'] = "✅ OK"
            print("✅ agents.root_agent encontrado")
        else:
            results['agents_root_agent'] = "❌ agents.root_agent não encontrado"
            print("❌ agents.root_agent não encontrado")
    except Exception as e:
        results['agents_root_agent'] = f"❌ ERRO: {e}"
        print(f"❌ Erro ao acessar agents.root_agent: {e}")
    
    # Teste 4: Testar invocação do agente
    try:
        if hasattr(agents, 'agent') and agents.agent:
            test_response = agents.agent.invoke({
                "messages": [{"role": "user", "content": "Test message"}]
            })
            results['agent_invoke'] = "✅ OK"
            print("✅ Agente pode ser invocado")
        else:
            results['agent_invoke'] = "❌ Agente não disponível para teste"
            print("❌ Agente não disponível para teste")
    except Exception as e:
        results['agent_invoke'] = f"❌ ERRO: {e}"
        print(f"❌ Erro ao invocar agente: {e}")
    
    # Teste 5: Listar atributos do módulo agents
    try:
        attrs = [attr for attr in dir(agents) if not attr.startswith('_')]
        results['agents_attributes'] = attrs
        print(f"📋 Atributos disponíveis em agents: {attrs}")
    except Exception as e:
        results['agents_attributes'] = f"❌ ERRO: {e}"
        print(f"❌ Erro ao listar atributos: {e}")
    
    return results

if __name__ == "__main__":
    print("🧪 Testando importações do projeto InsightEsfera...")
    print("=" * 50)
    results = test_imports()
    print("\n" + "=" * 50)
    print("📊 Resumo dos testes:")
    for test, result in results.items():
        print(f"  {test}: {result}")