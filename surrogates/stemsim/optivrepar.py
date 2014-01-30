import time

import numpy as np
import treedict

from natnet import FrameBuffer

from ..vrepsim import vrepcom


class OptiVrepAR(object):
    def __init__(self, cfg, port=1984, verbose=True, ppf=200, scene="../stemsim/ar.ttt", script="marker"):
        self.ppf = ppf
        self.port = 1984
        self.verbose = verbose
        self.scene = scene
        self.script = script
        cfg2 = cfg.copy(deep=True)
        cfg2.sprims.tip = False
        self.opivcom = vrepcom.OptiVrepCom(cfg2, load=False, verbose=self.verbose, headless=False, vrep_folder=None, ppf=self.ppf)
        if not self.opivcom.connected:
            self.opivcom.load(self.scene, self.script)

    def execute(self, trackdata):
        return self.opivcom.run_trajectory(trackdata)

    def close(self):
        self.opivcom.close()
