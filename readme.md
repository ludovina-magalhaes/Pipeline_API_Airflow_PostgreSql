
# Pipeline_API_Airflow_PostgreSql

Este repositório contém um pipeline orquestrado no **Airflow** que interage com uma API e persiste dados numa base de dados **PostgreSQL**.
Criação de um pipeline de dados que extrai informações de uma API, transforma os dados com Python e carrega em um banco de dados
Para isso neste projeto vou usar Random User Generator, uma API gratuita e de código aberto para gerar dados aleatórios de usuários. Este tipo de API é ótima para treinar e ver a vulnerabilidade e usabilidade dos dados sem expor dados reais.
A ideia surgiu da necessidade de estruturar dados provenientes de uma API de forma organizada e confiável, garantindo consistência e integridade para futuras análises.
Arquitetura: 
<img width="1605" height="688" alt="image" src="https://github.com/user-attachments/assets/d9c3f0d3-fbf9-4e38-86a8-8d4559a0fc34" />

---

## 📂 Estrutura do Projeto

| Pasta / Ficheiro | Descrição |
|------------------|-----------|
| `dags/` | DAGs do Airflow com tasks definidas para chamar a API e processar dados |
| `plugins/` | Plugins personalizados do Airflow (se existirem) |
| `docker-compose.yaml` | Definição dos serviços Docker: Airflow, PostgreSQL, webserver, scheduler etc. |
| `dockerfile` | Dockerfile para construir a imagem personalizada, se aplicável |
| `requirements.txt` | Dependências Python necessárias para o pipeline |
| `logs/` | Diretório de logs do Airflow (não versionado) |
| `.gitignore` | Arquivos e pastas ignorados no Git |
| `readme.md` | Este ficheiro de documentação |
| `.env` | (não commitado) Variáveis de ambiente sensíveis |

---

## 🛠️ Requisitos

- Docker & Docker Compose  
- Python 3.x  
- Ter configurado variável(s) de ambiente (ex: credenciais API, credenciais BD) via `.env`  
- Base de dados PostgreSQL (local ou no Docker)  

---
O pipeline foi composto por:
•	Coleta automática de dados: utilização da API Random User para obter informação simulada de utilizadores.
•	Armazenamento inicial em base de dados relacional: ingestão dos dados brutos na base PostgreSQL, especificamente na instância criada para o projeto (api_random_user).
•	Normalização e modelagem relacional: criação de tabelas normalizadas diretamente em SQL, seguindo uma abordagem de Data Warehouse, com dimensões (dim_user, dim_address, dim_login, dim_id, dim_picture) e uma tabela fato (fact_user). Este processo garantiu consistência, eliminação de duplicados e integridade referencial.
•	Execução e validação em ambiente de administração: utilização do pgAdmin para implementar queries de transformação, tratar tipos de dados (date, numeric, timestamp) e validar a qualidade da carga.
Este projeto ilustra um cenário prático de ETL com foco em Data Engineering, no qual dados de origem semi-estruturada são organizados em modelo relacional, servindo como base sólida para análises futuras e construção de dashboards.

O ficheiro requirements.txt é fundamental em qualquer projeto Python. Ele define todas as bibliotecas necessárias para que o projeto funcione corretamente. Com ele, qualquer pessoa pode preparar o ambiente de forma rápida e consistente. Este requirements.txt mostra que o projeto combina orquestração de dados (Airflow), armazenamento e consultas em PostgreSQL e modelos de inteligência artificial da Hugging Face.
<img width="1600" height="193" alt="image" src="https://github.com/user-attachments/assets/fffe670a-c9fd-457b-8131-f31827c58d75" />

O Dockerfile é um ficheiro usado para personalizar o ambiente do Airflow dentro do Docker. Ele é útil quando os teus DAGs precisam de bibliotecas Python extras que não vêm instaladas na imagem oficial do Airflow. A função dele é manter o ambiente isolado dentro do Docker.
Um Dockerfile simples tem apenas 3 instruções:
<img width="1618" height="234" alt="image" src="https://github.com/user-attachments/assets/562da6d9-0921-4c95-ad94-1185543c1fab" />

