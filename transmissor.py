import sys
import glob
import serial
from time import sleep

host: serial.Serial | None = None


def begin(porta):
    global host
    if porta != "x":
        if host is not None:
            if host.port == porta:
                print("[SERIAL] port ->", host.port)
                return True
        host = serial.Serial(porta, 115200, timeout=0.1, writeTimeout=0.1)
        print("[SERIAL] port ->", host.port)
        return True
    else:
        print("[SERIAL] port -> None [not connected]")
        host = None
        return False


def begin_host(porta):
    global host
    if porta != "x":
        if host is not None:
            if host.port == porta:
                print("[SERIAL] port ->", host.port)
                return True
        host = serial.Serial(porta, 115200, timeout=0.1, writeTimeout=0.1)
        print("[SERIAL] port ->", host.port)
        return (host, True)
    else:
        print("[SERIAL] port -> None [not connected]")
        host = None
        return (host, False)


def list_ports():
    """Lists serial port names

    :returns:
        A list of the serial ports available on the system
    """
    if sys.platform.startswith("win"):
        ports = [f"COM{i + 1}" for i in range(256)]
    else:
        #ports = glob.glob("/dev/tty.*")
        ports = glob.glob("/dev/tty[A-Za-z]*[0-9]*")

    #TODO: lidar com plataformas erradas

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except OSError:
            pass
        except serial.SerialException as se:
            print(f"SerialException: {port}: {se}")

    if not result:
        print("[SERIAL]: porta não encontrada. está ocupada?")
    return result


def send(data: list[int]) -> str:
    msg = "Send "
    for d in data:
        msg += f"{d} "
    println(msg)


def write(msg):
    global host
    if host is not None:
        try:
            print("[SERIAL] msg:", msg)
            # host.write(bytes(msg, "utf-8"))
            host.write(msg.encode())
            # host.flush()
            host.reset_output_buffer()
        except:
            host = None


def println(msg):
    write(msg + "\n")

def close():
    if host is not None:
        send_ch_333([])
        print("[SERIAL] close")
        host.close()

_ID_TODOS = -1

set_pid_P     = lambda i,  bot=_ID_TODOS: println(f"P {bot} {i}")
set_pid_I     = lambda i,  bot=_ID_TODOS: println(f"I {bot} {i}")
#set_pid_I_MAX = lambda i, bot=_ID_TODOS: println(f"I_MAX {bot} {i}")#TODO
set_pid_D     = lambda i,  bot=_ID_TODOS: println(f"D {bot} {i}")

set_pid_kp    = lambda kp, bot=_ID_TODOS: println(f"kp {bot} {kp}")
set_pid_ki    = lambda ki, bot=_ID_TODOS: println(f"ki {bot} {ki}")
set_pid_kd    = lambda kd, bot=_ID_TODOS: println(f"kd {bot} {kd}")

pid_start     = lambda      bot=_ID_TODOS: println(f"start {bot}")
set_pid_speed = lambda lin, bot=_ID_TODOS: println(f"speed {bot} {lin}")
set_pid_angle = lambda ang, bot=_ID_TODOS: println(f"w {bot} {ang}") 

stop = lambda bot=_ID_TODOS: println(f"stop {bot}") #TODO: isso não para o PID!!!!!

"""
if __name__ == "__main__":
    L = list_ports()
    print(L)
    if len(L) > 0:
        begin(L[0])
        for i in range(10):
            write(f"ab azul {i}")
            sleep(0.02)

    while True:
        if host is not None:
            if host.isOpen() == False:
                print(".")
                host.open()
            else:
                if host.in_waiting:
                    print(host.readline().decode("utf"))
                println("bot.bip")  # command to robot make bip sound
                sleep(1)
        else:
            L = list_ports()
            if len(L) > 0:
                begin(L[0])
"""
