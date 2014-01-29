from __future__ import division, print_function
import time
import random
import sys
import atexit

from toolbox import gfx
from natnet import FrameBuffer, MarkerError

from . import calibration
from . import stemsensors
from . import stembot
from . import optivrepar
from . import stemcfg

class OrderNotExecutableError(Exception):
    pass

class Episode(object):

    def __init__(self, cfg, verbose=True):
        self.cfg = cfg

        self.stem = stemcfg.stems[self.cfg.stem.uid]
        self.M_trans = calibration.load_calibration(self.stem)
        self.vs = stemsensors.VrepSensors(self.cfg)
        self.verbose = verbose

        atexit.register(self.close)

        if self.verbose:
            print("{}launching serial... {}".format(gfx.purple, gfx.end))
        self.sb = stembot.StemBot(cfg)
        if self.verbose:
            print("{}launching optitrack cature on {}... {}".format(gfx.purple, self.stem.optitrack_addr, gfx.end))
        self.fb = FrameBuffer(40.0, addr=self.stem.optitrack_addr)
        if self.verbose:
            print("{}launching vrep... {}".format(gfx.cyan, gfx.end))
        self.ovar = optivrepar.OptiVrepAR(cfg, verbose=False)

        self.exhibit_prims()

    def exhibit_prims(self):
        self.s_feats  = self.vs.s_feats
        self.s_bounds = self.vs.s_bounds
        self.s_fixed  = self.vs.s_fixed
        self.s_units  = self.vs.s_units
        self.real_s_bounds = self.vs.real_s_bounds

        self.m_feats = self.sb.m_feats
        self.m_bounds = self.sb.m_bounds

    def execute_order(self, order, tries=0):
        try:
            if self.verbose:
                print("{}executing movement on stem...{}".format(gfx.purple, gfx.end), end='\r')
            sys.stdout.flush()

            # execute movement on stem
            self.fb.track(self.stem.optitrack_side)
            start, end = self.sb.execute_order(order)
            self.fb.stop_tracking()
            if self.verbose:
                print('')
            time.sleep(0.01)

            # get optitrack trajectory
            opti_traj = self.fb.tracking_slice(start, end)

            # fill gaps
            opti_traj = calibration.transform.fill_gaps(opti_traj)
            vrep_traj = calibration.transform.opti2vrep(opti_traj, self.M_trans)

            if self.verbose:
                print("{}executing movement in vrep...{}".format(gfx.cyan, gfx.end))

            # execute in vrep
            object_sensors, joint_sensors, tip_sensors = self.ovar.execute(vrep_traj)

            # produce sensory feedback
            effect = self.vs.process_sensors(object_sensors, joint_sensors, tip_sensors)
            #print("{}order:{} {}".format(gfx.purple, gfx.end, gfx.ppv(order)))
            if self.verbose:
                print("{}effect:{} {}".format(gfx.cyan, gfx.end, gfx.ppv(effect)))

            return effect


        except stembot.CollisionError:
            self.fb.stop_tracking()
            raise OrderNotExecutableError

        except MarkerError:
            if tries == 0:
                print('{}caught marker error...                   {}'.format(gfx.red, gfx.end))
                time.sleep(0.1)
                self.fb = FrameBuffer(40.0, addr=self.stem.optitrack_addr)
                return self.execute_order(order, tries=1)
            else:
                raise OrderNotExecutableError

    def close(self):
        try:
            self.sb.close()
        except Exception:
            pass
        try:
            self.fb.stop()
            self.fb.join()
        except Exception:
            pass
        try:
            self.ovar.close()
        except Exception:
            pass