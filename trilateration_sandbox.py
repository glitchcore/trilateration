#! /usr/bin/python3

import math
import time

from trilateration_utils import *
import resero_multilat
import gradient_multilat

import plotly.io as pio
import plotly.graph_objects as go

beacon_debug = False

# main room
main_room_beacons = [
    [0.25, 2.45],
    [1.1, 4.6],
    [2.8, 4.6],
    [3.1, 0.8]
]

# bedroom beacons
bedroom_beacons = [
    [0.1, 0.1],
    [2.4, 4.8],
    [0.1, 4.8],
    [2.7, 0.7]
]


# main room
main_room_ids = [3, 4, 5, 6, 9, 10, 11]

main_room_positions = [
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

# bedroom
bedroom_ids = [0, 1, 2, 3, 4, 5]

bedroom_positions = [
    [1.5, 4.4], # 0
    [0.3, 2.5], # 1
    [1.6, 0.8], # 2
    [2.4, 2,5], # 3
    [1.4, 2.5], # 4
    [1.5, 4.4]  # 5
]

main_room = [3.4, 4.6]
bedroom = [2.8, 4.9]

def main():
    # main room vars
    shapes = []
    room = main_room
    beacons = main_room_beacons
    true_positions = main_room_positions

    shapes = draw_env(beacons, room, shapes=shapes)

    for measurement_id in main_room_ids:
        measurement_shapes = shapes.copy()
        # get all distance maps averaged sets
        distance_maps = get_measurement_data(measurement_id, beacons)[:]

        resero_shapes = measurement_shapes.copy()

        for distance_map in distance_maps:
            if beacon_debug:
                measurement_shapes = draw_distance_map(distance_map, measurement_shapes)

        resero_shapes = measurement_shapes.copy()
        for distance_map in distance_maps:
            result = resero_multilat.multilateration(distance_map, room, resero_shapes)
            result = check_result(result, true_positions[measurement_id], ["#00FF00", "#FF0000"])
            resero_shapes = draw_result(
                result,
                true_positions[measurement_id], 
                beacons, 
                resero_shapes
            )
        
        plot_shapes(str(measurement_id) + "_0", beacons, resero_shapes)  
        
        # ("#00AA00" if error_distances[1] < result[2] else "#AA0000"),

main()