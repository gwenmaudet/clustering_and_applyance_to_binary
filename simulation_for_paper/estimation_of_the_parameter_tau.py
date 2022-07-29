import json
import math
import numpy as np
import random
import statistics

import conf
from phenomena_construction_and_simulation_core.simulation_of_transmissions import do_the_simulation
from latex_comparison_strat import estimate_value_according_to_freshness


def prepare_reference_time_series():
    output_clusters, output, raw_output, output_according_to_label, nb_of_period_changes = do_the_simulation(
        conf.chosen_tau, period_update_funct_strat=2)
    raw_training = []
    estimation_training = []
    raw_test = []
    estimation_test = []
    sensor_ids_training = []
    sensor_ids_test = []
    for elt in output[2]:
        if elt["time"] > conf.beggining_time_for_estimation_of_sample:
            if elt["time"] < conf.stopping_time_for_estimation_of_sample:
                raw_training.append(elt)
                estimation_training.append({"time": elt["time"],
                                            "value": estimate_value_according_to_freshness(elt["time"], raw_training,
                                                                                           len(raw_training) - 1)})
                if elt["name"] not in sensor_ids_training:
                    sensor_ids_training.append(elt["name"])
            else:
                if elt["time"] < conf.stopping_time_for_test_of_sample:
                    raw_test.append(elt)
                    estimation_test.append({"time": elt["time"],
                                            "value": estimate_value_according_to_freshness(elt["time"], raw_test,
                                                                                           len(raw_test) - 1)})
                    if elt["name"] not in sensor_ids_test:
                        sensor_ids_test.append(elt["name"])
    json_file = {"raw_training": raw_training, "estimation_training": estimation_training,
                 "sensor_ids_training": sensor_ids_training, "raw_test": raw_test, "estimation_test": estimation_test,
                 "sensor_ids_test": sensor_ids_test}
    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\training_and_test.json",
            'w+') as file:
        json.dump(json_file, file)


def build_emissions_and_estimation_according_to_sampling_factor_and_logs(n, raw_values, sensor_ids,
                                                                         reference_phenomena):
    ### build the modification index of each of the sensors
    modification_index = {sensor_id: None for sensor_id in sensor_ids}
    counting = n
    beggining_time = 0
    index_of_elt = math.ceil(random.uniform(0, 2 * len(sensor_ids)))
    current_time = raw_values[0]["time"] + random.uniform(0, conf.chosen_tau * len(sensor_ids))
    while None in modification_index.items() or current_time - raw_values[0]["time"] < 3 * n * n * len(
            sensor_ids) * conf.chosen_tau and index_of_elt < len(
            raw_values):
        if counting == 1:
            if modification_index[raw_values[index_of_elt]["name"]] is None:
                modification_index[raw_values[index_of_elt]["name"]] = round(raw_values[index_of_elt]["time"], 3)
                beggining_time = raw_values[index_of_elt]["time"]
                counting = n
        else:
            counting -= 1
        # print(current_time)
        current_time = raw_values[index_of_elt]["time"]
        index_of_elt += 1
    # print(raw_values[0:3 * n* n * len(sensor_ids)])
    new_raw_values = []
    new_estimation = []
    index_the_sensor_emission = {sensor_id: 1 for sensor_id in sensor_ids}
    for index_of_elt in range(len(raw_values)):

        if modification_index[raw_values[index_of_elt]["name"]] != None and raw_values[index_of_elt]["time"] > \
                modification_index[raw_values[index_of_elt]["name"]]:
            if index_the_sensor_emission[raw_values[index_of_elt]["name"]] == n:
                index_the_sensor_emission[raw_values[index_of_elt]["name"]] = 1
                new_raw_values.append(raw_values[index_of_elt])
                new_estimation.append({"time": raw_values[index_of_elt]["time"],
                                       "value": estimate_value_according_to_freshness(raw_values[index_of_elt]["time"],
                                                                                      new_raw_values,
                                                                                      len(new_raw_values) - 1)})
            else:
                index_the_sensor_emission[raw_values[index_of_elt]["name"]] += 1
    distance = []
    j_estimation = 0
    for i in range(len(reference_phenomena)):
        if reference_phenomena[i]["time"] > beggining_time:
            j_estimation += 1
            while j_estimation < len(new_estimation) and new_estimation[j_estimation]["time"] <= reference_phenomena[i][
                "time"]:
                j_estimation += 1
            j_estimation -= 1
            distance.append(abs(new_estimation[j_estimation]["value"] - reference_phenomena[i]["value"]))
    return round(np.quantile(distance, .95), 4)


def find_the_fitting_sample_factor():
    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\training_and_test.json",
            'r') as file:
        json_file = json.load(file)
    reference_phenomena = []
    current_time = conf.stopping_time_for_estimation_of_sample
    while current_time < conf.stopping_time_for_test_of_sample:
        reference_phenomena.append({"time": current_time, "value": conf.T2(current_time)})
        current_time += conf.step_for_computation_of_aera

    open(
        "C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/estimation_of_tau.tex",
        "w").close()
    with open(
            'C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/estimation_of_tau.tex',
            'a+') as fout:
        factors = [1, 2, 3, 4, 5, 6, 7, 8, 10, 15, 20]
        for i in factors:
            print(i)
            estimated_distances = []
            real_distances = []
            for j in range(50):
                estimated_distances.append(
                    build_emissions_and_estimation_according_to_sampling_factor_and_logs(i, json_file["raw_training"],
                                                                                         json_file[
                                                                                             "sensor_ids_training"],
                                                                                         json_file[
                                                                                             "estimation_training"]))
                real_distances.append(
                    build_emissions_and_estimation_according_to_sampling_factor_and_logs(i, json_file["raw_test"],
                                                                                         json_file[
                                                                                             "sensor_ids_test"],
                                                                                         reference_phenomena))
            estimated_distance = round(statistics.mean(estimated_distances), 3)
            real_distance = round(statistics.mean(real_distances), 3)
            fout.write(str(i) + " & " + str(estimated_distance) + " & " + str(real_distance) + " & " + str(
                round(abs((estimated_distance - real_distance) / real_distance), 3)) + "\\\\")


if __name__ == '__main__':
    precision = [0.1 * i for i in range(1, 5)]
    # prepare_reference_time_series()
    find_the_fitting_sample_factor()
    # find_the_fitting_sample_factor(precision)
