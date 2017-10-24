import math

from simulation import Simulation
from camera_simulation import CameraSimulation
from locationencodingmodel import *
    
class ObservationSimulation(CameraSimulation):
    
    def __init__(self, width, height, rotation=0, location_encoding_model_type=RandomModel, title='ObservationSimulation', **kwargs):
        CameraSimulation.__init__(self, width, height, rotation, title=title);
        self.location_encoding_model = location_encoding_model_type(self.grid_width, self.grid_height, **kwargs);
        self.potential_groups = [];
        self.potential_locations = [];
        self.view_data = False;
        
    def render(self):
        CameraSimulation.render(self);
        
        scale = self.scale * Simulation.ZOOM_FACTOR ** self.zoom;
        edge = CameraSimulation.CELL_SIZE * scale;
        
        def highlight_square(i, j, fill='#bbbbbb'):
            tl = (float(self.width)/self.grid_width*(i), 
                  float(self.height)/self.grid_height*(j));
            tr = (tl[0] + CameraSimulation.CELL_SIZE, tl[1]);
            br = (tl[0] + CameraSimulation.CELL_SIZE, tl[1] + CameraSimulation.CELL_SIZE);
            bl = (tl[0], tl[1] + CameraSimulation.CELL_SIZE);
            center = (tl[0] + CameraSimulation.CELL_SIZE / 2, tl[1] + CameraSimulation.CELL_SIZE / 2);
            transformed = self.transform(center[0], center[1]);
            if transformed[0] + edge > 0 and transformed[0] - edge < self.canvas_width and transformed[1] + edge> 0 and transformed[1] - edge < self.canvas_height:
                points = [tl, tr, br, bl];
                self.draw_polygon(*(points + [points[0]]), fill=fill);
                
        cells = set();
        for potential_group in self.potential_groups:
            for cell in potential_group:
                cells.add(cell);
        for cell in cells:
            if cell not in self.visible:
                highlight_square(cell[0], cell[1]);
                
        for potential_location in self.potential_locations:
            self.draw_circle(*potential_location, radius=15 / max(1, Simulation.ZOOM_FACTOR ** self.zoom), fill='green');
        
        font_size_quadratic = int(math.sqrt(scale * CameraSimulation.CELL_SIZE * 6));
        font_size_linear = int(scale * CameraSimulation.CELL_SIZE * 0.4);
        font_size = min(font_size_linear, font_size_quadratic);
        if self.view_data and font_size >= 6:
            for i in range(self.grid_width):
                for j in range(self.grid_height):
                    center = (float(self.width)/self.grid_width*(i)
                              + CameraSimulation.CELL_SIZE / 2, 
                              float(self.height)/self.grid_height*(j)
                              + CameraSimulation.CELL_SIZE / 2);
                    transformed = self.transform(center[0], center[1]);
                    if transformed[0] + edge > 0 and transformed[0] - edge < self.canvas_width and transformed[1] + edge> 0 and transformed[1] - edge < self.canvas_height:
                        self.canvas.create_text(transformed[0], transformed[1],
                                                text=self.location_encoding_model.observe((i, j)),
                                                font=(None, font_size));
            
    def on_view(self, changed):
        self.potential_groups = [];
        self.potential_locations = [];
        
        if len(self.visible):
            #print ', '.join(map(lambda x: str(self.location_encoding_model.observe(x)) + ' ' + str(x), self.visible));

            group = list(self.visible);
            master = group[0];
            
            observed = map(lambda x: x * CameraSimulation.CELL_SIZE, group[0]);
            self.observation_offset = (observed[0] - self.location[0], observed[1] - self.location[1]);

            data = self.location_encoding_model.observe(master);
            possibilities = set(self.location_encoding_model.lookup(data));

            for i in range(1, len(group)):
                di = group[i][0] - master[0];
                dj = group[i][1] - master[1];
                d = self.location_encoding_model.observe(group[i]);
                impossibilities = set();
                for possibility in possibilities:
                    if self.location_encoding_model.observe((possibility[0] + di, possibility[1] + dj)) != d:
                        impossibilities.add(possibility);
                for impossibility in impossibilities:
                    possibilities.remove(impossibility);

            for i, j in possibilities:
                potential_group = [];
                for k in range(0, len(group)):
                    di = group[k][0] - master[0];
                    dj = group[k][1] - master[1];
                    potential_group.append((i + di, j + dj));
                self.potential_groups.append(potential_group);
            
            for group in self.potential_groups:
                self.potential_locations.append((group[0][0] * CameraSimulation.CELL_SIZE - self.observation_offset[0], 
                                                 group[0][1] * CameraSimulation.CELL_SIZE - self.observation_offset[1]));
            
    def key_down(self, event):
        if event.keysym == 'v':
            self.view_data = not self.view_data;
        CameraSimulation.key_down(self, event);
        
    def key_event(self, keysyms):
        CameraSimulation.key_event(self, keysyms);
        
    def get_instructions(self):
        instructions = CameraSimulation.get_instructions(self);
        return instructions + [['Toggle view data - V']];
    
    def get_status(self):
        status = CameraSimulation.get_status(self);
        return status + [['Observation offset: ' + str(map(int, self.observation_offset) if len(self.potential_locations) else [0, 0]),
                          'Matching locations: ' + str(len(self.potential_locations) or '--')]];
    