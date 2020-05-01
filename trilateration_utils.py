#! /usr/bin/python3

import math

def parse_measurements(filename, id):
    measurements = []

    with open(filename) as logfile:
        row = []
        
        rows = []

        for line in logfile:
            # print(line)

            if line[0:4] == "call":
                # print("start")
                if rows != []:
                    measurements.append(rows)
                    rows = []
                

            if line[2] == ':':
                if line[0:5] == "aa:69":
                    # print("rssi str", "aa:69", int(line[6:9]))
                    row[1] = int(line[6:9])

                if line[0:5] == "a4:a8":
                    # print("rssi str", "a4:a8", int(line[6:9]))
                    row[2] = int(line[6:9])


                if line[0:5] == "d9:ab":
                    # print("rssi str", "d9:ab", int(line[6:9]))
                    row[3] = int(line[6:9])


                if line[0:5] == "95:51":
                    # print("rssi str", "95:51", int(line[6:9]))
                    row[4] = int(line[6:9])

            elif line[0] == '[':
                # print("time", line[1:9])
                row = [line[1:9], 0, 0, 0, 0, 0, 0]

            elif line[0] == 'X':
                coordinate_str = line.split(": ")
                # print("coordinate str", coordinate_str)
                x_str = coordinate_str[1].split(";")[0]
                
                x = float(x_str)
                y = float(coordinate_str[2][:-1])

                row[5] = x
                row[6] = y

                # print("coordinate:", x, y)

                if row != []:
                    # print(str(row)[1:][:-1])
                    rows.append(row)

        for x, i in enumerate([x[-1][0] for x in measurements]):
            pass
            # print(x, i)

    measurement = measurements[id]
    measurements = [{"time": x[0], "rssi": [x[1], x[2], x[3], x[4]], "x": x[5], "y": x[5]} for x in measurement]

    return measurements

def circle_cross(oCircle1, oCircle2):
    # from https://litunovskiy.com/gamedev/intersection_of_two_circles/
    
    obj = dict(pos1=None, pos2=None, count=2)
    oPos1 = [0, 0]
    oPos2 = [oCircle2[0] - oCircle1[0], oCircle2[1] - oCircle1[1]]

    c = (oCircle2[2] * oCircle2[2] - oPos2[0] * oPos2[0] - oPos2[1] * oPos2[1] - oCircle1[2] * oCircle1[2]) / -2.0
    a = oPos2[0] * oPos2[0] + oPos2[1] * oPos2[1]
    if oPos2[0] != 0:
        b = -2 * oPos2[1] * c
        e = c * c - oCircle1[2] * oCircle1[2] * oPos2[0] * oPos2[0]
        D = b * b - 4 * a * e
        if D > 0:
            obj["pos1"] = [0, 0]
            obj["pos2"] = [0, 0]
            obj["pos1"][1] = (-b + math.sqrt(D)) / (2 * a)
            obj["pos2"][1] = (-b - math.sqrt(D)) / (2 * a)
            obj["pos1"][0] = (c - obj["pos1"][1] * oPos2[1]) / oPos2[0]
            obj["pos2"][0] = (c - obj["pos2"][1] * oPos2[1]) / oPos2[0]
        elif D == 0:
            obj["count"] = 1
            obj["pos1"] = [0, 0]
            obj["pos1"][1] = (-b + math.sqrt(D)) / (2 * a)
            obj["pos1"][0] = (c - obj["pos1"][1] * oPos2[1]) / oPos2[0]
        else:
            obj["count"] = 0
    else:
        D = oCircle1[2] * oCircle1[2] - (c * c) / (oPos2[1] * oPos2[1])
        if D > 0:
            obj["pos1"] = [0, 0]
            obj["pos2"] = [0, 0]
            obj["pos1"][0] = +Math.sqrt(D)
            obj["pos2"][0] = -Math.sqrt(D)
            obj["pos1"][1] = c / oPos2[1]
            obj["pos2"][1] = c / oPos2[1]
        elif D == 0:
            obj["count"] = 1
            obj["pos1"] = [0, 0]
            obj["pos1"][0] = 0
            obj["pos1"][1] = c / oPos2[1]
        else:
            obj["count"] = 0

    if obj["pos1"] != None:
        obj["pos1"][0] += oCircle1[0]
        obj["pos1"][1] += oCircle1[1]

    if obj["pos2"] != None:
        obj["pos2"][0] += oCircle1[0]
        obj["pos2"][1] += oCircle1[1]
    
    if obj["count"] == 0:
        return []
    elif obj["count"] == 1:
        return [obj["pos1"]]
    elif obj["count"] == 2:
        return [obj["pos1"], obj["pos2"]]
    else:
        return []

A = 0.7162624467
B = 8.195495665
C = 0.0894828774
ref = -59

def rssi2distance(rssi):
    return A * (rssi/ref)**B + C

def average_distance(distances, beacons):
    t_distances = [[distances[j][i] for j in range(len(distances))] for i in range(len(distances[0]))]
    
    res = []
    for beacon_distance in zip(t_distances, beacons):
        average = sum(beacon_distance[0])/float(len(beacon_distance[0]))
        res.append({
            "x": beacon_distance[1][0],
            "y": beacon_distance[1][1],
            "r": average,
            "var": math.sqrt(
                sum([(x - average)**2 for x in beacon_distance[0]])/
                float(len(beacon_distance[0]))
            )
        })

    return res

def add_point(center, size, color):
    return dict(
        type="circle",
        xref="x",
        yref="y",
        fillcolor=color,
        x0 = center[0] - size/2,
        y0 = center[1] - size/2,
        x1 = center[0] + size/2,
        y1 = center[1] + size/2,
        line=dict(width=0),
    )