import praw
import time
import datetime
import json

login = json.load(open("login"))

reddit = praw.Reddit(
    user_agent='<Linux>:<reddit-bot>:<v1.0> (by /u/JakeWisconsin)',
    client_id=login["clientid"],
    client_secret=login["clientsecret"],
    username=login["username"],
    password=login["password"]
)

# Post a comment to every new reddit submission in r/EuSOuOBabaca
sublist = open('idlist', 'r').readlines()
botxt = """## VOTE SE O OP É UM BABACA COMENTANDO NO POST COM AS SEGUINTES SIGLAS COMO A PRIMEIRA PALAVRA:

NEOB - Não é o babaca

EOB - É o babaca 

NGM - Ninguem (é o babaca) 

TEOB - Todo mundo é o babaca 

INFO - Falta informação 

OS VOTOS SÃO CONTADOS TODO DIA AS 15:07!

^(Eu sou um robô e esse comentário foi feito automáticamente. Beep bop!) 
^([Códiigdo fonte](https://github.com/BrenoMartinsDeOliveiraVasconcelos/EuSouOBabacaBOT))
"""
counted = 0
while True:
    currentime = datetime.datetime.now().strftime("%H:%M")
    assholecount = {
        "NEOB": 0,
        "EOB": 0,
        "NGM": 0,
        "TEOB": 0,
        "INFO": 0
    }
    submissons = reddit.subreddit('EuSOuOBabaca').new(limit=100)
    time.sleep(5)
    for submission in submissons:
        sublist = open('idlist', 'r').readlines()
        indx = -1
        for i in sublist:
            indx += 1
            sublist[indx] = i.strip()
        if submission.id not in sublist:
            submission.reply(body=botxt)
            print("a")
            sublist.append(submission.id)
            with open('idlist', 'a') as f:
                f.write(submission.id + '\n')
            print('Comentário enviado para ' + submission.id)
        comments = submission.comments.list()
        if currentime == "15:07":
            highest = 0
            key = ''
            for comment in comments:
                time.sleep(5)
                if comment.author != 'EuSouOBabacaBOT':
                    comment_body = comment.body.split(' ')[0].strip()
                    rate = []
                    for i in comment_body:
                        replaces = ["!", "?", ".", ",", ":", "(", ")", "[", "]", "{", "}", "-", 
                                    "+", "/", "\\", "'", '"', '~']
                        for c in replaces:
                            i = i.replace(c, "")
                        print(i)
                        rate.append(i)
                    rate = ''.join(rate).upper()
                    print(rate)
                    if rate in ["NEOB", "EOB", "TEOB", "NGM", "INFO"]:
                        print("OK")
                        assholecount[rate] += 1
                        # print(assholecount)
                        counted = 1   
                    else:
                        counted = 0
                    for k, v in assholecount.items():
                        if v >= highest:
                            highest = v                                       
                            key = k
                    time.sleep(5)
                    if counted == 1:
                        for com in submission.comments.list():
                            if com.author == "EuSouOBabacaBOT":
                                com.edit(body=f"# VEREDITO ATUAL: {key} ({highest} votos)\n"+botxt)
                                print("Comentário editado com sucesso")
                else:
                    pass
