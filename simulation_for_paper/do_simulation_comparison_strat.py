import json

from phenomena_construction_and_simulation_core.simulation_of_transmissions import do_the_simulation


def do_simulation_for_multiple_tau_for_period_update_func_strat_comparison(taus, period_update_funct_strat=True):
    # initialisation
    init = {}
    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\raw_results" + str(
                period_update_funct_strat) + ".json",
            'w+') as file:
        json.dump(init, file)

    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\nb_of_period_changes" + str(
                period_update_funct_strat) + ".json",
            'w+') as file:
        json.dump(init, file)
    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\results_according_to_label" + str(
                period_update_funct_strat) + ".json",
            'w+') as file:
        json.dump(init, file)


    # completion
    for tau in taus:
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\raw_results" + str(
                    period_update_funct_strat) + ".json",
                'r+') as file:
            main_raw_results = json.load(file)
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\nb_of_period_changes" + str(
                    period_update_funct_strat) + ".json",
                'r+') as file:
            main_nb_of_period_changes = json.load(file)
        with open(
                "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\results_according_to_label" + str(
                    period_update_funct_strat) + ".json",
                'r+') as file:
            main_results_clustering = json.load(file)
        if tau not in main_results_clustering.keys():
            output_clusters,output, raw_output, output_according_to_label, nb_of_period_changes = do_the_simulation(tau,
                                                                                                                    period_update_funct_strat=period_update_funct_strat)
            #main_out_put[tau] = output
            main_raw_results[tau] = raw_output
            main_nb_of_period_changes[tau] = nb_of_period_changes
            main_results_clustering[tau] = output
            #main_nb_of_clusters[tau] = output_clusters
            with open(
                    "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\raw_results" + str(
                        period_update_funct_strat) + ".json",
                    'w+') as file:
                json.dump(main_raw_results, file)
            with open(
                    "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\nb_of_period_changes" + str(
                        period_update_funct_strat) + ".json",
                    'w+') as file:
                json.dump(main_nb_of_period_changes, file)
            with open(
                    "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\results_according_to_label" + str(
                        period_update_funct_strat) + ".json",
                    'w+') as file:
                json.dump(main_results_clustering, file)
            print("done for tau = ")
            print(tau)
        else:
            print("already done for tau = ")
            print(tau)
        # print(main_out_put)


if __name__ == '__main__':
    """
    tau = 1
    output, raw_output , output_according_to_label, nb_of_period_changes = do_the_simulation(tau, clustering = 1)

    #with open("C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\results_by_cluster.json",
    #          'w+') as file:
    #    json.dump(output, file)
    #with open("C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\raw_results.json",
    #          'w+') as file:
    #    json.dump(raw_output, file)
    for index in output_according_to_label:
        times = []
        values = []
        for elt in output_according_to_label[index]:
            times.append(elt["time"])
            values.append(elt["value"])
        plt.scatter(times,values)
    #plt.legend()
    plt.show()
    """

    #### 0 = static : each sensor imply one cluster,
    # ## 1 = uni 2level round robin : all in the same cluster,
    # ## 2 = multi 2 level round robin : each label have its own 2level round robin

    #taus = [round(0.001 + i * 0.01, 3) for i in range(1, 200, 2)]
    #taus = [round(i * 0.02, 3) for i in range(50, 100, 1)]


    #taus = [round((0.5 + i * 0.02) * 3 + 0.01, 3) for i in range(0,40)]


    """taus = [round((8 + i * 0.4), 3) for i in range(0, 20)]
    do_simulation_for_multiple_tau_for_period_update_func_strat_comparison(taus, period_update_funct_strat=0)"""

    taus = [round(0.07 + i * 0.05, 3) for i in range(0, 40)]
    do_simulation_for_multiple_tau_for_period_update_func_strat_comparison(taus, period_update_funct_strat=2)

    #taus = [round(i * 0.02, 3) for i in range(200, 400, 4)]
    # for cluster_index in output: