import datetime


def logger(tp, sub_id="", ex=""):
    current_time = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    if tp == 0:
        print(f"[{current_time}] Comentário enviado em {sub_id}")
    elif tp == 1:
        print(f"[{current_time}] Comentário editado em {sub_id}")
    elif tp == 2:
        print(f"[{current_time}] {ex}")
