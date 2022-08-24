import random
import math
import numpy as np
import statistics
import json
import matplotlib.pyplot as plt


import conf
from phenomena_construction_and_simulation_core.sensors_and_logs import build_T1_T2_in_json
from simulation_for_paper.latex_comparison_strats2 import all_distances_between_reception_and_one_fct


def fraishness_estimation_simul(fraishness_estimation_file, t):
    json_t = fraishness_estimation_file["times"]
    json_log = fraishness_estimation_file["vals"]
    json_index_t = min(int(t / conf.step) - 5, len(json_t) - 1)
    while json_index_t < len(json_t) - 1 and json_t[json_index_t] < t:
        json_index_t += 1
    return json_log[json_index_t - 1]


def estimate_optimal_fraishness_parameter():
    output = {}
    t_max = 1000
    lambdas = [30, 50, 100,200]
    fraishnesses = [0.001 + 0.01 * i for i in range(0, 30)]
    for lambda_1 in lambdas:
        output [lambda_1] = []
        build_T1_T2_in_json(name="estimate_optimal_fraishness_parameter", initial_temp=0, t_max=t_max)
        emissions = []
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\estimate_optimal_fraishness_parameter_changing_points.json",
                'r') as file:
            fraishness_estimation_file = json.load(file)
        p = random.random()
        t = - math.log(p) / lambda_1
        while t < t_max:
            emissions.append(
                {"time": t, "value": fraishness_estimation_simul(fraishness_estimation_file, t) + np.random.normal(0, conf.sensor_precision)})
            p = random.random()
            t -= math.log(p) / lambda_1
        for fraishness in fraishnesses:
            distances,length = all_distances_between_reception_and_one_fct(emissions, fraishness_estimation_simul,additionnal_fonciton_feature=fraishness_estimation_file, current_t=None, fraishness=fraishness)
            output[lambda_1].append(statistics.mean(distances))
            print("one done")
    print(output)
    for lambda_1 in output.keys():
        plt.plot(fraishnesses,output[lambda_1], label="inclusion of sensor with rate " + str(lambda_1))
    plt.legend()
    plt.xlabel("chosen fraishness")
    plt.ylabel("mean distance between estimation and real phenomena")
    plt.show()



if __name__ == '__main__':
    estimate_optimal_fraishness_parameter()

