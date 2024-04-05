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

import config
import widgets as wg

FILE = __file__
path = os.path.dirname(FILE)
os.chdir(path)

# INICIA A JANELA ===================================================
window_gui = wg.window(
    "Visão do Futebol VSSS da UERJBotz", ico=os.path.join(path, "images/icon.png"), height=720
)
win = window_gui.win
# ===================================================================


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
painel_visão = wg.painel("ajustes_da_visão", win, x=810, y=10)
for ajuste in config.ajustes_visão:
    painel_visão.add_slider(**ajuste)
painel_visão.add_button()

# ajustes de cor
painel_cores = wg.painel("ajustes_de_cores", win, 810, 245)
for cor in config.ajustes_cores:
    painel_cores.add_slider(**cor, MIN=0, MAX=180, unit="º")
painel_cores.add_button()

# ajuste PID
painel_pid = wg.painel("ajustes_do_controlador", win, x=810, y=485)
for ajuste in config.ajustes_pid:
    painel_pid.add_slider(**ajuste)
painel_pid.add_button()



# tag 1
tag_pid = wg.tag(810, 480, win)

# ball
ball = wg.ball_tag(win, 10, 625, 65)

# tags dos bots
bot = {
    "darkblue": [wg.bot_tag(win, 235 + i * 195, 550, 60, "darkblue") for i in range(3)],
    "yellow":   [wg.bot_tag(win, 235 + i * 195, 630, 60, "yellow") for i in range(3)],
}

mode = wg.mode_selection( # TODO: mudar pra mode_wg ou strat_wg
    win,
    10,
    545,
    20,
    "playing options",
    ["STOP", "CENTRO", "REPELE", "VECT", "v_kick", "kick"],
    ["stop.png", "caminho.png", "raio.png", "happy.png", "ball.png", "kick2.png"],
)


def rec_step_call():
    if rec_step.can_write(True):
        rec_step.save_line([1, 2, 3, "A"])
rec_step = wg.record(10, 710, win, rec_step_call)
# rec_step = wg.record(810,720,win,rec_step_call)


def loop() -> tuple[dict, dict, dict]: # TODO: mudar nome para update ou tick alguma coisa assim, atualizar tipo

    # atualiza sliders
    painel_visão.update_sliders()
    painel_cores.update_sliders()
    painel_pid.update_sliders()
    rec_step.voltage.update_label()

    # UPDATE COLORS =================================================
    color_hue_min = [painel_cores.sliders[c].get() for c in painel_cores.sliders]
    color_hue_max = []
    color_hue_mean = []
    red_index = len(painel_cores.sliders) - 1
    for i, color in enumerate(painel_cores.sliders):
        if i == red_index:
            color_hue_max += [color_hue_min[0]]
            color_hue_mean += [((180 + color_hue_min[i] + color_hue_max[i]) // 2) % 180] # TODO: ? não parece mediana e tem um 180 a mais (?)
        else:
            color_hue_max += [color_hue_min[i + 1]]
            color_hue_mean += [(color_hue_min[i] + color_hue_max[i]) // 2]
        painel_cores.sliders[color].color(wg.hue2ttkColor(color_hue_mean[-1]))

    VS_COLORS = {
        "MEAN": {
            color: color_hue_mean[i] for i, color in enumerate(painel_cores.sliders)
        }, "MIN": {
            color: color_hue_min[i] for i, color in enumerate(painel_cores.sliders)
        }, "MAX": {
            color: color_hue_max[i] for i, color in enumerate(painel_cores.sliders)
        },
    }
    # UPDATE COLORS =================================================

    for i, color in enumerate(painel_cores.sliders):
        painel_cores.sliders[color].color(wg.hue2ttkColor(VS_COLORS["MEAN"][color]))

    VS_IN = {ajuste: painel_visão.sliders[ajuste].get() for ajuste in painel_visão.sliders}

    VS_OUT = {
        "monitor_camera": monitor_camera,
        "monitor_color":  monitor_colors,
        "monitor_mask":   monitor_mask,
        "BOTS":  bot,
        "tag0":  tag0,
        "tagHZ": tagHZ,
    }

    return (VS_COLORS, VS_IN, VS_OUT)


def update_tags(data):
    ball.update_pack(data["ball"])
    for team in "darkblue", "yellow":
        team_key = "team_yellow" if team == "yellow" else "team_blue"

        keys = list(data[team_key].keys())
        bot_detection = {
            "id":  0,
            "pos": 0,
            "orientation": 0,
            "dimension":   0,
            "vector": 0,
            "colors": ["orange", "orange"],
        }
        for i in range(3):
            if len(data[team_key]) > i:
                bot[team][i].update_pack(data[team_key][keys[i]])
            else:
                bot[team][i].update_pack(bot_detection)


# FOR TESTS =========================================================
if __name__ == "__main__":
    print("FILE -> ", FILE, "\nPATH:", path)
    monitor_camera.update_BGR(camera.read())
    loop()
    win.mainloop()
