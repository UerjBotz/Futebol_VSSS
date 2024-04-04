from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from ttkthemes import ThemedTk
from tkinter.font import Font
from tkinter import filedialog as fd

import os
import time

import cv2
import numpy as np
from PIL import Image, ImageTk

import widgets as wg

FILE = __file__
path = os.path.dirname(FILE)
os.chdir(path)

# INICIA A JANELA =========================================================
window_gui = wg.window(
    "Futebol VSSS - visão trevinho", ico=os.path.join(path, "images/icon.png"), height=720
)
win = window_gui.win
# =========================================================================


# BEGIN ==============================================================

# camera
camera = wg.camera(10, 450, "camera", win)
save = wg.save_image(10, 480, win)

# serial
serial = wg.console_serial(10, 510, win)

# monitores
monitor_camera = wg.monitor(10, 10, 500, 400, "Câmera", win)
monitor_mask = wg.monitor(530, 10, 250, 200, "Elementos", win)
tagHZ = wg.tag(530, 10, win)
monitor_colors = wg.monitor(530, 250, 250, 200, "Máscaras de Cores", win)

# tags
tag0 = wg.tag(10, 10, win)

# ajustes gerais
ajustes_visão = [
    dict(name="S min",    MIN=0,  MAX=255, default=86, unit=""),
    dict(name="V min",    MIN=0,  MAX=255, default=86, unit=""),
    dict(name="Y0",       MIN=0,  MAX=100, default=21, unit="px?"),
    dict(name="Y fim",    MIN=0,  MAX=100, default=94, unit="px?"),
    dict(name="H",        MIN=10, MAX=200, default=71, unit="cm"),
    dict(name="area min", MIN=1,  MAX=100, default=20, unit="px?"),
    dict(name="delta",    MIN=0,  MAX=100, default=15, unit="?"),
]
painel_visão = wg.painel("ajustes do sistema de visão", win, x=810, y=10)
for ajuste in ajustes_visão:
    painel_visão.add_slider(**ajuste)

# ajuste PID
ajustes_pid = [
    dict(name="vel",    MIN=0, MAX=100,  default=0,  unit="%"),
    dict(name="w",      MIN=0, MAX=100,  default=0,  unit="%"),
    dict(name="kl",     MIN=0, MAX=100,  default=18, unit="?"), # err max lin
    dict(name="kth",    MIN=0, MAX=100,  default=70, unit="?"), # err max lin
    dict(name="Q_ball", MIN=0, MAX=100,  default=30, unit="?"), # 68
    dict(name="Q_obs",  MIN=0, MAX=100,  default=9,  unit="?"),
    dict(name="Dmin",   MIN=1, MAX=100,  default=50, unit="%"),
    dict(name="theta",  MIN=1, MAX=1000, default=50, unit="%"),
    dict(name="raio",   MIN=1, MAX=1000, default=50, unit="%"),
]
painel_pid = wg.painel("ajustes do controlador", win, x=810, y=480)
for ajuste in ajustes_pid:
    painel_pid.add_slider(**ajuste)

# tag 1
tag_pid = wg.tag(810, 480, win)

# ajustes de cor
colors_default = {
    "orange": 3,  # 7,
    "yellow": 14,  # 18
    "green": 38,
    "blue": 72,
    "darkblue": 99,
    "pink": 134,
    "red": 180,  # 169
}
painel_cores = wg.painel("ajustes de cores", win, 810, 245)
for i, (color, hue) in enumerate(colors_default.items()):
    painel_cores.add_slider(name=color, MIN=0, MAX=180, default=hue, unit="º")

# ball
ball = wg.ball_tag(win, 10, 625, 65)

# tags dos bots
bot = {
    "darkblue": [wg.bot_tag(win, 235 + i * 195, 550, 60, "darkblue") for i in range(3)],
    "yellow": [wg.bot_tag(win, 235 + i * 195, 630, 60, "yellow") for i in range(3)],
}

