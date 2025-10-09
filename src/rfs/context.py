
class calContext:
    def __init__(self):
        self.aruco_coords = None

    def set_id(self, id_position):
        self.aruco_coords = id_position
        print(self.aruco_coords)

    def get_id(self):
        return self.aruco_coords
