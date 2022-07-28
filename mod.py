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


print("INIT MOD!!!")
while True:
    currentime = datetime.datetime.now().strftime("%H:%M")
    try:
        subcount = 0
        submissons = reddit.subreddit('EuSOuOBabaca').new(limit=100)
        for submission in submissons:
            time.sleep(1)
            subcount += 1
            print("MOD UPDATE")
            tools.logger(tp=3, num=subcount)
            sublist = open('modlist', 'r').readlines()
            indx = -1
            for i in sublist:
                indx += 1
                sublist[indx] = i.strip()   
            if submission.id not in sublist:
                subauthor = submission.author
                if subauthor.comment_karma + subauthor.link_karma < 0:
                    submission.mod.remove(spam=True)
                    bcomment = submission.reply("Publicação removida por karma negativo para evitar spam.")
                open("modlist", "a").write(submission.id + "\n")
    except Exception as e:
        tools.logger(2, e)