Assim, quando executas docker compose up, o Docker constrói a imagem já com todas as dependências e inicia o Airflow preparado para as DAGs. O Dockerfile é o passo que transforma o Airflow "padrão" no Airflow "à nossa medida", incluindo todas as bibliotecas extra que os teus projetos precisam.
<img width="1610" height="558" alt="image" src="https://github.com/user-attachments/assets/d283d6b5-b858-41d3-a846-35f15e6d6837" />

O código apresentado define um pipeline ETL (Extract, Transform, Load) utilizando o Apache Airflow como orquestrador de tarefas. Ele tem como objetivo consumir dados da API pública Random User, transformá-los num formato estruturado e carregá-los para uma tabela no PostgreSQL.
O pipeline está organizado em três fases principais:
1.	Extração (Extract)
A primeira tarefa, extract_random_user_data, realiza uma requisição à API https://randomuser.me/api/, pedindo 100 utilizadores aleatórios. Os dados retornados em formato JSON são enviados para o mecanismo de comunicação do Airflow (XCom) para que possam ser utilizados pelas próximas etapas.
2.	Transformação (Transform)
A segunda tarefa, transform_random_user_data, lê os dados brutos da etapa anterior e reorganiza-os num dicionário padronizado, facilitando a carga na base de dados.
o	São extraídos atributos como nome, email, morada, localização geográfica, credenciais de login, entre outros.
o	Converte-se o campo postcode para string (garantindo consistência).
o	É adicionado um campo adicional chamado etl_timestamp, que regista o momento exato em que a transformação ocorreu, útil para auditoria e rastreabilidade.
3.	Carga (Load)
A terceira tarefa, load_random_user_postgres, conecta-se a uma instância PostgreSQL utilizando a biblioteca psycopg2.
o	Se a tabela random_user_data ainda não existir, ela é criada com todas as colunas necessárias.
o	Cada registo é inserido na base de dados. Durante este processo, os campos de data são convertidos para o tipo TIMESTAMP do PostgreSQL.
o	Ao final, a transação é confirmada com commit() e a conexão é encerrada.
Estrutura da DAG
A DAG chama-se random_user_pipeline e tem as seguintes configurações:
•	Execução diária (@daily).
•	Início a 1 de janeiro de 2025.
•	Reexecução automática em caso de falha (1 retry).
•	Ordem de execução:
task1_get_random_user → task2_clean_data → task3_insert_postgres.
Conclusão
Este pipeline exemplifica bem a utilização do Airflow para orquestrar processos de ETL:
•	A extração automatiza a coleta de dados de uma API pública.
•	A transformação garante consistência e qualidade nos dados antes de carregá-los.
•	A carga integra os dados num repositório relacional (PostgreSQL), possibilitando análises posteriores.

Execução do Docker com os ficheiros todos já feitos :
Verificar se o Docker está a correr
docker ps
Mostra os containers em execução.
Subir os serviços (iniciar Airflow + Postgres + Redis + etc.)
docker compose up -d
Parar os serviços
docker compose down
Para e remove todos os containers definidos no docker-compose.yaml.
Reconstruir a imagem (se alteraste o Dockerfile ou requirements.txt)
docker compose build
E depois voltas a subir:
docker compose up -d

Resumindo o fluxo típico para trabalhares com o Airflow no Docker:
1.	docker compose build (se tiveres Dockerfile personalizado).
2.	docker compose up -d (sobe os serviços).
3.	Abrir o Airflow no navegador: http://localhost:8080.
4.	docker compose down (quando quiseres parar).


1. O que é o Airflow
O Apache Airflow é uma ferramenta usada para orquestração de workflows, baseada em DAGs (Directed Acyclic Graphs).
•	DAGs: representam fluxos de tarefas que seguem uma ordem específica. Não há ciclos, ou seja, uma tarefa não pode voltar para a anterior.
•	Pipelines ETL: esta estrutura torna o Airflow ideal para processos de Extração, Transformação e Carga (ETL), seguindo a sequência Extrair → Transformar → Carregar.
2. Arquitetura do Airflow com Docker
A forma mais simples de instalar e executar o Airflow é com Docker e Docker Compose. A arquitetura típica inclui:
<img width="886" height="361" alt="image" src="https://github.com/user-attachments/assets/14ec6fd0-876f-4dad-9c7a-7314638449a7" />

