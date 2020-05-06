#! /usr/bin/python3

import math

import plotly.io as pio
import plotly.graph_objects as go

BEACON_SIZE = 0.1


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
            # pass
            print(x, i)

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
            obj["pos1"][0] = +math.sqrt(D)
            obj["pos2"][0] = -math.sqrt(D)
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


'''
name — string
result — [[x,y,var,color]]
position — [x,y]
'''
def draw_result(result, position, beacons=[], shapes=[]):
    TRUE_POINT_SIZE = 0.2
    # cross for true point
    shapes.append(dict(
        type="line",
        x0=position[0] - TRUE_POINT_SIZE/2,
        y0=position[1],
        x1=position[0] + TRUE_POINT_SIZE/2,
        y1=position[1],
        line=dict(color="#00BB00", width=2)
    ))

    # draw bounds
    if True:
        shapes.append(dict(
            type="circle",
            xref="x",
            yref="y",
            x0 = result[0] - result[2],
            y0 = result[1] - result[2],
            x1 = result[0] + result[2],
            y1 = result[1] + result[2],
            line=dict(width=1, color=result[3]),
        ))

    shapes.append(add_point(result[0:2], 0.1, result[3]))

    return shapes


def plot_shapes(name, beacons=[], shapes=[]):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[item[0] for item in beacons],
        y=[(item[1] + BEACON_SIZE) for item in beacons],
        text=["aa:69", "a4:a8", "d9:ab", "95:51"],
        mode="text",
    ))

    fig.update_xaxes(range=[-1, 5], zeroline=False)
    fig.update_yaxes(range=[-1, 5])

    fig.update_layout(shapes=shapes)
    fig.update_layout(width=800, height=800)

    # fig.show()

    fig.write_image(name + ".png")

def get_measurement_data(measurement_id, beacons, AVERAGING_STEP = 5):
    measurements = parse_measurements("full_measurement_logs_raw", measurement_id)
    # measurements = parse_measurements("full_measurement_logs_bedroom", measurement_id)

    raw_distance_maps = [
        [rssi2distance(rssi) for rssi in measurement["rssi"]] for measurement in measurements
    ]

    # print(len(raw_distance_maps))

    raw_distance_maps = [
        raw_distance_maps[i:i+AVERAGING_STEP]
        for i in range(0, len(raw_distance_maps), AVERAGING_STEP)
    ]

    distance_maps = [
        average_distance(
            raw_distance_map,
            beacons
        ) for raw_distance_map in raw_distance_maps
    ]

    return distance_maps

'''
beacons: [[x, y]]
room: [x, y]
'''
def draw_env(beacons, room, shapes=[]):
    # beacons
    for beacon in beacons:
        shapes.append(
            dict(
                type="circle",
                xref="x",
                yref="y",
                fillcolor="#002200",
                x0 = beacon[0] - BEACON_SIZE/2,
                y0 = beacon[1] - BEACON_SIZE/2,
                x1 = beacon[0] + BEACON_SIZE/2,
                y1 = beacon[1] + BEACON_SIZE/2,
                line=dict(width=0),
            )
        )


    # room
    shapes.append(
        dict(
            type="rect",
            xref="x",
            yref="y",
            x0=0,
            y0=0,
            x1=room[0],
            y1=room[1],
            line=dict(
                color="#AAAAFF",
                width=1,
            )
        )
    )

    return shapes

def draw_distance_map(distance_map, shapes=[]):
    for beacon in distance_map:
        r = beacon["r"]
        var = beacon["var"]

        # beacon distance var circle
        shapes.append(
            dict(
                type="circle",
                xref="x",
                yref="y",
                x0 = beacon["x"] - r,
                y0 = beacon["y"] - r,
                x1 = beacon["x"] + r,
                y1 = beacon["y"] + r,
                line=dict(width=var*200, color="rgba(127, 127, 127, 0.1)")
            )
        )

        # beacon distance circle
        shapes.append(
            dict(
                type="circle",
                xref="x",
                yref="y",
                x0 = beacon["x"] - r,
                y0 = beacon["y"] - r,
                x1 = beacon["x"] + r,
                y1 = beacon["y"] + r,
                line=dict(width=2),
            )
        )

    return shapes

def check_result(result, true_position, colors):
    error_distance = math.sqrt(
        (result[0] - true_position[0])**2 +
        (result[1] - true_position[1])**2
    )

    bound_color = colors[0] if error_distance < result[2] else colors[1]

    result.append(bound_color)

    return result