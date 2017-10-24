from simulation import Simulation
        
class PannableSimulation(Simulation):
    
    def __init__(self, width, height, rotation=0, title='PannableSimulation'):
        Simulation.__init__(self, width, height, rotation, title=title);
        self.initial_rotation = rotation;
        
    def loop(self):
        Simulation.loop(self);
    
    def pre_render(self):
        Simulation.pre_render(self);
    
    def render(self):
        Simulation.render(self);
    
    def done_rendering(self):
        Simulation.done_rendering(self);
    
    def key_down(self, event):
        Simulation.key_down(self, event);
        
    def key_up(self, event):
        Simulation.key_up(self, event);

    def key_event(self, keysyms):
        camera_speed = 50;
        rotation_speed = 2;
        if 'Left' in keysyms:
            self._canvas_pos = (self._canvas_pos[0] - camera_speed, self._canvas_pos[1]);
        if 'Up' in keysyms:
            self._canvas_pos = (self._canvas_pos[0], self._canvas_pos[1] - camera_speed);
        if 'Right' in keysyms:
            self._canvas_pos = (self._canvas_pos[0] + camera_speed, self._canvas_pos[1]);
        if 'Down' in keysyms:
            self._canvas_pos = (self._canvas_pos[0], self._canvas_pos[1] + camera_speed);
        if 'equal' in keysyms:
            self.zoom  = self.zoom + 1;
        if 'minus' in keysyms:
            self.zoom = max(-30, self.zoom - 1);
        if 'comma' in keysyms:
            self.rotation -= rotation_speed;
        if 'period' in keysyms:
            self.rotation += rotation_speed;
        if 'r' in keysyms:
            self.zoom = 0;
            self.set_canvas_pos(0, 0);
            self.rotation = self.initial_rotation;
        Simulation.key_event(self, keysyms);
        
    def get_instructions(self):
        instructions = Simulation.get_instructions(self);
        return instructions + [['Pan - Arrow keys',
                                'Rotate - </>',
                                'Zoom in - Plus',
                                'Zoom out - Minus',
                                'Reset view - R']];
    
    def get_status(self):
        status = Simulation.get_status(self);
        return status + [];
        