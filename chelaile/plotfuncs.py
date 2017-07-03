import matplotlib

from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties

fontfp = "support/font/simsun.ttc"
fontset = FontProperties(fname=fontfp)

colors = {i for i, x in matplotlib.colors.cnames.items() if
          (int(x[1:3], 16) + int(x[3:5], 16) + int(x[5:7], 16)) / 3 < 100}