import conf

import copy


def normalized_DTW_distance(emission_list1, emission_list2, radius=conf.DTW_radius):
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
            dtw_matrix[i][j] = abs(emission_list1[i].emission_value - emission_list2[j].emission_value)

    for i in range(1, len(emission_list1)):
        for j in range(max(1, i - radius), min(len(emission_list2), i + radius+1)):
            dtw_matrix[i][j] += min(dtw_matrix[i - 1][j], dtw_matrix[i][j - 1], dtw_matrix[i - 1][j - 1])
    dtw_fin = dtw_matrix[len(emission_list1) - 1][len(emission_list2) - 1] / max(len(emission_list1), len(emission_list2))
    return dtw_fin



"""def prepare_for_comparison_of_two_time_series(simul_time, message_list1_before, message_list2_before, observation_window = conf.max_observation_window_for_merging, nb_min_of_messages_for_comparison = conf.nb_min_of_messages_merging):
    if len(message_list1_before)==0 or len(message_list2_before) ==0:
        return [],[],False
    t_min = max(message_list1_before[0].time, message_list2_before[0].time, simul_time - observation_window)
    message_list1 = copy.deepcopy(message_list1_before)
    message_list2 = copy.deepcopy(message_list2_before)
    for message_list in [message_list1,message_list2]:
        while len(message_list)>0 and t_min>message_list[0].time:
            message_list.pop(0)

    if len(message_list1)<nb_min_of_messages_for_comparison or len(message_list2)<nb_min_of_messages_for_comparison:
        return message_list1,message_list2, False
    return message_list1, message_list2, True"""

"""def prepare_for_comparison_of_two_time_series(simul_time, message_list1_before, message_list2_before,
                                              observation_window=conf.max_observation_window_for_merging,
                                              nb_min_of_messages_for_comparison=conf.nb_min_of_messages_splitting):
    if len(message_list1_before) == 0 or len(message_list2_before) == 0:
        return [], [], False
    stamp1 = copy.deepcopy(message_list1_before)
    stamp2 = copy.deepcopy(message_list2_before)
    t_min = simul_time - observation_window

    message_list1 = []
    message_list2 = []
    new_mess1 = stamp1.pop()
    new_mess2 = stamp2.pop()
    while min(new_mess1.time,new_mess2.time)>= t_min:
        if min(len(stamp1),len(stamp2)) == 0:
            return message_list1_before, message_list2_before, False
        message_list1.insert(0, new_mess1)
        message_list2.insert(0, new_mess2)
        new_mess1 = stamp1.pop()
        new_mess2 = stamp2.pop()
    return message_list1, message_list2, True"""


def prepare_for_comparison_of_two_time_series(simul_time, message_list1_before, message_list2_before,
                                              observation_window=conf.max_observation_window_for_merging,
                                              nb_min_of_messages_for_comparison=conf.nb_min_of_messages_splitting):
    if len(message_list1_before) == 0 or len(message_list2_before) == 0:
        return [], [], False

    t_min = simul_time - observation_window
    if message_list2_before[0].time > t_min or message_list1_before[0].time > t_min:
        return message_list1_before, message_list2_before, False
    stamp1 = copy.deepcopy(message_list1_before)
    stamp2 = copy.deepcopy(message_list2_before)
    new_mess1 = None
    while stamp1[0].time <= t_min:
        new_mess1 = stamp1.pop(0)
        if len(stamp1) == 0:
            return message_list1_before, message_list2_before, False
    if new_mess1 is not None:
        stamp1.insert(0, new_mess1)

    new_mess2 = None
    while stamp2[0].time <= t_min:
        new_mess2 = stamp2.pop(0)
        if len(stamp2) == 0:
            return message_list1_before, message_list2_before, False
    if new_mess2 is not None:
        stamp2.insert(0, new_mess2)
    return stamp1, stamp2, True


def update_time_series_according_to_observation_window(simul_time, message_list,
                                                       observation_window=conf.max_observation_window_for_merging):
    t_min = simul_time - observation_window
    last_elt = None

    while len(message_list) > 0 and message_list[0].time <= t_min:
        last_elt = message_list.pop(0)

    if last_elt is not None:
        message_list.insert(0, last_elt)
    return message_list


"""def modify_time_series_for_the_clustering(new_message, raw_sensor_message_list):
    new_raw_message_list = {}
    t_min = raw_sensor_message_list[new_message.name][0].time
    for sensor_messages_id in raw_sensor_message_list:
        new_sensor_messages = copy.deepcopy(raw_sensor_message_list[sensor_messages_id])
        while len(new_sensor_messages)>0 and new_sensor_messages[0].time<t_min:
            new_sensor_messages.pop()
        new_raw_message_list[sensor_messages_id] = new_sensor_messages
    return new_raw_message_list"""


def remove_sensor_from_clusters(new_message, clusters, cluster_index):
    """for cluster_index in clusters:
        if new_message.name in clusters[cluster_index]:"""
    clusters[cluster_index].remove(new_message.name)
    if len(clusters[cluster_index]) == 0:
        clusters.pop(cluster_index)

    return cluster_index, clusters


def is_the_sensor_out_of_scope(new_message, raw_sensor_message_list, clustering_messages, clusters, sensor_cluster_index):

    emissions_of_the_sensor = raw_sensor_message_list[new_message.name]
    """print(new_message.time)
    print("after")

    for elt in emissions_of_the_sensor:
        print(str(elt.time))"""
    """print("befor")
    print(new_message.time)
    for elt1, elt2 in zip(emissions_of_the_sensor, clustering_messages[sensor_cluster_index]):
        print(elt1.emission_value, elt2.emission_value)"""
    """print(list_to_compare1)
    print(list_to_compare2)"""
    list_to_compare1, list_to_compare2, is_possible_for_comparion = prepare_for_comparison_of_two_time_series(
        new_message.time, emissions_of_the_sensor, clustering_messages[sensor_cluster_index],
        observation_window=conf.max_observation_window_for_splitting,
        nb_min_of_messages_for_comparison=conf.nb_min_of_messages_splitting)
    if is_possible_for_comparion:
        distance = normalized_DTW_distance(list_to_compare1, list_to_compare2)
        if distance > conf.max_distance_for_splitting * (2 * len(clusters[sensor_cluster_index]) - 1) / (2 * len(
                clusters[sensor_cluster_index])):
            return True, sensor_cluster_index
    """print("after")
    print("dist = " + str(distance))
    print(new_message.time)
    for elt1,elt2 in zip(list_to_compare1,list_to_compare2):
        print(elt1.emission_value,elt2.emission_value)"""
    """print(list_to_compare1)
    print(list_to_compare2)"""
    """print("spliiit")
    print(new_message.time)
    print(is_possible_for_comparion)
    print("dist = " + str(distance))
    print(len(list_to_compare1))
    print(len(list_to_compare2))"""

    return False, sensor_cluster_index


# , build_a_time_series_for_each_sensor=True


"""def merge_two_time_series(TS1,TS2):#TS1>TS2 
    i = 0
    elt1 = TS1[0]
    for elt2 in TS2:
        while elt1.time<=elt2.time:
            i+= 1
            if i<len(TS1):
                elt1 = TS1[i]
            else:
                elt1 = TS2[len(TS2)-1].time
        TS1.insert(i, elt2)
    return TS1"""


def do_merging_if_necessary(simul_time, cluster_index, clustering_messages, clusters):
    max_number_of_sensor_in_the_cluster = 1
    chosen_cluster = None
    emissions_of_the_interesting_cluster = copy.deepcopy(clustering_messages[cluster_index])
    for other_cluster_index in clusters:
        if other_cluster_index != cluster_index:
            list_to_compare1, list_to_compare2, is_possible_for_comparion = prepare_for_comparison_of_two_time_series(
                simul_time, emissions_of_the_interesting_cluster, clustering_messages[other_cluster_index],
                observation_window=conf.max_observation_window_for_merging,
                nb_min_of_messages_for_comparison=conf.nb_min_of_messages_merging)
            if is_possible_for_comparion:

                distance = normalized_DTW_distance(list_to_compare1, list_to_compare2)
                """print("merjjjj")
                print(simul_time)
                print(is_possible_for_comparion)
                print("dist = " + str(distance))
                print(len(list_to_compare1))
                print(len(list_to_compare2))"""
                if conf.max_distance_for_merging > distance and len(
                        clusters[other_cluster_index]) >= max_number_of_sensor_in_the_cluster:
                    max_number_of_sensor_in_the_cluster = len(clusters[other_cluster_index])
                    chosen_cluster = other_cluster_index
    """print("##########################################")
    for other_cluster_index in clustering_messages:
        print(other_cluster_index)
        print(clusters[other_cluster_index])
        for mess in clustering_messages[other_cluster_index]:
            print(mess.time,mess.emission_value)
    print(cluster_index)
    print(minimum_distance_with_other_clusters)"""
    if chosen_cluster is not None:

        if len(clusters[chosen_cluster]) >= len(clusters[cluster_index]):
            clusters[chosen_cluster] = clusters[chosen_cluster] + clusters[cluster_index]
            clusters.pop(cluster_index)
            clustering_messages.pop(cluster_index)
            return chosen_cluster, clusters, clustering_messages
        else:
            clusters[cluster_index] = clusters[chosen_cluster] + clusters[cluster_index]
            clusters.pop(chosen_cluster)
            clustering_messages.pop(chosen_cluster)
            return cluster_index, clusters, clustering_messages

    return cluster_index, clusters, clustering_messages


# 'clusters' : {cluster_index:[sensor_ids..]}
# clustering_messages : {cluster_index[message 1, message 2 ..]}
# sensor_message_listfor_clustering and raw_sensor_message_list : {sensor_id : [list of emissions...]}
def clustering_method(new_message, start_clustering = conf.start_clustering):
    global clustering_messages
    global raw_sensor_message_list
    global clusters
    global index_of_non_used_cluster

    if new_message is None:
        index_of_non_used_cluster = 0
        clusters = {}
        raw_sensor_message_list = {}
        clustering_messages = {}
        return
    """print("yeaghhh")
    print(new_message.name)
    print(raw_sensor_message_list.keys())
    print("raw data")
    for sensor_id in raw_sensor_message_list:
        print(sensor_id)
        for message in raw_sensor_message_list[sensor_id]:
            print(message.time,message.emission_value)"""
    if new_message.name not in raw_sensor_message_list.keys():
        raw_sensor_message_list[new_message.name] = [copy.deepcopy(new_message)]
        clustering_messages[index_of_non_used_cluster] = [copy.deepcopy(new_message)]
        clusters[index_of_non_used_cluster] = [new_message.name]
        cluster_index_of_the_sensor = index_of_non_used_cluster
        index_of_non_used_cluster += 1

    else:
        if new_message.time < start_clustering:
            raw_sensor_message_list[new_message.name].append(new_message)
            for cluster_index in clusters:
                if new_message.name in clusters[cluster_index]:
                    cluster_index_of_the_sensor = cluster_index
            if new_message.is_empty_value is True:
                clusters[cluster_index_of_the_sensor].remove(new_message.name)
                if len(clusters[cluster_index_of_the_sensor]) == 0:
                    clusters.pop(cluster_index_of_the_sensor)
                raw_sensor_message_list.pop(new_message.name)
                return cluster_index_of_the_sensor

            clustering_messages[cluster_index_of_the_sensor].append(new_message)
            return cluster_index_of_the_sensor
        else:
            for cluster_index in clusters:
                if new_message.name in clusters[cluster_index]:
                    cluster_index_of_the_sensor = cluster_index
            # update time according to mergin window
            clustering_messages[cluster_index_of_the_sensor] = update_time_series_according_to_observation_window(
                new_message.time,
                clustering_messages[cluster_index_of_the_sensor],
                observation_window=1 * conf.max_observation_window_for_merging)
            raw_sensor_message_list[new_message.name] = update_time_series_according_to_observation_window(
                new_message.time,
                raw_sensor_message_list[
                    new_message.name],
                observation_window=1 * conf.max_observation_window_for_merging)


            is_out, cluster_index_of_the_sensor = is_the_sensor_out_of_scope(new_message, raw_sensor_message_list,
                                                                             clustering_messages, clusters, cluster_index_of_the_sensor)
            raw_sensor_message_list[new_message.name].append(new_message)

            if is_out:
                clusters[cluster_index_of_the_sensor].remove(new_message.name)
                clusters[index_of_non_used_cluster] = [new_message.name]

                clustering_messages[index_of_non_used_cluster] = copy.deepcopy(
                    raw_sensor_message_list[new_message.name])
                cluster_index_of_the_sensor = index_of_non_used_cluster

                index_of_non_used_cluster += 1
            clustering_messages[cluster_index_of_the_sensor].append(new_message)
            if new_message.is_empty_value is True:
                clusters[cluster_index_of_the_sensor].remove(new_message.name)
                if len(clusters[cluster_index_of_the_sensor]) == 0:
                    clusters.pop(cluster_index_of_the_sensor)
                raw_sensor_message_list.pop(new_message.name)
                return cluster_index_of_the_sensor
            # raw_sensor_message_list[new_message.name].append(new_message)
            cluster_index_of_the_sensor, clusters, clustering_messages = do_merging_if_necessary(new_message.time,
                                                                                                 cluster_index_of_the_sensor,
                                                                                                 clustering_messages,
                                                                                                 clusters)
            """for index in clustering_messages:
                print(len(clustering_messages[index]))
                for message in clustering_messages[index]:
                    print(message.name, message.time,message.emission_value)"""
            """print("ici meme")
            for cluster_index in clusters:
                print(cluster_index)
                print(clusters[cluster_index])"""
            """print(clustering_messages[cluster_index_of_the_sensor])
            print(clustering_messages[cluster_index_of_the_sensor][0])
            print(clustering_messages[cluster_index_of_the_sensor][0].time)"""
            # print("cluster")
            clustering_messages[cluster_index_of_the_sensor] = update_time_series_according_to_observation_window(
                new_message.time,
                clustering_messages[cluster_index_of_the_sensor],
                observation_window=conf.max_observation_window_for_merging)
            # print("raw")
            raw_sensor_message_list[new_message.name] = update_time_series_according_to_observation_window(
                new_message.time,
                raw_sensor_message_list[
                    new_message.name],
                observation_window=2 * conf.max_observation_window_for_merging)
    return cluster_index_of_the_sensor
    # raw_sensor_message_list = update_time_series_according_to_observation_window(new_message.time, raw_sensor_message_list)
    # sensor_message_list_for_comparison = modify_time_series_for_the_clustering(new_message, raw_sensor_message_list)
    # cluster_index, clusters = find_the_cluster_index(new_message.name,sensor_message_list_for_comparison, clusters)
    # sensor_cluster_index, clusters = is_still_in_the_cluster(new_message, sensor_message_list_for_clustering, raw_sensor_message_list, clusters)
    # sensor_message_list_for_clustering, raw_sensor_message_list = add_new_message_in_sensor_message_list(new_message, sensor_message_list_for_clustering, raw_sensor_message_list,                                            clusters, sensor_cluster_index)
    # sensor_message_list_for_clustering = build_homogeneous_time_series(sensor_message_list_for_clustering)
