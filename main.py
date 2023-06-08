'''
This file is the main file
Copyright (C) 2023  Breno Martins

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import praw
import json
import tools
import multiprocessing
import shutil
import time
import datetime
import traceback
import random
import os
import psutil

config = json.load(open('config.json', 'r'))
api = json.load(open("api.json"))
splashes = json.load(open('splashes.json', 'r'))
reasons = json.load(open("reasons.json", "r"))

settings = {
    "clientid": api["clientid"],
    "clientsecret": api["clientsecret"],
    "username": api["rusername"],
    "password": api["password"],
    "useragent": api["useragent"],
    "submissions": config['submissions'],
    "subreddit": config["subreddit"],
    "backup": config["backup"],
    "clear_log": config["clear_log"]
}

flairs = config["flairs"]

reddit = praw.Reddit(
    user_agent=settings["useragent"],
    client_id=settings["clientid"],
    client_secret=settings["clientsecret"],
    username=settings["username"],
    password=settings["password"]
)

# Post a comment to every new reddit submission in r/EuSOuOBabaca
botxt = f"\n\n**{config['upper_text']}**\n\nVou contar as respostas que as pessoas dão nesse post! Pra ser contado, " \
        f"responda com essas siglas o post:\n\n"

votxt = ["", "", ""]
for k, v in flairs.items():
    votxt[v[1]] += f"{k} - {v[2]}\n\n"

botxt += votxt[0] + "**Votos especiais**\n\n" + votxt[1] + "\n\n"
botxt += "##Nota: Pode demorar cerca de 2 horas para atualizar!\n\n"


def runtime():
    reddit.validate_on_submit = True
    while True:
        try:
            ftxt = f"# Veredito atual:" \
                   f" Não processado ainda \n\nÚltima atualização feita em: " \
                   f"{datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}\n\n "
            subcount = 0
            submissons = reddit.subreddit(settings["subreddit"]).new(limit=int(settings["submissions"]))
            adds = ""
            edits = ""
            flairchanges = ""
            atime = datetime.datetime.now().timestamp()

            for submission in submissons:

                joke = random.choice(splashes)
                etxt = f"""
                                
*{joke}* 
*{config['info']['name']} v{config['info']['version']} - by [{config['info']['creator']}](https://www.reddit.com/u/{config['info']['creator']}).*
*Veja meu código fonte: [Código fonte]({config['info']['github']}).*"""

                assholecount = {}
                for flair in flairs.keys():
                    if flair not in config["flairs_ignore"]:
                        assholecount[flair] = 0

                subcount += 1
                tools.logger(tp=3, num=subcount, sub_id=submission.id)
                sublist = open('idlist', 'r').readlines()
                indx = -1
                for sub in sublist:
                    indx += 1
                    sublist[indx] = sub.strip()
                if submission.id not in sublist:
                    botcomment = submission.reply(body=ftxt + botxt + etxt)
                    tools.logger(0, sub_id=submission.id)
                    botcomment.mod.distinguish(sticky=True)
                    botcomment.mod.approve()
                    sublist.append(submission.id)
                    submission.flair.select(flairs["NOT_CLASSIFIED"][0])
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
                percent = 0
                rates = [x for x in assholecount.keys()]
                judges = config["vote_name"]
                for comment in comments:
                    try:
                        if comment.author != settings["username"] and comment.author not in users \
                                and comment.author != submission.author:
                            comment_body = comment.body.split(' ')
                            indx = -1
                            for sub in comment_body:
                                indx += 1
                                sub = sub.split("\n")
                                comment_body[indx] = sub[0]
                                try:
                                    comment_body.insert(indx + 1, sub[1])
                                except IndexError:
                                    pass
                            rate = []
                            for sub in comment_body:
                                sub = sub.strip()
                                replaces = ["!", "?", ".", ",", ":", "(", ")", "[", "]", "{", "}", "-",
                                            "+", "/", "\\", "'", '"', '~']
                                for c in replaces:
                                    sub = sub.replace(c, "")
                                rate.append(sub)

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

                            '''judgment = "Não é o babaca" if key == "NEOB" else \
                                "É o babaca" if key == "EOB" else \
                                "Todo mundo é babaca" if key == "TEOB" else \
                                "Ninguém é o babaca" if key == "NGM" else \
                                "Falta informação" if key == "INFO"  "FANFIC" "Fake"'''

                            ind = rates.index(key)
                            judgment = judges[ind]

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
                    except Exception:
                        tools.logger(5, ex=traceback.format_exc())

                percents = {}
                for k, v in assholecount.items():
                    try:
                        percents[k] = f"{(int(v) / total) * 100:.2f}"
                    except ZeroDivisionError:
                        percents[k] = f"0.00"
                tools.logger(2, ex="Submissão analizada!")

                votxt = f"""
# Tabela de votos
Voto | Quantidade | %
:--:|:--:|:--:
"""

                for k, v in assholecount.items():
                    votxt += f"{k} | {v} | {percents[k]}%\n"

                etxt = votxt + etxt
                if percent >= 0.5 and total > 0:
                    submission.flair.select(flairs[key][0])
                    if key in ["FANFIC", "OT"]:
                        removes = open('rid', "r").readlines()

                        indx = -1
                        for sub in removes:
                            indx += 1
                            removes[indx] = sub.strip()

                        if submission.id not in removes and total > 1:
                            reason = reasons["FAKE_OT"]
                            submission.mod.remove(mod_note=f"{reason['note']}", spam=False)
                            submission.reply(body=f"{reason['body']}")
                            tools.logger(tp=4, sub_id=submission.id, reason="VIolação")
                            open("rid", "a").write(f"{submission.id}\n")
                elif percent < 0.5 and total > 0:
                    submission.flair.select(flairs["INCONCLUSIVE"][0])
                elif total == 0:
                    submission.flair.select(flairs["NOT_AVALIABLE"][0])
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
            btime = datetime.datetime.now().timestamp()
            tools.logger(2, ex=f"runtime(): {btime-atime}s", bprint=False)
        except Exception as e:
            tools.logger(5, ex=traceback.format_exc())


def backup():
    while True:
        try:
            folder = f"{settings['backup']}/{datetime.datetime.now().strftime('%Y-%m-%d/%H-%M-%S')}"
            src = "."
            shutil.copytree(src, folder, ignore=shutil.ignore_patterns("venv", ".", "__"))
            tools.logger(2, bprint=False, ex="Backup realizado")
        except:
            pass
        time.sleep(3600)


def clearlog():
    while True:
        time.sleep(config["clear_log"])
        open("log", "w+").write("")


def textwall():
    reddit.validate_on_submit = True
    while True:
        atime = datetime.datetime.now().timestamp()
        try:
            subcount = 0
            submissons = reddit.subreddit(settings["subreddit"]).new(limit=int(settings["submissions"]))
            for submission in submissons:
                time.sleep(1)
                subcount += 1
                subid = submission.id

                tools.logger(tp=3, num=subcount, sub_id=subid)

                sublist = open('rid', 'r').readlines()
                indx = -1
                for i in sublist:
                    indx += 1
                    sublist[indx] = i.strip()

                if subid not in sublist:
                    try:
                        body = submission.selftext
                    except:
                        body = ""
                    paragraphs = 1
                    sentences = 0

                    # Detyerminar quantos parágrafos tem o texto
                    index = -1
                    paragraph_cond = False
                    if body != "":
                        for i in body:
                            index += 1
                            try:
                                if i == "\n" and body[index+1] == "\n":
                                    paragraphs += 1
                                    sentences += 1
                                    paragraph_cond = True
                            except IndexError:
                                pass

                            # Quantas frases tem
                            if i == "." and not paragraph_cond:
                                sentences += 1

                            paragraph_cond = False
                    else:
                        paragraphs = 0
                        sentences = 0

                    if sentences != 0 and paragraphs != 0:
                        spp = sentences / paragraphs
                    else:
                        spp = 0

                    if paragraphs < 2 or sentences <= 2:
                        reason = reasons['TEXTWALL']
                        submission.mod.remove(mod_note=reason['note'], spam=False)
                        submission.reply(body=reason['body'])
                        tools.logger(tp=4, sub_id=subid, reason="Parede de texto")

                        open("rid", "a").write(f"{subid}\n")
            btime = datetime.datetime.now().timestamp()
            tools.logger(tp=2, ex=f"textwall(): {btime-atime}s", bprint=False)
        except Exception:
            tools.logger(tp=5, ex=traceback.format_exc())


if __name__ == '__main__':
    funcs = [runtime, backup, clearlog, textwall]
    processes = [multiprocessing.Process(target=x, args=[]) for x in funcs]

    pids = [os.getpid()]

    index = -1
    for i in processes:
        index += 1
        i.start()
        pids.append(i.pid)
        print(f"Iniciado processo com o PID {i.pid} (função {funcs[index].__name__}())")

    while True:
        inp = input("=> ").upper().split(" ")
        if len(inp) >= 1:
            if inp[0] == "R":
                config = json.load(open('config.json', 'r'))
                api = json.load(open("api.json"))
                splashes = json.load(open('splashes.json', 'r'))
                print("Valores recarregados na memória.")
            elif inp[0] == "E":
                for i in processes:
                    i.terminate()
                    break
            elif inp[0] == "RESTART":
                for i in processes:
                    i.terminate()

                os.system(f"{config['python']} ./main.py")
                break
            elif inp[0] == "MEMORY":
                mem = 0
                perc = 0
                all_processes = psutil.process_iter()

                for process in all_processes:
                    if process.pid in pids:
                        perc += process.memory_percent()
                        memory_info = process.memory_info()
                        mem += memory_info.rss / 1024 / 1024

                print(f"{mem:.0f} mb ({perc:.2f}%)")
