import datetime
import multiprocessing


def logit(msg):
    open("log", "a").write(msg + "\n")


def logger(tp, sub_id="", ex=""):
    current_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    if tp == 0:
        msg = f"[{current_time}] Comentário enviado em {sub_id}"
    elif tp == 1:
        msg = f"[{current_time}] Comentário editado em {sub_id}"
    elif tp == 2:
        msg = f"[{current_time}] {ex}"

    multiprocessing.Process(target=logit, args=(msg, )).start()
    print(msg)
