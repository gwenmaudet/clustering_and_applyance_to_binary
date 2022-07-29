import conf
import numpy as np
import matplotlib.pyplot as plt
import json
import statistics
import math
import copy
import pandas as pd
# from tslearn.clustering import TimeSeriesKMeans
import numpy as np


def latex_normalized_DTW_distance(emission_list1, emission_list2, radius=conf.DTW_radius):
    radius = max(radius, abs(len(emission_list1) - len(emission_list2)))
    dtw_matrix = [
        [10000 for j in range(len(emission_list2))]
        for i in range(len(emission_list1))]
    if len(dtw_matrix) == 0:
        return 100

    else:
        if len(dtw_matrix[0]) == 0:
            return 100

    for i in range(0, len(emission_list1)):
        for j in range(max(0, i - radius), min(len(emission_list2), i + radius + 1)):
            dtw_matrix[i][j] = abs(emission_list1[i]["value"] - emission_list2[j]["value"])

    for i in range(1, len(emission_list1)):
        for j in range(max(1, i - radius), min(len(emission_list2), i + radius + 1)):
            dtw_matrix[i][j] += min(dtw_matrix[i - 1][j], dtw_matrix[i][j - 1], dtw_matrix[i - 1][j - 1])
    dtw_fin = dtw_matrix[len(emission_list1) - 1][len(emission_list2) - 1] / max(len(emission_list1),
                                                                                 len(emission_list2))
    return dtw_fin


def latex_prepare_for_comparison_of_two_time_series(message_list1_before, message_list2_before):
    if len(message_list1_before) == 0 or len(message_list2_before) == 0:
        return [], [], False

    t_min = max(message_list1_before[0]["time"], message_list2_before[0]["time"])
    stamp1 = copy.deepcopy(message_list1_before)
    stamp2 = copy.deepcopy(message_list2_before)
    new_mess1 = None
    while stamp1[0]["time"] <= t_min:
        new_mess1 = stamp1.pop(0)
        if len(stamp1) == 0:
            return message_list1_before, message_list2_before, False
    if new_mess1 is not None:
        stamp1.insert(0, new_mess1)

    new_mess2 = None
    while stamp2[0]["time"] <= t_min:
        new_mess2 = stamp2.pop(0)
    if new_mess2 is not None:
        stamp2.insert(0, new_mess2)
    t_max = min(message_list1_before[-1]["time"], message_list2_before[-1]["time"])

    new_mess1 = None
    while stamp1[-1]["time"] >= t_max:
        new_mess1 = stamp1.pop()
    if new_mess1 is not None:
        stamp1.append(new_mess1)
    new_mess2 = None
    while stamp2[-1]["time"] <= t_min:
        new_mess2 = stamp2.pop()
    if new_mess2 is not None:
        stamp2.append(new_mess2)
    return stamp1, stamp2, True


def all_distances_between_reception_and_one_fct(TS, fct, current_t=None):
    distance = []
    # current_t = round(TS[10]["time"], 3)
    if current_t is None:
        current_t = round(TS[0]["time"], 3)
    i = 0
    while current_t < TS[len(TS) - 1]["time"]:
        while i < len(TS) and round(TS[i]["time"], 3) <= round(current_t, 3):
            i += 1
        i -= 1
        new_dist = abs(TS[i]["value"] - fct(current_t))
        # print(new_dist)
        new_dist = abs(estimate_value_according_to_freshness(current_t, TS, i) - fct(current_t))
        distance.append(new_dist)
        current_t += conf.step_for_computation_of_aera

    return distance


def estimate_value_according_to_freshness(current_t, TS, i):
    sum = 0
    ratio = 0
    continue_loop = True
    j = 0
    while j <= i and continue_loop:
        expo = math.exp(-(abs(current_t - TS[i - j]["time"])) / conf.fraichness_time)
        ratio += expo
        sum += expo * TS[i - j]["value"]
        j += 1
        if expo < 0.1:
            continue_loop = False
    if round(ratio, 3) == 0:
        return TS[i]["value"]
    return sum / ratio


def build_emissions_accrording_to_sensor_list(raw_result, sensor_list_stamp):
    emissions = []
    sensor_list = copy.deepcopy(sensor_list_stamp)
    indexes = {sensor: 0 for sensor in sensor_list}

    current_t = 0
    print("////////////////////////////////////")
    while len(sensor_list) > 0:
        closest_sensor = None
        closest_value = 1000000000
        for sensor in sensor_list:
            while len(raw_result[sensor]) > indexes[sensor] and raw_result[sensor][indexes[sensor]][
                "time"] - current_t < 0:
                indexes[sensor] += 1
            if raw_result[sensor][indexes[sensor]]["time"] - current_t > 0 and raw_result[sensor][indexes[sensor]][
                "time"] - current_t < closest_value:
                closest_value = raw_result[sensor][indexes[sensor]]["time"]
                closest_sensor = sensor

        emissions.append(raw_result[closest_sensor][indexes[closest_sensor]])
        indexes[closest_sensor] += 1
        current_t = closest_value
        print(current_t)
        if indexes[closest_sensor] == len(raw_result[closest_sensor]):
            sensor_list.remove(closest_sensor)
    return emissions


def compute_distance_between_2clusters(sensor_list1, sensorlist2, distance_matrix):
    distance = 0
    for sensor1 in sensor_list1:
        for sensor2 in sensorlist2:
            if sensor1 in distance_matrix.keys():
                distance += distance_matrix[sensor1][sensor2]
            else:
                distance += distance_matrix[sensor2][sensor1]
    return distance / (len(sensor1))


