import conf
import numpy as np
import matplotlib.pyplot as plt
import json
import statistics
import math
import copy

######### np.quantile(diversities, .05)
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
        for j in range(max(0, i - radius), min(len(emission_list2), i + radius+1)):
            dtw_matrix[i][j] = abs(emission_list1[i]["value"] - emission_list2[j]["value"])

    for i in range(1, len(emission_list1)):
        for j in range(max(1, i - radius), min(len(emission_list2), i + radius+1)):
            dtw_matrix[i][j] += min(dtw_matrix[i - 1][j], dtw_matrix[i][j - 1], dtw_matrix[i - 1][j - 1])
    dtw_fin = dtw_matrix[len(emission_list1) - 1][len(emission_list2) - 1] / max(len(emission_list1), len(emission_list2))
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
    while stamp2[0].time <= t_min:
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
    while stamp2[-1].time <= t_min:
        new_mess2 = stamp2.pop()
    if new_mess2 is not None:
        stamp2.append(new_mess2)
    return stamp1, stamp2, True

def plot_clustering_method(output):
    # print(output)
    # print(output.keys())
    """with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\results_by_cluster.json",
            'r') as file:
        output = json.load(file)"""
    for index in output:
        times = []
        values = []
        #print(output[index])
        for elt in output[index]:
            times.append(elt["time"])
            values.append(elt["value"])
        plt.scatter(times, values, label=index)
    plt.legend()
    #plt.xlim(0,25000)
    plt.show()


def build_estimation_according_to_clusterings(K, results_clustering):
    clustering_info, max_time = extract_some_info_on_clustering(results_clustering)
    chosen_clusters = []
    emissions_for_K_phenomenas = []
    representative_sensors_K = []
    for i in range(K):
        representative_sensors = []
        max_time = 0
        chosen_cluster = None
        for cluster in clustering_info:
            if cluster not in chosen_clusters and results_clustering[cluster][-1]["time"] > max_time:
                max_time = results_clustering[cluster][-1]["time"]
                chosen_cluster = cluster
        chosen_clusters.append(chosen_cluster)
        sensors_candidates = clustering_info[chosen_cluster]["sensors"]
        emissions = results_clustering[chosen_cluster]
        current_time = clustering_info[chosen_cluster]['start']
        keep_finding = True
        while keep_finding:
            closest_value = 2
            closest_cluster = None
            index = 0
            for cluster in clustering_info:
                if cluster not in chosen_clusters and (clustering_info[cluster]["start"] <= current_time < clustering_info[cluster]["end"]) and (
                        clustering_info[cluster]["length"] > 1):
                    i = 0
                    found = False
                    while found is False and i < len(results_clustering[cluster]):
                        if results_clustering[cluster][i]["time"] > current_time:
                            found = True
                        else:
                            i += 1
                    if abs(emissions[0]['value'] - results_clustering[cluster][i]["value"])<closest_value:
                        closest_value = abs(emissions[0]['value'] - results_clustering[cluster][i]["value"])
                        closest_cluster = cluster
                        index = i
            if closest_cluster is None:
                for cluster in chosen_clusters:
                    if (clustering_info[cluster]["start"] < current_time < clustering_info[cluster]["end"]) and (
                            clustering_info[cluster]["length"] > 1):
                        i = 0
                        found = False
                        while found is False and i < len(results_clustering[cluster]):
                            if results_clustering[cluster][i]["time"] > current_time:
                                found = True
                            else:
                                i += 1
                        if abs(emissions[0]['value'] - results_clustering[cluster][i]["value"]) < closest_value:
                            closest_value = abs(emissions[0]['value'] - results_clustering[cluster][i]["value"])
                            closest_cluster = cluster
                            index = i
            if closest_cluster is None:
                keep_finding = False
            else:
                emissions = results_clustering[closest_cluster][0:index] + emissions
                chosen_clusters.append(closest_cluster)
                current_time = clustering_info[closest_cluster]['start']
                sensors_candidates += clustering_info[closest_cluster]["sensors"]
                if current_time < conf.start_clustering:
                    keep_finding = False

        #### find the sensors that belong to the phenomena
        """for sensor in sensors_candidates:
            list1, list2 = latex_prepare_for_comparison_of_two_time_series(raw_results[sensor], emissions)
            distance = latex_normalized_DTW_distance(list1,list2)
            if distance < 3:
                representative_sensors.append(sensor)"""

        emissions_for_K_phenomenas.append(emissions)
    return emissions_for_K_phenomenas


