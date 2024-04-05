# fmt: off
ajustes_visão = [
    dict(name="S min",    MIN=0,  MAX=255, default=86, unit=""),   
    dict(name="V min",    MIN=0,  MAX=255, default=86, unit=""),   
    dict(name="Y0",       MIN=0,  MAX=100, default=21, unit="px?"),
    dict(name="Y fim",    MIN=0,  MAX=100, default=94, unit="px?"),
    dict(name="H",        MIN=10, MAX=200, default=71, unit="cm"), 
    dict(name="area min", MIN=1,  MAX=100, default=20, unit="px?"),
    dict(name="delta",    MIN=0,  MAX=100, default=15, unit="?"),
]

ajustes_pid = [
     dict(name="vel",    MIN=0, MAX=100,  default=0,  unit="%"),
     dict(name="w",      MIN=0, MAX=100,  default=0,  unit="%"),
     dict(name="kl",     MIN=0, MAX=100,  default=18, unit="?"), # err     max lin
     dict(name="kth",    MIN=0, MAX=100,  default=70, unit="?"), # err     max lin
     dict(name="Q_ball", MIN=0, MAX=100,  default=30, unit="?"), # 68
     dict(name="Q_obs",  MIN=0, MAX=100,  default=9,  unit="?"),
     dict(name="Dmin",   MIN=1, MAX=100,  default=50, unit="%"),
     dict(name="theta",  MIN=1, MAX=1000, default=50, unit="%"),
     dict(name="raio",   MIN=1, MAX=1000, default=50, unit="%"),
]

ajustes_cores = [
    dict(name="orange",   default=3  ), # 7,
    dict(name="yellow",   default=14 ), # 18  
    dict(name="green",    default=38 ),
    dict(name="blue",     default=72 ),
    dict(name="darkblue", default=99 ),
    dict(name="pink",     default=134),
    dict(name="red",      default=180), # 169 
]
# fmt: on

