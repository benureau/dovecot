import numpy as np
import random

import env
from dovecot import prims
from cfg import cfg0

mprims = prims.create_mprim(cfg0.mprim.name, cfg0)
print('   slope    offset    center     width')
for i in range(1000):
    order = tuple(random.uniform(a, b) for a, b in mprims.m_bounds)
    traj, max_step = mprims.process_order(order)
    for i, (pos, vel) in enumerate(traj):
        if any(np.isnan(e) for e in pos) or any(np.isnan(e) for e in vel):
            print("  ".join("{:8.3f}".format(e) for e in order[4*i:4*i+4]))
