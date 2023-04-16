import praw
import json
import tools
import multiprocessing
import shutil
import time
import datetime
import traceback

config = json.load(open('config.json', 'r'))
api = json.load(open("api.json"))

settings = {
    "clientid": api["clientid"],
    "clientsecret": api["clientsecret"],
    "username": api["rusername"],
    "password": api["password"],
    "useragent": api["useragent"],
    "submissions": config['submissions'],
    "subreddit": config["subreddit"],
    "backup": config["backup"]
}

reddit = praw.Reddit(
    user_agent=settings["useragent"],
    client_id=settings["clientid"],
    client_secret=settings["clientsecret"],
    username=settings["username"],
    password=settings["password"]
)

# Post a comment to every new reddit submission in r/EuSOuOBabaca
botxt = \
    """Vou contar as respostas que as pessoas dão nesse post! Pra ser contado, responda com essas siglas o post:

NEOB - Não é o babaca (E o resto sim)

EOB - É o babaca 

NGM - Ninguem (é o babaca) 

TEOB - Todo mundo é o babaca 

INFO - Falta informaçã

FANFIC - Quando algo é obviamente falso 

Demora um pouco até eu contar tudo, então espere alguns minutos... Ou sei lá, tanto faz.

Nota: Eu não conto respostas a comentários, somente comentários.
"""