mode = wg.mode_selection( # TODO: mudar pra mode_wg ou strat_wg
    win,
    10,
    545,
    20,
    "playing options",
    ["STOP", "CENTRO", "REPELE", "VECT", "v_kick", "kick"],  # 'CONFIG'],
    ["stop.png", "caminho.png", "raio.png", "happy.png", "ball.png", "kick2.png"],
)  # 'settings.png'])


def rec_step_call_default():
    if rec_step.can_write(True):
        rec_step.save_line([1, 2, 3, "A"])


rec_step = wg.record(10, 710, win, rec_step_call_default)
# rec_step = wg.record(810,720,win,rec_step_call_default)


# LOOP ==================================================================
def loop() -> dict: # TODO: mudar nome para update ou tick alguma coisa assim, atualizar tipo

    # atualiza sliders
    painel_visão.update_sliders()
    painel_cores.update_sliders()
    painel_pid.update_sliders()
    rec_step.voltage.update_label()

    # UPDATE COLORS =======================================================================
    color_hue_min = [painel_cores.sliders[c].get() for c in painel_cores.sliders]
    color_hue_max = []
    color_hue_mean = []
    red_index = len(painel_cores.sliders) - 1
    for i, color in enumerate(painel_cores.sliders):
        if i == red_index:
            color_hue_max += [color_hue_min[0]]
            color_hue_mean += [((180 + color_hue_min[i] + color_hue_max[i]) // 2) % 180]
        else:
            color_hue_max += [color_hue_min[i + 1]]
            color_hue_mean += [(color_hue_min[i] + color_hue_max[i]) // 2]
        painel_cores.sliders[color].color(wg.hue2ttkColor(color_hue_mean[-1]))
    VS_COLORS = {}
    VS_COLORS["MEAN"] = {
        color: color_hue_mean[i] for i, color in enumerate(painel_cores.sliders)
    }
    VS_COLORS["MIN"] = {
        color: color_hue_min[i] for i, color in enumerate(painel_cores.sliders)
    }
    VS_COLORS["MAX"] = {
        color: color_hue_max[i] for i, color in enumerate(painel_cores.sliders)
    }
    # UPDATE COLORS =======================================================================

    for i, color in enumerate(painel_cores.sliders):
        painel_cores.sliders[color].color(wg.hue2ttkColor(VS_COLORS["MEAN"][color]))

    VS_IN = {ajuste: painel_visão.sliders[ajuste].get() for ajuste in painel_visão.sliders}

    # print( "VS IN:", VS_IN )

    VS_OUT = {}
    VS_OUT["monitor_camera"] = monitor_camera
    VS_OUT["monitor_color"] = monitor_colors
    VS_OUT["monitor_mask"] = monitor_mask
    VS_OUT["BOTS"] = bot
    VS_OUT["tag0"] = tag0
    VS_OUT["tagHZ"] = tagHZ

    return (VS_COLORS, VS_IN, VS_OUT)


def update_tags(data):
    # ATUALIZA AS TAGS ------------------------------------------------------------------------
    ball.update_pack(data["ball"])
    for team in ["darkblue", "yellow"]:
        if team == "yellow":
            team_key = "team_yellow"
        else:
            team_key = "team_blue"
        keys = list(data[team_key].keys())
        bot_detection = {
            "id": 0,
            "pos": 0,
            "orientation": 0,
            "dimension": 0,
            "vector": 0,
            "colors": ["orange", "orange"],
        }
        for i in range(3):
            if len(data[team_key]) > i:
                bot[team][i].update_pack(data[team_key][keys[i]])
            else:
                bot[team][i].update_pack(bot_detection)
    # -----------------------------------------------------------------------------------------


# FOR TESTS ==============================================================
if __name__ == "__main__":
    print("FILE -> ", FILE, "\nPATH:", path)
    monitor_camera.update_BGR(camera.read())
    loop()
    win.mainloop()
