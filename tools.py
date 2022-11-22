import datetime
import multiprocessing


def logit(msg):
    open("log", "a").write(msg + "\n")

    if datetime.datetime.now().hour == 0:
        open("log", "w+").write(msg + "\n")

def logger(tp, sub_id="", ex="", num="", reason=""):
    current_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    msg = ""

    if tp == 0:
        msg = f"[{current_time}] Comentário enviado em {sub_id}"
    elif tp == 1:
        msg = f"[{current_time}] Comentário editado em {sub_id}"
    elif tp == 2:
        msg = f"[{current_time}] {ex}"
    elif tp == 3:
        msg = f"[{current_time}] Número {num}"
    elif tp == 4:
        msg = f"[{current_time}] {sub_id} foi removido. MOTIVO: {reason}"

    multiprocessing.Process(target=logit, args=(msg, )).start()
    print(msg)
