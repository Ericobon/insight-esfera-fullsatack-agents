# Vertex AI RAG Agent with ADK

🧠 InsightEsfera - Equipe de Agentes de IA
Repositório: https://github.com/Ericobon/insight-esfera-fullsatack-agents

1. Visão Geral do Projeto
Este repositório materializa a visão da InsightEsfera de transformar desafios de negócios em oportunidades de crescimento através de soluções data-driven e automação inteligente. Desenvolvemos e implementamos um time colaborativo de agentes de Inteligência Artificial no Google Cloud Platform (GCP), focado em otimizar a entrega de valor aos nossos clientes.

Nosso time de agentes é projetado para atuar como uma equipe de consultoria de dados e IA altamente eficiente, onde cada agente possui um papel bem definido, comunica-se de forma inteligente e contribui para a resolução de tarefas complexas, sob a orquestração de um Agente Líder Técnico.

Objetivos Chave:

Automação Inteligente: Automatizar e otimizar a coleta, engenharia, análise, modelagem e integração de dados.
Decisões Data-Driven: Fornecer insights acionáveis e baseados em evidências.
Escalabilidade e Custo-Benefício: Utilizar a infraestrutura serverless do GCP para garantir flexibilidade e otimização de recursos (incluindo o consumo de tokens de LLM).
Colaboração Eficaz: Estabelecer protocolos de comunicação e compartilhamento de conhecimento entre agentes.
2. Componentes e Serviços do Google Cloud Platform (GCP)
2.1. Ambiente de Desenvolvimento e Orquestração
Serviço: Vertex AI Workbench (Managed Notebooks)
Nome da Instância: ie-agents
Proprietário (Conta de Serviço Principal): 487071349303-compute@developer.gserviceaccount.com
Região: us-central1 (Iowa) - Garante proximidade e latência otimizada para os serviços do Vertex AI.
Tipo de Máquina: e2-standard-4 (4 vCPUs, 16 GB RAM) - Balanceado para desenvolvimento e orquestração sem GPU (o LLM é externo).
Uso: Ambiente principal para desenvolvimento, depuração e execução inicial do Agente Tech Lead e das funções-ferramentas.
2.2. Modelos de Linguagem (LLMs)
Utilizamos modelos de ponta do Vertex AI para o raciocínio e geração de conteúdo dos nossos agentes.

Para Raciocínio Complexo e Orquestração (Agente Tech Lead):
Modelo: Claude 3 Opus (da Anthropic via Vertex AI Model Garden) - Excelente para compreensão complexa, raciocínio de múltiplos passos e planejamento.
Uso: Será o "cérebro" principal do Agente Tech Lead para decompor tarefas, delegar e sintetizar.
Para Geração Aumentada por Recuperação (Agente RAG):
Modelo: Gemini 2.5 Flash Preview 04-17 (do Google via Vertex AI) - Otimizado para alta performance e menor latência em operações RAG.
Uso: Pelo RagAgent para buscas e respostas baseadas em corpora de documentos.
Para Geração de Embeddings (Interno ao RAG Engine):
Modelo: publishers/google/models/text-embedding-005 (ou similar, gerenciado pelo Vertex AI RAG Engine).
Uso: Automaticamente pelo Vertex AI RAG Engine para criar as representações vetoriais dos documentos e consultas para a busca de similaridade.
2.3. Armazenamento de Dados e Memória Persistente
Serviço: Cloud Storage
Nome do Bucket: insightesfera-companies
Estrutura de Pastas:
insightesfera-companies/
├── companies/
│   ├── [NOME_CLIENTE_1]/  # Ex: "InsightEsfera" (para projetos internos), "ClienteXYZ"
│   │   ├── projects/
│   │   │   ├── [NOME_PROJETO_CLIENTE_1_A]/
│   │   │   │   ├── data/             # Dados brutos/processados específicos do projeto
│   │   │   │   └── reports/          # Relatórios gerados pelo agente
│   │   │   └── ...
│   │   └── memory/             # Memória de longo prazo específica do cliente
│   │       ├── client_context.json   # Dados de preferência, histórico, contatos
│   │       └── project_summary_latest.json # Resumo dos projetos do cliente
│   └── ...
├── agents/
│   ├── memory/                 # Memória de longo prazo dos próprios agentes
│   │   ├── tech_lead_knowledge.json  # Conhecimento do Tech Lead sobre fluxos e padrões
│   │   ├── data_engineer_skills.json # Conhecimento do Eng. Dados sobre fontes e formatos
│   │   └── ...
│   └── scripts/                # Templates de scripts ou snippets de código para agentes
│       ├── data_collection_templates.py
│       └── ml_model_templates.py
├── internal/                   # Dados internos da consultoria (templates de proposta, documentação interna)
│   └── templates/
│       └── ...
└── temp_github_ingest/         # **NOVO:** Pasta temporária para conteúdo clonado do GitHub antes da ingestão RAG.
Uso: Repositório centralizado para dados brutos, resultados, memória de longo prazo (LTM) de clientes/agentes e arquivos temporários.
2.4. Bases de Conhecimento RAG
Serviço: Vertex AI RAG Engine (anteriormente parte do Vertex AI Search)
Uso: Armazena os corpora (coleções de documentos) que são a base de conhecimento para a funcionalidade RAG. Os documentos são processados (chunking, embedding, indexação) automaticamente por este serviço.
Localização no Console: Vertex AI > RAG Engine.
2.5. Comunicação Externa e Serverless (Futura Escalabilidade)
Serviço (Futuro): Cloud Run ou Cloud Functions
Uso: Para hospedar o Agente Tech Lead em produção, permitindo que ele seja acionado por requisições HTTP (ex: de plataformas como Twilio para integração WhatsApp) e escale para zero instâncias quando inativo, otimizando custos.
Serviço (Integração WhatsApp - Futuro): Twilio ou Dialogflow CX
Uso: Gateway para comunicação via WhatsApp com o Agente Tech Lead.
3. Arquitetura e Fluxo de Trabalho do Time de Agentes
Nosso time de agentes segue uma arquitetura colaborativa e hierárquica, orquestrada pelo Agente Tech Lead.

