import math

import plotly.io as pio
import plotly.graph_objects as go

import numpy as np
import tensorflow as tf

def multilateration(distance_map, room, shapes):
    beacons_x = [distance_map[id]["x"] for id in [0, 2, 3]]
    beacons_y = [distance_map[id]["y"] for id in [0, 2, 3]]
    beacons_r = [distance_map[id]["r"] for id in [0, 2, 3]]

    x = tf.Variable([0], dtype=tf.float32)
    y = tf.Variable([0], dtype=tf.float32)

    X = tf.placeholder(tf.float32, [3, ])
    Y = tf.placeholder(tf.float32, [3, ])
    R = tf.placeholder(tf.float32, [3, ])

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
        if sum(err) < 0.05:
            print(sum(err))
            break

    print(sum(err))

    
    x, y, = sess.run(
        [x, y], {
            X: beacons_x, 
            Y: beacons_y, 
            R: beacons_r
        })

    print(x, y)

    return [x[0], y[0], sum(err)**0.5]