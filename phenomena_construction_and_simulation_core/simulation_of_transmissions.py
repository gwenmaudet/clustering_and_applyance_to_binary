import random
import math

import conf
from phenomena_construction_and_simulation_core.abstractions_of_sensors import sensor, sensor_view

from phenomena_construction_and_simulation_core.binary_tree_v2_without_any_conditions import binary_tree
from clustering_package.merging_splitting_clustering_method import clustering_method

"""
This file represents the envelope of the sensor_and_period_monitoring.

First, the initialization function of the sensors, with respect to their activation time.
Then, the sensor_and_period_monitoring function of the sensors behavior, using the "event" object,
 which for any 'simul_time' instant, is an ordered list of sensors emission instant.
"""


def initiate_birth_and_death_of_sensors(lambda_1, mu, stopping_time):
    t_i = []
    t_s = []
    t = 0
    p = random.uniform(0, 1)
    t -= math.log(p) / lambda_1
    while t < stopping_time:
        t_i.append(t)
        p = random.uniform(0, 1)
        new_time = t - math.log(p) / mu
        t_s.append(new_time)
        p = random.uniform(0, 1)
        t -= math.log(p) / lambda_1

    return t_i, t_s


"""
This file returns :
Return False if a new sensor emmit after all the sensor are dead : means that the inter arrival is more than tau

simul_time : the time instant of the last emission
dt : the list of the time difference beween 2 consecutives emissions
emission_time_per_sensor : dictionary of sensor name and their emision time = {sensor_name_1:[emission_time1,emission_time2],
                                                                                ,sensor_name_1:[emission_time1,..]..}
changed_period :  dictionary of sensors and their period change time  = {sensor_name_1:[changing_time1,changing_time2],
                                                                                ,sensor_name_1:[changing_time1,..]..}
t_0 : initial emission
"""


def do_the_simulation(tau, period_update_funct_strat=2, clustering_method=clustering_method,
                      stopping_time=conf.stopping_time):
    s_list = []
    # p1s = [i / (5 * (conf.nb_of_sensors - 1)) for i in range(int(conf.nb_of_sensors/2))]
    dt = []
    t_is, t_ss = initiate_birth_and_death_of_sensors(conf.lambda_activation_T1, conf.mu_exit, conf.T_inclusion)
    event = []
    i = 0
    #t_is = [0,1,3,4,5,6]
    #t_ss = [1000,1000,1000,1000,1000,1000]
    for t_i, t_s in zip(t_is, t_ss):
        s = sensor(1, 0, name="sensor number " + str(i), fst_wake_up=t_i, event=event,
                   shut_down=t_s, battery_type=2)
        s_list.append(s)
        i += 1
    t_is, t_ss = initiate_birth_and_death_of_sensors(conf.lambda_activation_T2, conf.mu_exit, conf.T_inclusion)
    #t_is = [0, 1, 3, 4, 5, 6]
    #t_ss = [1000, 1000, 1000, 1000, 1000, 1000]
    for t_i, t_s in zip(t_is, t_ss):
        s = sensor(0, 1, name="sensor number " + str(i), fst_wake_up=t_i, event=event,
                   shut_down=t_s, battery_type=2)
        s_list.append(s)
        i += 1

    """t_is, t_ss = initiate_birth_and_death_of_sensors(conf.lambda_activation_noise, conf.mu_exit, conf.T_inclusion)
    for t_i, t_s in zip(t_is, t_ss):
        s = sensor(0.5, 0.5, name="sensor number " + str(i), fst_wake_up=t_i, event=event,
                   shut_down=t_s, battery_type=2)
        s_list.append(s)
        i += 1"""
    nb_of_period_changes = 0
    simul_time = 0
    t_0 = 0
    output = {}
    raw_output = {}
    output_according_to_label = {1: [], 2: []}
    clusters_length = {1: [{"time": 0, "value": 0}], 2: [{"time": 0, "value": 0}]}

    binary_tree(None, 0, tau, 0)
    clustering_method(None)
    while len(event) != 0 and (simul_time) < stopping_time:
        evt = event.pop(0)
        # print(simul_time)
        assert (evt.wake_up >= simul_time)
        if t_0 == 0:
            simul_time = evt.wake_up
            t_0 = simul_time
        simul_time = evt.wake_up
        emission_value = evt.draw()
        if evt.name not in raw_output.keys():
            raw_output[evt.name] = []

            clusters_length[evt.label].append({"time": simul_time,
                                               "value": clusters_length[evt.label][len(clusters_length[evt.label]) - 1][
                                                            "value"] + 1})
        output_according_to_label[evt.label].append({"time": evt.wake_up, "value": emission_value})
        view = sensor_view(evt, emission_value, simul_time, battery=True)
        if period_update_funct_strat == 0:
            cluster_index = evt.name
            new_period = tau
            #new_period = binary_tree(view, evt.wake_up, tau, cluster_index, M=0, known_battery=True, )
            #cluster_index = clustering_method(view)
            """elif period_update_funct_strat == 1:
            cluster_index = 0"""
        elif period_update_funct_strat == 2:  # if clustering == 2
            cluster_index = clustering_method(view)
            new_period = binary_tree(view, evt.wake_up, tau, cluster_index, M=0,
                                     known_battery=True, )
        # real clustering
        raw_output[evt.name].append({"time": evt.wake_up, "value": emission_value, "cluster_index": cluster_index})

          ######## use of the management function. return the value if it has changed, None otherwise

        if evt.is_empty_value is False:

            if cluster_index not in output.keys():
                output[cluster_index] = []  # {"times":[],"values":[],"name":[]}
            output[cluster_index].append({"time": simul_time, "value": view.emission_value, "name": view.name})
            if new_period is not None and new_period != evt.period:
                evt.set_period(new_period)
                nb_of_period_changes += 1
            evt.expected_next_emission = evt.wake_up + evt.period
        else:
            clusters_length[evt.label].append({"time": simul_time,
                                               "value": clusters_length[evt.label][len(clusters_length[evt.label]) - 1][
                                                            "value"] - 1})
        event = evt.sleep(evt.wake_up, event)
        #print(simul_time)
    return clusters_length, output, raw_output, output_according_to_label, nb_of_period_changes


if __name__ == '__main__':
    tau = 1
    # output_clusters, output, raw_output , output_according_to_label, nb_of_period_changes = do_the_simulation(tau, clustering = 1)
