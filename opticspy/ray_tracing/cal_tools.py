# calculation tools
from __future__ import division as __division__
import numpy as np

# spot diagram rms calculator

def rms(xy_list):
	x = xy_list[0] - np.mean(xy_list[0])
	y = xy_list[1] - np.mean(xy_list[1])
	# rms = np.sqrt(sum(x**2+y**2)/len(xy_list))
	rms = np.hypot(x, y).mean()
	return rms
