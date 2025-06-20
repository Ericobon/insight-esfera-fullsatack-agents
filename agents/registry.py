# agents/registry.py
"""
Agent Registry - Funções para persistência de agentes
"""
import json
import os
from typing import Dict, Any, List
from datetime import datetime

# Diretório onde os agentes criados são salvos
AGENTS_DIR = os.path.join(os.path.dirname(__file__), 'created')

def ensure_agents_directory():
    """Garante que o diretório de agentes existe"""
    if not os.path.exists(AGENTS_DIR):
        os.makedirs(AGENTS_DIR)

def save_agent(agent_config: Dict[str, Any]) -> str:
    """
    Salva a configuração de um agente no disco
    """
    ensure_agents_directory()
    
    agent_name = agent_config.get('name', 'unnamed_agent')
    # Sanitizar o nome para uso em arquivo
    safe_name = "".join(c for c in agent_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_').lower()
    
    filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(AGENTS_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(agent_config, f, indent=2, ensure_ascii=False)
    
    return filepath

def register_agent(agent_config: Dict[str, Any]) -> str:
    """
    Registra um agente (alias para save_agent para compatibilidade)
    """
    return save_agent(agent_config)

def load_agent(agent_name: str) -> Dict[str, Any]:
    """
    Carrega a configuração de um agente pelo nome
    """
    ensure_agents_directory()
    
    # Buscar arquivos que contenham o nome do agente
    for filename in os.listdir(AGENTS_DIR):
        if filename.endswith('.json') and agent_name.lower() in filename.lower():
            filepath = os.path.join(AGENTS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    raise FileNotFoundError(f"Agente '{agent_name}' não encontrado")

def list_agents() -> List[Dict[str, Any]]:
    """
    Lista todos os agentes salvos
    """
    ensure_agents_directory()
    
    agents = []
    for filename in os.listdir(AGENTS_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(AGENTS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    agent_config = json.load(f)
                    agents.append({
                        'filename': filename,
                        'config': agent_config
                    })
            except Exception as e:
                print(f"Erro ao carregar {filename}: {e}")
    
    return agents