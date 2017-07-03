import json
import numpy as np

class Base():

    def __init__(self, fp):
        d = {}
        e = {}
        f = {}
        with open(fp) as file:
            for line in file:
                line = json.loads(line)
                lineNo = line["number"]
                stns1 = np.array([[stn["lon"], stn["lat"]] for stn in line["stations1"]])
                stns2 = np.array([[stn["lon"], stn["lat"]] for stn in line["stations2"]])
                name1 = [stn["name"] for stn in line["stations1"]]
                name2 = [stn["name"] for stn in line["stations2"]]
                route1 = np.array([[stn["lon"], stn["lat"]] for stn in line["routes1"]])
                route2 = np.array([[stn["lon"], stn["lat"]] for stn in line["routes2"]])
                d[(lineNo, 0)] = stns1
                d[(lineNo, 1)] = stns2
                e[(lineNo, 0)] = route1
                e[(lineNo, 1)] = route2
                f[(lineNo, 0)] = name1
                f[(lineNo, 1)] = name2
        self.d = d
        self.e = e
        self.f = f

    def get_location(self, lineNo, dir, order):
        return self.d.get((lineNo, int(dir)), [None] * 100)[int(order)-1]

    def get_route(self, lineNo, dir):
        return self.e.get((lineNo, int(dir)))

    def get_stations(self, lineNo, dir):
        return np.array(self.d.get((lineNo, int(dir))))

    def get_station_name(self, lineNo, dir):
        return self.f.get((lineNo, int(dir)))

    def overlay_id(self, lineId, map, order=False):
        from chelaile.plotfuncs import plt,colors, fontset
        color = colors.pop()
        lineNo, direction = map.get_lineNo(lineId)
        route = self.e.get((lineNo, int(direction)))
        stns = self.d.get((lineNo, int(direction)))
        if route is None: return
        plt.plot(route[:,0], route[:,1], label = lineId, color = color, alpha = 0.3)
        plt.plot(stns[:,0], stns[:,1], "o", color = color, alpha = 0.3)
        plt.plot([route[0,0]], [route[0,1]], "s", color = color)
        if order:
            for i in range(len(stns)):
                plt.annotate(str(i+1), xy=stns[i])
        plt.legend(prop=fontset)
        plt.axis("equal")

    def overlay_no(self, lineNo, direction, so = False):
        from chelaile.plotfuncs import plt,colors, fontset
        color = colors.pop()
        route = self.e.get((lineNo, int(direction)))
        stns = self.d.get((lineNo, int(direction)))
        if route is None: return
        plt.plot(route[:,0], route[:,1], label = lineNo + "-" + str(direction), color = color, alpha = 0.3)
        plt.plot(stns[:,0], stns[:,1], "o", color = color, alpha = 0.3)
        plt.plot([route[0,0]], [route[0,1]], "s", color = color)
        plt.legend(prop=fontset)
        plt.axis("equal")
        if so:
            for i in range(len(stns)):
                plt.annotate(str(i+1), xy=stns[i])



class Map():
    def __init__(self, fp):
        d = {}
        e = {}
        with open(fp) as file:
            for line in file:
                line = line.strip("\n").split(",")
                d[(line[0], line[1])] = line[2]
                e[line[2]] = (line[0], line[1])
        self.d = d
        self.e = e

    def get_lineNo(self, lineId):
        return self.e.get(lineId, (None, None))

    def get_lineId(self, lineNo, direction):
        return self.d.get((lineNo, direction), None)