def extract_some_info_on_clustering(results_clustering):
    clustering_info = {}
    max_time = 0
    for cluster in results_clustering:
        names = []
        info = {"start": results_clustering[cluster][0]["time"], "end": results_clustering[cluster][-1]["time"]}
        if results_clustering[cluster][-1]["time"] > max_time:
            max_time = results_clustering[cluster][-1]["time"]
        for elt in results_clustering[cluster]:
            if elt["name"] not in names:
                names.append(elt["name"])
        info["length"] = len(names)
        info["sensors"] = names
        clustering_info[cluster] = info
    return clustering_info, max_time


"""def next_cluster(infos_on_clusters, current_t, results_clustering, last_val, ending_time):#### meaning that there is no clusters found for this phenomena, and that there should be one in the area
    the_closer = ending_time - current_t
    chosen_cluster = None
    for cluster in infos_on_clusters:
        if abs((results_clustering[cluster][0]["value"] - last_val)/(results_clustering[cluster][0]["time"] - current_t))<2:
            if (results_clustering[cluster][0]["time"] - current_t)< the_closer:
                chosen_cluster = cluster
    next_clusster_info = infos_on_clusters.pop(chosen_cluster)
    return next_clusster_info,chosen_cluster, infos_on_clusters"""



def find_biggest_cluster(infos_on_clusters, current_t, results_clustering, last_val= None):
    print("#################################################################")
    print(current_t, last_val)
    biggest_cluster = None
    cluster_size = 0
    clusters_to_remove = []
    for cluster in infos_on_clusters:
        if current_t > infos_on_clusters[cluster]["end"]:
            clusters_to_remove.append(cluster)
        #elif last_val is not None:

        if (infos_on_clusters[cluster]["start"] <=current_t < infos_on_clusters[cluster]["end"]) and (infos_on_clusters[cluster]["length"]>cluster_size):

            if (last_val is None):
                biggest_cluster = cluster
                cluster_size = infos_on_clusters[cluster]["length"]
            else:
                i = 0
                found = False
                while found is False and i <len(results_clustering[cluster]):
                    if results_clustering[cluster][i]["time"]>current_t:
                        found = True
                    else:
                        i += 1
                print(cluster)
                print(current_t)
                print(infos_on_clusters[cluster])
                print(last_val)
                print(results_clustering[cluster][i]["value"])
                if abs(last_val - results_clustering[cluster][i]["value"]) < 8:
                    biggest_cluster = cluster
                    cluster_size = infos_on_clusters[cluster]["length"]
    for cluster in clusters_to_remove:
        infos_on_clusters.pop(cluster)
    """first_start = 1000000
    if biggest_cluster is None:
        for cluster in infos_on_clusters:
            if infos_on_clusters[cluster]["start"] < first_start and ((last_val is None) or (last_val is not None and abs(last_val - results_clustering[cluster][0]["value"]) < 5)):
                biggest_cluster = cluster
                first_start = infos_on_clusters[cluster]["start"]
        if abs(first_start - current_t) > 20:
            return None, None, infos_on_clusters"""
    if biggest_cluster is None:
        return None, None, infos_on_clusters
    biggest_cluster_info = infos_on_clusters.pop(biggest_cluster)
    return biggest_cluster_info,biggest_cluster, infos_on_clusters


def estimate_value_according_to_freshness(current_t, TS, i):

    sum = 0
    ratio = 0
    continue_loop = True
    j = 0
    while j<=i and continue_loop:
        expo = math.exp(-(abs(current_t - TS[i-j]["time"]))/conf.fraichness_time)
        ratio += expo
        sum += expo * TS[i-j]["value"]
        j += 1
        if expo < 0.1:
            continue_loop = False
    if round(ratio, 3) == 0:
        return TS[i]["value"]
    return sum/ratio

