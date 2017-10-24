import math

from pannable_simulation import PannableSimulation
        
class CameraSimulation(PannableSimulation):
    
    VIEW_SIZE = 60; #100
    CELL_SIZE = 40; #40
    
    def __init__(self, width, height, rotation=0, title='Simulation'):
        PannableSimulation.__init__(self, width, height, rotation, title=title);
        self.location = (550, 450);
        self.orientation = -rotation;
        self.view_size = CameraSimulation.VIEW_SIZE;
        self.grid_width = width / CameraSimulation.CELL_SIZE;
        self.grid_height = height / CameraSimulation.CELL_SIZE;
        self.visible = set();
        self.keep_centered = False;
        
    def loop(self):
        if self.keep_centered:
            transformed = self.rotate_transform(self.location[0], self.location[1]);
            self.set_canvas_pos(transformed[0] - self.width / 2, transformed[1] - self.height / 2);
        PannableSimulation.loop(self);
        
    def pre_render(self):
        PannableSimulation.pre_render(self);
        
        points = self.get_world_coordinates();
        self.draw_polygon(*(points + [points[0]]), fill='#1294fc', width=2);
        
        for i, j in self.visible:
            tl = (float(self.width)/self.grid_width*(i),
                  float(self.height)/self.grid_height*(j));
            tr = (tl[0] + CameraSimulation.CELL_SIZE, tl[1]);
            br = (tl[0] + CameraSimulation.CELL_SIZE, tl[1] + CameraSimulation.CELL_SIZE);
            bl = (tl[0], tl[1] + CameraSimulation.CELL_SIZE);
            points = [tl, tr, br, bl];
            self.draw_polygon(*(points + [points[0]]), fill='#48d593');
    
    def render(self):
        PannableSimulation.render(self);
        
        points = self.get_world_coordinates();
        self.draw_grid();
            
    def done_rendering(self):
        points = self.get_world_coordinates();
        self.draw_polygon(*(points + [points[0]]), width=2);
        PannableSimulation.done_rendering(self);
                    
    def draw_grid(self):
        for i in range(self.grid_width - 1):
            self.draw_line(float(self.width)/self.grid_width*(i+1), 0, float(self.width)/self.grid_width*(i+1), self.height, outline='black', dash=(1, 5));
        for i in range(self.grid_height - 1):
            self.draw_line(0, float(self.height)/self.grid_height*(i+1), self.width, float(self.height)/self.grid_height*(i+1), outline='black', dash=(1, 5));
        
    def get_world_coordinates(self):
        x, y = self.location;
        s = self.view_size / 2;
        points = [(x - s, y - s), (x + s, y - s), (x + s, y + s), (x - s, y + s)];
        points = map(lambda x: self.rotate_transform(x[0], x[1], rotation=self.orientation, about=self.location), points);
        return points;
    
    def update_visible(self):
        old_visible = set(self.visible);
        self.visible = set();
        vs = self.view_size / 2 * 1.5;
        transformed = self.rotate_transform(self.location[0], self.location[1], rotation=self.orientation);
        x, y = self.location;
        s = self.view_size / 2 * math.sqrt(2);
        low_i = max(0, int(math.floor(float(x - s) / CameraSimulation.CELL_SIZE)));
        high_i = min(int(math.ceil(float(x + s) / CameraSimulation.CELL_SIZE)), self.grid_width - 1);
        low_j = max(0, int(math.floor(float(y - s) / CameraSimulation.CELL_SIZE)));
        high_j = min(int(math.ceil(float(y + s) / CameraSimulation.CELL_SIZE)), self.grid_height - 1);
        
        for i in range(low_i, high_i + 1):
            for j in range(low_j, high_j + 1):
                tl = (float(self.width)/self.grid_width*(i), float(self.height)/self.grid_height*(j));
                tr = (tl[0] + CameraSimulation.CELL_SIZE, tl[1]);
                br = (tl[0] + CameraSimulation.CELL_SIZE, tl[1] + CameraSimulation.CELL_SIZE);
                bl = (tl[0], tl[1] + CameraSimulation.CELL_SIZE);
                bounds = map(lambda x: self.rotate_transform(x[0], x[1], rotation=self.orientation), [tl, tr, br, bl]);
                xs = map(lambda x: x[0], bounds);
                ys = map(lambda x: x[1], bounds);
                if min(xs) >= transformed[0] - vs and max(xs) < transformed[0] + vs and min(ys) >= transformed[1] - vs and max(ys) < transformed[1] + vs:
                    self.visible.add((i, j));
        
        self.on_view(self.visible != old_visible);
            
    def on_view(self, changed):
        if len(self.visible):
            print ', '.join(map(lambda x: str(x), self.visible));
            
    def key_down(self, event):
        if event.keysym == 'c':
            self.keep_centered = not self.keep_centered;
        PannableSimulation.key_down(self, event);
    
    def key_event(self, keysyms):
        instrument_speed = 35;
        rotation_speed = 2;
        canvas_pos = self.get_canvas_pos();
        offset = self.rotate_transform(self.location[0], self.location[1]);
        offset = (-offset[0] + self.width / 2 + canvas_pos[0],
                  -offset[1] + self.height / 2 + canvas_pos[1]);
        old_orientation = self.orientation;
        old_location = tuple(self.location);
        old_view_size = self.view_size;
        rads = -math.radians(self.rotation);
        if 'a' in keysyms:
            self.location = (self.location[0] - instrument_speed * math.cos(rads),
                             self.location[1] - instrument_speed * math.sin(rads));
        if 'w' in keysyms:
            self.location = (self.location[0] + instrument_speed * math.sin(rads),
                             self.location[1] - instrument_speed * math.cos(rads));
        if 'd' in keysyms:
            self.location = (self.location[0] + instrument_speed * math.cos(rads),
                             self.location[1] + instrument_speed * math.sin(rads));
        if 's' in keysyms:
            self.location = (self.location[0] - instrument_speed * math.sin(rads),
                             self.location[1] + instrument_speed * math.cos(rads));
        if 'q' in keysyms:
            self.orientation -= rotation_speed;
            self.rotation += rotation_speed;
            transformed = self.rotate_transform(self.location[0], self.location[1]);
            self.set_canvas_pos(transformed[0] - self.width / 2 + offset[0], transformed[1] - self.height / 2 + offset[1]);
        if 'e' in keysyms:
            self.orientation += rotation_speed;
            old_offset = self.transform(*self.location);
            self.rotation -= rotation_speed;
            transformed = self.rotate_transform(self.location[0], self.location[1]);
            self.set_canvas_pos(transformed[0] - self.width / 2 + offset[0], transformed[1] - self.height / 2 + offset[1]);
        if 'o' in keysyms:
            self.view_size = max(40, self.view_size - 10);
        if 'i' in keysyms:
            self.view_size = self.view_size + 10;
        if old_location != self.location or old_orientation != self.orientation or old_view_size != self.view_size:
            self.update_visible();
        if old_location != self.location:
            translation = (self.location[0] - old_location[0], self.location[1] - old_location[1]);
            self.on_move(translation);
        if old_orientation != self.orientation:
            rotation = self.orientation - old_orientation;
            self.on_rotate(rotation);
        PannableSimulation.key_event(self, keysyms);
        
    def on_move(self, translation):
        pass;
        
    def on_rotate(self, rotation):
        pass;
        
    def get_instructions(self):
        instructions = PannableSimulation.get_instructions(self);
        return instructions + [['Move instrument - A/S/D/W',
                                'Rotate instrument - Q/E',
                                'Increase field of view - I',
                                'Decrease field of view - O',
                                'Toggle snap to center - C']];
    
    def get_status(self):
        status = PannableSimulation.get_status(self);
        status[0].insert(0, 'Grid size: ' + str(self.grid_width) + ' x ' + str(self.grid_height));
        return status + [['Camera orientation: ' + str(self.orientation),
                          'Observation size: ' + str(len(self.visible)),
                          'Field of view: ' + str(self.view_size),
                          'Camera pos: ' + str(map(int, self.location))]];
    