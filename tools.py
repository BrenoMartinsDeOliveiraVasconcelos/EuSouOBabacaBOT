import datetime
import os
import platform


def logit(msg):
    open("log", "a").write(msg + "\n")


def logger(tp, sub_id="", ex="", num="", reason=""):
    current_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    msg = ""

    if tp == 0:
        msg = f"Comentário enviado em {sub_id}"
    elif tp == 1:
        msg = f"Comentário editado em {sub_id}"
    elif tp == 2:
        msg = f"{ex}"
    elif tp == 3:
        msg = f"Número {num}"
    elif tp == 4:
        msg = f"{sub_id} foi removido. MOTIVO: {reason}"

    logit(f"[{current_time}] "+msg)
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

    print(f"""Beep bop!
Ação mais recente: {msg}
Horário do evento: {current_time}    
Rodando em: {platform.system()} {''.join(platform.version())} {' '.join(platform.architecture())} 
Python: {' '.join(platform.python_build())}""")
