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
</br>
# 2 Dependências necessárias
* python 3.7 ou superior
* praw
</br>
# 3 Preparações para rodar
## 3.1 Configurando o bot
Primeiro, vamos instalar as dependências
* Insatle a linguagem de programação Python (confira como instalar para seu sistema operacional)
* Abra o prompt de comando do seu sistema e digite "python3 -m pip install praw"
* Baixe os arquivos do BOT na pasta que desejar
* Na pasta, crie um arquivo chamado "login" (sem extensão)
## 3.2 Criando uma aplicação no Reddit
Agora devemos criar uma aplicação na sua conta Reddit para poder executar o bot.
* Entre em https://www.reddit.com e logue sua conta
* Vá em https://www.reddit.com/prefs/apps e, em baixo clique em "create an app"
* Digite o nome desejado no campo "name" e, selecione "script"
* No campo "description" descreva o seu bot
* em "about url" e "redirect url" digite qualquer link
* Anote os códigos "secret" e "personal use script"
## 3.3 Configurando o login do bot
Agora vamos escrever as configurações de login
* Vá na pasta que você baixou os aarquivos e abra o arquivo "login" num editor de texto qualquer
* Escreva isso no arquivo: `{
    "clientid": "PERSONAL",
    "clientsecret": "SECRET",
    "username": "USERNME",
    "password": "SENHA"
}`
* Substitua as palavras em capslock pelos cpódigos pedidos
## 3.4 Rodando o bot
Por fim, vamos rodar o bot.
* Abra o prompt de comando do seu respectivo sistema operacional na pasta onde está os arquivos
* Digite: python3 main.py