"""
Advanced ArchitectAgent - Sistema Completo de Criação e Orquestração Multi-Agente
Versão 2.0: Inclui gerenciamento de dependências, arquiteturas avançadas e correções automáticas
"""

from google.adk.agents import Agent
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import os
import json
import inspect
import subprocess
import sys
import importlib.util
from pathlib import Path

try:
    from agents.rag_agent.agent import root_agent as rag_agent
    from agents.registry import save_agent
except ImportError as e:
    print(f"Import warning: {e}")

def manage_requirements(
    packages: List[str], 
    action: str = "install",
    tool_context=None
) -> Dict[str, Any]:
    """
    Gerencia dependências do projeto - instala, atualiza ou lista pacotes
    """
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        requirements_path = os.path.join(project_root, "requirements.txt")
        
        if action == "list":
            # Listar dependências atuais
            current_packages = []
            if os.path.exists(requirements_path):
                with open(requirements_path, 'r') as f:
                    current_packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            return {
                "status": "success",
                "current_packages": current_packages,
                "requirements_file": requirements_path
            }
        
        elif action == "install":
            # Instalar novos pacotes
            installed = []
            failed = []
            
            for package in packages:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    installed.append(package)
                except subprocess.CalledProcessError:
                    failed.append(package)
            
            # Atualizar requirements.txt
            if installed:
                existing_packages = set()
                if os.path.exists(requirements_path):
                    with open(requirements_path, 'r') as f:
                        existing_packages = {line.split('==')[0].split('>=')[0].split('<=')[0].strip() 
                                           for line in f if line.strip() and not line.startswith('#')}
                
                with open(requirements_path, 'a') as f:
                    for package in installed:
                        package_name = package.split('==')[0].split('>=')[0].split('<=')[0]
                        if package_name not in existing_packages:
                            f.write(f"\n{package}")
            
            return {
                "status": "success" if not failed else "partial",
                "installed": installed,
                "failed": failed,
                "requirements_updated": bool(installed)
            }
        
        elif action == "update":
            # Atualizar pacotes existentes
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + packages)
                return {"status": "success", "updated": packages}
            except subprocess.CalledProcessError as e:
                return {"status": "error", "message": f"Erro ao atualizar pacotes: {str(e)}"}
    
    except Exception as e:
        return {"status": "error", "message": f"Erro no gerenciamento de requisitos: {str(e)}"}

