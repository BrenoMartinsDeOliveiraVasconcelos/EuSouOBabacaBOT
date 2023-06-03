import datetime
import os
import platform


def logit(msg):
    open("log", "a").write(msg + "\n")


def logger(tp, sub_id="", ex="", num="", reason="", bprint=False):
    current_time = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    msg = ""

    if tp == 0:
        msg = f"Comentário enviado em {sub_id}"
    elif tp == 1:
        msg = f"Comentário editado em {sub_id}"
    elif tp == 2 or tp == 5:
        msg = f"{ex}"
        if tp == 5:
            print(f"ERRO ({current_time}): {ex}")

        if bprint:
            print(ex)
    elif tp == 3:
        msg = f"Número {num} ({sub_id})"
    elif tp == 4:
        msg = f"{sub_id} foi removido. MOTIVO: {reason}"

    logit(f"[{current_time}] "+msg)
