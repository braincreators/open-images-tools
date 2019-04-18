def get_column(row, header_to_idx, column_name):\
    return row[header_to_idx[column_name]]


def get_bbox(row, header_to_idx, width, height):
    x1 = int(float(get_column(row, header_to_idx, 'XMin')) * width)
    y1 = int(float(get_column(row, header_to_idx, 'YMin')) * height)
    x2 = int(float(get_column(row, header_to_idx, 'XMax')) * width)
    y2 = int(float(get_column(row, header_to_idx, 'YMax')) * height)

    return BBox(x1, y1, x2, y2)


class BBox:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def to_list(self, mode='xyxy'):
        if mode == 'xyxy':
            return [self.x1, self.y1, self.x2, self.y2]
        elif mode == 'xywh':
            return [self.x1, self.y1, self.x2 - self.x1, self.y2 - self.y1]
        else:
            raise ValueError("Invalid Mode: {}".format(mode))

    def area(self):
        return self.x2 - self.x1 * self.y2 - self.y1