def all_distances_between_reception_and_one_fct(TS, fct, current_t =None):
    distance = []
    #current_t = round(TS[10]["time"], 3)
    if current_t is None:
        current_t = round(TS[0]["time"], 3)
    i = 0
    while current_t < TS[len(TS) - 1]["time"]:
        while i < len(TS) and round(TS[i]["time"],3) <= round(current_t,3):
            i += 1
        i -= 1
        new_dist = abs(TS[i]["value"] - fct(current_t))
        # print(new_dist)
        new_dist = abs(estimate_value_according_to_freshness(current_t, TS, i) - fct(current_t))
        distance.append(new_dist)
        current_t += conf.step_for_computation_of_aera

    return distance


def get_duration_according_to(output_clusters):
    time = 0
    beggin = False
    Stopping = True
    stamp = None
    for elt in output_clusters:
        if stamp is not None and elt["value"] < conf.minimum_number_of_sensors_for_monitoring:
            time += abs(elt["time"] - stamp)
        elif stamp is None and elt["value"] >= conf.minimum_number_of_sensors_for_monitoring:
            stamp = elt["time"]
    return time


"""def put_in_json_life_spans_according_to_quantile_precision():
    ## INITIALISATION
    for clustering in ['0', '2']:


        init = {}
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\life_span_precision_" + str(
                    clustering) + ".json",
                'w+') as file:
            json.dump(init, file)

    ## COMPLETION
    for clustering in ['2', '0']:

        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\nb_of_clusters" + str(
                    clustering) + ".json",
                'r+') as file:
            main_nb_of_clusters = json.load(file)
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\results_according_to_label" + str(
                    clustering) + ".json",
                'r+') as file:
            main_results_clustering = json.load(file)
        for tau in main_results_clustering:
            with open(
                    "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\life_span_precision_" + str(
                        clustering) + ".json",
                    'r+') as file:
                life_span_precision = json.load(file)
            print("is doing for tau = " + str(tau))
            if tau not in life_span_precision.keys():
                list_distance_T1 = []
                list_distance_T2 = []
                cluster_id_index_T1 = []
                cluster_id_index_T2 = []
                plot_clustering_method(main_results_clustering[tau])
                infos_on_clusters, max_time = extract_some_info_on_clustering(main_results_clustering[tau])
                print(infos_on_clusters)
                current_t = conf.start_clustering

                biggest_cluster_info, biggest_cluster, infos_on_clusters = find_biggest_cluster(infos_on_clusters,
                                                                                                current_t, main_results_clustering[tau])
                distance_w_T1  = all_distances_between_reception_and_one_fct(main_results_clustering[tau][biggest_cluster],
                                                                  conf.T1,current_t=biggest_cluster_info["start"])
                distance_w_T2 = all_distances_between_reception_and_one_fct(main_results_clustering[tau][biggest_cluster],
                                                                conf.T2, current_t=biggest_cluster_info["start"])
                biggest_cluster_info2, biggest_cluster2, infos_on_clusters = find_biggest_cluster(infos_on_clusters,
                                                                                                  current_t, main_results_clustering[tau])
                if biggest_cluster_info2 is None:
                    list_distance_T1 += distance_w_T1
                    list_distance_T2 += distance_w_T2
                    ending_time_for_T1 = biggest_cluster_info["end"]
                    ending_time_for_T2 = biggest_cluster_info["end"]
                    last_values_T1 = main_results_clustering[tau][biggest_cluster][-1]["value"]
                    last_values_T2 = main_results_clustering[tau][biggest_cluster][-1]["value"]
                    cluster_id_index_T1.append(biggest_cluster)
                    cluster_id_index_T2.append(biggest_cluster)
                elif statistics.mean(distance_w_T1)<statistics.mean(distance_w_T2):
                    list_distance_T1 += distance_w_T1
                    ending_time_for_T1 = biggest_cluster_info["end"]
                    last_values_T1 = main_results_clustering[tau][biggest_cluster][-1]["value"]
                    cluster_id_index_T1.append(biggest_cluster)
                    distance_w_T2 = all_distances_between_reception_and_one_fct(
                        main_results_clustering[tau][biggest_cluster2],
                        conf.T2, current_t=biggest_cluster_info2["start"])
                    list_distance_T2 += distance_w_T2
                    ending_time_for_T2 = biggest_cluster_info2["end"]
                    last_values_T2 = main_results_clustering[tau][biggest_cluster2][-1]["value"]
                    cluster_id_index_T2.append(biggest_cluster2)
                else:
                    list_distance_T2 += distance_w_T2
                    ending_time_for_T2 = biggest_cluster_info["end"]
                    last_values_T2 = main_results_clustering[tau][biggest_cluster][-1]["value"]
                    cluster_id_index_T2.append(biggest_cluster)
                    distance_w_T1 = all_distances_between_reception_and_one_fct(
                        main_results_clustering[tau][biggest_cluster2],
                        conf.T1, current_t=biggest_cluster_info2["start"])
                    list_distance_T1 += distance_w_T1
                    ending_time_for_T1 = biggest_cluster_info2["end"]
                    last_values_T1 = main_results_clustering[tau][biggest_cluster2][-1]["value"]
                    cluster_id_index_T1.append(biggest_cluster2)


                while min(ending_time_for_T1,ending_time_for_T2)<max_time:
                    if ending_time_for_T1<ending_time_for_T2:
                        biggest_cluster_info, biggest_cluster, infos_on_clusters = find_biggest_cluster(
                            infos_on_clusters,
                            ending_time_for_T1,main_results_clustering[tau], last_val=last_values_T1)
                        if biggest_cluster_info is None:
                            duration_T1 = ending_time_for_T1
                            ending_time_for_T1 = 1000000
                        else:
                            distance_w_T1 = all_distances_between_reception_and_one_fct(
                                main_results_clustering[tau][biggest_cluster],
                                conf.T1, current_t=biggest_cluster_info["start"])
                            list_distance_T1 += distance_w_T1
                            ending_time_for_T1 = biggest_cluster_info["end"]
                            last_values_T1 = main_results_clustering[tau][biggest_cluster][-1]["value"]
                            cluster_id_index_T1.append(biggest_cluster)
                    else:
                        biggest_cluster_info, biggest_cluster, infos_on_clusters = find_biggest_cluster(
                            infos_on_clusters,
                            ending_time_for_T2,main_results_clustering[tau], last_val=last_values_T2)
                        if biggest_cluster_info is None:
                            duration_T2 = ending_time_for_T2
                            ending_time_for_T2 = 1000000
                        else:
                            distance_w_T2 = all_distances_between_reception_and_one_fct(
                                main_results_clustering[tau][biggest_cluster],
                                conf.T2, current_t=biggest_cluster_info["start"])
                            list_distance_T2 += distance_w_T2
                            ending_time_for_T2 = biggest_cluster_info["end"]
                            last_values_T2 = main_results_clustering[tau][biggest_cluster][-1]["value"]
                            cluster_id_index_T2.append(biggest_cluster)

                if ending_time_for_T1 == 1000000:
                    duration_T2 = max_time
                else:
                    duration_T1 = max_time
                quantile_1 =round(np.quantile(list_distance_T1, .95), 4)
                quantile_2 = round( np.quantile(list_distance_T2, .95), 4)
                frequency = np.array(distance)
                pdf = frequency / np.sum(frequency)
                cdf = np.cumsum(pdf)
                plt.plot(cdf)
                plt.show()
                life_span_precision[tau] = {"quantile": max(quantile_1,quantile_2), "duration_T1": duration_T1,
                                            "duration_T2": duration_T2, "clusters_T1":cluster_id_index_T1, "clusters_T2": cluster_id_index_T2 }

                for index in cluster_id_index_T1:
                    times = []
                    values = []
                    # print(output[index])
                    for elt in main_results_clustering[tau][index]:
                        times.append(elt["time"])
                        values.append(elt["value"])
                    plt.scatter(times, values, label="Cluster index T1")
                times = []
                values = []
                for index in cluster_id_index_T2:

                    # print(output[index])
                    for elt in main_results_clustering[tau][index]:
                        times.append(elt["time"])
                        values.append(elt["value"])
                plt.scatter(times, values, label="Cluster index T2")
                plt.legend()
                plt.show()


                with open(
                        "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\life_span_precision_" + str(
                            clustering) + ".json",
                        'w+') as file:
                    json.dump(life_span_precision, file)"""
