class DetectionRegion:
    def __init__(self):
        self.points = []

    def set_points(self, x, y):
        point = (x, y)
        self.points.append(point)

    def is_point_inside(self, test_point):
        n = len(self.points)
        is_inside = False
        x, y = test_point

        for i in range(n):
            x1, y1 = self.points[i]
            x2, y2 = self.points[(i + 1) % n]

            # 判断射线是否与当前边相交
            if (y1 > y) != (y2 > y):  # 确保测试点在当前边的y坐标范围内
                intersect_x = (x2 - x1) * (y - y1) / (y2 - y1) + x1
                if x < intersect_x:  # 判断射线是否穿过边
                    is_inside = not is_inside
        return is_inside

