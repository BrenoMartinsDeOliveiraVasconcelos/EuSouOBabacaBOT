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

import preparation as prep


start = datetime.datetime.now().timestamp()

config = json.load(open('config.json', 'r'))
api = json.load(open("api.json", "r"))
splashes = json.load(open('splashes.json', 'r'))
reasons = json.load(open("reasons.json", "r"))

reddit = praw.Reddit(
    user_agent=api["useragent"],
    client_id=api["clientid"],
    client_secret=api["clientsecret"],
    username=api["username"],
    password=api["password"]
)

# Post a comment to every new reddit submission in r/EuSOuOBabaca


def runtime():
    botxt = f"\n\n# {config['upper_text']}\n\nVou contar as respostas que as pessoas dão nesse post! Pra ser contado, " \
            f"responda com essas siglas o post:\n\n"

    votxt = ["", "", ""]
    for k, v in config["flairs"].items():
        votxt[v[1]] += f"{k} - {v[2]}\n\n"

    botxt += votxt[0] + "**Votos especiais**\n\n" + votxt[1] + "\n\n"
    botxt += "##Nota: Pode demorar cerca de 2 horas para atualizar!\n\n"

    reddit.validate_on_submit = True
    while True:
        try:
            ftxt = f"# Veredito atual:" \
                   f" Não processado ainda \n\nÚltima análise feita em: " \
                   f"{datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}\n\n "
            subcount = 0
            submissons = reddit.subreddit(config["subreddit"]).new(limit=int(config["submissions"]))
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
                for flair in config["flairs"].keys():
                    if flair not in config["flairs_ignore"]:
                        assholecount[flair] = 0

                subcount += 1
                sublist = tools.getfiletext(open("idlist", "r"))

                indx = -1
                bdlist = open("bodies/bdlist", "r").readlines()
                for sub in bdlist:
                    indx += 1
                    bdlist[indx] = sub.strip()
                indx = -1
                # abrir a lista de corpos já salvos ou não
                bodylist = json.load(open("./bodies/bodies.json", "r"))
                try:
                    bodylist[f"{submission.id}"]
                except KeyError:
                    bodylist[f"{submission.id}"] = submission.selftext

                bodies_json = json.dumps(bodylist, indent=4)

                open("./bodies/bodies.json", "w+").write(bodies_json)
                if submission.id not in sublist:
                    botcomment = submission.reply(body=ftxt + botxt + etxt)
                    tools.logger(0, sub_id=submission.id)
                    botcomment.mod.distinguish(sticky=True)
                    botcomment.mod.approve()
                    sublist.append(submission.id)
                    submission.flair.select(config["flairs"]["NOT_CLASSIFIED"][0])
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
                num_coms = 0
                for comment in comments:
                    num_coms += 1

                numbers = json.load(open("./data/number_comments.json", "r"))
                try:
                    saved = numbers[f"{submission.id}"]
                    ignore_saved = False
                except KeyError:
                    saved = numbers[f"{submission.id}"] = num_coms
                    ignore_saved = True

# Temporariamente tirando otimização
                for comment in comments:
                    try:
                        if comment.author != api["username"] and comment.author not in users \
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
                numbers[f"{submission.id}"] = num_coms
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
                    submission.flair.select(config["flairs"][key][0])
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
                    submission.flair.select(config["flairs"]["INCONCLUSIVE"][0])
                elif total == 0:
                    submission.flair.select(config["flairs"]["NOT_AVALIABLE"][0])
                flairchanges += f"\n* Flair de https://www.reddit.com/{submission.id} é '{judgment}'"
                tools.logger(2, ex=f"Flair editada em {submission.id}")

                notInBody = False
                if submission.id not in bdlist:
                    notInBody = True
                    open('./bodies/bdlist', "a").write(f"{submission.id}\n")

                body_obj = bodylist[f"{submission.id}"].split("\n\n")
                index = 0
                for line in body_obj:
                    body_obj[index] = ">" + line + "\n\n"
                    index += 1

                body_obj = ''.join(body_obj)
                bodytxt = f"\n\n# Texto original\n\n{body_obj}\n\n>!NOEDIT!<"

                for com in comments:
                    if com.author == f"{api['username']}":
                        bd = com.body.split("\n")
                        if subcount >= int(config["submissions"]):
                            ftxt += "# Essa publicação será mais atualizada!\n\n"
                        fullbody = ftxt + botxt + etxt
                        if notInBody:
                            com.reply(body=bodytxt)
                        if ">!NOEDIT!<" not in bd:
                            com.edit(
                                body=fullbody)
                            tools.logger(1, sub_id=submission.id)
                            edits += f"\n* Comentário do bot editado em https://www.reddit.com/{submission.id}\n"
                ftxt = f"# Veredito atual:" \
                        f" Não disponível \n\nÚltima atualização feita em: " \
                        f"{datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}\n\n "

            numstring = json.dumps(numbers, indent=4)

            open("./data/number_comments.json", "w+").write(numstring)

            btime = datetime.datetime.now().timestamp()
            tools.log_runtime(runtime, atime, btime)
        except Exception as e:
            tools.logger(5, ex=traceback.format_exc())


def backup():
    while True:
        atime = datetime.datetime.now().timestamp()
        try:
            folder = f"{config['backup']}/{datetime.datetime.now().strftime('%Y-%m-%d/%H-%M-%S')}"
            src = "."
            shutil.copytree(src, folder, ignore=shutil.ignore_patterns("venv", ".", "__"))
            tools.logger(2, bprint=False, ex="Backup realizado")
        except:
            pass
        time.sleep(3600)
        btime = datetime.datetime.now().timestamp()
        tools.log_runtime(backup, atime, btime)
        


