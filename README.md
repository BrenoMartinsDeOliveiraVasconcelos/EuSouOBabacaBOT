# 1 Descrição
Isso é um bot simples que comenta em todo post da comunidade do reddit EuSouOBabaca e então avalia cada post conforme o nível de babaquice de acordo com o veredito dos membros.</br>
Para os votos contarem, deve ser feito um comentário com a primeira palavra sendo uma das seguintes siglas:
</br>
</br>
* NEOB: Não é o babaca
* EOB: É o babaca
* NGM: Ninguém é o babaca
* TEOB: Todo mundo é o babaca
* INFO: Falta informação.
# 2 Dependências necessárias
* python 3.7 ou superior
* praw
# 3 Preparações para rodar </br>
## 3.1 Configurando o bot</br>
Primeiro, vamos instalar as dependências</br>
* Insatle a linguagem de programação Python (confira como instalar para seu sistema operacion</br>
* Abra o prompt de comando do seu sistema e digite "python3 -m pip install praw"</br>
* Baixe os arquivos do BOT na pasta que desejar</br>
* Na pasta, crie um arquivo chamado "login" (sem extensão) e outro chamado "log" (sem extensão)</br>
## 3.2 Criando uma aplicação no Reddit</br>
Agora devemos criar uma aplicação na sua conta Reddit para poder executar o bot.</br>
* Entre em https://www.reddit.com e logue sua conta</br>
* Vá em https://www.reddit.com/prefs/apps e, em baixo clique em "create an app"</br>
* Digite o nome desejado no campo "name" e, selecione "script"</br>
* No campo "description" descreva o seu bot</br>
* em "about url" e "redirect url" digite qualquer link</br>
* Anote os códigos "secret" e "personal use script"</br>
## 3.3 Configurando o login do bot</br>
Agora vamos escrever as configurações de login</br>
* Vá na pasta que você baixou os aarquivos e abra o arquivo "login" num editor de texto qualquer</br>
* Escreva isso no arquivo: `{
    "clientid": "PERSONAL",
    "clientsecret": "SECRET",
    "username": "USERNME",
    "password": "SENHA"
}`</br>
* Substitua as palavras em capslock pelos cpódigos pedidos</br>
## 3.4 Rodando o bot</br>
Por fim, vamos rodar o bot.</br>
* Abra o prompt de comando do seu respectivo sistema operacional na pasta onde está os arquivos</br>
* Digite: python3 main.py</br>