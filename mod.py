import praw
import json
import tools
import datetime
import time


login = json.load(open("login"))


reddit = praw.Reddit(
    user_agent='<Linux>:<reddit-bot>:<v1.0> (by /u/JakeWisconsin)',
    client_id=login["clientid"],
    client_secret=login["clientsecret"],
    username=login["username"],
    password=login["password"]
)

while True:
    currentime = datetime.datetime.now().strftime("%H:%M")
    subcount = 0
    submissons = reddit.subreddit('EuSOuOBabaca').new(limit=100)
    for submission in submissons:
        try:
            time.sleep(1)
            subcount += 1
            print("MOD UPDATE")
            tools.logger(tp=3, num=subcount)
            sublist = open('modlist', 'r').readlines()
            indx = -1
            for i in sublist:
                indx += 1
                sublist[indx] = i.strip().replace("\n", "")  
            if submission.id not in sublist:
                subauthor = submission.author
                if subauthor.comment_karma + subauthor.link_karma < 0:
                    submission.mod.remove(spam=True)
                    bcomment = submission.reply(body="Publicação removida por karma negativo para evitar spam.")
                    tools.logger(tp=4, sub_id=submission.id, reason="Karma negativo")
                subtxt = submission.selftext
                subtxt = subtxt.split(" ")
                badwords = open("palavroes", "r").readlines()
                bd = ""
                indx = -1
                for i in badwords:
                    indx += 1
                    i = i.strip().replace("\n", "").lower()
                    badwords[indx] = i
                for i in subtxt:
                    i = i.strip().replace(" ", "").replace("\n", "")
                    if i.startswith("[http") and r"//" in i:
                        submission.mod.remove(spam=True)
                        submission.reply(body="Não é permitido links nesse subreddit! Sua publicação foi removida.")
                        tools.logger(tp=4, sub_id=submission.id, reason="Link")
                        break
                    if i.lower() in badwords:
                        bd = i.lower()
                        submission.mod.remove(spam=False)
                        submission.reply(body=f"Por favor mantenha o respeito ao contar sua história! Post removido pois contêm palavrão ({bd}).")
                        tools.logger(tp=4, sub_id=submission.id, reason=f"Falta de respeito. ({bd})")
                        break
                open("modlist", "a").write(submission.id + "\n")
        except Exception as e:
            tools.logger(2, ex=e)