3. Funcionamento de um DAG no Airflow
Os DAGs são definidos em ficheiros Python.
Exemplo de um pipeline ETL que extrai dados da API e carrega para uma base Postgres:
1.	Extract Task - obtém dados (ex: 50 modelos mais recentes), envia os brutos para o XCOM.
2.	Transform Task - recebe dados do XCOM, remove duplicados, trata nulos, normaliza colunas, envia dados limpos de volta ao XCOM.
3.	Load Task - lê dados transformados do XCOM e insere no Postgres através de um Postgres, com conexão configurada no Airflow UI.
•	XCOM: mecanismo de troca de dados entre tarefas.
•	PythonOperator: define tarefas em Python dentro do DAG.
•	Conexões (Admin > Connections): configuram credenciais e parâmetros para bases externas (ex: host do Postgres no Docker, nome da base pg_db).
4. Gestão de Dependências
Para incluir bibliotecas necessárias no ambiente Airflow (ex: psycopg2, huggingface):
•	requirements.txt: lista de pacotes Python.
•	Dockerfile: copia o requirements.txt e instala dependências com pip.
•	docker-compose.yaml: ajustado para usar a build personalizada, garantindo que a imagem do Airflow tenha todas as dependências.
<img width="886" height="339" alt="image" src="https://github.com/user-attachments/assets/d8f8f246-d272-4163-983a-25a3c9386874" />

PostgreSQL e PG Admin no Pipeline Airflow
O PostgreSQL (Psql/Postgress) e o PG Admin são componentes essenciais para hospedar e gerir a base de dados utilizada pelo Apache Airflow em pipelines ETL.
PostgreSQL (Psql/Postgress)
•	Função no ETL: Serve como banco de dados backend e destino final (Load) dos dados. Exemplo: extrair dados de modelos de IA, transformar e carregar no Psql.
•	Hospedagem: Alojado no ambiente Docker e gerido pelo Docker Compose.
•	Conexão Airflow: É necessário configurar a conexão no Airflow UI (Admin > Connections). O Host deve ser Postgress (com P maiúsculo) para que o Docker encontre o serviço automaticamente, mesmo que o IP mude.
•	Base de Dados: Criar uma base específica, ex: PG_DB.
•	Credenciais Padrão: Username: airflow, 
•	Password: airflow,
•	 Porta: 5432.
PG Admin
•	Função Principal: Interface para explorar, gerir e consultar os dados no PostgreSQL. Permite verificar a inserção correta dos dados, e para confirmar se todos os modelos foram carregados.
•	Hospedagem em Docker: Serviço incluído manualmente no docker-compose.yaml, normalmente abaixo do Postgres.
•	Configuração: Definir credenciais e porta no Docker Compose:
o	Email: admin@admin.com
o	Password: root
o	Porta: 5050
•	Servidor PG Admin: Após aceder à interface (localhost:5050), adicionar um novo servidor:
o	Nome do Host: postgress
o	Credenciais: Username airflow, Password airflow
<img width="489" height="797" alt="image" src="https://github.com/user-attachments/assets/86772e40-aff1-4a1c-8c90-0eafb97de5a8" />


## 🔧 Como usar

1. Clona este repositório:
   ```bash
   git clone https://github.com/ludovina-magalhaes/Pipeline_API_Airflow_PostgreSql.git
   cd Pipeline_API_Airflow_PostgreSql


Criar ficheiro .env com configurações necessárias, por exemplo:
POSTGRES_USER=usuario
POSTGRES_PASSWORD=senha
POSTGRES_DB=nome_db
API_URL=https://exemplo.com/api


 Testes & Debugging
Ver logs do Airflow para verificar execução das tasks
Confirmar ligação à base de dados PostgreSQL
Se houver falha de API: examinar endpoint, headers e dados retornados

Licença
Este projeto está sob a licença MIT (ou outra que escolheres) — podes modificar para a licença que preferires.

