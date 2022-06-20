import distance_between_time_series
import conf

import random
import math
import json
import copy
import matplotlib.pyplot as plt


def fuzzy_c_mean_algo(distance_f, time_series_s, nb_of_clusters):
    # get min and max values in order to create some random centroids
    time_series_length = len(time_series_s[0])
    # Initialisation of the fuzzy paritition u
    new_us = [[(1- math.sqrt(2)/2)*1 / nb_of_clusters for i in range(nb_of_clusters)] for j in range(len(time_series_s))]
    for u in new_us:
        i = random.randint(0, nb_of_clusters - 1)
        u[i] += math.sqrt(2)/2
    us = [[0 for i in range(nb_of_clusters)] for j in range(len(time_series_s))]

    while distance_between_partitions(us, new_us) > conf.threshold_fuzzy_c_mean:
        #print(distance_between_partitions(us, new_us))

        us = copy.deepcopy(new_us)
        vs = [[0 for i in range(time_series_length)] for j in range(nb_of_clusters)]
        cluster_sum = [0 for i in range (nb_of_clusters)]

        #creation of 'nb_of_cluster' centroids
        for time_series, time_series_weights in zip(time_series_s, us):
            #print(time_series,time_series_weights)
            for cluster_index in range(nb_of_clusters):
                cluster_sum[cluster_index] += math.pow(time_series_weights[cluster_index], conf.fuzzyness_power)
                for i in range(time_series_length):
                    vs[cluster_index][i] += math.pow(time_series_weights[cluster_index], conf.fuzzyness_power) * time_series[i]
        for i in range(len(vs)):
            for j in range(len(vs[i])):
                vs[i][j] = vs[i][j] / cluster_sum[i]
        new_us = [[0 for i in range(nb_of_clusters)] for j in range(len(time_series_s))]
        for time_series_index in range (len(time_series_s)):
            for cluster_index in range(nb_of_clusters):
                sum_ = 0
                cluster_distance = distance_f(time_series_s[time_series_index], vs[cluster_index])
                for cluster_index2 in range(nb_of_clusters):
                    distance_with_centroid = distance_f(time_series_s[time_series_index], vs[cluster_index2])
                    sum_ += math.pow(cluster_distance / distance_with_centroid, (2 / (conf.fuzzyness_power - 1)))

                new_us[time_series_index][cluster_index] = 1/sum_
        #print("prr")
    return new_us, vs



def distance_between_partitions(u, u_prime):
    distance = 0
    for el1, el2 in zip(u, u_prime):
        for partition1, partition2 in zip(el1, el2):
            distance += math.pow(partition1 - partition2, 2)
    return math.sqrt(distance)



if __name__ == '__main__':
    with open(
            "/json_files/sensor_vals.json",
            'r') as file:
        time_series_json = json.load(file)
    time_series_sensors = []
    for sensor_info in time_series_json:
        time_series_sensors.append(sensor_info["vals"][0:conf.nb_of_emissions])
    new_us, vs = fuzzy_c_mean_algo(distance_between_time_series.euclidean_distance, time_series_sensors, 2)
    print(new_us)


    with open(
            "/json_files/sensor_vals.json",
            'r') as file:
        json_f = json.load(file)
        pct_p1= []
        pct_cluster = []
        for i in range (len(json_f)):
            colo = 'green'
            pct_cluster.append(new_us[i][1])
            pct_p1.append(json_f[i]["infos"][1])
            if new_us[i][0]>conf.confidence_threshold_clustering:
                colo = 'blue'
            if new_us[i][1]>conf.confidence_threshold_clustering:
                colo = 'red'
            plt.plot(json_f[i]["times"],json_f[i]["vals"], label=json_f[i]["infos"][0], color = colo)
    plt.plot(json_f[i]["times"][0:conf.nb_of_emissions], vs[0], color="blue", linewidth=7.0)
    plt.plot(json_f[i]["times"][0:conf.nb_of_emissions], vs[1], color="red", linewidth=7.0)
    plt.legend()
    plt.show()
    plt.plot(pct_cluster)
    plt.plot(pct_p1)
    plt.show()





