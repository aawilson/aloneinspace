class Rect(object):
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        return (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2

    def intersects(self, other):
        return (
            self.x1 <= other.x2 and
            self.x2 >= other.x1 and
            self.y1 <= other.y2 and
            self.y2 >= other.y1
        )


if __name__ == '__main__':
    rect1 = Rect(0, 0, 20, 20)
    rect2 = Rect(21, 20, 5, 5)
    rect3 = Rect(20, 20, 5, 5)

    assert not rect1.intersects(rect2)
    assert rect1.intersects(rect3)
    assert rect1.center() == (10, 10)
