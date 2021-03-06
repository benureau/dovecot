"""This implements simulated motors

Simulated motors receive the same serial packets as real motors, and they
are connected in a daisy chain manner much like real motors.

>>> m0 = KinMotor('AX-12', 0)
>>> m1 = KinMotor('AX-12', 1)
>>> c01 = KinCable(m0.ports[1], m1.ports[0])
"""
from __future__ import print_function, division

#import new
import time

from ...refs import protocol as pt
from ...refs import conversions as conv
from ...refs import limits
from ..serialio import packet
from ..serialio import serialcom
from ..fakeio import fakememory
from ...dynamixel import motor
from ...dynamixel import memory


_to_params = serialcom.SerialCom._to_params
_to_values = serialcom.SerialCom._to_values

CTRL_ADDR = {(ctrl.addr, sum(ctrl.sizes)): ctrl for ctrl in pt.CTRL_LIST}

def _register_write(self, control, values):
    """Write write request immediately in memory"""
    if not hasattr(values, '__iter__'):
        values = (values,)
    offset = 0
    for size, value in zip(control.sizes, values):
        self.mmem[control.addr+offset] = value
        offset += size
    self.mmem.update() # could be more selective, but this would be useless optimization.

class KinMotor(object):

    def __init__(self, model, mid):
        fakemem = fakememory.MODELS[model]
        mmem = memory.DynamixelMemory(mid, save=False, memory=fakemem)
        self.motor = motor.MOTOR_MODELS[model](mmem)
        self.motor._register_write = _register_write.__get__(self.motor, self.motor.__class__) # new.instancemethod(_register_write, self.motor, None)
        self.motor.id = mid
        self.motor.status_return_level = 1

        self.ports = (KinPort(self), KinPort(self))
        self.control_port = None
        self.status_port = None
        self._motor_time = time.time()
        self._timestep = 0.001
        self._present_position = self.motor.present_position

    def receive(self, port, msg):
        """Receiving a message from a port"""
        self._update()

        # the first message received is from the control port
        if self.control_port is None:
            self.control_port = port
            self.status_port = self.ports[1] if self.ports[0] == port else self.ports[0]

        if port is self.control_port:
            p = packet.StatusPacket(msg) # but it is an InstructionPacket
            if p.mid == self.motor.id or p.mid == pt.BROADCAST:
                status_msg = self._process_instruction(p)
                if status_msg is not None:
                    self.send(self.control_port, status_msg)
            if p.mid != self.motor.id:
                # passing control message for another motor
                self.send(self.status_port, msg)

        else:
            assert port is self.status_port
            self.send(self.control_port, msg) # passing status messages

    def send(self, port, msg):
        """Sending a message on a port"""
        assert port is self.control_port or port is self.status_port
        port.send(msg)

    def _process_instruction(self, p):
        assert p.mid == self.motor.id or p.mid == pt.BROADCAST
        if self.motor.status_return_level == 2:
            raise NotImplementedError
        instruction = p.error
        if instruction == pt.PING:
            msg = self._ping(p)
        elif instruction == pt.WRITE_DATA:
            msg = self._write_data(p)
        elif instruction == pt.READ_DATA:
            msg = self._read_data(p)
            assert msg is not None
        elif instruction == pt.SYNC_WRITE:
            msg = self._sync_write(p)
        else:
            raise NotImplementedError
        if msg is not None:
            self.send(self.control_port, msg)


    def _ping(self, p):
        status_data = [255, 255, self.motor.id, 2, 0]
        status_data.append(packet.Packet.checksum(status_data[2:]))
        return bytearray(status_data)

    def _read_data(self, p):
        try:
            control = CTRL_ADDR[(p.params[0], p.params[1])]
        except KeyError:
            raise NotImplementedError # we don't support custom controls (yet)
        values, offset = [], 0
        for size in control.sizes:
            values.append(self.motor.mmem[control.addr+offset])
            offset += size
        params = _to_params(control, values)
        status_data = [255, 255, self.motor.id, len(params)+2, 0] + list(params)
        status_data.append(packet.Packet.checksum(status_data[2:]))
        return bytearray(status_data)

    def _write_data(self, p):
        try:
            control = CTRL_ADDR[(p.params[0], len(p.params)-1)]
        except KeyError:
            raise NotImplementedError # we don't support custom controls (yet)
        # write data appropriately
        values = _to_values(control, p.params[1:])
        offset = 0
        for size, value in zip(control.sizes, values):
            self.motor.mmem[control.addr+offset] = value
            offset += size
        self.motor.mmem.update()
        if self.motor.status_return_level == 2:
            raise NotImplementedError

    def _sync_write(self, p):
        try:
            control = CTRL_ADDR[(p.params[0], p.params[1])]
        except KeyError:
            raise NotImplementedError # we don't support custom controls (yet)

        params, offset = None, 2
        while offset < len(p.params):
            if p.params[offset] == self.motor.id:
                offset += 1
                params = p.params[offset:offset+sum(control.sizes)]
                break
            else:
                offset += 1 + sum(control.sizes)

        if params is not None:
            values = _to_values(control, params)
            offset = 0
            for size, value in zip(control.sizes, values):
                self.motor.mmem[control.addr+offset] = value
                offset += size
            self.motor.mmem.update()

    def _step(self):
        m = self.motor
        max_speed = limits.POSITION_RANGES[self.motor.modelclass][1]
        speed = m.moving_speed if m.moving_speed != 0 else max_speed
        if m.goal_position > m.present_position:
            self._present_position += min((self._timestep*speed), m.goal_position - m.present_position)
        else:
            self._present_position -= min((self._timestep*speed), abs(m.goal_position - m.present_position))
        m.mmem[pt.PRESENT_POSITION.addr] = conv.CONV[pt.PRESENT_POSITION][0](self._present_position,
                                                                             modelclass=m.modelclass,
                                                                                   mode=m.mode)
        self._motor_time += self._timestep

    def _update(self):
        now = time.time()
        while now > self._motor_time:
            self._step()


class KinPort(object):

    def __init__(self, motor):
        self.cable = None
        self.motor = motor

    def receive(self, msg):
        self.motor.receive(self, msg)

    def send(self, msg):
        if self.cable is not None:
            self.cable.transmit(self, msg)

class KinCable(object):

    def __init__(self, port1, port2):
        self.port1 = port1
        self.port1.cable = self
        self.port2 = port2
        self.port2.cable = self

    def transmit(self, sender_port, msg):
        if sender_port == self.port1:
            self.port2.receive(msg)
        else:
            self.port1.receive(msg)
