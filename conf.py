import json
import math

beggining_time = 0
stopping_time = 100


#sensor caracteristics
C = 1000000000000000
c_e = 1
c_r = 1

nb_of_sensors = 6
nb_of_emissions = int(math.pi * 38)
#nb_of_emissions = int(math.pi * 30)
initial_sensor_period = 1




beta_for_pearson_distance = 1


max_observation_window_for_merging = 50
nb_min_of_messages_for_all_comparisons = 50

nb_mini_of_elt_for_out_of_scope = 10

max_distance_for_splitting = 3
max_distance_fo_merging = 1

fuzzyness_power = 2.5
threshold_fuzzy_c_mean= 0.3
confidence_threshold_clustering = 0.7




#phenomena functions

T1_step = 0.01
T1_amplitude_variation = 0.5
T1_initial_temp = 10
T2_step = 0.01
T2_amplitude_variation = 0.1
T2_initial_temp = -1

with open(
        "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T1_changing_points.json",
        'r') as file:
    T1_file = json.load(file)

with open("C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T2_changing_points.json",
              'r') as file:
    T2_file = json.load(file)

def T1(t):

    output_logs = []
    json_t = T1_file["times"]
    json_log = T1_file["vals"]
    json_index_t = 0
    json_index_t = 0
    while json_index_t < len(json_t) and json_t[json_index_t] < t:
        json_index_t += 1
    return json_log[json_index_t - 1]

def T2(t):

    json_t = T2_file["times"]
    json_log = T2_file["vals"]
    json_index_t = 0
    while json_index_t < len(json_t) and json_t[json_index_t]<t:
        json_index_t += 1
    return json_log[json_index_t-1]

