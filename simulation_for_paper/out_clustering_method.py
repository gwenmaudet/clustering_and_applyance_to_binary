import matplotlib.pyplot as plt
import json

import conf
from phenomena_construction_and_simulation_core.simulation_of_transmissions import do_the_simulation








def write_latex_according_to_json_for_a_clustering_method(title):
    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\results_by_cluster.json",
            'r') as file:
        output = json.load(file)
    open(
        "C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/clustering_results" + title + ".tex",
        "w").close()
    with open(
            "C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/clustering_results" + title + ".tex",
            'a') as fout:

        for index in output:
            if len(output[index]) >= conf.min_number_of_emissions_for_plotting_the_cluster:
                fout.write(
                    "\\addplot+[only marks,mark size=1pt,] plot coordinates{")
                i = 0
                for elt in output[index]:
                    if i % conf.min_number_of_emissions_for_plotting_the_cluster == 0:
                        fout.write(
                            "(" + str(elt["time"]) + "," + str(elt["value"]) + ')')
                    i += 1
                fout.write("};")


if __name__ == '__main__':
    tau = 0.5

    output_clusters, output, raw_output, output_according_to_label, nb_of_period_changes = do_the_simulation(tau)
    with open("C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\results_by_cluster.json",
              'w+') as file:
        json.dump(output, file)
    write_latex_according_to_json_for_a_clustering_method(str(conf.max_distance_for_merging)
                                                          + str(conf.max_distance_for_splitting)
                                                          + str(conf.max_observation_window_for_merging)
                                                          + str(conf.max_observation_window_for_splitting))


    plot_clustering_method(output)

