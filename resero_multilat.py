import math
import time

from trilateration_utils import *

import plotly.io as pio
import plotly.graph_objects as go

tilateration_debug = False

def trilateration(distance_map, room, shapes):

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
            line=dict(width=2, color="#FF9999"),
        ))

        shapes.append(add_point(result[0:2], 0.05, "#FF9999"))

    return result



def multilateration(distance_map, room, shapes):

    results = [
        trilateration([distance_map[i] for i in [1,2,3]], room, shapes),
        trilateration([distance_map[i] for i in [0,2,3]], room, shapes),
        trilateration([distance_map[i] for i in [0,1,3]], room, shapes),
        trilateration([distance_map[i] for i in [0,1,2]], room, shapes)
    ]

    result = sorted(results, key=lambda x: x[2])[0]

    return result