def put_in_json_life_spans_according_to_quantile_precision():
    ## INITIALISATION
    for clustering in ['0', '2']:


        init = {}
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\life_span_precision_" + str(
                    clustering) + ".json",
                'w+') as file:
            json.dump(init, file)

    ## COMPLETION
    for clustering in ['2', '0']:

        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\nb_of_clusters" + str(
                    clustering) + ".json",
                'r+') as file:
            main_nb_of_clusters = json.load(file)
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\results_according_to_label" + str(
                    clustering) + ".json",
                'r+') as file:
            main_results_clustering = json.load(file)
        for tau in main_results_clustering:
            with open(
                    "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\life_span_precision_" + str(
                        clustering) + ".json",
                    'r+') as file:
                life_span_precision = json.load(file)
            print("is doing for tau = " + str(tau))
            if tau not in life_span_precision.keys():
                plot_clustering_method(main_results_clustering[tau])
                """k_phenomena = build_estimation_according_to_clusterings(2, main_results_clustering[tau])
                distance_k_0_w_T1 = all_distances_between_reception_and_one_fct(
                                k_phenomena[0],
                                conf.T1)
                distance_k_0_w_T2 = all_distances_between_reception_and_one_fct(
                    k_phenomena[0],
                    conf.T2)
                if distance_k_0_w_T1<distance_k_0_w_T2:
                    quantile_1 =round(np.quantile(distance_k_0_w_T1, .95), 4)
                    duration_T1 = k_phenomena[0][-1]["time"] - k_phenomena[0][0]["time"]

                    distance_k_1_w_T2 = all_distances_between_reception_and_one_fct(
                        k_phenomena[1],
                        conf.T2)
                    quantile_2 = round( np.quantile(distance_k_1_w_T2, .95), 4)
                    duration_T2 = k_phenomena[1][-1]["time"] - k_phenomena[1][0]["time"]
                else:
                    quantile_2 = round(np.quantile(distance_k_0_w_T2, .95), 4)
                    duration_T2 = k_phenomena[0][-1]["time"] - k_phenomena[0][0]["time"]
                    distance_k_1_w_T1 = all_distances_between_reception_and_one_fct(
                        k_phenomena[1],
                        conf.T1)
                    quantile_1 = round(np.quantile(distance_k_1_w_T1, .95), 4)
                    duration_T1 = k_phenomena[1][-1]["time"] - k_phenomena[1][0]["time"]
                life_span_precision[tau] = {"quantile": max(quantile_1,quantile_2), "duration_T1": duration_T1,
                                            "duration_T2": duration_T2}
                for emissions in k_phenomena:
                    times = []
                    values = []
                    # print(output[index])
                    for elt in emissions:
                        times.append(elt["time"])
                        values.append(elt["value"])
                    plt.scatter(times, values, label="Cluster index T")
                plt.legend()
                plt.show()"""


                """with open(
                        "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\life_span_precision_" + str(
                            clustering) + ".json",
                        'w+') as file:
                    json.dump(life_span_precision, file)"""




