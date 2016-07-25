from regraa_dynamic_parametrization import *
from regraa_reactive_base import *

class ctrl_(event):
    def __init__(self, *args):
        event.__init__(self)
        self.ctrl_tuples = []
        for ctrl in args:            
            self.ctrl_tuples.append(ctrl)            
    def execute(self):
        for ctrl in self.ctrl_tuples:
            if type(ctrl) is tuple:
                ctrl[0](*ctrl[1:])
            elif callable(ctrl):
                ctrl()
    def update(self):
        pass


class wait_(event):
    def __init__(self):
        event.__init__(self)
    def execute(self):
        pass
    def update(self):
        pass