3.1. Agente Tech Lead (Orquestrador Principal)
Papel: O Agente Líder Técnico é o maestro da equipe. Ele recebe as requisições, planeja a execução, delega tarefas aos agentes especializados e sintetiza os resultados. Possui uma visão holística e orientada a negócios.
LLM: Claude 3 Opus (via Vertex AI).
Fluxo de Interação:
Recebe uma requisição (ex: "Analise os dados de vendas do cliente X e identifique as principais tendências do último trimestre, incorporando também a documentação do novo produto Y que está no nosso GitHub privado").
Planejamento: Decompõe a requisição em subtarefas (ex: "Verificar/Criar corpus do Cliente X", "Adicionar documentação do produto Y ao corpus", "Coletar dados de vendas", "Analisar dados", "Sintetizar relatório").
Delegação: Chama as ferramentas dos agentes especializados apropriados para cada subtarefa.
Coordenação: Monitora o status das subtarefas, lida com erros e combina os resultados parciais.
Síntese: Utiliza o Claude Opus para gerar o relatório final ou a resposta completa, adicionando contexto e insights estratégicos.
Persistência: Salva o histórico da interação e os resultados importantes na memória de longo prazo (Cloud Storage).
3.2. Agentes Especializados (Sub-Agentes)
Cada agente especializado é uma função-ferramenta ou um módulo de código Python invocado pelo Agente Tech Lead, utilizando um LLM e ferramentas específicas para sua área.

Vertex AI RAG Agent (rag_agent - Este repositório):
Papel: Especialista em gerenciamento e consulta de bases de conhecimento documentais no Vertex AI RAG Engine.
LLM: Gemini 2.5 Flash (via Vertex AI) - Otimizado para RAG.
Ferramentas Expostas: rag_query, list_corpora, create_corpus, add_data (com suporte a GitHub), get_corpus_info, delete_corpus, delete_document.
Comunicação: Recebe instruções do Agente Tech Lead (via chamadas Python para suas funções-ferramentas) e retorna resultados estruturados.
Agente Engenheiro de Dados:
Papel: Responsável pela coleta, limpeza, transformação e validação de dados de diversas fontes (BigQuery, Cloud Storage, APIs externas, bancos de dados).
LLM: Gemini 1.5 Pro ou Claude 3 Sonnet (via Vertex AI) - Bom para lógica de transformação e validação de dados.
Ferramentas Expostas: fetch_from_bigquery(query), transform_data(data, schema), validate_data(data, rules), load_to_gcs(data, path).
Comunicação: Recebe requisições de coleta/transformação do Tech Lead e entrega dados limpos/transformados (salvos em GCS) ou confirmações.
Agente Cientista de Dados:
Papel: Focado em análise de dados, identificação de padrões, construção/avaliação de modelos preditivos e geração de insights acionáveis.
LLM: Claude 3 Opus ou Gemini 1.5 Pro (via Vertex AI) - Para raciocínio analítico avançado.
Ferramentas Expostas: analyze_trends(data), run_ml_model(model_id, features), generate_insights(analysis_results), create_dashboard_spec(insights).
Comunicação: Recebe dados do Tech Lead (geralmente via GCS), realiza análises e retorna insights ou especificações de modelos.
Agente Desenvolvedor Full-stack:
Papel: Gera, refatora e integra código para APIs, scripts de automação e interfaces simples, garantindo a interoperabilidade dos componentes.
LLM: Gemini 1.5 Pro (via Vertex AI) - Para geração de código e entendimento de estruturas de software.
Ferramentas Expostas: generate_api_code(spec), create_automation_script(task_description), integrate_api(api1_spec, api2_spec).
Comunicação: Recebe especificações do Tech Lead e retorna snippets de código ou confirmações de integração.
3.3. Papel Colaborativo Detalhado
A colaboração ocorre através de um loop contínuo de delegação e feedback, mediado pelo Agente Tech Lead:

