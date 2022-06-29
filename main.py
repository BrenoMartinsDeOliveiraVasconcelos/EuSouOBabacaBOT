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
botxt = """## VOTE SE O OP É UM BABACA COMENTANDO NO POST COM AS SEGUINTES SIGLAS EM ALGUMA PARTE DO TEXTO!:

NEOB - Não é o babaca

EOB - É o babaca 

NGM - Ninguem (é o babaca) 

TEOB - Todo mundo é o babaca 

INFO - Falta informação 

OS VOTOS SÃO CONTADOS COM ALGUNS MINUTOS DE ATRASO, ENTÃO TENHAM PACIÊNCIA!

^(Eu sou um robô e esse comentário foi feito automáticamente. Beep bop!) 
^([Códiigdo fonte](https://github.com/BrenoMartinsDeOliveiraVasconcelos/EuSouOBabacaBOT))
"""
while True:
    currentime = datetime.datetime.now().strftime("%H:%M")
    subcount = 0
    try:
        submissons = reddit.subreddit('EuSOuOBabaca').new(limit=100)
        time.sleep(1)
        for submission in submissons:
            subcount += 1
            print(f"== {subcount} ==")
            assholecount = {
                            "NEOB": 0,
                            "EOB": 0,
                            "NGM": 0,
                            "TEOB": 0,
                            "INFO": 0
                            }
            sublist = open('idlist', 'r').readlines()
            indx = -1
            for i in sublist:
                indx += 1
                sublist[indx] = i.strip()
            if submission.id not in sublist:
                botcomment = submission.reply(body=botxt)
                botcomment.mod.distinguish(sticky=True)
                print("a")
                sublist.append(submission.id)
                with open('idlist', 'a') as f:
                    f.write(submission.id + '\n')
                print('Comentário enviado para ' + submission.id)
            comments = submission.comments.list()
            if currentime: #== "15:07":
                highest = 0
                key = ''
                for comment in comments:
                    if comment.author != 'EuSouOBabacaBOT':
                        comment_body = comment.body.split(' ')
                        indx = -1
                        for i in comment_body:
                            indx += 1
                            i = i.split("\n")
                            comment_body[indx] = i[0]
                            try:
                                comment_body.insert(indx+1, i[1])
                            except IndexError:
                                pass
                        rate = []
                        for i in comment_body:
                            i = i.strip()
                            replaces = ["!", "?", ".", ",", ":", "(", ")", "[", "]", "{", "}", "-",
                                        "+", "/", "\\", "'", '"', '~']
                            for c in replaces:
                                i = i.replace(c, "")
                            print(i)
                            rate.append(i)
                        #= ''.join(rate).upper()
                        print(rate)
                        rates = ["NEOB", "EOB", "TEOB", "NGM", "INFO"]
                        indx =-1
                        for w in rate:
                            indx += 1
                            rate[indx] = w.upper().strip()
                        for r in rates:
                            if r in rate:
                                assholecount[r] += 1
                                print("Ok")
                        #if rate in ["NEOB", "EOB", "TEOB", "NGM", "INFO"]:
                        #    print("OK")
                        #    assholecount[rate] += 1
                            # print(assholecount)
                                counted = 1
                                break
                        else:
                            counted = 0
                        for k, v in assholecount.items():
                            if v >= highest:
                                highest = v
                                key = k
                        if counted == 1:
                            for com in submission.comments.list():
                                if com.author == "EuSouOBabacaBOT":
                                    com.edit(body=f"# VEREDITO ATUAL: {key} ({highest} votos)\n"+botxt)
                                    print("Comentário editado com sucesso")
                    else:
                        pass
    except Exception as e:
        print(f"{e}")
