# Sistema Conciliador – Protótipo

## Descrição

Esse é um protótipo de sistema conciliador desenvolvido para realizar **conciliação bancária entre extratos bancários e relatórios de adquirentes** (operadoras de cartão).

A proposta do projeto foi criar um conciliador bancário simples, mas direto e funcional: o sistema recebe upload de extratos bancários e relatórios de pagamentos, cruza esses dados, e retorna uma conciliação bancária, identificando divergências, pendências e inconsistências de valores, pagamentos e transações.

Unifica dados de diferentes fontes em um único fluxo de processamento, transformando em informações claras e permitindo interpretar corretamente cada caso. Além disso, oferece geração de um relatório objetivo e apresentável, o que facilita ainda mais a análise.

---

## Tecnologias Utilizadas
- Python
- Streamlit
- Git para controle de versão

---

## Funcionalidades (Features)

- Upload de extratos e relatórios de pagamentos
- Validação de dados de entrada
- Processamento de regras de conciliação
- Comparação automática entre arquivos
- Identificação de divergências
- Persistência estruturada em arquivos
- Tratamento de erros e exceções

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

1. Editar e preencher users.yaml na pasta config.
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


2. Adicionar senha Hasheada ao arquivo 'users.yaml'
   ```
   from streamlit_authenticator.utilities.hasher import Hasher

   senha_hash = Hasher.hash("1234")
   print(senha_hash)
   ```

3. Rodar no terminal
   ```
   streamlit run main.py
   ```


## Demonstração do Sistema
https://github.com/user-attachments/assets/09cd806d-4569-4c89-8e31-8d0666a3ed09

https://github.com/user-attachments/assets/1d9342bf-a0f2-4748-bb5c-3fc58d2a3e3b




   
