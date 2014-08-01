from __future__ import print_function, division, absolute_import
import os
import math

import numpy as np

import toolbox
from toolbox import gfx
import dynamics.fwdkin.smodel as smodel


class CollisionFilter(object):
    """
        Given two objects (one static), tell if there is :
        - absolutely no possibility of collision
        - maybe a possibility
    """

    _u = np.matrix([[0], [0], [0], [1]])

    def __init__(self, cfg, obj_pos, obj_geom, marker_radius):
        print(obj_pos)
        print(obj_geom)
        self.cfg           = cfg
        self.obj_pos       = obj_pos
        self.obj_geom      = obj_geom
        self.marker_radius = marker_radius

        self._register_object()

        model_filepath = os.path.abspath(os.path.join(__file__, '..')) + '/' + 'stem.smodel'
        self.stem_model    = smodel.SymbolicModel.from_file(model_filepath)


    def _register_object(self):
        if len(self.obj_geom) == 3: # cube
            obj_radius = math.sqrt(sorted(self.obj_geom)[2]**2 + sorted(self.obj_geom)[1]**2)
        self.min_d_sq = 1.1*((obj_radius + self.marker_radius)**2)


    def may_collide(self, poses):
        for pose in poses:
            orientation = [1.0, -1.0, -1.0, 1.0, 1.0, 1.0]
            pose_r = [math.radians(p*o) for p, o in zip(pose, orientation)]
            tip_pos = self.tip(pose_r)
            #print(gfx.ppv(pose), gfx.ppv(tip_pos), gfx.ppv(self.obj_pos))
            #print('{:.1f} {:.1f}'.format(toolbox.dist_sq(tip_pos, self.obj_pos), self.min_d_sq))
            if self._collision_detected(tip_pos):
                return True
        return False

    def fake_collision(self, poses):
        """Somehow simulates a collision effect on the object position. Very crude."""
        obj_pose = []
        for i, pose in enumerate(poses):
            orientation = [1.0, -1.0, -1.0, 1.0, 1.0, 1.0]
            pose_r = [math.radians(p*o) for p, o in zip(pose, orientation)]
            tip_pos = self.tip(pose_r)
            #print(gfx.ppv(pose), gfx.ppv(tip_pos), gfx.ppv(self.obj_pos))
            #print('{:.1f} {:.1f}'.format(toolbox.dist_sq(tip_pos, self.obj_pos), self.min_d_sq))
            if self._collision_detected(tip_pos):
                displacement = self.cfg.execute.kin.force*10*np.average([np.array(poses[j]) - np.array(poses[j-1]) for j in range(max(i-10, 0), i)])
                return [self.obj_pos, np.array(self.obj_pos) + displacement]
        return [self.obj_pos, self.obj_pos]

    def _collision_detected(self, tip_pos):
        return toolbox.dist_sq(tip_pos, self.obj_pos) < self.min_d_sq

    def tip(self, pose):
        tip = self.stem_model.f(*pose)*self._u
        return (tip[0, 0], tip[1, 0], tip[2, 0])



class FakeColliderCube(CollisionFilter):

    def _register_object(self):
        pass


    def _collision_detected(self, tip_pos):
        return all(o_c - o_d/2.0 - self.marker_radius < t_c < o_c + o_d/2.0 + self.marker_radius
                   for t_c, o_c, o_d in zip(tip_pos, self.obj_geom, self.obj_pos))

