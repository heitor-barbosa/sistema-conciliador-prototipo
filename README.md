# Sistema Conciliador – Protótipo

## Descrição

O Sistema Conciliador é um protótipo desenvolvido para realizar **conciliação bancária entre extratos bancários e arquivos de adquirentes** (operadoras de cartão).

A proposta do projeto foi criar um conciliador bancário simples, direto e funcional, capaz de comparar os lançamentos presentes no extrato bancário com os valores informados nos arquivos das adquirentes, identificando divergências como diferenças de valores, registros não encontrados, pagamentos pendentes ou inconsistências de data.

O objetivo foi desenvolver um **protótipo rápido, mas funcional**, validando na prática a lógica central de um sistema de conciliação bancária. A prioridade foi garantir que o fluxo principal de comparação funcionasse corretamente, mantendo o código organizado e preparado para evolução.

Embora seja um protótipo, o sistema foi estruturado com preocupação arquitetural, separação de responsabilidades e modelagem consistente, permitindo que possa evoluir facilmente para uma versão mais robusta e pronta para produção.

---

## Tecnologias Utilizadas
- Python
- Streamlit
- Git para controle de versão

---

## Funcionalidades (Features)

- Cadastro de registros
- Validação de dados de entrada
- Processamento de regras de conciliação
- Comparação automática entre bases de dados
- Identificação de divergências
- Persistência estruturada em banco relacional
- Tratamento de erros e exceções
- Estrutura modular preparada para expansão

---

## Processo de Desenvolvimento

O desenvolvimento foi dividido em etapas estruturadas para garantir organização e consistência.

### 1. Levantamento de Requisitos
- Identificação do problema de conciliação
- Definição das entradas e saídas do sistema
- Mapeamento das regras de comparação
- Definição dos cenários de inconsistência

### 2. Implementação
- Estruturação do projeto em camadas
- Separação entre regras de negócio e acesso a dados
- Implementação das validações
- Tratamento de exceções

### 3. Testes
- Testes manuais de fluxo completo
- Validação de cenários com dados inconsistentes
- Teste de entradas inválidas
- Verificação da consistência dos dados persistidos

---
<!--
## Como Melhorar

O projeto pode evoluir com as seguintes melhorias:

- Implementação de autenticação e autorização (JWT)
- Criação de testes automatizados (unitários e integração)
- Dashboard com métricas e indicadores
- Exportação de relatórios (PDF ou Excel)
- Containerização com Docker
- Deploy em ambiente cloud
- Implementação de logs estruturados
- Otimização de performance para grandes volumes de dados
- Monitoramento e observabilidade

---

## Considerações Finais

Este projeto demonstra capacidade de:

- Modelagem de banco de dados
- Estruturação de regras de negócio
- Organização arquitetural
- Aplicação de boas práticas
- Planejamento para escalabilidade

-->


## Como rodar

1. Adicionar users.yaml na pasta config.
   Estrutura:
```
credentials:
  usernames:
    heitor:
      role: admin
      first_name: Heitor
      last_name: Souza
      logged_in: False
      password: senha_hasheada 
  
    usuario_exemplo1:
      role: viewer
      first_name: usuario
      last_name: exemplo
      logged_in: False
      password: senha_hasheada
  
cookie:
  expiry_days: 1
  key: cookie_chave
  name: cookie_nome
```


2. Adicionar senha Hasheada
   ```
   from streamlit_authenticator.utilities.hasher import Hasher

   senha_hash = Hasher.hash("1234")
   print(senha_hash)
   ```

3. Rodar no terminal
   ```
   streamlit run main.py
   ```