Delegação Inteligente: O Tech Lead, usando seu LLM (Claude Opus), analisa a requisição e "decide" qual agente especializado e qual de suas ferramentas são mais adequados para a próxima subtarefa.
Chamada de Ferramenta (Tool Calling): O Tech Lead invoca a função Python que representa a ferramenta do agente especializado (ex: rag_agent_instance.add_data()).
Execução da Subtarefa: O agente especializado (o código Python por trás da ferramenta) executa sua lógica, que pode envolver chamadas a serviços do GCP (Vertex AI Search, BigQuery, Cloud Storage) ou a outros LLMs específicos (como o Gemini Flash para RAG).
Compartilhamento de Resultados: Os resultados das subtarefas são retornados ao Tech Lead (via retorno da função Python). Para grandes volumes de dados, os resultados são salvos em Cloud Storage, e apenas a referência (URL do GCS) é passada.
Ciclo de Feedback: O Tech Lead avalia o resultado. Se for insuficiente, ambíguo ou necessitar de correção, ele pode solicitar refinamentos ou chamar outro agente para uma etapa diferente.
Memória Compartilhada: A memória de longo prazo no Cloud Storage (insightesfera-companies/) serve como um "cérebro" compartilhado, onde os agentes podem persistir e recuperar informações relevantes para o projeto atual ou histórico de clientes.
4. Detalhes de Implementação e Ferramentas
4.1. Permissões de IAM (Identity and Access Management)
A Conta de Serviço principal da sua instância do Vertex AI Workbench (487071349303-compute@developer.gserviceaccount.com no projeto silent-text-458716-c9) necessita das seguintes permissões para operar todos os agentes e suas ferramentas:

roles/aiplatform.user: Essencial para interagir com a API Vertex AI (incluindo LLMs como Claude Opus, Gemini, e o Vertex AI Search/RAG Engine).
roles/storage.admin: Para gerenciar (ler, gravar, deletar) todos os objetos no bucket insightesfera-companies. (Para maior granularidade em produção, considere roles/storage.objectAdmin e roles/storage.objectViewer para pastas específicas).
roles/bigquery.dataEditor: Se os agentes precisarem escrever dados no BigQuery.
roles/bigquery.dataViewer: Se os agentes precisarem ler dados do BigQuery.
roles/bigquery.jobUser: Para executar jobs de BigQuery.
roles/iam.serviceAccountUser: Necessário se o Agente Tech Lead for operar como outras contas de serviço mais granulares para sub-agentes (não estritamente necessário para MVP).
roles/logging.logWriter: Para garantir que os logs da aplicação sejam enviados para o Cloud Logging.
roles/sourcerepo.reader: Para ler repositórios no Cloud Source Repositories (se você optar por espelhar o GitHub para lá).
4.2. Funções-Ferramentas (Python)
As "mãos" e "olhos" dos agentes. Implementadas em Python, são invocadas pelo LLM do agente supervisor (ou o próprio agente, se for autônomo).

rag_agent/tools/add_data.py: Implementado! Inclui lógica para clonar repositórios GitHub para GCS e ingerir via Vertex AI RAG Engine.
rag_agent/tools/rag_query.py: Interage com o Vertex AI RAG Engine para consultas.
rag_agent/tools/create_corpus.py, list_corpora.py, get_corpus_info.py, delete_corpus.py, delete_document.py: Gerenciam os corpora no Vertex AI RAG Engine.
Novas Ferramentas para outros Agentes (futuro):
Engenheiro de Dados: fetch_from_bigquery, clean_and_transform_data, upload_to_gcs.
Cientista de Dados: run_descriptive_analysis, execute_prediction_model, generate_data_insights.
Dev Full-stack: generate_api_spec, create_boilerplate_code, perform_api_call.
4.3. Estratégias de Memória e RAG (Boas Práticas e Otimização de Custos)
A implementação de memória eficiente e RAG é crucial para a inteligência e custo-benefício dos agentes.

