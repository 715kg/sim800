import time

from termcolor import colored


# процедура для отправки строки в модем и получения ответа
def str_send(ser, textline):
    print(colored("<<: ", 'red') + colored(textline, 'blue'))
    ser.write(bytes(textline, "utf-8"))
    out = ''
    start_while = True
    timeout = time.time() + 10  # 10 sec timeout white

    while start_while:

        while ser.inWaiting() > 0:
            out += ser.read(1).decode('utf-8').rstrip('str')

        if 'OK' in out or '>' in out:
            return True, out
        elif 'ERROR' in out:
            return False, out

        test = 0
        if test == 5 or time.time() > timeout:
            return False, out
        test = test - 1
