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
    while stamp1[0]["time"] < t_min:
        new_mess1 = stamp1.pop(0)
        if len(stamp1) == 0:
            return message_list1_before, message_list2_before, 0, False
    if new_mess1 is not None:
        stamp1.insert(0, new_mess1)

    new_mess2 = None
    while stamp2[0]["time"] < t_min:
        new_mess2 = stamp2.pop(0)
        if len(stamp2) == 0:
            return message_list1_before, message_list2_before, 0, False
    if new_mess2 is not None:
        stamp2.insert(0, new_mess2)
    t_max = min(message_list1_before[-1]["time"], message_list2_before[-1]["time"])

    new_mess1 = None
    while stamp1[-1]["time"] > t_max:
        new_mess1 = stamp1.pop()
        if len(stamp2) == 0:
            return message_list1_before, message_list2_before, 0, False
    if new_mess1 is not None:
        stamp1.append(new_mess1)

    new_mess2 = None
    while stamp2[-1]["time"] > t_max:
        new_mess2 = stamp2.pop()
        if len(stamp2) == 0:
            return message_list1_before, message_list2_before, 0, False
    if new_mess2 is not None:
        stamp2.append(new_mess2)
    return stamp1, stamp2, t_max - t_min, True


def all_distances_between_reception_and_one_fct(TS, fct, current_t=None,fraishness = conf.fraichness_time , additionnal_fonciton_feature=None):
    distance = []
    # current_t = round(TS[10]["time"], 3)
    if current_t is None:
        current_t = round(TS[0]["time"], 3)
    i = 0
    while current_t < TS[len(TS) - 1]["time"]:
        while i < len(TS) and round(TS[i]["time"], 3) <= round(current_t, 3):
            i += 1
        i -= 1
        #new_dist = abs(TS[i]["value"] - fct(current_t))
        # print(new_dist)
        if additionnal_fonciton_feature is None:
            new_dist = abs(estimate_value_according_to_freshness(current_t, TS, i, fraishness ) - fct(current_t))
        else:
            new_dist = abs(estimate_value_according_to_freshness(current_t, TS, i, fraishness ) - fct(additionnal_fonciton_feature, current_t))

        distance.append(new_dist)
        current_t += conf.step_for_computation_of_aera

    return distance, TS[len(TS) - 1]["time"] - TS[0]["time"]


def estimate_value_according_to_freshness(current_t, TS, i, fraishness = conf.fraichness_time ):
    sum = 0
    ratio = 0
    continue_loop = True
    j = 0
    while j <= i and continue_loop:
        expo = math.exp(-(abs(current_t - TS[i - j]["time"])) /fraishness)
        ratio += expo
        sum += expo * TS[i - j]["value"]
        j += 1
        if abs(current_t - TS[i - j]["time"])> 3 * fraishness:
            continue_loop = False
    if round(ratio, 3) == 0:
        return TS[i]["value"]
    return sum / ratio


def build_emissions_accrording_to_sensor_list(raw_result, sensor_list_stamp):
    emissions = []
    sensor_list = copy.deepcopy(sensor_list_stamp)
    indexes = {sensor: 0 for sensor in sensor_list}

    current_t = 0
    while len(sensor_list) > 0:
        closest_sensor = None
        closest_value = 1000000000
        for sensor in sensor_list:
            while len(raw_result[sensor]) > indexes[sensor] and raw_result[sensor][indexes[sensor]][
                "time"] - current_t < 0:
                indexes[sensor] += 1
            if len(raw_result[sensor]) > indexes[sensor]:
                if raw_result[sensor][indexes[sensor]][
                    "time"] - current_t < closest_value:
                    closest_value = raw_result[sensor][indexes[sensor]]["time"] - current_t
                    closest_sensor = sensor
            else:
                sensor_list.remove(sensor)
        emissions.append(raw_result[closest_sensor][indexes[closest_sensor]])
        current_t = raw_result[closest_sensor][indexes[closest_sensor]]["time"]
        indexes[closest_sensor] += 1
        if indexes[closest_sensor] == len(raw_result[closest_sensor]):
            sensor_list.remove(closest_sensor)
    return emissions


def count_length(string):
    count = 1
    for i in range(0, len(string)):

        # Check each char
        # is blank or not
        if string[i] == "-":
            count += 1

    return count


