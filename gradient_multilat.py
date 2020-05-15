import math

import plotly.io as pio
import plotly.graph_objects as go

from .trilateration_utils import *

import numpy as np
import tensorflow as tf

tilateration_debug = False

def trilateration(distance_map, room, shapes):
    beacons_x = [distance_map_item["x"] for distance_map_item in distance_map]
    beacons_y = [distance_map_item["y"] for distance_map_item in distance_map]
    beacons_r = [distance_map_item["r"] for distance_map_item in distance_map]
    beacons_var = [distance_map_item["var"] for distance_map_item in distance_map]

    x = tf.Variable([0], dtype=tf.float32)
    y = tf.Variable([0], dtype=tf.float32)

    X = tf.placeholder(tf.float32, [len(beacons_x), ])
    Y = tf.placeholder(tf.float32, [len(beacons_y), ])
    R = tf.placeholder(tf.float32, [len(beacons_r), ])

    cost = ((x - X) ** 2 + (y - Y) ** 2 - R ** 2) ** 2

    sess = tf.Session()
    sess.run(tf.global_variables_initializer())

    learning_rate = 0.001
    optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)

    n_iter = 1000
    # errors = []

    err = []

    for i in range(n_iter):
        _, err = sess.run([optimizer, cost], {
            X: beacons_x,
            Y: beacons_y,
            R: beacons_r
        })

        # errors.append(err)
        avg_error = (sum(err) / float(len(err))) ** 0.5
        if avg_error < 0.2:
            print(sum(err))
            break

    
    x, y, = sess.run(
        [x, y], {
            X: beacons_x, 
            Y: beacons_y, 
            R: beacons_r
        })

    avg_error = (sum(err) / float(len(err))) ** 0.5

    avg_error += max(beacons_var)

    result = [
        0.0 if math.isnan(x[0]) else x[0].astype(float),
        0.0 if math.isnan(y[0]) else y[0].astype(float),
        1000.0 if math.isnan(avg_error) else avg_error
    ]

    # result = [result[0].astype(float), result[1].astype(float), result[2]]

    print(result, sum(err))

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

def multilateration(distance_map, room, shapes, SET_SIZE=3):
    print(distance_map)

    if len(distance_map) == 4:
        results = [
            trilateration([distance_map[i] for i in [1,2,3]], room, shapes),
            trilateration([distance_map[i] for i in [0,2,3]], room, shapes),
            trilateration([distance_map[i] for i in [0,1,3]], room, shapes),
            trilateration([distance_map[i] for i in [0,1,2]], room, shapes),
            trilateration(distance_map, room, shapes)
        ]

        result = sorted(results, key=lambda x: x[2])[0]
    else:
        result = trilateration(distance_map, room, shapes)
    
    return result