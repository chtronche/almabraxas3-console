from kivy.garden.mapview import MapLayer, MapView
from kivy.graphics import *
from math import cos, pi, radians, sin

class _InMap:

    def __init__(self, bbox):
        self.y0, self.x0, self.y1, self.x1 = bbox

    def in_map(self, p):
        res = p[0] >= self.x0 and p[0] <= self.x1 and p[1] >= self.y0 and p[1] <= self.y1
        return res

class _Converter:

    def __init__(self, bbox, size):
        self.xa = float(size[0]) / (bbox[3] - bbox[1])
        self.xb = -self.xa * bbox[1]

        self.ya = float(size[1]) / (bbox[2] - bbox[0])
        self.yb = -self.ya * bbox[0]

    def convert(self, p, delta):
        return (p[0] * self.xa + self.xb - delta, p[1] * self.ya + self.yb - delta)

class AlmaNavLayer(MapLayer):

    def __init__(self, navPlan):
        super(AlmaNavLayer, self).__init__()
        self.navPlan = navPlan
        self.path = []
        self.convert = None
        with self.canvas:
            self.navPlanIG = InstructionGroup()
            self.pathIG = InstructionGroup()

    def _addPointGL(self):
        convert = self.convert
        if not convert: return
        path = self.path
        if len(path) < 2: return  # We need at least 2 points
        p0 = path[-2]
        p = path[-1]

        if not self.in_map(p0['point']) and not self.in_map(p['point']): return

        if len(path) > 4:
            rec = path.pop(0)
            deletedIG = rec.get('ig')
            if deletedIG:
                self.pathIG.remove(deletedIG)

        pos0 = convert(p0['point'], 5)
        pos = convert(p['point'], 5)
        
        centerx = pos[0] + 5
        centery = pos[1] + 5
        
        path[-1]['ig'] = ig = InstructionGroup()
        self.pathIG.add(ig)
        add = ig.add

        add(Color(0,0,0))
        add(Ellipse(pos=pos, size=(10,10)))
        add(Line(points=[pos0[0] + 5, pos0[1] + 5, centerx, centery], dash_offset=5, dash_length=2))

        theta = radians(90 - p['heading'])
        dx = 50 * cos(theta)
        dy = 50 * sin(theta)
        add(Color(0,0,1))
        add(Line(points=[centerx, centery, centerx + dx, centery + dy]))

        theta = radians(90 - p['targetHeading'])
        dx = 35 * cos(theta)
        dy = 35 * sin(theta)
        add(Color(1, 0.65, 0))
        add(Line(points=[centerx, centery, centerx + dx, centery + dy]))

    def addPoint(self, lon, lat, heading, targetHeading):
        self.path.append({
            'point': (lon, lat),
            'heading': heading,
            'targetHeading': targetHeading,
        })
        self._addPointGL()

    def reposition(self, *args):
        mapview = self.parent
        bbox = mapview.get_bbox()
        convert = self.convert = _Converter(bbox, mapview.size).convert
        in_map = self.in_map = _InMap(bbox).in_map
        self.navPlanIG.clear()
        self.pathIG.clear()

        add = self.navPlanIG.add
        add(Color(1,0,0))
        p0 = self.navPlan[0]
        pos0 = convert(p0, 5)
        for p in self.navPlan[1:]:
            pos = convert(p, 5)
            if not in_map(p0) and not in_map(p):
                p0 = p
                pos0 = pos
                continue
            add(Line(points=[pos0[0]+5, pos0[1]+5, pos[0]+5, pos[1]+5]))
            add(Rectangle(pos=pos,size=(10,10)))

            p0 = p
            pos0 = pos

        addPointGL = self._addPointGL
        p = self.path[:]
        self.path = []
        papp = self.path.append
        for point in p:
            papp(point)
            addPointGL()

