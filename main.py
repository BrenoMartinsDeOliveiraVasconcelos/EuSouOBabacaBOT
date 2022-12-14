import praw
import json
import tools
import multiprocessing
import discord
from discord.ext import commands
import os
import psutil
import datetime
import traceback

config = json.load(open('config', 'r'))
api = json.load(open("private/0.json"))

settings = {
    "clientid": api["clientid"],
    "clientsecret": api["clientsecret"],
    "username": api["rusername"],
    "password": api["password"],
    "discord_token": api["discord_token"],
    "submissions": config['submissions']
}

reddit = praw.Reddit(
    user_agent='<Linux>:<reddit-bot>:<v2.0> (by /u/JakeWisconsin)',
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

INFO - Falta informação 

FANFIC - Quando é fanfic

Demora um pouco até eu contar tudo, então espere alguns minutos... Ou sei lá, tanto faz.

Nota: Eu não conto respostas a comentários, somente comentários.
"""


def runtime():
    reddit.validate_on_submit = True
    while True:
        try:
            ftxt = f"# Veredito atual:" \
                   f" Não processado ainda \n\nÚltima atualização feita em: " \
                   f"{datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}\n\n "
            etxt = """
^(Eu sou um robô e esse comentário foi feito automáticamente. Beep bop!) 
^(Lucas Bot v2.0 - by [JakeWisconsin](https://www.reddit.com/u/JakeWisconsin))"""
            subcount = 0
            submissons = reddit.subreddit('EuSOuOBabaca').new(limit=int(settings["submissions"]))

            for submission in submissons:
                rst = open("restart", "r").readlines()
                if rst[0] == "1":
                    open("restart", "w+").write("0")
                    tools.logger(tp=2, ex="Bot reiniciado remotamente.")
                    break
                subcount += 1
                open("last", "w+").write(f"{subcount}")
                tools.logger(tp=3, num=subcount)
                assholecount = {
                    "NEOB": 0,
                    "EOB": 0,
                    "NGM": 0,
                    "TEOB": 0,
                    "INFO": 0,
                    "FANFIC": 0
                }
                sublist = open('idlist', 'r').readlines()
                indx = -1
                for i in sublist:
                    indx += 1
                    sublist[indx] = i.strip()
                if submission.id not in sublist:
                    botcomment = submission.reply(body=ftxt + botxt + etxt)
                    tools.logger(0, sub_id=submission.id)
                    botcomment.mod.distinguish(sticky=True)
                    botcomment.mod.lock()
                    botcomment.mod.approve()
                    sublist.append(submission.id)
                    submission.flair.select("5462ec04-70c6-11ed-8642-aa07fd483ac4")
                    with open('idlist', 'a') as f:
                        f.write(submission.id + '\n')
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
                                "Falta informação" if key == "INFO" else \
                                "Fake"

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

                tools.logger(2, ex="Submissão analizada!")
                etxt = f"""
# Tabela de votos
Voto | Quantidade | %
:--:|:--:|:--:
"""
                for k, v in assholecount.items():
                    etxt += f"{k} | {v} | {percents[k]}%\n"

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
                    case "Fake":
                        submission.flair.select("5c55d140-700a-11ed-8d83-1e3195d8e0d4")
                    case "Não avaliado":
                        submission.flair.select("528e0f44-7017-11ed-bf35-7a08e652fb3d")

                tools.logger(2, ex=f"Flair editada em {submission.id}")
                for com in comments:
                    if com.author == "EuSouOBabacaBot":
                        if subcount >= int(config["submissions"]):
                            ftxt += "# Essa publicação será mais atualizada!\n\n"
                        com.edit(
                            body=ftxt + botxt + etxt)
                        tools.logger(1, sub_id=submission.id)

                ftxt = f"# Veredito atual:" \
                       f" Não disponível \n\nÚltima atualização feita em: " \
                       f"{datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}\n\n "
        except Exception:
            tools.logger(2, ex=traceback.format_exc())


if __name__ == '__main__':
    bot_thread = multiprocessing.Process(target=runtime, args=(), )
    bot_thread.start()

    intents = discord.Intents().all()
    bot = commands.Bot(command_prefix="/", intents=intents)
    discord_token = settings["discord_token"]


    @commands.has_permissions(administrator=True)
    @bot.command(name="ping", help="Pong!")
    async def ping(ctx):
        await ctx.send("Pong!")
        dpid = os.getpid()
        rpid = bot_thread.pid
        pingdict = {
            "is_alive": bot_thread.is_alive(), "current_post": open("last", "r").readline().strip("\n"),
            "log_size": f'{os.stat("log").st_size / 1024:.0f} kb',
            "reddit_thread_pid": rpid,
            "discord_pid": dpid,
            "memory_d": f"{psutil.Process(dpid).memory_info().rss / 1024 ** 2:.0f} mb",
            "memory_rd": f"{psutil.Process(rpid).memory_info().rss / 1024 ** 2:.0f} mb",
            "memory_total": f""
            f"{(psutil.Process(dpid).memory_info().rss/1024**2)+(psutil.Process(rpid).memory_info().rss/1024**2):.0f}"
            f"mb",
            "cpu_d": f"{psutil.Process(dpid).cpu_percent() * 100:.3f}%",
            "cpu_rd": f"{psutil.Process(rpid).cpu_percent() * 100:.3f}%",
            "cpu_total": f"{psutil.Process(dpid).cpu_percent() * 100 + psutil.Process(rpid).cpu_percent() * 100:.3f}%",
        }

        for k, v in pingdict.items():
            await ctx.send(f"{k} = {v}")

        await ctx.send("Log", file=discord.File(r"log"))


    @commands.has_permissions(administrator=True)
    @bot.command(name="reiniciar", help="Reinicia a sessão no reddit")
    async def reset(ctx):
        await ctx.send("Ok")
        open("restart", "w+").write("1")
        await ctx.send("Pronto.")


    @commands.has_permissions(administrator=True)
    @bot.command(name="log", help="Retorna o arquivo de log caso não tenha um argumento"
                                  "\nCaso tenha o argumento 'limpar', limpa o arquivo de log")
    async def send_log(ctx, *args):
        if len(args) == 0:
            await ctx.send("Aqui está!")
            await ctx.send(".", file=discord.File(r"log"))
        elif args[0] == "limpar":
            await ctx.send("Ok")
            open("log", "w+").write("")


    @commands.has_permissions(administrator=True)
    @bot.command(name="fechar", help="Fecha o programa ou o bot.\n"
                                     "\n'bot' fecha apenas a sessão do bot"
                                     "\np'programa' fecha o programa inteiro. Pode ser"
                                     "necessário entrar no servidor para iniciar de novo.")
    async def close(ctx, *args):
        if len(args) > 0:
            tools.logger(tp=2, ex="Bot ou programa fechado remotamente.")
            if args[0] == "bot":
                await ctx.send("Blz")
                try:
                    bot_thread.terminate()
                except (AssertionError, AttributeError):
                    pass
            elif args[0] == "programa":
                await ctx.send("Se é isso que você quer, tanto faz pra mim.")
                exit(0)


    @bot.command(name="configurar", help="Troca a configuração no arquivo json 'config'. 'mostrar' para "
                                         "mostrar as configurações atuais. <key> <value> para alterar.")
    async def config(ctx, *args):
        if len(args) >= 2:
            settings[args[0]] = args[1]
        elif len(args) == 1:
            if args[0] == "mostrar":
                await ctx.send(f"{settings}")

        open("config", "w+").write(json.dumps(settings, indent=4))

    bot.run(discord_token)