def clearlog():
    while True:
        atime = datetime.datetime.now().timestamp()
        time.sleep(config["clear_log"])
        open("log", "w+").write("")
        btime = datetime.datetime.now().timestamp()
        tools.log_runtime(clearlog, atime, btime)


def textwall():
    reddit.validate_on_submit = True
    while True:
        atime = datetime.datetime.now().timestamp()
        try:
            subcount = 0
            submissons = reddit.subreddit(config["subreddit"]).new(limit=int(config["submissions"]))
            for submission in submissons:
                time.sleep(1)
                subcount += 1
                subid = submission.id

                sublist = tools.getfiletext(open("rid", "r"))
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
                    sentences = 1

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
                            if i in [".", "?", "!"] and not paragraph_cond:
                                sentences += 1

                            paragraph_cond = False
                    else:
                        paragraphs = 0
                        sentences = 0

                    if sentences != 0 and paragraphs != 0:
                        spp = sentences / paragraphs
                    else:
                        spp = 0

                    if paragraphs < config["text_filter"]["min_paragraphs"] or sentences < config["text_filter"]["min_sentences"]  or len(body) > config["text_filter"]["max_body"] :
                        reason = reasons['TEXTWALL']
                        submission.mod.remove(mod_note=reason['note'], spam=False)
                        submission.reply(body=reason['body'])
                        tools.logger(tp=4, sub_id=subid, reason="Parede de texto")

                        open("rid", "a").write(f"{subid}\n")
            btime = datetime.datetime.now().timestamp()
            tools.log_runtime(textwall, atime, btime)
        except Exception:
            tools.logger(tp=5, ex=traceback.format_exc())


def verify_user():
    reddit.validate_on_submit = True
    while config["karma_filter"]["enabled"]:
        # espera por x segundos para executar o filtro
        time.sleep(config["karma_filter"]["wait"])
        sublist = tools.getfiletext(open("rid", "r"))
        indx = -1
        for i in sublist:
            indx += 1
            sublist[indx] = i.strip()

        atime = datetime.datetime.now().timestamp()
        try:
            subcount = 0
            submissons = reddit.subreddit(config["subreddit"]).new(limit=int(config["submissions"]))
            for submission in submissons:
                time.sleep(1)
                subcount += 1
                subid = submission.id

                if subid not in sublist:
                    # filtra os users por comment_karma
                    redditor = reddit.redditor(submission.author)
                    try:
                        karma = redditor.comment_karma + redditor.link_karma
                    except AttributeError:
                        karma = config["karma_filter"]["min"]

                    if karma < config["karma_filter"]["min"]:
                        reason = reasons["KARMA"]
                        submission.mod.remove(mod_note=reason["note"], spam=False)
                        submission.reply(body=reason["body"])
                        tools.logger(tp=4, sub_id=subid, reason="Karma")

                        open("rid", "a").write(f"{subid}\n")
            btime = datetime.datetime.now().timestamp()
            tools.log_runtime(verify_user, atime, btime)
        except Exception:
            tools.logger(tp=5, ex=traceback.format_exc())


def agechecker():
    '''
    Checa se tem idade no post

    :return: None
    '''

    sublist = tools.getfiletext(open("aid", "r"))
    rid = tools.getfiletext(open("rid", "r"))
    submissions = reddit.subreddit(config["subreddit"]).new(limit=int(config["submissions"]))

    try:
        while True:
            a = datetime.datetime.now().timestamp()
            time.sleep(10)
            for submission in submissions:
                if submission.id not in sublist:
                    open("aid", "a").write(f"{submission.id}\n")
                    title_body = []
                    for i in submission.title.split(" "):
                        title_body.append(i)

                    for i in submission.selftext.split(" "):
                        title_body.append(i)

                    index = 0
                    for i in title_body:
                        title_body[index] = i.replace("\n\n", "")
                        index += 1

                    index = 0
                    status = True
                    for word in title_body:
                        # checar se tem numero na palavra, se tiver quebra tudo
                        letters = []

                        for l in word:
                            letters.append(l)

                        place = 0
                        status = False
                        for x in letters:
                            x: str
                            if x.isnumeric():
                                status = True

                            place += 1

                        if status:
                            break

                        index += 1

                    if submission.id not in rid and not status:
                        reason = reasons["NO_AGE"]
                        submission.mod.remove(mod_note=reason["note"], spam=False)
                        submission.reply(body=reason["body"])
                        tools.logger(tp=4, sub_id=submission.id, reason="Sem idade")

                        open("rid", "a").write(f"{submission.id}\n")

            b = datetime.datetime.now().timestamp()
            tools.log_runtime(agechecker, a, b)
    except Exception:
        tools.logger(tp=5, ex=traceback.format_exc())


if __name__ == '__main__':
    # Preparar os arquivos
    prep.begin()

    funcs = [runtime, backup, clearlog, textwall, verify_user, agechecker]
    processes = [multiprocessing.Process(target=x, args=[], name=x.__name__) for x in funcs]

    pids = [os.getpid()]

    index = -1
    for i in processes:
        index += 1
        i.start()
        pids.append(i.pid)
        print(f"Iniciado processo com o PID {i.pid} para a função {funcs[index].__name__}()")

    end = datetime.datetime.now().timestamp()
    print(f"main: {(end-start)*1000:.0f} ms.")
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