def plot_life_spans_according_to_quantile_precision():
    colors = ["red", "blue", "green"]
    for clustering in ['0', '1', '2']:
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\life_span_precision_" + str(
                    clustering) + ".json",
                'r+') as file:
            life_span_precision = json.load(file)
        quantiles_x = []
        duration_T1s_y = []
        duration_T2s_y = []
        duration_T1s = {}
        duration_T2s = {}
        taus = sorted([float(tau) for tau in life_span_precision.keys()])
        for fltau in taus:
            tau = str(fltau)

            if life_span_precision[tau]["quantile"] not in duration_T2s.keys():
                duration_T1s[life_span_precision[tau]["quantile"]] = [life_span_precision[tau]["duration_T1"]]
                duration_T2s[life_span_precision[tau]["quantile"]] = [life_span_precision[tau]["duration_T2"]]
            else:
                duration_T1s[life_span_precision[tau]["quantile"]].append(life_span_precision[tau]["duration_T1"])
                duration_T2s[life_span_precision[tau]["quantile"]].append(life_span_precision[tau]["duration_T2"])
        duration_T1s = {key:duration_T1s[key] for key in sorted(duration_T1s.keys())}
        for quantile in duration_T1s.keys():
            quantiles_x.append(quantile)
            duration_T1s_y.append(statistics.mean(duration_T1s[quantile]))
            duration_T2s_y.append(statistics.mean(duration_T2s[quantile]))

        plt.scatter(quantiles_x, duration_T1s_y, marker=".", label="duration of T1 with strat " + clustering,
                    color=colors[int(clustering)], )
        plt.scatter(quantiles_x, duration_T2s_y,  marker="+", label="duration of T2 with strat " + clustering,
                    color=colors[int(clustering)])
    plt.xlim(0, 1)
    plt.xlabel("maximum distance between estiamtion and phenomena in 75% of time")
    plt.ylabel("monitoring time for a phenomenon")
    plt.savefig("C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\plots\\precision_and_monitoring_time.pdf", format='pdf', dpi=1200)

    plt.legend()
    plt.show()


