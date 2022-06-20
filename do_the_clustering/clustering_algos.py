from distance_between_time_series import DTW_distance


def find_the_cluster_index(sensor_id_to_cluster, sensor_message_list_for_comparison, clusters):
    sensor_time_series = sensor_message_list_for_comparison[sensor_id_to_cluster]
    smallest_distance = 1000000
    good_cluster_index = None
    for cluster_index in clusters:
        distance = 0
        for sensor_id in cluster_index:
            sensor_time_series_to_compare_to = sensor_message_list_for_comparison[sensor_id]
            distance += DTW_distance(sensor_time_series,sensor_time_series_to_compare_to)/  (max(len(sensor_time_series), len(sensor_time_series_to_compare_to)))
        distance = distance / len(cluster_index)
        if distance <smallest_distance :
            good_cluster_index = cluster_index
            smallest_distance = distance
    if smallest_distance <0:
        return 0