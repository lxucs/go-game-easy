class PointDict:
    def __init__(self):
        self.d = {'BLACK': {}, 'WHITE': {}}

    def get_groups(self, color, point):
        if point not in self.d[color]:
            self.d[color][point] = []
        return self.d[color][point]

    def set_groups(self, color, point, groups):
        self.d[color][point] = groups

    def remove_point(self, color, point):
        if point in self.d[color]:
            del self.d[color][point]

    def get_items(self, color):
        return self.d[color].items()