def write_latex_life_span_according_to_precision():
    colors = ["red", "blue", "green"]
    for clustering in ['0', '1', '2']:
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\life_span_precision_" + str(
                    clustering) + ".json",
                'r+') as file:
            life_span_precision = json.load(file)
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\nb_of_period_changes" + str(
                    clustering) + ".json",
                'r+') as file:
            period_changes = json.load(file)
        quantiles_x = []
        duration_T1s_y = []
        duration_T2s_y = []
        period_change_for_latex = []
        duration_T1s = {}
        duration_T2s = {}
        period_change_stamp = {}
        taus = sorted([float(tau) for tau in life_span_precision.keys()])
        for fltau in taus:
            tau = str(fltau)
            quantile = round(life_span_precision[tau]["quantile"], 2)
            if quantile not in duration_T2s.keys():
                duration_T1s[quantile] = [life_span_precision[tau]["duration_T1"]]
                duration_T2s[quantile] = [life_span_precision[tau]["duration_T2"]]
                period_change_stamp[quantile] = [period_changes[tau]]
            else:
                duration_T1s[quantile].append(life_span_precision[tau]["duration_T1"])
                duration_T2s[quantile].append(life_span_precision[tau]["duration_T2"])
                period_change_stamp[quantile].append(period_changes[tau])

        duration_T1s = {key: duration_T1s[key] for key in sorted(duration_T1s.keys())}
        for quantile in duration_T1s.keys():
            quantiles_x.append(quantile)
            duration_T1s_y.append(statistics.mean(duration_T1s[quantile]))
            duration_T2s_y.append(statistics.mean(duration_T2s[quantile]))
            period_change_for_latex.append(statistics.mean(period_change_stamp[quantile]))

        ### file T1
        open("C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/results_T_1_trat_ " + str(clustering) + ".tex",
             "w").close()
        with open(
                'C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/results_T_1_trat_ ' + str(clustering) + ".tex",
                'a') as fout:
            fout.write("\\addplot+[only marks,mark size=1pt,color="+ colors[int(clustering)]+",mark=*] plot coordinates{")
            i = 0
            for time, val in zip(quantiles_x, duration_T1s_y):
                fout.write("(" + str(time) + ',' + str(round(val, 3)) + ')')
                i += 1
            fout.write("};")

        ### file T2

        open(
            "C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/results_T_2_trat_ " + str(clustering) + ".tex",
            "w").close()
        with open(
                'C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/results_T_2_trat_ ' + str(clustering) + ".tex",
                'a') as fout:
            fout.write("\\addplot+[only marks, mark size=1pt, color=" + colors[int(clustering)] + ",mark=square] plot coordinates{")
            i = 0
            for time, val in zip(quantiles_x, duration_T2s_y):
                fout.write("(" + str(time) + ',' + str(round(val, 3)) + ')')
                i += 1
            fout.write("};")
        ## file period changes
        open(
            "C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/nb_period_changes" + str(
                clustering) + ".tex",
            "w").close()
        with open(
                'C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/nb_period_changes' + str(clustering) + ".tex",
                'a') as fout:
            fout.write("\\addplot+[only marks,mark size=1pt,color=" + colors[int(clustering)] + "] plot coordinates{")
            i = 0
            for time, val in zip(quantiles_x, period_change_for_latex):
                fout.write("(" + str(time) + ',' + str(round(val, 3)) + ')')
                i += 1
            fout.write("};")

if __name__ == '__main__':
    put_in_json_life_spans_according_to_quantile_precision()
    #plot_life_spans_according_to_quantile_precision()
    #write_latex_life_span_according_to_precision()