def do_AHC(raw_result):
    distance_matrix = {}
    for sensor_id in raw_result.keys():
        sensor_w_other_matix = {}
        for sensor_id2 in raw_result.keys():
            if sensor_id != sensor_id2 and sensor_id2 not in distance_matrix.keys():
                l1, l2, duration, yeah = latex_prepare_for_comparison_of_two_time_series(raw_result[sensor_id],
                                                                                         raw_result[sensor_id2])

                sensor_w_other_matix[sensor_id2] = {}
                if yeah:
                    distance = latex_normalized_DTW_distance(l1, l2)
                    if distance != 100:
                        sensor_w_other_matix[sensor_id2]["D"] = distance
                        sensor_w_other_matix[sensor_id2]["t"] = duration

                    else:
                        sensor_w_other_matix[sensor_id2]["D"] = 100000
                        sensor_w_other_matix[sensor_id2]["t"] = 0

                else:
                    sensor_w_other_matix[sensor_id2]["D"] = 100000
                    sensor_w_other_matix[sensor_id2]["t"] = 0

        distance_matrix[sensor_id] = sensor_w_other_matix
    # mean_dist = statistics.mean(mean_dist)
    keep_clustering = True
    while keep_clustering:
        d_arg1_arg2 = 1000
        arg1 = None
        arg2 = None
        for cluster_list in distance_matrix.keys():
            for cluster_list2 in distance_matrix[cluster_list].keys():
                # distance_matrix[cluster_list][cluster_list2] is not None and
                if distance_matrix[cluster_list][cluster_list2]["D"] < d_arg1_arg2:
                    d_arg1_arg2 = distance_matrix[cluster_list][cluster_list2]["D"]
                    arg1 = cluster_list
                    arg2 = cluster_list2
        if d_arg1_arg2 < 5 and len(distance_matrix) > 2:
            # if len(distance_matrix) > 2:
            distance_w_others = {}
            for cluster_list in distance_matrix:
                if cluster_list != arg1 and cluster_list != arg2:
                    if arg1 in distance_matrix[cluster_list]:
                        stamp = distance_matrix[cluster_list].pop(arg1)
                        d_arg1_sens = stamp["D"]
                        t_arg1_sens = stamp["t"]
                    else:
                        stamp = distance_matrix[arg1][cluster_list]
                        d_arg1_sens = stamp["D"]
                        t_arg1_sens = stamp["t"]
                    if arg2 in distance_matrix[cluster_list]:
                        stamp = distance_matrix[cluster_list].pop(arg2)
                        d_arg2_sens = stamp["D"]
                        t_arg2_sens = stamp["t"]
                    else:
                        stamp = distance_matrix[arg2][cluster_list]
                        d_arg2_sens = stamp["D"]
                        t_arg2_sens = stamp["t"]
                    if t_arg2_sens == 0 and t_arg1_sens == 0:
                        distance_w_others[cluster_list] = {"D": 100000,
                                                           "t": t_arg1_sens + t_arg2_sens}
                    else:
                        distance_w_others[cluster_list] = {"D": 1 / (t_arg1_sens + t_arg2_sens) * (
                                t_arg1_sens * d_arg1_sens + t_arg2_sens * d_arg2_sens),
                                                           "t": t_arg1_sens + t_arg2_sens}



            new_name = arg1 + "-" + arg2
            distance_matrix[new_name] = distance_w_others
            distance_matrix.pop(arg1)
            distance_matrix.pop(arg2)

        else:
            keep_clustering = False
    clusters = [cluster_list.split('-') for cluster_list in distance_matrix]
    print(clusters)
    lengths = [len(cluster) for cluster in clusters]
    m = max(lengths)
    chosen_clusters = []
    chosen_clusters.append(clusters.pop(lengths.index(m)))
    lengths = [len(cluster) for cluster in clusters]
    m = max(lengths)
    chosen_clusters.append(clusters.pop(lengths.index(m)))

    return chosen_clusters


def do_clustering_according_to_raw_emissions_AHC(period_update_funct_strat):
    # INITIALISATION
    """init = {}
    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\emissions_of_phenomena" + str(
                period_update_funct_strat) + ".json",
            'w+') as file:
        json.dump(init, file)"""

    # COMPLETION
    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\raw_results" + str(
                period_update_funct_strat) + ".json",
            'r+') as file:
        main_raw_results = json.load(file)
    for tau in main_raw_results.keys():
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\emissions_of_phenomena" + str(
                    period_update_funct_strat) + ".json",
                'r+') as file:
            main_emissions_of_phenomena = json.load(file)
        if tau not in main_emissions_of_phenomena.keys():
            print(tau)
            raw_result = main_raw_results[tau]
            """for sensor in raw_result.keys():
                times = []
                values = []
                for elt in raw_result[sensor]:
                    times.append(elt["time"])
                    values.append(elt["value"])
                plt.plot(times,values, label=sensor)
            plt.legend()
            plt.show()"""

            # matrix distance with all the sensors
            clusters = do_AHC(raw_result)
            estimation1 = build_emissions_accrording_to_sensor_list(raw_result, clusters[0])
            estimation2 = build_emissions_accrording_to_sensor_list(raw_result, clusters[1])
            """
            for sensor in raw_result:
                times = []
                values = []
                for elt in raw_result[sensor]:
                    times.append(elt["time"])
                    values.append(elt["value"])
                plt.plot(times, values)
            plt.show()
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
            plt.show()"""
            main_emissions_of_phenomena[tau] = [estimation1, estimation2]
            with open(
                    "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\emissions_of_phenomena" + str(
                        period_update_funct_strat) + ".json",
                    'w+') as file:
                json.dump(main_emissions_of_phenomena, file)


