import math
import numpy as np
from sklearn import mixture

from simulation import Simulation
from observation_simulation import ObservationSimulation
from locationencodingmodel import *
from mcl import MCL

class MCLSimulation(ObservationSimulation):
    
    def __init__(self, width, height, rotation=0, location_encoding_model_type=RandomModel, title='MCLSimulation', **kwargs):
        ObservationSimulation.__init__(self, width, height, rotation, location_encoding_model_type=location_encoding_model_type, title=title);
        self.mcl = MCL(1000, (self.width, self.height));
        self.auto_mcl = True;
        self.update_on_view_change_only = True;
        self.view_particles = True;
        self.mixture = [];
        #self.reset_particles();
    
    def render(self):
        
        for i in range(len(self.mixture)):
            weight, mean, covariance = self.mixture[i];
            if weight >= self.mixture_mean_weight / 2:
                v, w = np.linalg.eigh(covariance);
                v = 2.0 * np.sqrt(2) * np.sqrt(v);
                u = w[0] / np.linalg.norm(w[0]);
                rads = np.arctan(u[1] / u[0])
                points = poly_oval(mean[0] - v[0] / 2, mean[1] - v[1] / 2, mean[0] + v[0] / 2, mean[1] + v[1] /2, steps=20, rads=rads);
                self.draw_polygon(*points, fill='#F' + str(9 - int(weight * 10)) * 2, outline='');
        
        ObservationSimulation.render(self);
        
        if self.view_particles:
            radius = 8 / max(1, Simulation.ZOOM_FACTOR ** self.zoom);
            line_length = 30 / max(1, Simulation.ZOOM_FACTOR ** self.zoom);
            max_weight_scale = 3;

            x, y = self.location;
            s = self.view_size / 2;
            points = [(x + s, y), (x + s + line_length * 1.5, y)];
            points = map(lambda x: self.rotate_transform(*x, rotation=self.orientation, about=self.location), points);
            self.draw_line(points[0][0], points[0][1], points[1][0], points[1][1], width=2);

            max_weight = self.mcl.get_max_weight();
            min_weight = self.mcl.get_min_weight();
            count = 0;
            for particle in self.mcl.get_particles():
                count += 1;
                if (self.count + count) % 1 != 0:
                    continue;
                particle_scale = (particle.get_weight() - min_weight) / max_weight;
                radius_scale = max(1, (particle_scale) * max_weight_scale);
                
                position = particle.get_position();
                orientation_offset = particle.get_orientation_offset();
                
                self.draw_circle(position[0], position[1], radius * radius_scale, fill='red', outline='');
                line_offset = self.rotate_transform(radius * radius_scale, 0, rotation=(self.orientation - orientation_offset[0]), about=(0, 0));
                
                self.draw_line(position[0] + line_offset[0], position[1] + line_offset[1], *self.rotate_transform(position[0] + radius + line_length, position[1], rotation=(self.orientation - orientation_offset[0]), about=position))
    
    def reset_particles(self):
        for particle in self.mcl.particles:
            particle.set_position(self.location);
            particle.set_orientation_offset([0]);
    
    def on_move(self, translation):
        self.mcl.translate(*translation);
        if self.auto_mcl:
            self.mcl.update_weights(self.potential_locations);
    
    def on_rotate(self, rotation):
        self.mcl.rotate(rotation);
        
    def on_view(self, changed):
        ObservationSimulation.on_view(self, changed);
        self.update_gaussians();
        if len(self.visible) and (changed or not self.update_on_view_change_only) and self.auto_mcl:
            #print ', '.join(map(lambda x: str(self.location_encoding_model.observe(x)) + ' ' + str(x), self.visible));
            self.mcl.resample();
            self.mcl.update_weights(self.potential_locations);
    
    def update_gaussians(self):
        mix = mixture.BayesianGaussianMixture(n_components=4);
        mix.fit(self.mcl.get_positions());
        self.mixture = sorted(zip(mix.weights_, mix.means_, mix.covariances_));
        self.mixture_mean_weight = np.mean(mix.weights_);
            
    def key_down(self, event):
        if event.keysym == 'm':
            self.auto_mcl = not self.auto_mcl;
        if event.keysym == 'b':
            self.view_particles = not self.view_particles;
        if event.keysym == 'j':
            self.mcl.resample();
        if event.keysym == 't':
            self.location = tuple(np.random.rand(2) * (self.width, self.height));
        ObservationSimulation.key_down(self, event);
        
    def key_event(self, keysyms):
        if 'x' in keysyms:
            self.reset_particles();
        if 'u' in keysyms:
            self.mcl.update_weights(self.potential_locations);
        ObservationSimulation.key_event(self, keysyms);
        
    def get_instructions(self):
        instructions = ObservationSimulation.get_instructions(self);
        return instructions + [['Toggle auto MCL - M',
                                'Toggle view particles - B',
                                'Update particle weights - U',
                                'Resample particles - J',
                                'Reset particles - X',
                                'Teleport away - T']];
    
    def get_status(self):
        status = ObservationSimulation.get_status(self);
        return status + [['Rotation error: ' + str(self.mcl.rotation_error),
                          'Translation error: ' + str((self.mcl.translation_magnitude_error, self.mcl.translation_direction_error)),
                          'Variance: ' + str(self.mcl.get_variance()),
                          'Particles: ' + str(len(self.mcl.particles))]];
    
    
def poly_oval(x0, y0, x1, y1, steps=20, rads=0):
    points = []
    a = (x1 - x0) / 2.0;
    b = (y1 - y0) / 2.0;
    xc = x0 + a;
    yc = y0 + b;

    for i in range(steps):
        theta = (math.pi * 2) * (float(i) / steps);
        x1 = a * math.cos(theta);
        y1 = b * math.sin(theta);
        x = (x1 * math.cos(rads)) + (y1 * math.sin(rads));
        y = (y1 * math.cos(rads)) - (x1 * math.sin(rads));
        points.append((round(x + xc), round(y + yc)));

    return points;