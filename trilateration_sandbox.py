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

            shapes.append(add_point(cross, CROSS_SIZE, "#AA0000"))

    results = []

    for cross_0 in crosses[0]:
        for cross_1 in crosses[1]:
            for cross_2 in crosses[2]:
                # draw triangles
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
                    math.sqrt((triangle_center[0] - cross_0[0])**2 + (triangle_center[1] - cross_0[1])**2),
                    math.sqrt((triangle_center[0] - cross_1[0])**2 + (triangle_center[1] - cross_1[1])**2),
                    math.sqrt((triangle_center[0] - cross_2[0])**2 + (triangle_center[1] - cross_2[1])**2)
                ])

                shapes.append(
                    dict(
                        type="circle",
                        xref="x",
                        yref="y",
                        x0 = triangle_center[0] - triangle_r,
                        y0 = triangle_center[1] - triangle_r,
                        x1 = triangle_center[0] + triangle_r,
                        y1 = triangle_center[1] + triangle_r,
                        line=dict(width=2, color="#AAAA00"),
                    )
                )

                shapes.append(add_point(triangle_center, 0.05, "#0000FF"))

                results.append([triangle_center[0], triangle_center[1], triangle_r])

    result = sorted(results, key=lambda x: x[2])[0]

    shapes.append(dict(
        type="circle",
        xref="x",
        yref="y",
        x0 = result[0] - result[2],
        y0 = result[1] - result[2],
        x1 = result[0] + result[2],
        y1 = result[1] + result[2],
        line=dict(width=4, color="#FF0000"),
    ))

    shapes.append(add_point(result[0:2], 0.1, "#FF0000"))

    print(result)



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