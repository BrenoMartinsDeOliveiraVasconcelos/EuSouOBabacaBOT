import praw
import datetime
import json
import tools
import multiprocessing
import os

# multiprocessing.Process(target=os.system, args=["python3 mod.py",]).start()

login = json.load(open("login"))

reddit = praw.Reddit(
    user_agent='<Linux>:<reddit-bot>:<v1.0> (by /u/JakeWisconsin)',
    client_id=login["clientid"],
    client_secret=login["clientsecret"],
    username=login["username"],
    password=login["password"]
)

# Post a comment to every new reddit submission in r/EuSOuOBabaca
botxt = """## VOTE SE O OP É UM BABACA COMENTANDO NO POST COM AS SEGUINTES SIGLAS EM ALGUMA PARTE DO TEXTO! (O BOT NÃO CONTA RESPOSTAS):

NEOB - Não é o babaca

EOB - É o babaca 

NGM - Ninguem (é o babaca) 

TEOB - Todo mundo é o babaca 

INFO - Falta informação 

FANFIC - Quando é fanfic

OS VOTOS SÃO CONTADOS COM ALGUNS MINUTOS DE ATRASO, ENTÃO TENHAM PACIÊNCIA!

Nota: O bot não conta respostas.

^(Eu sou um robô e esse comentário foi feito automáticamente. Beep bop!) 
^([Código fonte](https://github.com/BrenoMartinsDeOliveiraVasconcelos/EuSouOBabacaBOT))
"""


def runtime():
    while True:
        currentime = datetime.datetime.now().strftime("%H:%M")
        subcount = 0
        try:
            submissons = reddit.subreddit('EuSOuOBabaca').new(limit=100)
            for submission in submissons:
                subcount += 1
                tools.logger(tp=3, num=subcount)
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
                    reddit.validate_on_submit = True
                    botcomment = submission.reply(body=botxt)
                    redditor = submission.author
                    tools.logger(0, sub_id=submission.id)
                    botcomment.mod.distinguish(sticky=True)
                    botcomment.mod.lock()
                    botcomment.mod.approve()
                    sublist.append(submission.id)
                    with open('idlist', 'a') as f:
                        f.write(submission.id + '\n')
                submission.comments.replace_more(limit=100, threshold=100)
                comments = submission.comments.list()
                if currentime:
                    highest = 0
                    key = ''
                    users = []
                    for comment in comments:
                        try:
                            if comment.author != 'EuSouOBabacaBOT' and comment.author not in users:
                                users.append(comment.author)
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
                                    rate.append(i)
                                rates = ["NEOB", "EOB", "TEOB", "NGM", "INFO"]
                                indx = -1
                                for w in rate:
                                    indx += 1
                                    rate[indx] = w.upper().strip()
                                for r in rates:
                                    if r in rate:
                                        assholecount[r] += 1
                                        counted = 1
                                        break
                                else:
                                    counted = 0
                                total = 0
                                for k, v in assholecount.items():
                                    total += v
                                    if v >= highest:
                                        highest = v
                                        key = k
                                try:
                                    percent = highest/total
                                except ZeroDivisionError:
                                    percent = 1.00
                                if counted == 1:
                                    for com in submission.comments.list():
                                        if com.author == "EuSouOBabacaBOT":
                                            judgment = "Não é o babaca" if key == "NEOB" else \
                                                "É o babaca" if key == "EOB" else \
                                                "Todo mundo é babaca" if key == "TEOB" else \
                                                "Ninguém é o babaca" if key == "NGM" else \
                                                "Falta informação" if key == "INFO" else \
                                                "Fanfic"
                                            com.edit(body=f"# VEREDITO ATUAL: {judgment} ({percent*100:.2f}% de {total}"
                                                          f" "
                                                          f""
                                                          f"votos)\n"+botxt)
                                            tools.logger(1, sub_id=submission.id)
                                            com.mod.lock()
                                            com.mod.approve()
                            else:
                                pass
                        except Exception as e:
                            tools.logger(2, ex=e)
        except Exception as e:
            tools.logger(2, ex=e)


if __name__ == '__main__':
    runtime()
