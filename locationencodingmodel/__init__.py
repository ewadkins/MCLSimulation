import random

class LocationEncodingModel:
    
    def __init__(self, n, m):
        self.n = n;
        self.m = m;
        self.cell_data_map = {};
        self.data_cell_map = {};
        for i in range(n):
            for j in range(m):
                data = self.generate(i, j);
                self.cell_data_map[(i, j)] = data;
                self.data_cell_map[data] = self.data_cell_map.get(data, []) + [(i, j)];
        
    def observe(self, cell):
        return self.cell_data_map.get(cell, None);
    
    def lookup(self, data):
        return self.data_cell_map.get(data, []);
    
class RandomModel(LocationEncodingModel):
    
    def __init__(self, n, m, k=128):
        self.k = k;
        LocationEncodingModel.__init__(self, n, m);
    
    def generate(self, i, j):
        return random.randrange(self.k);
    
class ModuloModel(LocationEncodingModel):
    
    def __init__(self, n, m, k=64):
        self.k = k;
        LocationEncodingModel.__init__(self, n, m);
    
    def generate(self, i, j):
        return (j * self.n + i) % self.k;
