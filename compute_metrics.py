import logging
import random
import math
import matplotlib.pyplot as plt
import json

import conf




def dif_between_reception_and_one_fct(TS, fct):
    distance = 0
    current_t = TS[0]["time"]
    i = 0
    while current_t<TS[len(TS)-1]["time"]:
        while i<len(TS) and TS[i]["time"]<current_t:
            i += 1
        i -=1
        distance += abs(TS[i]["value"] - fct(current_t))
        current_t += conf.step_for_computation_of_aera
    return distance



def compute_difference_between_emission_and_real_phenomena_from_json(fct, clustering, fct_name_for_json):
    print("completion of")
    print(fct_name_for_json)
    print("with clustering ")
    print(clustering)
    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\results_by_cluster" + str(clustering)+ ".json",
            'r+') as file:
        main_out_put = json.load(file)
    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\raw_results" + str(clustering)+ ".json",
            'r+') as file:
        main_raw_out_put = json.load(file)


    ##initialisation of the filled json file
    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\closeness_TS_and_phenomena_w_clustering" + str(clustering)+fct_name_for_json + ".json",
            'w+') as file:
        json.dump({}, file)


    for tau in main_out_put:
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\closeness_TS_and_phenomena_w_clustering" + str(clustering)+ fct_name_for_json + ".json",
                'r+') as file:
            json_file = json.load(file)
        if tau not in json_file:
            print("distance for tau = ")
            print(tau)

            #compute consumptions
            consumption = 0
            for sensor_id in main_raw_out_put[tau]:
                consumption += len(main_raw_out_put[tau][sensor_id])
            with open(
                    "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\nb_of_period_changes" + str(
                        clustering) + ".json",
                    'r+') as file:
                main_nb_of_period_changes = json.load(file)
            consumption += main_nb_of_period_changes[tau]

            ##### Finding the clusters according to fct
            t = conf.beggining_time_for_distance_computation
            aera = 0
            while t<conf.stopping_time_for_distance_computation:
                print(t)
                min_chosen_clust = None
                min_distance = 100000
                for cluster_index in main_out_put[tau]:
                    if len(main_out_put[tau][cluster_index])>1 and main_out_put[tau][cluster_index][0]["time"]<t< main_out_put[tau][cluster_index][len(main_out_put[tau][cluster_index]) - 1]["time"]:
                        is_ok = False
                        i = 0
                        while is_ok is False:
                            if main_out_put[tau][cluster_index][i]["time"]<t:
                                i+=1
                            else:
                                is_ok = True
                        i -= 1

                        distance = dif_between_reception_and_one_fct(main_out_put[tau][cluster_index][i:], fct)/ (main_out_put[tau][cluster_index][len(main_out_put[tau][cluster_index]) - 1]["time"] - main_out_put[tau][cluster_index][i]["time"])
                        if distance<min_distance:
                            min_distance = distance
                            min_chosen_clust = cluster_index
                is_ok = False
                i = 0
                while is_ok is False:
                    if main_out_put[tau][min_chosen_clust][i]["time"] < t:
                        i += 1
                    else:
                        is_ok = True
                j = len(main_out_put[tau][min_chosen_clust]) - 1
                while main_out_put[tau][min_chosen_clust][j]["time"] > conf.stopping_time_for_distance_computation:
                    j -= 1
                j+= 1
                aera += dif_between_reception_and_one_fct(main_out_put[tau][min_chosen_clust][i:j], fct)
                t = main_out_put[tau][min_chosen_clust][len(main_out_put[tau][min_chosen_clust]) - 1]["time"]
            with open(
                    "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\closeness_TS_and_phenomena_w_clustering" + str(clustering)+ fct_name_for_json + ".json",
                    'r+') as file:
                json_file = json.load(file)
            json_file[tau] = [aera, consumption]
            with open(
                    "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\closeness_TS_and_phenomena_w_clustering" + str(clustering)+ fct_name_for_json + ".json",
                    'w+') as file:
                json.dump(json_file, file)


def display_distances():
    for is_clustered in ["True", "False"]:
        #for phenomena in ["T1", "T2"]:
        for phenomena in ["T1"]:
            with open(
                    "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\closeness_TS_and_phenomena_w_clustering" + is_clustered + phenomena + ".json",
                    'r+') as file:
                json_file = json.load(file)
            distance = []
            consumption = []
            for tau in json_file.keys():
                distance.append(json_file[tau][0] * conf.step_for_computation_of_aera/(conf.stopping_time_for_distance_computation - conf.beggining_time_for_distance_computation))
                consumption.append(json_file[tau][1]/(conf.stopping_time - conf.beggining_time))


            plt.scatter(consumption, distance, label = "with use of clustering method: " + is_clustered + " for phenomena: "+phenomena)
    plt.legend()
    plt.show()


if __name__ == '__main__':
    compute_difference_between_emission_and_real_phenomena_from_json(conf.T1,True, "T1")
    compute_difference_between_emission_and_real_phenomena_from_json(conf.T1, False, "T1")

    #compute_difference_between_emission_and_real_phenomena_from_json(conf.T2, True, "T2")
    #compute_difference_between_emission_and_real_phenomena_from_json(conf.T2, False, "T2")
    display_distances()
