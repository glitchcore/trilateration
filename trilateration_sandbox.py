#! /usr/bin/python3

import math
import time

from trilateration_utils import *

import plotly.io as pio
import plotly.graph_objects as go

fig = go.Figure()
shapes = []

tilateration_debug = False

def trilateration(distance_map, room):
    for beacon in distance_map:
        r = beacon["r"]
        var = beacon["var"]

        # beacon distance var circle
        if False:
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

    # circle crosses
    crosses_id = [[0, 1], [1, 2], [0, 2]]

    crosses = []

    for id in crosses_id:

        a = distance_map[id[0]]
        b = distance_map[id[1]]
        
        # cross for average
        cross_set = circle_cross(
            [a["x"], a["y"], a["r"]],
            [b["x"], b["y"], b["r"]]
        )

        deviation = math.sqrt(a["var"]**2 + b["var"]**2) * 1.4

        if cross_set == []:
            cross_set = [[
                (a["x"] * b["r"] + b["x"] * a["r"]) / (a["r"] + b["r"]),
                (a["y"] * b["r"] + b["y"] * a["r"]) / (a["r"] + b["r"])
            ]]

        cross_set = [[x[0], x[1], deviation] for x in cross_set]

        crosses.append(cross_set)

        # draw crosses and var bound
        if tilateration_debug:
            for cross in cross_set:
                shapes.append(add_point(cross, 0.05, "#AA00AA"))

                shapes.append(
                    dict(
                        type="circle",
                        xref="x",
                        yref="y",
                        x0 = cross[0] - cross[2],
                        y0 = cross[1] - cross[2],
                        x1 = cross[0] + cross[2],
                        y1 = cross[1] + cross[2],
                        line=dict(width=1, color="#AA00AA"),
                    )
                )

    results = []

    for cross_0 in crosses[0]:
        for cross_1 in crosses[1]:
            for cross_2 in crosses[2]:
                # draw triangles
                if tilateration_debug:
                    shapes.append(dict(
                        type="line",
                        x0=cross_0[0],
                        y0=cross_0[1],
                        x1=cross_1[0],
                        y1=cross_1[1],
                        line=dict(color="RoyalBlue", width=1)
                    ))

                    shapes.append(dict(
                        type="line",
                        x0=cross_1[0],
                        y0=cross_1[1],
                        x1=cross_2[0],
                        y1=cross_2[1],
                        line=dict(color="RoyalBlue", width=1)
                    ))

                    shapes.append(dict(
                        type="line",
                        x0=cross_2[0],
                        y0=cross_2[1],
                        x1=cross_0[0],
                        y1=cross_0[1],
                        line=dict(color="RoyalBlue", width=1)
                    ))

                triangle_center = [
                    sum([cross_0[0], cross_1[0], cross_2[0]])/3.0,
                    sum([cross_0[1], cross_1[1], cross_2[1]])/3.0
                ]

                triangle_r = max([
                    math.sqrt(
                        (triangle_center[0] - cross_0[0])**2 +
                        (triangle_center[1] - cross_0[1])**2
                    ) + cross_0[2],
                    math.sqrt(
                        (triangle_center[0] - cross_1[0])**2 +
                        (triangle_center[1] - cross_1[1])**2
                    ) + cross_1[2],
                    math.sqrt(
                        (triangle_center[0] - cross_2[0])**2 +
                        (triangle_center[1] - cross_2[1])**2
                    ) + cross_2[2]
                ])

                if tilateration_debug:
                    shapes.append(
                        dict(
                            type="circle",
                            xref="x",
                            yref="y",
                            x0 = triangle_center[0] - triangle_r,
                            y0 = triangle_center[1] - triangle_r,
                            x1 = triangle_center[0] + triangle_r,
                            y1 = triangle_center[1] + triangle_r,
                            line=dict(width=1, color="#AAAA00"),
                        )
                    )

                    shapes.append(add_point(triangle_center, 0.05, "#0000FF"))

                if triangle_center[0] > 0.0 and triangle_center[0] < room[0]:
                    if triangle_center[1] > 0.0 and triangle_center[1] < room[1]:
                        results.append([triangle_center[0], triangle_center[1], triangle_r])

    # print(results)

    if results == []:
        return [room[0]/2, room[1]/2, max(room[0], room[1])]

    result = sorted(results, key=lambda x: x[2])[0]

    if tilateration_debug:
        shapes.append(dict(
            type="circle",
            xref="x",
            yref="y",
            x0 = result[0] - result[2],
            y0 = result[1] - result[2],
            x1 = result[0] + result[2],
            y1 = result[1] + result[2],
            line=dict(width=3, color="#FF9999"),
        ))

        shapes.append(add_point(result[0:2], 0.05, "#FF9999"))

    return result



