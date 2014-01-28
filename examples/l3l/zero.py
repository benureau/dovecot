from __future__ import division, print_function
import sys
import time

from pydyn import MotorSet
import env
from surrogates.stemsim import stemcfg

uid = 0 if len(sys.argv) == 1 else int(sys.argv[1])

stem = stemcfg.stems[uid]
stem.cycle_usb()

ms = MotorSet(serial_id=stem.serial_id, motor_range=stem.motorid_range, verbose=True)
ms.zero_pose = stem.zero_pose

ms.compliant = False
time.sleep(0.1)
ms.max_speed  = 100
ms.max_torque = 50
ms.pose = (0.0,)*6

time.sleep(3.0)
print("pos: [{}]".format(', '.join('{:.1f}'.format(p) for p in ms.pose)))