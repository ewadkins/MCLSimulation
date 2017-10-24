from Tkinter import *
import math
import numpy as np
import itertools
import cv2
from pyscreenshot import grab
import time

class Simulation:
    
    MAX_CANVAS_WIDTH = 1200;
    MAX_CANVAS_HEIGHT = 800;
    ZOOM_FACTOR = 21.0 / 20;
    TARGET_FPS = 20;
    
    def __init__(self, width, height, rotation=0, title='Simulation'):
        self.width = width;
        self.height = height;
        self.rotation = rotation;
        self.init_canvas();
        self.root.title(title);
        self.zoom = 0;
        self.pressed_set = set();
        self.timestamp_memory = 10;
        self.timestamps = [time.time()] * self.timestamp_memory;
        self.fps = Simulation.TARGET_FPS;
        self.max_render_skips = 5;
        self.count = 0;
        self.render_skips = 1;
        self.video = None;
        self.recording = False;
        self.recording_start = 0.0;
        self.recording_stop = 0.0;
        
        scale = self.scale * Simulation.ZOOM_FACTOR ** self.zoom;
        self.canvas_balance_offset = ((self.canvas_width - 1) / 2 * (1 - scale) / scale,
                                      (self.canvas_height - 1) / 2 * (1 - scale) / scale);
        self._canvas_pos = tuple(self.canvas_balance_offset);
        
        self.root.after(0, self._loop);
        
    def _loop(self):
        if self.count % 4 == 0:
            self.render_skips = min(int(max(1, Simulation.TARGET_FPS / self.fps)), self.max_render_skips);
        decrement_attempt = self.count % 16 == 0;
        if decrement_attempt:
            self.render_skips = max(1, self.render_skips - 1);
        if self.count % self.render_skips == 0 or self.recording or decrement_attempt:
            timestamp = time.time();
            self.fps = 1.0/(timestamp - self.timestamps.pop(0)) * self.timestamp_memory;
            self.timestamps.append(timestamp);
        self.count += 1;
        
        self.fire_key_events();
        self.loop();
        
        if self.count % self.render_skips == 0 or self.recording:
            self.clear();
            self.pre_render();
            self.render();
            self.done_rendering();
            
        self.root.after(1, self._loop);
        
    def loop(self):
        pass;
        
    def init_canvas(self):
        corners = map(lambda x: self.rotate_transform(x[0], x[1]), 
                      [(0, 0),
                       (self.width, 0),
                       (self.width, self.height),
                       (0, self.height)]);
        xs = map(lambda x: x[0], corners);
        ys = map(lambda x: x[1], corners);
        min_margin = 0.15;
        #self.adjusted_width = max(max(xs) - min(xs), (1 + min_margin) * self.width);
        #self.adjusted_height = max(max(ys) - min(ys), (1 + min_margin) * self.height);
        margin = max(max(xs) - min(xs), max(ys) - min(ys)) * min_margin;
        self.adjusted_width = max(xs) - min(xs) + margin;
        self.adjusted_height = max(ys) - min(ys) + margin;
        
        self.init_scale();
        self.root = Tk();
        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)
        self.canvas = Canvas(self.root,
                             width=self.canvas_width, 
                             height=self.canvas_height,
                             background='gray');
        self.canvas.pack();
        
    def init_scale(self):
        desired_width = Simulation.MAX_CANVAS_WIDTH;
        desired_height = Simulation.MAX_CANVAS_HEIGHT;
        self.scale = min(float(desired_width)/self.adjusted_width,
                         float(desired_height)/self.adjusted_height);
        self.canvas_width = self.adjusted_width * self.scale + 1;
        self.canvas_height = self.adjusted_height * self.scale + 1;
        self.x_offset = self.scale * float(self.adjusted_width - self.width) / 2 + 3;
        self.y_offset = self.scale * float(self.adjusted_height - self.height) / 2 + 3;
                            
    def clear(self):
        self.canvas.delete('all');
        
    def pre_render(self):
        # Render border
        self.draw_polygon((0, 0), (self.width, 0), (self.width, self.height), (0, self.height), fill='white');
        self.canvas.create_text(10, 15, text='Controls:', anchor='w', font=(None, 16));
        instructions = self.get_instructions();
        statuses = self.get_status();
        col = 0;
        offset = 100;
        kerning = 6;
        col_spacing = 20;
        lines_per_group = 5;
        for instruction_set in instructions:
            max_width = 0;
            for i in range(len(instruction_set)):
                if i % lines_per_group == 0 and i > 0:
                    offset += kerning * max_width + col_spacing;
                    max_width = 0;
                    col += 1;
                max_width = max(max_width, len(instruction_set[i]));
                self.canvas.create_text(offset, 15 + 10 * (i % lines_per_group), text=instruction_set[i], anchor='w', font=('monaco', 10));
            offset += kerning * max_width + col_spacing;
            col += 1;
            
        offset = 10;
        for status_set in statuses:
            max_width = 0;
            for i in range(len(status_set)):
                if i % lines_per_group == 0 and i > 0:
                    offset += kerning * max_width + col_spacing;
                    max_width = 0;
                    col += 1;
                max_width = max(max_width, len(status_set[i]));
                self.canvas.create_text(offset, self.canvas_height - 10 - 10 * (i % lines_per_group), text=status_set[i], anchor='w', font=('monaco', 10));
            offset += kerning * max_width + col_spacing;
            col += 1;
            
    def render(self):
        pass
        
    def done_rendering(self):
        self.draw_polygon((0, 0), (self.width, 0), (self.width, self.height), (0, self.height));
        self.root.update();
        if self.recording:
            self.recording_stop = time.time();
            print 'RECORDING ' + str(np.round(self.recording_stop - self.recording_start, 1)) + 's';
            bbox = self.get_bbox();
            img = grab(bbox);
            img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR);
            if self.video is None:
                height, width, _ = np.shape(img);
                self.video = cv2.VideoWriter('video' + str(int(time.time())) + '.mp4', -1, 20, (width, height), True);
            self.video.write(img);
    
    def draw_line(self, x1, y1, x2, y2, **kwargs):
        self.draw_polygon((x1, y1), (x2, y2), **kwargs);
    
    def draw_polygon(self, *points, **kwargs):
        kwargs['fill'] = kwargs.get('fill', '');
        kwargs['outline'] = kwargs.get('outline', 'black');
        points = map(lambda p: self.transform(p[0], p[1]), points);
        points = list(itertools.chain(*points));
        self.canvas.create_polygon(*points, **kwargs);
    
    def draw_circle(self, x, y, radius=1, transformed=True, **kwargs):
        x, y = self.transform(x, y);
        radius *= self.scale * Simulation.ZOOM_FACTOR ** self.zoom;
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, **kwargs);
        
    def transform(self, x, y):
        x, y = self.rotate_and_scale(x, y);
        
        scaled_x_offset = self.x_offset * Simulation.ZOOM_FACTOR ** self.zoom;
        scaled_y_offset = self.y_offset * Simulation.ZOOM_FACTOR ** self.zoom;
        
        x -= self._canvas_pos[0];
        y -= self._canvas_pos[1];
            
        return x + scaled_x_offset, y + scaled_y_offset;
    
    def rotate_and_scale(self, x, y):
        x, y = self.rotate_transform(x, y);
        x, y = self.scale_transform(x, y);
        return x, y;
    
    def rotate_transform(self, x, y, rotation=None, about=None):
        if rotation is None:
            rotation = self.rotation;
        if about is None:
            about = (self.width / 2.0, self.height / 2.0);
        x, y = x - about[0], y - about[1];
        rads = math.radians(rotation)
        x, y = x * math.cos(rads) + y * -math.sin(rads), x * math.sin(rads) + y * math.cos(rads);
        x, y = x + about[0], y + about[1];
        return x, y;
    
    def scale_transform(self, x, y, scale=None, about=None):
        if scale is None:
            scale = self.scale * Simulation.ZOOM_FACTOR ** self.zoom;
        if about is None:
            about = (self._canvas_pos[0] + self.canvas_width / 2,
                     self._canvas_pos[1] + self.canvas_height / 2);
        x, y = x - about[0], y - about[1];
        x, y = x * scale, y * scale;
        x, y = x + about[0], y + about[1];
        return x, y;
    
    def set_canvas_pos(self, x, y):
        self._canvas_pos = (x + self.canvas_balance_offset[0], y + self.canvas_balance_offset[1]);
        
    def get_canvas_pos(self):
        return self._canvas_pos[0] - self.canvas_balance_offset[0], self._canvas_pos[1] - self.canvas_balance_offset[1];
    
    def key_down(self, event):
        self.pressed_set.add(event.keysym);
        # Immediate response
        if event.keysym == 'Escape' or event.keysym == 'Return':
            sys.exit();
        if event.keysym == 'p':
            self.screenshot();
        if event.keysym == 'l':
            if self.recording:
                self.stop_recording();
            else:
                self.start_recording();
        
    def key_up(self, event):
        self.pressed_set.remove(event.keysym);
    
    def fire_key_events(self):
        self.key_event(self.pressed_set);

    def key_event(self, keysyms):
        pass;
            
    def screenshot(self):
        timestamp = int(time.time());
        bbox = self.get_bbox();
        img = grab(bbox);
        img.save('screenshot' + str(timestamp) + '.png', 'png');
        print 'screenshot' + str(timestamp) + '.png';
        
    def get_bbox(self):
        return self.root.winfo_x(), self.root.winfo_y() + 22, self.canvas_width + 6, self.canvas_height + 6;
        
    def start_recording(self):
        self.recording = True;
        self.recording_start = time.time();
        
    def stop_recording(self):
        self.recording = False;
        self.video.release();
        self.video = None;
            
    def get_instructions(self):
        return [['Exit - Esc', 
                 'Screenshot - P']];
            
    def get_status(self):
        return [['Canvas size: ' + str(int(self.canvas_width)) + ' x ' + str(int(self.canvas_height)),
                 'World size: ' + str(int(self.width)) + ' x ' + str(int(self.height)),
                 'FPS: ' + str(int(self.fps * 10) / 10.0,) + ' (\\' + str(1 if self.recording else self.render_skips) + ')'],
                ['Rotation: ' + str(self.rotation),
                 'Zoom: ' + str(self.zoom),
                 'Scale: ' + str(self.scale * Simulation.ZOOM_FACTOR ** self.zoom),
                 'Canvas pos: ' + str(map(int, self.get_canvas_pos()))]];
        