def get_precision_and_durations(period_update_funct_strat):
    # INITIALISATION
    """init = {}
    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\life_span_precision_" + str(
                period_update_funct_strat) + ".json",
            'w+') as file:
        json.dump(init, file)"""

    # COMPLETION
    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\emissions_of_phenomena" + str(
                period_update_funct_strat) + ".json",
            'r+') as file:
        main_emissions_of_phenomena = json.load(file)
    for tau in main_emissions_of_phenomena.keys():
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\life_span_precision_" + str(
                    period_update_funct_strat) + ".json",
                'r+') as file:
            life_span_precision = json.load(file)
        print("is doing for tau = " + str(tau))
        if tau == '2.02':
            times = []
            values = []
            for elt in main_emissions_of_phenomena[tau][0]:
                times.append(elt["time"])
                values.append(elt["value"])
            plt.plot(times, values, label="fst")
            times = []
            values = []
            for elt in main_emissions_of_phenomena[tau][1]:
                times.append(elt["time"])
                values.append(elt["value"])
            plt.plot(times, values, label="scd")
            plt.legend()
            plt.show()

        if tau not in life_span_precision.keys():
            emission_f = main_emissions_of_phenomena[tau]
            distance0_w_T1, dur0T1 = all_distances_between_reception_and_one_fct(emission_f[0], conf.T1, current_t=None)
            distance0_w_T2, dur0T2 = all_distances_between_reception_and_one_fct(emission_f[0], conf.T2, current_t=None)
            if distance0_w_T1 < distance0_w_T2:
                distance1_w_T2, dur1T2 = all_distances_between_reception_and_one_fct(emission_f[1], conf.T2,
                                                                                     current_t=None)
                duration_T1 = dur0T1
                duration_T2 = dur1T2
                quantile_1 = round(np.quantile(distance0_w_T1, .75), 2)
                quantile_2 = round(np.quantile(distance1_w_T2, .75), 2)
            else:
                distance1_w_T1, dur1T1 = all_distances_between_reception_and_one_fct(emission_f[1], conf.T1,
                                                                                     current_t=None)
                duration_T1 = dur1T1
                duration_T2 = dur0T2
                quantile_1 = round(np.quantile(distance1_w_T1, .75), 2)
                quantile_2 = round(np.quantile(distance0_w_T2, .75), 2)
            life_span_precision[tau] = {"quantile_T1": quantile_1, "duration_T1": duration_T1,
                                        "quantile_T2": quantile_2,
                                        "duration_T2": duration_T2}
            with open(
                    "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\life_span_precision_" + str(
                        period_update_funct_strat) + ".json",
                    'w+') as file:
                json.dump(life_span_precision, file)



def plot_life_spans_according_to_quantile_precision():
    colors = ["red", "blue", "green"]
    for clustering in ['0', '2']:
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\life_span_precision_" + str(
                    clustering) + ".json",
                'r+') as file:
            life_span_precision = json.load(file)
        quantiles_x = []
        duration_y = []
        # duration_T2s_y = []
        life_spans = {}
        # duration_T2s = {}
        # taus = sorted([float(tau) for tau in life_span_precision.keys()])
        for tau in life_span_precision.keys():
            # tau = str(fltau)
            # print(life_span_precision[tau])
            duration = int(statistics.mean(
                [life_span_precision[tau]["duration_T1"], life_span_precision[tau]["duration_T2"]]) / 100) * 100
            quantile = statistics.mean([life_span_precision[tau]["quantile_T1"], life_span_precision[tau]["quantile_T2"]])
            # print(duration)
            if quantile > 3:
                print(tau)
            elif duration not in life_spans.keys():
                life_spans[duration] = [quantile]

                # duration_T2s[life_span_precision[tau]["quantile"]] = [life_span_precision[tau]["duration_T2"]]
            else:
                life_spans[duration].append(quantile)
                # duration_T2s[life_span_precision[tau]["quantile"]].append(life_span_precision[tau]["duration_T2"])
        # quantiles = {key: life_spans[key] for key in sorted(life_spans.keys())}
        for duration in life_spans.keys():
            quantiles_x.append(statistics.mean(life_spans[duration]))
            duration_y.append(duration)
            # duration_T2s_y.append(statistics.mean(duration_T2s[quantile]))

        plt.scatter(quantiles_x,duration_y, marker=".", label="duration with strat " + clustering,
                    color=colors[int(clustering)], )
        """plt.scatter(quantiles_x, duration_T2s_y,  marker="+", label="duration of T2 with strat " + clustering,
                    color=colors[int(clustering)])"""
    plt.xlim(xmin=0, xmax=3)
    #plt.ylim(ymin=0, ymax=3.5)

    plt.xlabel("maximum distance between estiamtion and phenomena in 75% of time")
    plt.ylabel("monitoring time for a phenomenon")
    # plt.savefig("C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\plots\\precision_and_monitoring_time.pdf", format='pdf', dpi=1200)

    plt.legend()
    plt.show()





if __name__ == '__main__':
    #do_clustering_according_to_raw_emissions_AHC(period_update_funct_strat=2)

    #do_clustering_according_to_raw_emissions_AHC(period_update_funct_strat=0)
    #get_precision_and_durations(0)
    get_precision_and_durations(2)
    plot_life_spans_according_to_quantile_precision()