def runtime():
    reddit.validate_on_submit = True
    current_loop = int("".join(open("last", "r").readlines()).replace('\n', ''))
    while True:
        current_loop += 1
        try:
            ftxt = f"# Veredito atual:" \
                   f" Não processado ainda \n\nÚltima atualização feita em: " \
                   f"{datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}\n\n "
            etxt = """
            
^(Eu sou um robô e esse comentário foi feito automáticamente. Beep bop!) 
^(Lucas Bot v2.0 - by [JakeWisconsin](https://www.reddit.com/u/JakeWisconsin))"""
            subcount = 0
            submissons = reddit.subreddit(settings["subreddit"]).new(limit=int(settings["submissions"]))
            adds = ""
            edits = ""
            flairchanges = ""
            table = ""
            atime = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

            for submission in submissons:
                assholecount = {
                    "NEOB": 0,
                    "EOB": 0,
                    "NGM": 0,
                    "TEOB": 0,
                    "INFO": 0,
                    "FANFIC": 0,
                }
                rst = open("restart", "r").readlines()
                if rst[0] == "1":
                    open("restart", "w+").write("0")
                    tools.logger(tp=2, ex="Bot reiniciado remotamente.")
                    break
                subcount += 1
                tools.logger(tp=3, num=subcount, sub_id=submission.id)
                sublist = open('idlist', 'r').readlines()
                indx = -1
                for i in sublist:
                    indx += 1
                    sublist[indx] = i.strip()
                if submission.id not in sublist:
                    botcomment = submission.reply(body=ftxt + botxt + etxt)
                    tools.logger(0, sub_id=submission.id)
                    botcomment.mod.distinguish(sticky=True)
                    botcomment.mod.approve()
                    sublist.append(submission.id)
                    submission.flair.select("5462ec04-70c6-11ed-8642-aa07fd483ac4")
                    with open('idlist', 'a') as f:
                        f.write(submission.id + '\n')
                    adds += f"\n* Adicionado https://www.reddit.com/{submission.id} a lista de ids.\n"
                submission.comment_sort = 'new'
                submission.comments.replace_more(limit=None)
                comments = submission.comments.list()
                highest = 0
                key = ''
                users = []
                total = 0
                judgment = ""

                for comment in comments:
                    try:
                        if comment.author != settings["username"] and comment.author not in users \
                                and comment.author != submission.author:
                            comment_body = comment.body.split(' ')
                            indx = -1
                            for i in comment_body:
                                indx += 1
                                i = i.split("\n")
                                comment_body[indx] = i[0]
                                try:
                                    comment_body.insert(indx + 1, i[1])
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
                            rates = ["NEOB", "EOB", "TEOB", "NGM", "INFO", "FANFIC"]
                            indx = -1
                            for w in rate:
                                indx += 1
                                rate[indx] = w.upper().strip()
                            for r in rates:
                                if r in rate:
                                    assholecount[r] += 1
                                    break
                            total = 0
                            for k, v in assholecount.items():
                                total += v
                                if v >= highest:
                                    highest = v
                                    key = k
                            try:
                                percent = highest / total
                            except ZeroDivisionError:
                                percent = 1.00
                            judgment = "Não é o babaca" if key == "NEOB" else \
                                "É o babaca" if key == "EOB" else \
                                "Todo mundo é babaca" if key == "TEOB" else \
                                "Ninguém é o babaca" if key == "NGM" else \
                                "Falta informação" if key == "INFO" else "Fake"

                            if percent < 0.50:
                                judgment = "Inconclusivo"
                                votetxt = f"{total} votos contados ao total"
                            else:
                                votetxt = f"{percent * 100:.2f}% de {total} votos"

                            if total == 0:
                                judgment = "Não avaliado"
                                votetxt = f"{total} votos contados ao total"
                            ftxt = f"# Veredito atual: " \
                                   f"{judgment} ({votetxt})\n\nÚltima atualização feita em: " \
                                   f"{datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}\n\n "
                            users.append(comment.author)
                    except Exception as e:
                        tools.logger(2, ex=e)

                percents = {}
                for k, v in assholecount.items():
                    try:
                        percents[k] = f"{(int(v) / total) * 100:.2f}"
                    except ZeroDivisionError:
                        percents[k] = f"0.00"
                with open(f"rates/{submission.id}.json", "w") as json_file:
                    json.dump(assholecount, json_file, indent=4)
                tools.logger(2, ex="Submissão analizada!")

                etxt = f"""
# Tabela de votos
Voto | Quantidade | %
:--:|:--:|:--:
"""
                for k, v in assholecount.items():
                    etxt += f"{k} | {v} | {percents[k]}%\n"
                table += f"\n* A tabela de https://www.reddit.com/{submission.id} agora é:\n\n{etxt}\n"
                etxt += """
                                
^(Eu sou um robô e esse comentário foi feito automáticamente. Beep bop!) 
^(Lucas Bot v2.0 - by [JakeWisconsin](https://www.reddit.com/u/JakeWisconsin))"""
                match judgment:
                    case 'Não é o babaca':
                        submission.flair.select("fad0940c-6841-11ed-baed-365116e43406")
                    case 'É o babaca':
                        submission.flair.select("e46b8208-6841-11ed-99cd-cec761e4d61c")
                    case 'Todo mundo é babaca':
                        submission.flair.select("8cb95bb0-6842-11ed-9cdf-a2c7df914eb2")
                    case 'Ninguém é o babaca':
                        submission.flair.select("3704e1da-6842-11ed-924e-e273ede5d967")
                    case 'Falta informação':
                        submission.flair.select("562808bc-6842-11ed-8dd7-86bf8dba8041")
                    case "Inconclusivo":
                        submission.flair.select("17ace5be-6cd2-11ed-880b-f6403a5de3db")
                    case "Não avaliado":
                        submission.flair.select("528e0f44-7017-11ed-bf35-7a08e652fb3d")
                    case "Fake":
                        submission.flair.select("5c55d140-700a-11ed-8d83-1e3195d8e0d4")

                        

                flairchanges += f"\n* Flair de https://www.reddit.com/{submission.id} é '{judgment}'"
                tools.logger(2, ex=f"Flair editada em {submission.id}")
                for com in comments:
                    if com.author == f"{settings['username']}":
                        bd = com.body.split("\n")
                        if subcount >= int(settings["submissions"]):
                            ftxt += "# Essa publicação será mais atualizada!\n\n"
                        if ">!NOEDIT!<" not in bd:
                            com.edit(
                                body=ftxt + botxt + etxt)
                            tools.logger(1, sub_id=submission.id)
                            edits += f"\n* Comentário do bot editado em https://www.reddit.com/{submission.id}\n"
                ftxt = f"# Veredito atual:" \
                       f" Não disponível \n\nÚltima atualização feita em: " \
                       f"{datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}\n\n "
                btime = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            satxt = f""""# Adioções na lista de ids:
{adds}"""
            setxt = f"""
# Edições de comentário:
{edits}"""
            sftxt = f""" 
# Edições de flair de posts:
{flairchanges}
"""
            sttxt = f""" 
# Tabelas
{table}
"""
            reddit.subreddit("EuSouOBabacaBOT").submit(f"[ADD] LOG PARA O LOOP NUMERO {current_loop} ({atime} até {btime})",
                                                       selftext=satxt)
            reddit.subreddit("EuSouOBabacaBOT").submit(
                f"[EDIT] LOG PARA O LOOP NUMERO {current_loop} ({atime} até {btime})",
                selftext=setxt)
            reddit.subreddit("EuSouOBabacaBOT").submit(
                f"[FLAIR] LOG PARA O LOOP NUMERO {current_loop} ({atime} até {btime})",
                selftext=sftxt)
            open("last", "w+").write(f"{current_loop}")
        except Exception as e:
            tools.logger(2, ex=traceback.format_exc())
            reddit.subreddit("EuSouOBabacaBOT").submit(
                f"ERRO! {e.__cause__}", selftext="u/JakeWisconsin\n\n"+traceback.format_exc())


def backup():
    while True:
        try:
            folder = f"{settings['backup']}/{datetime.datetime.now().strftime('%Y-%m-%d/%H-%M-%S')}"
            src = "."
            shutil.copytree(src, folder, ignore=shutil.ignore_patterns("venv", ".", "__"))
            print("Copiado")
            reddit.subreddit("EuSouOBabacaBOT").submit(
                f"Backup realizado",
                selftext=f"Diretório: {folder}")
        except:
            reddit.subreddit("EuSouOBabacaBOT").submit(
                f"Erro na função de backup",
                selftext=f"{traceback.format_exc()}\n\nu/JakeWisconsin")
        time.sleep(3600)


def clearlog():
    while True:
        time.sleep(86400)
        open("log", "w+").write("")
        reddit.subreddit("EuSouOBabacaBOT").submit(
            f"Arquivo de log limpo",
            selftext=f"Log limpo em {datetime.datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}. u/JakeWisconsin")


if __name__ == '__main__':
    multiprocessing.Process(target=runtime, args=[]).start()
    multiprocessing.Process(target=backup, args=[]).start()
    multiprocessing.Process(target=clearlog, args=[]).start()

    while True:
        continue