Memória de Curto Prazo (STM) - Gerenciamento de Janela de Contexto:
Técnica: Mantém as últimas N interações (mensagens/respostas) na memória RAM do Agente Tech Lead.
Otimização de Custos: Usamos LLMs com grandes janelas de contexto (Claude Opus), mas é vital monitorar o tamanho do prompt. Para conversas muito longas, implemente:
Resumização: O próprio LLM pode ser instruído a periodicamente resumir partes mais antigas da conversa, compactando o contexto e reduzindo o consumo de tokens.
Sliding Window: Manter apenas as X mensagens mais recentes.
Memória de Longo Prazo (LTM) - RAG com Vertex AI RAG Engine:
Técnica: Documentos de conhecimento (clientes, projetos, internos) são armazenados no Cloud Storage e indexados no Vertex AI RAG Engine.
Processo:
Ingestão Otimizada: Documentos (incluindo de GitHub) são divididos em chunks (pedacinhos de texto) e convertidos em embeddings pelo Vertex AI RAG Engine.
Busca de Relevância (RAG): Quando uma pergunta surge, ela é convertida em um embedding, e o Vertex AI RAG Engine encontra os chunks mais semanticamente relevantes na LTM.
Aumento do Prompt: Apenas os chunks mais relevantes são adicionados ao prompt enviado ao LLM.
Otimização de Custos de Tokens: O RAG é a técnica principal para reduzir o volume de tokens enviado ao LLM, pois evita que o LLM precise "ler" toda a base de conhecimento a cada requisição. Você paga apenas pelos tokens do prompt mais os tokens dos chunks relevantes recuperados.
Escolha do Embedding Model: O Vertex AI RAG Engine gerencia o modelo de embedding (text-embedding-005 ou similar), que é otimizado para custo e precisão.
4.4. Monitoramento, Rastreabilidade e Controle de Custos
Para cada componente e cada interação:

Cloud Logging: Logs detalhados de todas as ações dos agentes (início/fim de tarefa, chamadas de ferramentas, erros, interações com LLMs) para depuração e rastreabilidade do fluxo de trabalho.
Cloud Monitoring:
Métricas de Plataforma: CPU, RAM (Workbench/Cloud Run), requisições, latência (Cloud Run, Vertex AI Search).
Métricas Customizadas: Número de tarefas concluídas/falhas por agente, latência média por tipo de tarefa, contagem de tokens (entrada/saída) por chamada de LLM (crucial para custo), volume de dados adicionados ao RAG Engine.
Alertas: Notificações proativas sobre erros, alto consumo de recursos ou estouro de orçamentos.
Cloud Trace: Visualização do caminho completo de uma requisição (trace) através de múltiplos agentes e serviços, essencial para identificar gargalos de latência. Instrumentar o código com OpenTelemetry SDK.
Cloud Billing: Monitoramento regular dos relatórios de custo, filtrando por Vertex AI (LLMs, RAG Engine), Cloud Storage e Compute Engine (Workbench). Configurar orçamentos com alertas para controlar gastos.
5. Estrutura de Código e Versionamento (GitHub)
Todo o código-fonte, prompts e scripts auxiliares são versionados no GitHub, garantindo colaboração e rastreabilidade.

Repositório: https://github.com/Ericobon/insight-esfera-fullsatack-agents

Estrutura de Pastas:

insight-esfera-fullsatack-agents/
├── docs/                             # Documentação do projeto (arquitetura, guias de setup)
├── agents/                           # Código dos agentes
│   ├── rag_agent/                    # Implementação do Vertex AI RAG Agent
│   │   ├── agent.py                  # Definição do RagAgent (com o Instruction/Prompt)
│   │   ├── prompts/                  # Arquivos de prompts/persona específicos do RagAgent
│   │   │   └── rag_agent_persona.txt
│   │   ├── tools/                    # Implementação das ferramentas do RagAgent
│   │   │   ├── add_data.py           # **ATUALIZADO (com lógica GitHub)**
│   │   │   ├── create_corpus.py
│   │   │   ├── delete_corpus.py
│   │   │   ├── delete_document.py
│   │   │   ├── get_corpus_info.py
│   │   │   ├── list_corpora.py
│   │   │   └── rag_query.py
│   │   └── config.py                 # Configurações do RagAgent (chunk size, etc.)
│   ├── tech_lead_agent/              # **NOVO:** Implementação do Agente Tech Lead
│   │   ├── agent.py                  # Definição do TechLeadAgent (com o Instruction/Prompt)
│   │   ├── prompts/                  # Arquivos de prompts/persona específicos do TechLeadAgent
│   │   │   └── tech_lead_persona.txt
│   │   └── tools/                    # Ferramentas que o TechLeadAgent usa (incluindo chamar o RagAgent)
│   │       ├── query_knowledge_base.py # Exemplo: Ferramenta que chama o RagAgent
│   │       └── ... (outras ferramentas para BigQuery, etc.)
│   ├── data_engineer_agent/          # **PRÓXIMO PASSO:** Futuro Agente Engenheiro de Dados
│   │   └── ...
│   ├── data_scientist_agent/         # **PRÓXIMO PASSO:** Futuro Agente Cientista de Dados
│   │   └── ...
│   └── dev_fullstack_agent/          # **PRÓXIMO PASSO:** Futuro Agente Dev Full-stack
│       └── ...
├── notebooks/                        # Notebooks Jupyter para desenvolvimento e experimentação
│   └── 01_adk_rag_agent_test.ipynb
├── config/                           # Arquivos de configuração globais (se houver)
├── scripts/                          # Scripts de deploy, utilitários
├── .env                              # **CRÍTICO:** Variáveis de ambiente LOCALMENTE (ADICIONADO AO .gitignore)
├── .gitignore                        # Para ignorar arquivos sensíveis e temporários
├── README.md                         # Este arquivo
└── requirements.txt                  # Dependências Python (atualizado com `GitPython`)
Versionamento por Agentes de IA:
A contribuição dos agentes de IA ao versionamento será de natureza colaborativa:

Geração de Artefatos: Agentes (como o Dev Full-stack) podem gerar trechos de código ou especificações que, após revisão humana, podem ser comitados.
Otimização de Prompts: Insights de agentes sobre a eficácia dos prompts podem levar a melhorias nos arquivos agents/prompts/, que são então versionados.
Relatórios e Análises: Relatórios ou sumarizações gerados pelos agentes podem ser salvos no Cloud Storage e seus metadados versionados, com links nos relatórios gerados.
6. Próximos Passos Cruciais para a Integração Completa
Agora que o RagAgent está funcionando e integrado ao GitHub, o foco é construir o restante do time.

6.1. Configuração do TechLeadAgent e Orquestração
Definição do TechLeadAgent: Crie o arquivo agents/tech_lead_agent/agent.py definindo o Agent (com o Claude 3 Opus) e seu instruction (prompt).
Criação das Ferramentas do Tech Lead:
Crie agents/tech_lead_agent/tools/query_knowledge_base.py (e outras ferramentas, se necessário). Esta ferramenta chamará as funções do RagAgent (ex: rag_agent_instance.rag_query()).
O TechLeadAgent usará a instância do RagAgent como uma de suas ferramentas.
Configuração do root_agent: No seu ponto de entrada principal (provavelmente agent.py na raiz do adk-rag-agent ou um novo main.py), configure o TechLeadAgent como o root_agent que será exposto pela interface web adk web.
6.2. Desenvolvimento dos Agentes Especializados (Engenheiro de Dados, Cientista de Dados, Dev Full-stack)
Para cada papel, defina um novo Agent no ADK (em suas respectivas pastas, como agents/data_engineer_agent/agent.py).
Escolha um LLM adequado (Gemini 1.5 Pro/Flash, Claude 3 Sonnet) para a tarefa.
Defina as ferramentas específicas para suas habilidades (ex: query_bigquery, run_analysis, generate_api_spec).
O Agente Tech Lead será o responsável por chamar esses agentes especializados através de suas ferramentas, passando o contexto e os dados necessários.
6.3. Otimização e Refinamento
Monitoramento Ativo: Utilize Cloud Logging, Monitoring e Trace para acompanhar o desempenho, latência e custos de todas as interações entre os agentes. Isso é fundamental para identificar gargalos e otimizações.
Teste de Ponta a Ponta: Crie cenários de teste abrangentes que envolvam a colaboração de múltiplos agentes para uma tarefa complexa.
Gestão de Erros: Implemente um tratamento de erros robusto em todas as ferramentas e na lógica de orquestração do Tech Lead.
Segurança (Produção): Migre o GITHUB_PERSONAL_ACCESS_TOKEN para o Secret Manager do GCP e configure a injeção via variáveis de ambiente para serviços como Cloud Run.
Escalabilidade (Produção): Ao mover do Vertex AI Workbench, migre o Agente Tech Lead (e talvez os outros agentes) para serviços como Cloud Run para se beneficiar da escalabilidade automática e do modelo de custo pay-per-use.
