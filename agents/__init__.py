"""
InsightEsfera Agents Package
"""

def _safe_import():
    try:
        # Importar apenas agent e root_agent do agent.py
        from .agent import agent, root_agent
        # Importar funções utilitárias, se existirem
        from .registry import register_agent, load_agent, list_agents, save_agent
        return {
            'root_agent': root_agent,
            'agent': agent,
            'register_agent': register_agent,
            'load_agent': load_agent,
            'list_agents': list_agents,
            'save_agent': save_agent
        }
    except ImportError as e:
        print(f"Import warning in agents/__init__.py: {e}")
        # Fallback mínimo - tenta importar do architect_agent direto
        try:
            from .architect_agent import advanced_architect_agent
            agent = advanced_architect_agent
            root_agent = advanced_architect_agent
            return {
                'root_agent': root_agent,
                'agent': agent,
            }
        except ImportError as e2:
            print(f"Critical import error: {e2}")
            return {}

_imports = _safe_import()

root_agent = _imports.get('root_agent')
agent = _imports.get('agent')
register_agent = _imports.get('register_agent')
load_agent = _imports.get('load_agent')
list_agents = _imports.get('list_agents')
save_agent = _imports.get('save_agent')

__all__ = [k for k, v in _imports.items() if v is not None]

if root_agent is None or agent is None:
    print("⚠️  WARNING: agents.root_agent ou agents.agent é None!")
    print(f"Available imports: {list(_imports.keys())}")
else:
    print("✅ agents package loaded successfully")
