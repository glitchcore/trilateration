#! /usr/bin/python3

import math
from trilateration_utils import *

import plotly.io as pio
import plotly.graph_objects as go

fig = go.Figure()
shapes = []


def trilateration(distance_map):
    for beacon in distance_map:
        r = beacon["r"]

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
        
        cross_set = circle_cross(
            [distance_map[id[0]]["x"], distance_map[id[0]]["y"], distance_map[id[0]]["r"]],
            [distance_map[id[1]]["x"], distance_map[id[1]]["y"], distance_map[id[1]]["r"]]
        )

        crosses.append(cross_set)

        for cross in cross_set:
            CROSS_SIZE = 0.08

            shapes.append(
                dict(
                    type="circle",
                    xref="x",
                    yref="y",
                    fillcolor="#AA0000",
                    x0 = cross[0] - CROSS_SIZE/2,
                    y0 = cross[1] - CROSS_SIZE/2,
                    x1 = cross[0] + CROSS_SIZE/2,
                    y1 = cross[1] + CROSS_SIZE/2,
                    line=dict(width=0),
                )
            )

    triangles = []
    for cross_0 in crosses[0]:
        for cross_1 in crosses[1]:
            for cross_2 in crosses[2]:
                triangles.append([cross_0, cross_1, cross_2])

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



    print(triangles)



def multilateration(distance_map, room):
    trilateration([distance_map[i] for i in [3,0,2]])

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

measurements = parse_measurements("full_measurement_logs_raw", 3)

raw_distance_maps = [
    [rssi2distance(rssi) for rssi in measurement["rssi"]] for measurement in measurements
]

distance_map = average_distance(raw_distance_maps, beacons)

multilateration(distance_map, [3.4, 4.6])

fig.update_layout(shapes=shapes)
fig.update_layout(width=800, height=800)

fig.show()