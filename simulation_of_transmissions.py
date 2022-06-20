import logging
import random
import math
import matplotlib.pyplot as plt

import conf
from sensor_and_period_monitoring.abstractions_of_sensors import sensor, sensor_view

from binary_tree_v2_without_any_conditions import binary_tree

from do_the_clustering.clustering_main_framework import clustering_method

"""
This file represents the envelope of the sensor_and_period_monitoring.

First, the initialization function of the sensors, with respect to their activation time.
Then, the sensor_and_period_monitoring function of the sensors behavior, using the "event" object,
 which for any 'simul_time' instant, is an ordered list of sensors emission instant.
"""


def initiate_birth_and_death_of_sensors():
    t_i = []
    t_s = []
    t = 0
    p = random.uniform(0, 1)
    t -= math.log(p) / conf.lambda_1
    while t < conf.stopping_time:

        t_i.append(t)
        p = random.uniform(0, 1)
        new_time = t - math.log(p) / conf.mu
        t_s.append(new_time)
        p = random.uniform(0, 1)
        if t < conf.change_of_parameters:
            t -= math.log(p) / conf.lambda_1
        else:
            t -= math.log(p) / conf.lambda_2
    return t_i,t_s



def initialisation_of_sensors(activation_times, battery=conf.C, shut_down=None, battery_type = 0):
    event = []
    names = []
    for i in range(len(activation_times)):
        t_i = activation_times[i]
        if shut_down is None:
            s = sensor(name="sensor number " + str(i), fst_wake_up=t_i, event=event, battery=battery, shut_down=10000000000000000000000000000, battery_type=battery_type)
        else:
            s = sensor(name="sensor number " + str(i), fst_wake_up=t_i, event=event, battery=battery,
                       shut_down=shut_down[i], battery_type=battery_type)
        names.append(s.name)

    return names, event


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



def do_the_simulation(tau):
    event = []
    s_list = []
    #p1s = [i / (5 * (conf.nb_of_sensors - 1)) for i in range(int(conf.nb_of_sensors/2))]
    dt = []
    p1s = [1,1,1]
    j = 0
    for i in range(len(p1s)):
        p1 = p1s[i]
        p2 = 1 - p1
        fst_emission = random.uniform(0, conf.initial_sensor_period)
        s = sensor(p1, p2, fst_wake_up=fst_emission, name=j, event=event)
        s_list.append(s)
        j += 1

    p1s = [(2/3 - 2*i/(3 *(conf.nb_of_sensors - 1))) for i in range(int(conf.nb_of_sensors/2))]
    p1s = [0.1, 0.3, 0.6]
    for i in range(len(p1s)):
        p1 = p1s[i]
        p2 = 1 - p1
        fst_emission = random.uniform(0, conf.initial_sensor_period)
        s = sensor(p1, p2, fst_wake_up=fst_emission, name=j, event=event)
        s_list.append(s)
        j+= 1

    simul_time = 0
    t_0 = 0
    output = {}
    raw_output = {}

    binary_tree(None, 0, tau,0)
    clustering_method(None)
    while len(event) != 0 and (simul_time) < conf.stopping_time:
        evt = event.pop(0)
        assert (evt.wake_up >= simul_time)
        if t_0 == 0:
            simul_time = evt.wake_up
            t_0 = simul_time
            """else:
            if evt.is_empty_value is False:
                delta_t = evt.wake_up - simul_time

                simul_time = evt.wake_up
                if simul_time > conf.beggining_time:
                    dt.append(delta_t)
            if round(delta_t, 3) > round(tau, 3):
                logging.info("the result from the function with parameters M="
                             + str(M) + " and tau=" + str(tau) + " because the monitoring ends before all the sensors get included")
                #return False"""
        simul_time = evt.wake_up
        emission_value = evt.draw()
        if evt.name not in raw_output.keys():
            raw_output[evt.name] = {"times":[],"values":[]}
        raw_output[evt.name]["times"].append( evt.wake_up)
        raw_output[evt.name]["values"].append(emission_value)
        view = sensor_view(evt, emission_value, simul_time, battery=True)
        cluster_index = clustering_method(view)
        print("the chosen cluster is ")
        print(cluster_index)
        new_period = binary_tree(view, evt.wake_up, tau,cluster_index, M=0, known_battery=True, )  ######## use of the management function. return the value if it has changed, None otherwise
        print("period is")
        print(new_period)
        print("for sensor")
        print(view.name)
        print("cause cluster order is")
        print(cluster_index)
        if evt.is_empty_value is False:

            if cluster_index not in output.keys():
                output[cluster_index] = {}
            if view.name not in output[cluster_index].keys():
                output[cluster_index][view.name] = {"times":[], "values":[]}
            output[cluster_index][view.name]["times"].append(simul_time)
            output[cluster_index][view.name]["values"].append(view.emission_value)
            if new_period is not None and new_period != evt.period:
                evt.set_period(new_period)
                """nb_of_changes += 1
                if simul_time > conf.beggining_time:
                    changed_period[evt.name].append(evt.wake_up)"""
            evt.expected_next_emission = evt.wake_up + evt.period
            """if simul_time > conf.beggining_time:
                emission_time_per_sensor[evt.name].append(evt.wake_up)"""
        event = evt.sleep(evt.wake_up, event)


    return output, raw_output


if __name__ == '__main__':
    tau = 1
    output, raw_output = do_the_simulation(tau)
    biggest_index = None
    biggest_index_size = 0
    for sensor_id in [0,1,2,3,4,5]:
        print(raw_output[sensor_id])
        plt.scatter(raw_output[sensor_id]["times"],raw_output[sensor_id]["values"],label=sensor_id )

    for cluster_id in output:
        print(cluster_id)
        print(output[cluster_id].keys())
    plt.xlabel("time")
    plt.ylabel("physical quantity")
    plt.legend()
    plt.show()

    #for cluster_index in output:

