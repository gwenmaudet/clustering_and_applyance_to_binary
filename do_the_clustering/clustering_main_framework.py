import conf


import copy


def normalized_DTW_distance(emission_list1, emission_list2):
    dtw_matrix = [[abs(emission_list1[i].emission_value - emission_list2[j].emission_value) for j in range (len(emission_list2))]for i in range (len(emission_list1))]
    for i in range(1, len(emission_list1)):
        for j in range(1, len(emission_list2)):
            dtw_matrix[i][j] += min(dtw_matrix[i-1][j], dtw_matrix[i][j-1], dtw_matrix[i-1][j-1])
    if len(dtw_matrix)==0:
        return 100
    else:
        if len(dtw_matrix[0])== 0:
            return 100
    return dtw_matrix[len(emission_list1)-1][len(emission_list2) - 1]/max(len(emission_list1),len( emission_list2))


def prepare_for_comparison_of_two_time_series(simul_time, message_list1_before, message_list2_before, observation_window = conf.max_observation_window_for_merging, nb_min_of_messages_for_comparison = conf.nb_min_of_messages_for_all_comparisons):
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
    return message_list1, message_list2, True


def build_homogeneous_time_series(sensor_message_list):
    min_number_of_messages_per_sensor = 10000
    for sensor_messages in sensor_message_list:
        if len(sensor_messages ) <min_number_of_messages_per_sensor:
            min_number_of_messages_per_sensor = len(sensor_messages)
    new_list = []
    for sensor_messages in sensor_message_list:
        new_list.append(sensor_messages[len(sensor_messages) - min_number_of_messages_per_sensor:len(sensor_messages)])
    return new_list

def update_time_series_according_to_observation_window(simul_time, raw_sensor_message_list, observation_window=conf.max_observation_window_for_merging):
    t_min = simul_time - observation_window

    for sensor_messages_id in raw_sensor_message_list:
        while len(raw_sensor_message_list[sensor_messages_id])>0 and raw_sensor_message_list[sensor_messages_id][0].time<t_min:
            raw_sensor_message_list[sensor_messages_id].pop()
    return raw_sensor_message_list


def modify_time_series_for_the_clustering(new_message, raw_sensor_message_list):
    new_raw_message_list = {}
    t_min = raw_sensor_message_list[new_message.name][0].time
    for sensor_messages_id in raw_sensor_message_list:
        new_sensor_messages = copy.deepcopy(raw_sensor_message_list[sensor_messages_id])
        while len(new_sensor_messages)>0 and new_sensor_messages[0].time<t_min:
            new_sensor_messages.pop()
        new_raw_message_list[sensor_messages_id] = new_sensor_messages

    return new_raw_message_list


def remove_sensor_from_clusters(new_message, clusters, cluster_index):
    for cluster_index in clusters:
        if new_message.name in clusters[cluster_index]:
            clusters[cluster_index].remove(new_message.name)
            if len(clusters) == 0:
                clusters.pop[cluster_index]

            return cluster_index, clusters


def is_the_sensor_out_of_scope(new_message,raw_sensor_message_list,clustering_messages, clusters):

    for cluster_index in clusters:
        if new_message.name in clusters[cluster_index]:
            sensor_cluster_index = cluster_index
    emissions_of_the_sensor = raw_sensor_message_list[new_message.name]
    list_to_compare1, list_to_compare2, is_possible_for_comparion = prepare_for_comparison_of_two_time_series(new_message.time, emissions_of_the_sensor, clustering_messages[sensor_cluster_index])
    distance = normalized_DTW_distance(list_to_compare1, list_to_compare2)
    if distance > conf.max_distance_for_splitting and is_possible_for_comparion:
        return True, sensor_cluster_index
    return False, sensor_cluster_index

# , build_a_time_series_for_each_sensor=True


def do_merging_if_necessary(simul_time, cluster_index, clustering_messages, clusters):

    print("initial cluster index")
    print(cluster_index)
    minimum_distance_with_other_clusters = 10000
    chosen_cluster = None
    emissions_of_the_interesting_cluster = copy.deepcopy(clustering_messages[cluster_index])
    for other_cluster_index in clustering_messages:
        if other_cluster_index != cluster_index:
            list_to_compare1, list_to_compare2, is_possible_for_comparion = prepare_for_comparison_of_two_time_series(
                simul_time, emissions_of_the_interesting_cluster, clustering_messages[other_cluster_index])
            distance = normalized_DTW_distance(list_to_compare1, list_to_compare2)
            if is_possible_for_comparion and minimum_distance_with_other_clusters>distance:
                minimum_distance_with_other_clusters = distance
                chosen_cluster = other_cluster_index
    """print("##########################################")
    for other_cluster_index in clustering_messages:
        print(other_cluster_index)
        print(clusters[other_cluster_index])
        for mess in clustering_messages[other_cluster_index]:
            print(mess.time,mess.emission_value)
    print(cluster_index)
    print(minimum_distance_with_other_clusters)"""
    if minimum_distance_with_other_clusters < conf.max_distance_fo_merging :
        if clusters[chosen_cluster]>= clusters[cluster_index]:
            clusters[chosen_cluster] = clusters[chosen_cluster] + clusters[cluster_index]
            del clusters[cluster_index]
            del clustering_messages[cluster_index]
        else:
            clusters[cluster_index] = clusters[chosen_cluster] + clusters[cluster_index]
            del clusters[chosen_cluster]
            del clustering_messages[chosen_cluster]
        return chosen_cluster, clusters, clustering_messages
    print(cluster_index)
    return cluster_index, clusters, clustering_messages


# 'clusters' : {cluster_index:[sensor_ids..]}
#clustering_messages : {cluster_index[message 1, message 2 ..]}
# sensor_message_listfor_clustering and raw_sensor_message_list : {sensor_id : [list of emissions...]}
def clustering_method(new_message):
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
        raw_sensor_message_list[new_message.name] = [new_message]
        clustering_messages[index_of_non_used_cluster] = copy.deepcopy(raw_sensor_message_list[new_message.name])
        clusters[index_of_non_used_cluster] = [new_message.name]
        cluster_index_of_the_sensor = index_of_non_used_cluster
        index_of_non_used_cluster += 1

    else:
        raw_sensor_message_list[new_message.name].append(new_message)

        is_out, cluster_index_of_the_sensor = is_the_sensor_out_of_scope(new_message, raw_sensor_message_list, clustering_messages,clusters)
        if is_out:
            clusters[cluster_index_of_the_sensor].remove(new_message.name)
            clusters[index_of_non_used_cluster] = [new_message.name]

            clustering_messages[index_of_non_used_cluster] = copy.deepcopy(raw_sensor_message_list[new_message.name])
            cluster_index_of_the_sensor = index_of_non_used_cluster

            index_of_non_used_cluster += 1
        else:
            clustering_messages[cluster_index_of_the_sensor].append(new_message)
    if new_message.is_empty_value is True:
        return cluster_index_of_the_sensor
    #raw_sensor_message_list[new_message.name].append(new_message)
    cluster_index_of_the_sensor, clusters, clustering_messages = do_merging_if_necessary(new_message.time, cluster_index_of_the_sensor, clustering_messages, clusters)
    """for index in clustering_messages:
        print(len(clustering_messages[index]))
        for message in clustering_messages[index]:
            print(message.name, message.time,message.emission_value)"""
    """print("ici meme")
    for cluster_index in clusters:
        print(cluster_index)
        print(clusters[cluster_index])"""
    return cluster_index_of_the_sensor
    #raw_sensor_message_list = update_time_series_according_to_observation_window(new_message.time, raw_sensor_message_list)
    #sensor_message_list_for_comparison = modify_time_series_for_the_clustering(new_message, raw_sensor_message_list)
    #cluster_index, clusters = find_the_cluster_index(new_message.name,sensor_message_list_for_comparison, clusters)
    #sensor_cluster_index, clusters = is_still_in_the_cluster(new_message, sensor_message_list_for_clustering, raw_sensor_message_list, clusters)
    #sensor_message_list_for_clustering, raw_sensor_message_list = add_new_message_in_sensor_message_list(new_message, sensor_message_list_for_clustering, raw_sensor_message_list,                                            clusters, sensor_cluster_index)
    #sensor_message_list_for_clustering = build_homogeneous_time_series(sensor_message_list_for_clustering)
