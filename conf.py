import json
import math

beggining_time = 0
stopping_time = 40000




##### estimation of tau parameter
maximum_factor = 60
chosen_tau = 0.05
beggining_time_for_estimation_of_sample = 300
stopping_time_for_estimation_of_sample = 500
stopping_time_for_test_of_sample = 700



#sensor caracteristics
C = 1000000000000000
c_e = 1
c_r = 1

nb_of_sensors = 6
nb_of_emissions = int(math.pi * 38)
#nb_of_emissions = int(math.pi * 30)
time_interval_activation = 1

lambda_activation_T1 = 0.1
#lambda_activation_T2 = 0.5
lambda_activation_T2 = 0.05
#T_inclusion = 10
lambda_activation_noise = 0.005

T_inclusion = 300


mu_exit = 0.0001
gama_consumption = 0.005


##computation of metrics
max_nb_for_distance_computation = 30
fraichness_time = 0.1
minimum_number_of_sensors_for_monitoring = 5
step_for_computation_of_aera = 0.004



#parameters for the construction of clusters
start_clustering = 0
DTW_radius = 50

max_observation_window_for_merging = 100
max_observation_window_for_splitting = 100

nb_min_of_messages_merging = 10
nb_min_of_messages_splitting = 10


max_distance_for_splitting = 2
max_distance_for_merging = 1

"""fuzzyness_power = 2.5
threshold_fuzzy_c_mean= 0.3
confidence_threshold_clustering = 0.7"""



min_number_of_emissions_for_plotting_the_cluster = 5



#phenomena functions

T1_step = 0.01
T1_amplitude_variation = 0.1
T1_initial_temp = -10
T2_step = 0.01
T2_amplitude_variation = 0.1
T2_initial_temp = 10

with open(
        "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T1_changing_points.json",
        'r') as file:
    T1_file = json.load(file)

with open("C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T2_changing_points.json",
              'r') as file:
    T2_file = json.load(file)

def T1(t):

    json_t = T1_file["times"]
    json_log = T1_file["vals"]
    json_index_t = min(int(t/T1_step) - 5,  len(json_t) - 1)
    while json_index_t < len(json_t) - 1 and json_t[json_index_t] < t:
        json_index_t += 1
    return json_log[json_index_t - 1]

def T2(t):

    json_t = T2_file["times"]
    json_log = T2_file["vals"]
    json_index_t = min(int(t/T1_step) - 5,  len(json_t) - 1)
    while json_index_t < len(json_t) and json_t[json_index_t]<t:
        json_index_t += 1
    return json_log[json_index_t-1]