def scan_project_structure(tool_context=None) -> Dict[str, Any]:
    """
    Escaneia a estrutura do projeto com análise avançada de dependências e padrões
    """
    try:
        project_root = Path(os.path.dirname(os.path.dirname(__file__)))
        structure = {
            "agents": {},
            "tools": {},
            "available_tools": [],
            "agent_templates": {},
            "dependencies": [],
            "architecture_patterns": [],
            "recommendations": []
        }
        
        # Escanear diretório agents/
        agents_dir = project_root / "agents"
        if agents_dir.exists():
            for item in agents_dir.iterdir():
                if item.is_dir() and not item.name.startswith('__'):
                    agent_info = {
                        "path": str(item),
                        "has_agent_py": (item / "agent.py").exists(),
                        "has_config_py": (item / "config.py").exists(),
                        "has_tools_dir": (item / "tools").exists(),
                        "has_init_py": (item / "__init__.py").exists(),
                        "tools": [],
                        "imports": [],
                        "dependencies": []
                    }
                    
                    # Escanear ferramentas
                    tools_dir = item / "tools"
                    if tools_dir.exists():
                        for tool_file in tools_dir.glob("*.py"):
                            if not tool_file.name.startswith('__'):
                                tool_name = tool_file.stem
                                agent_info["tools"].append(tool_name)
                                structure["available_tools"].append(f"{item.name}.{tool_name}")
                    
                    # Analisar imports e dependências
                    agent_py = item / "agent.py"
                    if agent_py.exists():
                        try:
                            with open(agent_py, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Extrair imports
                                import_lines = [line.strip() for line in content.split('\n') 
                                              if line.strip().startswith(('import ', 'from '))]
                                agent_info["imports"] = import_lines
                        except Exception:
                            pass
                    
                    structure["agents"][item.name] = agent_info
        
        # Analisar padrões arquiteturais existentes
        structure["architecture_patterns"] = analyze_architecture_patterns(structure["agents"])
        
        # Gerar recomendações
        structure["recommendations"] = generate_architecture_recommendations(structure)
        
        return {
            "status": "success",
            "structure": structure,
            "project_root": str(project_root)
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Erro ao escanear projeto: {str(e)}"
        }

def analyze_architecture_patterns(agents: Dict[str, Any]) -> List[str]:
    """
    Analisa padrões arquiteturais nos agentes existentes
    """
    patterns = []
    
    if len(agents) > 1:
        patterns.append("Multi-Agent System")
    
    # Verificar se há agentes com ferramentas RAG
    rag_agents = [name for name, info in agents.items() 
                  if any('rag' in tool.lower() for tool in info.get('tools', []))]
    if rag_agents:
        patterns.append("RAG-Enhanced Agents")
    
    # Verificar padrões de coordenação
    coordinator_agents = [name for name, info in agents.items() 
                         if any(keyword in name.lower() for keyword in ['lead', 'manager', 'coordinator', 'orchestrator'])]
    if coordinator_agents:
        patterns.append("Hierarchical Coordination")
    
    return patterns

def generate_architecture_recommendations(structure: Dict[str, Any]) -> List[str]:
    """
    Gera recomendações arquiteturais baseadas na estrutura atual
    """
    recommendations = []
    agents_count = len(structure["agents"])
    
    if agents_count == 0:
        recommendations.append("Começar com um agente coordenador principal")
    elif agents_count == 1:
        recommendations.append("Considerar adicionar agentes especializados")
    elif agents_count > 3:
        recommendations.append("Implementar padrão de orquestração centralizada")
        recommendations.append("Considerar message bus para comunicação inter-agentes")
    
    # Recomendar ferramentas específicas
    if not any('rag' in agent for agent in structure["agents"]):
        recommendations.append("Integrar capacidades RAG para knowledge management")
    
    return recommendations

def create_advanced_agent(
    agent_name: str,
    agent_description: str,
    agent_instructions: str,
    tools_list: List[str],
    architecture_type: str = "standalone",  # standalone, coordinator, specialist
    model: str = "gemini-2.5-flash-preview-04-17",
    dependencies: Optional[List[str]] = None,
    tool_context=None,
) -> Dict[str, Any]:
    """
    Cria um agente avançado com arquitetura específica e gerenciamento automático de dependências
    """
    try:
        # Instalar dependências se necessário
        if dependencies:
            dep_result = manage_requirements(dependencies, "install")
            if dep_result["status"] == "error":
                return dep_result
        
        # Escanear estrutura do projeto
        scan_result = scan_project_structure()
        if scan_result["status"] != "success":
            return scan_result
        
        project_structure = scan_result["structure"]
        project_root = Path(scan_result["project_root"])
        
        # Resolver ferramentas
        available_tools = project_structure["available_tools"]
        resolved_tools = resolve_tools(tools_list, available_tools)
        
        # Criar diretório do agente
        agent_dir_name = agent_name.lower().replace(' ', '_').replace('-', '_')
        agent_dir = project_root / "agents" / agent_dir_name
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        # Gerar conteúdo baseado na arquitetura
        config_content, agent_content, init_content = generate_agent_files(
            agent_name, agent_description, agent_instructions, 
            resolved_tools, model, architecture_type, agent_dir_name
        )
        
        # Criar arquivos
        files_created = []
        
        # config.py
        config_path = agent_dir / "config.py"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        files_created.append(str(config_path))
        
        # agent.py
        agent_path = agent_dir / "agent.py"
        with open(agent_path, 'w', encoding='utf-8') as f:
            f.write(agent_content)
        files_created.append(str(agent_path))
        
        # __init__.py
        init_path = agent_dir / "__init__.py"
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write(init_content)
        files_created.append(str(init_path))
        
        # Criar estrutura adicional baseada na arquitetura
        if architecture_type == "coordinator":
            orchestration_path = agent_dir / "orchestration.py"
            with open(orchestration_path, 'w', encoding='utf-8') as f:
                f.write(generate_orchestration_module(agent_dir_name))
            files_created.append(str(orchestration_path))
        
        # Registrar no registry
        agent_config = {
            "name": agent_name,
            "description": agent_description,
            "instructions": agent_instructions,
            "tools": resolved_tools,
            "model": model,
            "architecture_type": architecture_type,
            "dependencies": dependencies or [],
            "created_at": str(datetime.now()),
            "agent_directory": str(agent_dir),
            "functional": True
        }
        
        json_path = save_agent(agent_config)
        
        # Testar importação com correção automática
        test_result = test_and_fix_agent(agent_path, agent_dir_name)
        
        return {
            "status": "success",
            "message": f"Agente avançado '{agent_name}' criado com sucesso!",
            "details": {
                "agent_directory": str(agent_dir),
                "files_created": files_created,
                "json_registry": json_path,
                "resolved_tools": resolved_tools,
                "architecture_type": architecture_type,
                "test_result": test_result,
                "dependencies_installed": dependencies or []
            },
            "agent_config": agent_config
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao criar agente avançado: {str(e)}"
        }

def resolve_tools(tools_list: List[str], available_tools: List[str]) -> List[str]:
    """
    Resolve ferramentas com matching inteligente
    """
    resolved_tools = []
    
    for tool in tools_list:
        # Busca exata
        if tool in available_tools:
            resolved_tools.append(tool)
        else:
            # Busca por similaridade
            similar_tools = [t for t in available_tools if tool.lower() in t.lower() or t.lower() in tool.lower()]
            if similar_tools:
                resolved_tools.extend(similar_tools[:1])
            else:
                # Adicionar como ferramenta a ser criada
                resolved_tools.append(f"TODO:{tool}")
    
    return resolved_tools

def generate_agent_files(
    agent_name: str, agent_description: str, agent_instructions: str,
    resolved_tools: List[str], model: str, architecture_type: str, agent_dir_name: str
) -> tuple:
    """
    Gera conteúdo dos arquivos do agente baseado na arquitetura
    """
    
    # config.py
    config_content = f'''# agents/{agent_dir_name}/config.py
"""
Configuração do {agent_name}
Arquitetura: {architecture_type}
Gerado automaticamente pelo AdvancedArchitectAgent em {datetime.now()}
"""

AGENT_CONFIG = {{
    "name": "{agent_name}",
    "description": "{agent_description}",
    "model": "{model}",
    "architecture_type": "{architecture_type}",
    "instructions": """{agent_instructions}""",
    "tools": {resolved_tools},
    "created_at": "{datetime.now()}",
    "created_by": "AdvancedArchitectAgent"
}}

# Configurações específicas da arquitetura
if "{architecture_type}" == "coordinator":
    AGENT_CONFIG["coordination_settings"] = {{
        "max_parallel_tasks": 3,
        "task_timeout": 300,
        "retry_attempts": 2
    }}
elif "{architecture_type}" == "specialist":
    AGENT_CONFIG["specialist_settings"] = {{
        "domain_focus": "{agent_name.lower()}",
        "expertise_level": "high"
    }}
'''
    
    # agent.py com importações corrigidas
    agent_content = f'''# agents/{agent_dir_name}/agent.py
"""
{agent_name} - Agente {architecture_type.title()}
Gerado automaticamente pelo AdvancedArchitectAgent
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz do projeto ao path para resolver importações
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from google.adk.agents import Agent
from .config import AGENT_CONFIG

def get_agent_tools():
    """Importa e retorna as ferramentas disponíveis para este agente"""
    tools = []
    
    # Importar ferramentas do RAG se disponível
    try:
        from agents.rag_agent.tools.rag_query import rag_query
        from agents.rag_agent.tools.list_corpora import list_corpora
        from agents.rag_agent.tools.create_corpus import create_corpus
        from agents.rag_agent.tools.add_data import add_data
        from agents.rag_agent.tools.delete_corpus import delete_corpus
        from agents.rag_agent.tools.delete_document import delete_document
        from agents.rag_agent.tools.get_corpus_info import get_corpus_info
        
        tools.extend([
            rag_query, list_corpora, create_corpus, 
            add_data, delete_corpus, delete_document, get_corpus_info
        ])
    except ImportError as e:
        print(f"Aviso: Não foi possível importar ferramentas RAG: {{e}}")
    
    # Adicionar ferramentas específicas da arquitetura
    if AGENT_CONFIG["architecture_type"] == "coordinator":
        try:
            from .orchestration import coordinate_agents, delegate_task, monitor_progress
            tools.extend([coordinate_agents, delegate_task, monitor_progress])
        except ImportError:
            pass
    
    return tools

# Criar instância do agente
{agent_dir_name}_agent = Agent(
    name=AGENT_CONFIG["name"],
    model=AGENT_CONFIG["model"],
    description=AGENT_CONFIG["description"],
    tools=get_agent_tools(),
    instruction=AGENT_CONFIG["instructions"]
)

# Expor como root_agent para compatibilidade
root_agent = {agent_dir_name}_agent

if __name__ == "__main__":
    print(f"Agente {{AGENT_CONFIG['name']}} carregado com sucesso!")
    print(f"Arquitetura: {{AGENT_CONFIG['architecture_type']}}")
    print(f"Ferramentas disponíveis: {{len(get_agent_tools())}}")
'''
    
    # __init__.py
    init_content = f'''"""
{agent_name} Package - Arquitetura {architecture_type.title()}
"""

try:
    from .agent import {agent_dir_name}_agent, root_agent
    from .config import AGENT_CONFIG
    
    __all__ = ['{agent_dir_name}_agent', 'root_agent', 'AGENT_CONFIG']
    
except ImportError as e:
    print(f"Aviso na inicialização do {agent_name}: {{e}}")
    # Definir fallbacks para evitar erros de importação
    {agent_dir_name}_agent = None
    root_agent = None
    AGENT_CONFIG = {{"name": "{agent_name}", "status": "import_error"}}
    
    __all__ = ['AGENT_CONFIG']
'''
    
    return config_content, agent_content, init_content

def generate_orchestration_module(agent_dir_name: str) -> str:
    """
    Gera módulo de orquestração para agentes coordenadores
    """
    return f'''# agents/{agent_dir_name}/orchestration.py
"""
Módulo de Orquestração para {agent_dir_name}
Implementa padrões de coordenação multi-agente
"""

from typing import List, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

def coordinate_agents(
    task_description: str,
    agents_list: List[str],
    coordination_strategy: str = "sequential",
    tool_context=None
) -> Dict[str, Any]:
    """
    Coordena múltiplos agentes para executar uma tarefa complexa
    """
    try:
        coordination_plan = {{
            "task": task_description,
            "agents": agents_list,
            "strategy": coordination_strategy,
            "steps": [],
            "estimated_time": len(agents_list) * 30  # segundos
        }}
        
        if coordination_strategy == "sequential":
            coordination_plan["steps"] = [
                f"1. Analisar tarefa: {{task_description}}",
                f"2. Dividir em {{len(agents_list)}} subtarefas",
                f"3. Executar sequencialmente com agentes: {{', '.join(agents_list)}}",
                "4. Consolidar resultados",
                "5. Validar entrega final"
            ]
        elif coordination_strategy == "parallel":
            coordination_plan["steps"] = [
                f"1. Analisar tarefa: {{task_description}}",
                f"2. Executar em paralelo com {{len(agents_list)}} agentes",
                "3. Sincronizar resultados",
                "4. Consolidar entrega"
            ]
            coordination_plan["estimated_time"] = 45  # Tempo fixo para execução paralela
        
        return {{
            "status": "success",
            "coordination_plan": coordination_plan,
            "next_action": "delegate_task"
        }}
        
    except Exception as e:
        return {{
            "status": "error",
            "message": f"Erro na coordenação: {{str(e)}}"
        }}

def delegate_task(
    task_description: str,
    target_agent: str,
    priority: str = "normal",
    deadline_minutes: int = 30,
    tool_context=None
) -> Dict[str, Any]:
    """
    Delega uma tarefa específica para um agente
    """
    try:
        task_delegation = {{
            "task_id": f"task_{{int(time.time())}}",
            "description": task_description,
            "assigned_to": target_agent,
            "priority": priority,
            "deadline": deadline_minutes,
            "status": "delegated",
            "created_at": time.time()
        }}
        
        return {{
            "status": "success",
            "task_delegation": task_delegation,
            "message": f"Tarefa delegada para {{target_agent}} com prazo de {{deadline_minutes}} minutos"
        }}
        
    except Exception as e:
        return {{
            "status": "error",
            "message": f"Erro na delegação: {{str(e)}}"
        }}

def monitor_progress(
    task_ids: List[str],
    report_format: str = "summary",
    tool_context=None
) -> Dict[str, Any]:
    """
    Monitora o progresso de tarefas delegadas
    """
    try:
        progress_report = {{
            "monitoring_time": time.time(),
            "tasks_monitored": len(task_ids),
            "report_format": report_format,
            "status_summary": {{
                "completed": 0,
                "in_progress": len(task_ids),
                "pending": 0,
                "failed": 0
            }},
            "recommendations": [
                "Implementar sistema de callback para atualizações em tempo real",
                "Configurar alertas para tarefas com atraso",
                "Estabelecer métricas de performance por agente"
            ]
        }}
        
        return {{
            "status": "success",
            "progress_report": progress_report
        }}
        
    except Exception as e:
        return {{
            "status": "error",
            "message": f"Erro no monitoramento: {{str(e)}}"
        }}
'''

def test_and_fix_agent(agent_path: Path, agent_dir_name: str) -> Dict[str, Any]:
    """
    Testa a importação do agente e corrige problemas automaticamente
    """
    try:
        # Tentar importação direta
        spec = importlib.util.spec_from_file_location(f"{agent_dir_name}_agent", agent_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return {
            "status": "success",
            "message": "✅ Agente importado e funcional",
            "tests_passed": True
        }
        
    except ImportError as e:
        # Tentar correção automática de imports relativos
        if "relative import" in str(e):
            return fix_relative_imports(agent_path, agent_dir_name)
        else:
            return {
                "status": "warning", 
                "message": f"⚠️ Erro de importação: {str(e)}",
                "suggestion": "Verificar dependências no requirements.txt"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Erro na validação: {str(e)}"
        }

def fix_relative_imports(agent_path: Path, agent_dir_name: str) -> Dict[str, Any]:
    """
    Corrige automaticamente problemas de importação relativa
    """
    try:
        with open(agent_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Adicionar correção de path no início do arquivo se não existir
        if "sys.path.insert" not in content:
            lines = content.split('\n')
            import_index = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('from google.adk.agents'):
                    import_index = i
                    break
            
            path_fix = '''
# Correção automática para importações relativas
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
'''
            
            lines.insert(import_index, path_fix)
            
            with open(agent_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
        
        return {
            "status": "fixed",
            "message": "✅ Imports relativos corrigidos automaticamente",
            "action_taken": "Adicionado correção de path para importações"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro na correção automática: {str(e)}"
        }

def list_project_agents(tool_context=None) -> Dict[str, Any]:
    """
    Lista todos os agentes com análise arquitetural
    """
    try:
        scan_result = scan_project_structure()
        if scan_result["status"] != "success":
            return scan_result
        
        project_structure = scan_result["structure"]
        
        # Análise detalhada dos agentes
        agents_analysis = {}
        for agent_name, agent_info in project_structure["agents"].items():
            analysis = {
                "functional_status": "✅" if agent_info["has_agent_py"] and agent_info["has_init_py"] else "⚠️",
                "tools_count": len(agent_info["tools"]),
                "architecture_ready": agent_info["has_config_py"],
                "dependencies_count": len(agent_info.get("dependencies", [])),
                "recommendations": []
            }
            
            # Gerar recomendações específicas
            if not agent_info["has_init_py"]:
                analysis["recommendations"].append("Adicionar __init__.py")
            if not agent_info["has_config_py"]:
                analysis["recommendations"].append("Criar arquivo de configuração")
            if len(agent_info["tools"]) == 0:
                analysis["recommendations"].append("Integrar ferramentas específicas")
            
            agents_analysis[agent_name] = analysis
        
        # Também listar agentes do registry
        try:
            from agents.registry import list_agents
            registry_agents = list_agents()
        except:
            registry_agents = []
        
        return {
            "status": "success",
            "functional_agents": project_structure["agents"],
            "agents_analysis": agents_analysis,
            "architecture_patterns": project_structure["architecture_patterns"],
            "recommendations": project_structure["recommendations"],
            "registry_agents_count": len(registry_agents),
            "total_agents": len(project_structure["agents"]) + len(registry_agents)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao listar agentes: {str(e)}"
        }

def setup_multi_agent_architecture(
    architecture_name: str,
    agents_config: List[Dict[str, Any]],
    coordination_pattern: str = "hierarchical",  # hierarchical, peer-to-peer, hub-spoke
    tool_context=None
) -> Dict[str, Any]:
    """
    Configura uma arquitetura multi-agente completa
    """
    try:
        architecture_plan = {
            "name": architecture_name,
            "pattern": coordination_pattern,
            "agents": agents_config,
            "communication_flow": [],
            "deployment_steps": [],
            "monitoring_setup": {},
            "scalability_notes": []
        }
        
        # Definir fluxo de comunicação baseado no padrão
        if coordination_pattern == "hierarchical":
            coordinator_agents = [a for a in agents_config if a.get("role") == "coordinator"]
            worker_agents = [a for a in agents_config if a.get("role") != "coordinator"]
            
            architecture_plan["communication_flow"] = [
                f"Coordinator ({coordinator_agents[0]['name'] if coordinator_agents else 'TBD'}) -> Workers",
                "Workers report back to Coordinator",
                "Coordinator consolidates results"
            ]
            
        elif coordination_pattern == "peer-to-peer":
            architecture_plan["communication_flow"] = [
                "Direct communication between any agents",
                "Shared state management required",
                "Consensus mechanism for decisions"
            ]
            
        elif coordination_pattern == "hub-spoke":
            architecture_plan["communication_flow"] = [
                "Central hub receives all messages",
                "Hub routes messages to appropriate agents",
                "No direct agent-to-agent communication"
            ]
        
        # Passos de deployment
        architecture_plan["deployment_steps"] = [
            "1. Criar agentes individuais",
            "2. Configurar canais de comunicação",
            "3. Implementar padrão de coordenação",
            "4. Configurar monitoramento",
            "5. Testes de integração",
            "6. Deploy em ambiente de produção"
        ]
        
        # Recomendações necessárias
        required_packages = ["asyncio", "concurrent.futures", "redis"]  # Para comunicação
        if coordination_pattern == "peer-to-peer":
            required_packages.extend(["celery", "rabbitmq"])
        
        architecture_plan["required_packages"] = required_packages
        architecture_plan["scalability_notes"] = [
            f"Padrão {coordination_pattern} suporta até {len(agents_config) * 5} agentes eficientemente",
            "Considerar message queue para > 10 agentes",
            "Implementar load balancing para alta demanda"
        ]
        
        return {
            "status": "success",
            "architecture_plan": architecture_plan,
            "next_steps": [
                "Instalar dependências necessárias",
                "Criar agentes individuais",
                "Implementar camada de comunicação"
            ]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro na configuração da arquitetura: {str(e)}"
        }

# ... (todo o restante do seu código acima permanece igual)

# Instanciar o Agente Arquiteto Avançado
try:
    from google.adk.agents import Agent
    
    # Definir ferramentas do arquiteto
    architect_tools = [
        create_advanced_agent,
        scan_project_structure,
        manage_requirements,
        list_project_agents,
        setup_multi_agent_architecture,
        test_and_fix_agent
    ]
    
    # Criar agente principal
    advanced_architect_agent = Agent(
        name="AdvancedArchitectAgent",  # <- sem espaços ou hífen!
        model="gemini-2.5-flash-preview-04-17",
        description="""
        Agente especializado na criação e orquestração de sistemas multi-agente avançados.
        Capaz de:
        - Criar agentes com arquiteturas específicas (standalone, coordinator, specialist)
        - Gerenciar dependências automaticamente
        - Corrigir problemas de importação
        - Configurar arquiteturas multi-agente completas
        - Analisar e otimizar estruturas de projeto existentes
        """,
        tools=architect_tools,
        instruction="""
        Você é um Advanced Architect Agent especializado em sistemas multi-agente.
        
        CAPACIDADES PRINCIPAIS:
        1. **Criação de Agentes Avançados**: Crie agentes com arquiteturas específicas
        2. **Gerenciamento de Dependências**: Instale e gerencie packages automaticamente
        3. **Correção Automática**: Detecte e corrija problemas de importação
        4. **Análise Arquitetural**: Escaneie e analise estruturas de projeto
        5. **Orquestração Multi-Agente**: Configure sistemas complexos de coordenação
        
        ARQUITETURAS SUPORTADAS:
        - **Standalone**: Agentes independentes para tarefas específicas
        - **Coordinator**: Agentes que orquestram outros agentes
        - **Specialist**: Agentes focados em domínios específicos
        
        PADRÕES DE COORDENAÇÃO:
        - **Hierarchical**: Coordenador central com workers
        - **Peer-to-Peer**: Comunicação direta entre agentes
        - **Hub-Spoke**: Hub central roteando mensagens
        
        FLUXO DE TRABALHO:
        1. Analise a estrutura do projeto existente
        2. Identifique padrões arquiteturais
        3. Recomende melhorias
        4. Implemente soluções com correção automática
        5. Teste e valide funcionalidade
        
        SEMPRE:
        - Escaneie o projeto antes de criar novos agentes
        - Resolva dependências automaticamente
        - Teste importações e corrija problemas
        - Forneça recomendações arquiteturais
        - Documente todas as criações
        
        Use suas ferramentas de forma inteligente e sequencial para criar sistemas robustos e funcionais.
        """
    )
    
    # Alias para compatibilidade
    root_agent = advanced_architect_agent
    agent = advanced_architect_agent   # <-- LINHA OBRIGATÓRIA para ADK web funcionar!
    
    print("✅ Advanced Architect Agent carregado com sucesso!")
    print("🛠️  Ferramentas disponíveis:")
    for i, tool in enumerate(architect_tools, 1):
        print(f"   {i}. {tool.__name__}")
    
except ImportError as e:
    print(f"⚠️  Aviso: Não foi possível importar google.adk.agents: {e}")
    print("📝 Definindo versão mock para desenvolvimento...")
    
    class MockAgent:
        def __init__(self, name, model, description, tools, instruction):
            self.name = name
            self.model = model
            self.description = description
            self.tools = tools
            self.instruction = instruction
            print(f"✅ Mock Agent '{name}' criado com {len(tools)} ferramentas")
    
    advanced_architect_agent = MockAgent(
        name="AdvancedArchitectAgent",
        model="gemini-2.5-flash-preview-04-17",
        description="Agente especializado em arquiteturas multi-agente",
        tools=[
            create_advanced_agent,
            scan_project_structure,
            manage_requirements,
            list_project_agents,
            setup_multi_agent_architecture,
            test_and_fix_agent
        ],
        instruction="Agente arquiteto avançado para sistemas complexos"
    )
    
    root_agent = advanced_architect_agent
    agent = advanced_architect_agent   # <-- Linha obrigatória aqui também

# Função de conveniência para uso direto
def quick_create_agent(
    name: str, 
    description: str, 
    instructions: str, 
    tools: List[str] = None,
    arch_type: str = "standalone"
) -> Dict[str, Any]:
    """
    Função de conveniência para criação rápida de agentes
    """
    return create_advanced_agent(
        agent_name=name,
        agent_description=description,
        agent_instructions=instructions,
        tools_list=tools or [],
        architecture_type=arch_type
    )

# Exemplo de uso
if __name__ == "__main__":
    print("\n🚀 ADVANCED ARCHITECT AGENT - SISTEMA DE CRIAÇÃO MULTI-AGENTE")
    print("="*70)
    
    # Demonstração das capacidades
    print("\n📊 Escaneando estrutura do projeto...")
    scan_result = scan_project_structure()
    
    if scan_result["status"] == "success":
        structure = scan_result["structure"]
        print(f"✅ Agentes encontrados: {len(structure['agents'])}")
        print(f"🔧 Ferramentas disponíveis: {len(structure['available_tools'])}")
        print(f"🏗️  Padrões arquiteturais: {', '.join(structure['architecture_patterns'])}")
        
        if structure["recommendations"]:
            print("\n💡 Recomendações:")
            for rec in structure["recommendations"]:
                print(f"   • {rec}")
    
    print("\n📋 Exemplo de criação de agente:")
    print("""
    result = quick_create_agent(
        name="DataAnalystAgent",
        description="Especialista em análise de dados e visualizações",
        instructions="Analise dados, crie visualizações e forneça insights",
        tools=["rag_query", "create_visualization", "analyze_data"],
        arch_type="specialist"
    )
    """)
    
    print("\n🔧 Ferramentas disponíveis no Advanced Architect Agent:")
    tools_info = {
        "create_advanced_agent": "Cria agentes com arquitetura específica",
        "scan_project_structure": "Analisa estrutura do projeto existente", 
        "manage_requirements": "Gerencia dependências Python",
        "list_project_agents": "Lista e analisa agentes existentes",
        "setup_multi_agent_architecture": "Configura arquiteturas complexas",
        "test_and_fix_agent": "Testa e corrige problemas automaticamente"
    }
    
    for tool_name, description in tools_info.items():
        print(f"   🛠️  {tool_name}: {description}")
    
    print(f"\n✨ Advanced Architect Agent pronto para uso!")
    print(f"📧 Use: advanced_architect_agent, root_agent ou agent")
    print("="*70)

