#! /usr/bin/python3

import math
import time

from trilateration_utils import *
import resero_multilat
import gradient_multilat

import plotly.io as pio
import plotly.graph_objects as go

beacon_debug = True


# main room
beacons = [
    [0.25, 2.45],
    [1.1, 4.6],
    [2.8, 4.6],
    [3.1, 0.8]
]

'''
# bedroom beacons
beacons = [
    [0.1, 0.1],
    [2.4, 4.8],
    [0.1, 4.8],
    [2.7, 0.7]
]
'''


# main room
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

'''
# bedroom
true_position = [
    [1.5, 4.4], # 0
    [0.3, 2.5], # 1
    [1.6, 0.8], # 2
    [2.4, 2,5], # 3
    [1.4, 2.5], # 4
    [1.5, 4.4]  # 5
]
'''

room = [3.4, 4.6]
# room = [2.8, 4.9]

fig = go.Figure()
shapes = []

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
        x1=room[0],
        y1=room[1],
        line=dict(
            color="#AAAAFF",
            width=1,
        )
    )
)


measurement_id = 3

measurements = parse_measurements("full_measurement_logs_raw", measurement_id)
# measurements = parse_measurements("full_measurement_logs_bedroom", measurement_id)

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

print(len(raw_distance_maps))

raw_distance_maps = [
    raw_distance_maps[i:i+AVERAGING_STEP]
    for i in range(0, len(raw_distance_maps), AVERAGING_STEP)
]

raw_distance_maps = raw_distance_maps[1:2]

for raw_distance_map in raw_distance_maps:
    # print("draw", i)
    distance_map = average_distance(
        raw_distance_map,
        beacons
    )

    for beacon in distance_map:
        r = beacon["r"]
        var = beacon["var"]

        # beacon distance var circle
        if beacon_debug:
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
    
    results = [
        resero_multilat.multilateration(distance_map, room, shapes),
        gradient_multilat.multilateration(distance_map, room, shapes)
    ]

    error_distances = [math.sqrt(
        (result[0] - true_position[measurement_id][0])**2 +
        (result[1] - true_position[measurement_id][1])**2
    ) for result in results]

    bound_colors = [
        ("#00FF00" if error_distances[0] < results[0][2] else "#FF0000"),
        ("#00AA00" if error_distances[1] < results[1][2] else "#AA0000"),
    ]

    for result in zip(results, bound_colors):
        # draw bounds
        if True:
            shapes.append(dict(
                type="circle",
                xref="x",
                yref="y",
                x0 = result[0][0] - result[0][2],
                y0 = result[0][1] - result[0][2],
                x1 = result[0][0] + result[0][2],
                y1 = result[0][1] + result[0][2],
                line=dict(width=1, color=result[1]),
            ))

        shapes.append(add_point(result[0][0:2], 0.1, result[1]))


fig.update_layout(shapes=shapes)
fig.update_layout(width=800, height=800)

fig.show()
