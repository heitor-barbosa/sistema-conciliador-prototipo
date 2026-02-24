# sistema-conciliador

1. Adicionar users.yaml na pasta config
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


2. Hasheando senha
   ```
   from streamlit_authenticator.utilities.hasher import Hasher

   senha_hash = Hasher.hash("1234")
   print(senha_hash)
   ```

3. Rodar no terminal
