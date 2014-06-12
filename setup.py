import os
from distutils.core import setup

setup(
    name         = 'dovecot',
    version      = '2.0',
    author       = 'Fabien Benureau, Paul Fudal',
    author_email = 'fabien.benureau@inria.fr',
    description  = ('A python library to drive the hardware and simulation experiment of the author PhD thesis'),
    license      = 'Open Science',
    keywords     = 'science experiment hardware simulation robots',
    url          = 'flowers.inria.fr',
    packages = ['dovecot',
                'dovecot.vizu',
                'dovecot.prims',
                'dovecot.ttts',
                'dovecot.ttts.files',
                'dovecot.kinsim',
                'dovecot.vrepsim',
                'dovecot.stemsim',
                'dovecot.stemsim',
                'dovecot.stemsim.stemcfg',
                'dovecot.collider',
                'dovecot.calibration',
                'dovecot.calibration.triocal',
                'dovecot.calibration.tttcal'
               ],
    classifiers = [],
    package_data = {'dovecot.ttts.files'    : ['vrep_center_cube.ttt',
                                                 'ar_center_cube.ttt',
                                                 'vizu_center_cube.ttt',
                                               'vrep_center_sphere.ttt',
                                                 'ar_center_sphere.ttt',
                                                 'vizu_center_sphere.ttt',
                                               'vrep_cylinder.ttt',
                                                 'ar_cylinder.ttt',
                                                 'vizu_cylinder.ttt',
                                               'vrep_other_cube.ttt',
                                                 'ar_other_cube.ttt',
                                                 'vizu_other_cube.ttt',
                                               'vrep_center_cylinder.ttt',
                                                 'ar_center_cylinder.ttt',
                                                 'vizu_center_cylinder.ttt',
                                               'vrep_center_tinycube.ttt',
                                                 'ar_center_tinycube.ttt',
                                                 'vizu_center_tinycube.ttt',
                                               'vrep_center_tinysphere.ttt',
                                                 'ar_center_tinysphere.ttt',
                                                 'vizu_center_tinysphere.ttt',
                                               'vrep_center_tinycylinder.ttt',
                                                 'ar_center_tinycylinder.ttt',
                                                 'vizu_center_tinycylinder.ttt',
                                               'vrep_side_tinycube.ttt',
                                                 'ar_side_tinycube.ttt',
                                                 'vizu_side_tinycube.ttt',
                                               'vrep_side_tinysphere.ttt',
                                                 'ar_side_tinysphere.ttt',
                                                 'vizu_side_tinysphere.ttt',
                                               'vrep_side_tinycylinder.ttt',
                                                 'ar_side_tinycylinder.ttt',
                                                 'vizu_side_tinycylinder.ttt',
                                               'vrep_calibrate.ttt',
                                               'ar.ttt'],
                    'dovecot.collider'      : ['stem.smodel'],
                    'dovecot.calibration.triocal' : ['calib0.data',
                                                     'calib1.data',
                                                     'calib2.data',
                                                     'calib3.data']}, # FIXME should be dynamic
)