def multilateration(distance_map, room):

    results = [
        trilateration([distance_map[i] for i in [1,2,3]], room),
        trilateration([distance_map[i] for i in [0,2,3]], room),
        trilateration([distance_map[i] for i in [0,1,3]], room),
        trilateration([distance_map[i] for i in [0,1,2]], room)
    ]

    result = sorted(results, key=lambda x: x[2])[0]

    return result

beacons = [
    [0.25, 2.45],
    [1.1, 4.6],
    [2.8, 4.6],
    [3.1, 0.8]
]

fig.update_xaxes(range=[-1, 5], zeroline=False)
fig.update_yaxes(range=[-1, 5])

# beacons
BEACON_SIZE = 0.1

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

fig.add_trace(go.Scatter(
    x=[item[0] for item in beacons],
    y=[(item[1] + BEACON_SIZE) for item in beacons],
    text=["aa:69", "a4:a8", "d9:ab", "95:51"],
    mode="text",
))

# room
shapes.append(
    dict(
        type="rect",
        xref="x",
        yref="y",
        x0=0,
        y0=0,
        x1=3.4,
        y1=4.6,
        line=dict(
            color="#AAAAFF",
            width=1,
        )
    )
)

measurement_id = 4

true_position = [
    [0, 0], # 0 10:12:47
    [0, 0], # 1 10:18:24
    [0, 0], # 2 10:21:24
    [1.7, 2.3], # 3 10:32:49
    [1.5, 0.0], # 4 10:37:40
    [1.5, 4.0], # 5 10:47:49
    [0.5, 4.0], # 6 10:52:49
    [0, 0], # 7 10:54:28
    [0, 0], # 8 10:59:03
    [2.9, 1.5], # 9 11:07:13
    [0.8, 1.7], # 10 11:15:02
    [3.2, 4.4] # 11 11:20:14
]

measurements = parse_measurements("full_measurement_logs_raw", measurement_id)

raw_distance_maps = [
    [rssi2distance(rssi) for rssi in measurement["rssi"]] for measurement in measurements
]

TRUE_POINT_SIZE = 0.2

# cross for true point
shapes.append(dict(
    type="line",
    x0=true_position[measurement_id][0] - TRUE_POINT_SIZE/2,
    y0=true_position[measurement_id][1],
    x1=true_position[measurement_id][0] + TRUE_POINT_SIZE/2,
    y1=true_position[measurement_id][1],
    line=dict(color="#00BB00", width=2)
))

shapes.append(dict(
        type="line",
        x0=true_position[measurement_id][0],
        y0=true_position[measurement_id][1] - TRUE_POINT_SIZE/2,
        x1=true_position[measurement_id][0],
        y1=true_position[measurement_id][1] + TRUE_POINT_SIZE/2,
        line=dict(color="#00BB00", width=2)
))

# print(distance_map)

AVERAGING_STEP = 5

for i in range(0, len(raw_distance_maps), AVERAGING_STEP):
    # print("draw", i)
    distance_map = average_distance(
        raw_distance_maps[i:i+AVERAGING_STEP],
        beacons
    )
    
    result = multilateration(distance_map, [3.4, 4.6])

    error_distance = math.sqrt(
        (result[0] - true_position[measurement_id][0])**2 +
        (result[1] - true_position[measurement_id][1])**2
    )

    bound_color = "#00FF00" if error_distance < result[2] else "#FF0000"

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
            line=dict(width=1, color=bound_color),
        ))

    shapes.append(add_point(result[0:2], 0.1, bound_color))


fig.update_layout(shapes=shapes)
fig.update_layout(width=800, height=800)

fig.show()