def count_length(string):
    count = 1
    for i in range(0, len(string)):

        # Check each char
        # is blank or not
        if string[i] == "-":
            count += 1

    return count


def do_clustering_according_to_raw_emissions_AHC(period_update_funct_strat):
    init = {}
    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\emissions_of_phenomena" + str(
                period_update_funct_strat) + ".json",
            'w+') as file:
        json.dump(init, file)

    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\raw_results" + str(
                period_update_funct_strat) + ".json",
            'r+') as file:
        main_raw_results = json.load(file)
    print(main_raw_results.keys())
    for tau in main_raw_results.keys():

        print(
            "##############################################################\n#####################################################################")
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\emissions_of_phenomena" + str(
                    period_update_funct_strat) + ".json",
                'r+') as file:
            main_emissions_of_phenomena = json.load(file)
        if tau not in main_emissions_of_phenomena.keys():
            raw_result = main_raw_results[tau]
            """for sensor in raw_result.keys():
                times = []
                values = []
                for elt in raw_result[sensor]:
                    times.append(elt["time"])
                    values.append(elt["value"])
                plt.plot(times,values)
            plt.show()"""

            # matrix distance with all the sensors
            distance_matrix = {}
            mean_dist = []
            for sensor_id in raw_result.keys():
                sensor_w_other_matix = {}
                for sensor_id2 in raw_result.keys():
                    if sensor_id != sensor_id2 and sensor_id2 not in distance_matrix.keys():
                        l1, l2, yeah = latex_prepare_for_comparison_of_two_time_series(raw_result[sensor_id],
                                                                                       raw_result[sensor_id2])

                        distance = latex_normalized_DTW_distance(l1, l2)
                        if distance == 100:
                            sensor_w_other_matix[sensor_id2] = None
                        else:
                            sensor_w_other_matix[sensor_id2] = distance
                            mean_dist.append(distance)

                distance_matrix[sensor_id] = sensor_w_other_matix
            mean_dist = statistics.mean(mean_dist)
            for cluster_list in distance_matrix:
                for cluster_list2 in distance_matrix[cluster_list]:
                    if distance_matrix[cluster_list][cluster_list2] is None:
                        distance_matrix[cluster_list][cluster_list2] = mean_dist
            keep_clustering = True
            while keep_clustering:
                d_arg1_arg2 = 1000
                arg1 = None
                arg2 = None
                for cluster_list in distance_matrix:
                    for cluster_list2 in distance_matrix[cluster_list]:
                        if distance_matrix[cluster_list][cluster_list2] < d_arg1_arg2:
                            d_arg1_arg2 = distance_matrix[cluster_list][cluster_list2]
                            arg1 = cluster_list
                            arg2 = cluster_list2

                print("%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                print(d_arg1_arg2)
                print(arg1)
                print(arg2)
                if len(distance_matrix) > 2:
                    distance_w_others = {}
                    for cluster_list in distance_matrix:
                        if cluster_list != arg1 and cluster_list != arg2:
                            if arg1 in distance_matrix[cluster_list]:
                                d_arg1_sens = distance_matrix[cluster_list].pop(arg1)
                            else:
                                d_arg1_sens = distance_matrix[arg1][cluster_list]
                            if arg2 in distance_matrix[cluster_list]:
                                d_arg2_sens = distance_matrix[cluster_list].pop(arg2)

                            else:
                                d_arg2_sens = distance_matrix[arg1][cluster_list]

                            distance_w_others[cluster_list] = 1 / (
                                        count_length(arg1) + count_length(arg2) + count_length(cluster_list)) * ((
                                                                                                                             count_length(
                                                                                                                                 cluster_list) + count_length(
                                                                                                                         arg1)) * d_arg1_sens + (
                                                                                                                             count_length(
                                                                                                                                 cluster_list) + count_length(
                                                                                                                         arg2)) * d_arg2_sens - count_length(
                                cluster_list) * d_arg1_arg2)
                    new_name = arg1 + "-" + arg2
                    distance_matrix[new_name] = distance_w_others
                    distance_matrix.pop(arg1)
                    distance_matrix.pop(arg2)
                    print(distance_matrix)
                    print(len(distance_matrix))
                else:
                    print("finito")
                    keep_clustering = False
            print(distance_matrix)
            clusters = [cluster_list.split('-') for cluster_list in distance_matrix]
            print(clusters)
            print(len(clusters))
            for elt in clusters:
                print(len(elt))

            estimation1 = build_emissions_accrording_to_sensor_list(raw_result, clusters[0])
            estimation2 = build_emissions_accrording_to_sensor_list(raw_result, clusters[1])

            times = []
            values = []
            for elt in estimation1:
                times.append(elt["time"])
                values.append(elt["value"])
            plt.plot(times, values, label="fst")
            times = []
            values = []
            for elt in estimation2:
                times.append(elt["time"])
                values.append(elt["value"])
            plt.plot(times, values, label="scd")
            plt.legend()
            plt.show()


# faire sklearn k means sur chaque capteur avec nombre de cluster = 2

# nettoyer en enlevant les capteurs qui


if __name__ == '__main__':
    do_clustering_according_to_raw_emissions_AHC(period_update_funct_strat=2)
    do_clustering_according_to_raw_emissions_AHC(period_update_funct_strat=0)
