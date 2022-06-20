import conf


import random
import json
import matplotlib.pyplot as plt
import numpy as np

class sensor():

    def __init__(self, p1, p2, period=conf.initial_sensor_period, fst_emisison=0,id=None ):
        self.id = id
        self.p1 = p1
        self.p2 = p2
        self.period = period
        self.fst_emission = fst_emisison
        self.precision = 0.5
        pass



    def get_val_time_list(self, ts):
        T1_vals = conf.T1(ts)
        T2_vals = conf.T2(ts)
        output_vals = []
        for i in range (len(T1_vals)):
            output_vals.append(self.p1 * T1_vals[i] + self.p2 * T2_vals[i] + np.random.normal(0,self.precision))
        return output_vals


def build_T1_T2_in_json():
    t_min = conf.beggining_time
    t_max = conf.stopping_time
    ts_T1 = [t_min + i * conf.T1_step for i in range(int((t_max - t_min)/conf.T1_step))]
    ts_T2 = [t_min + i * conf.T2_step for i in range(int((t_max - t_min)/conf.T2_step))]
    json_initialised = {}
    vals_T1 = []
    last_temp = conf.T1_initial_temp
    for i in range(len(ts_T1)):
        p = random.random()
        if p<0.5:
            last_temp -= conf.T1_amplitude_variation
        else:
            last_temp += conf.T1_amplitude_variation
        vals_T1.append(last_temp)
    json_file = {"times":ts_T1,"vals":vals_T1}
    with open("C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T1_changing_points.json", 'w+') as file:
        json.dump(json_file, file)
    vals_T2 = []
    last_temp = conf.T2_initial_temp
    for i in range(len(ts_T2)):
        p = random.random()
        if p < 0.5:
            last_temp -= conf.T2_amplitude_variation
        else:
            last_temp += conf.T2_amplitude_variation
        vals_T2.append(last_temp)
    json_file = {"times":ts_T2, "vals":vals_T2}
    with open("C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T2_changing_points.json",
              'w+') as file:
        json.dump(json_file, file)


def build_sensors():
    s_list = []
    p1s = [i/(1.0 *(conf.nb_of_sensors - 1)) for i in range(int(conf.nb_of_sensors))]
    for i in range(len(p1s)):
        p1 = p1s[i]
        p2 = 1 - p1
        fst_emission = random.uniform(0,conf.initial_sensor_period)
        s = sensor(p1, p2, fst_emisison=fst_emission, id=i)
        s_list.append(s)
    """p1s = [(1 - i/(1.0 *(conf.nb_of_sensors - 1))) for i in range(int(conf.nb_of_sensors/2))]
    for i in range(len(p1s)):
        p1 = p1s[i]
        p2 = 1 - p1
        fst_emission = random.uniform(0, conf.initial_sensor_period)
        s = sensor(p1, p2, fst_emisison=fst_emission, id=i)
        s_list.append(s)"""
    return s_list



def build_sensor_vals_in_json():
    s_list = build_sensors()
    vals = []
    times = [s_list[0].fst_emission + i * s_list[0].period for i in
             range(int((conf.t_max - s_list[0].fst_emission) / s_list[0].period))]
    nb_of_emissions = len(times)
    for sensor in s_list:
        times = [sensor.fst_emission + i * sensor.period for i in range(nb_of_emissions)]
        vals.append({"infos":[sensor.id,sensor.p1,sensor.p2,sensor.period,sensor.fst_emission], "times":times,"vals":sensor.get_val_time_list(times)})
    with open("C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\sensor_vals.json",
              'w+') as file:
        json.dump(vals, file)

def plot_T1_T2_sensors():


    """ with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\sensor_vals.json",
            'r') as file:
        json_f = json.load(file)
        for sensor_file in json_f:
            plt.plot(sensor_file["times"],sensor_file["vals"], label=sensor_file["infos"][0])"""

    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T1_changing_points.json",
            'r') as file:
        json_f = json.load(file)
        plt.plot(json_f["times"],json_f["vals"], label="T1", color="blue" , linewidth=7.0)
    with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T2_changing_points.json",
            'r') as file:
        json_f = json.load(file)
        plt.plot(json_f["times"],json_f["vals"], label="T2", color="red",  linewidth=7.0)
    plt.legend()
    plt.xlabel("time")
    plt.ylabel("physical quantity")
    plt.show()




if __name__ == '__main__':
    #build_T1_T2_in_json()
    #build_sensor_vals_in_json()
    plot_T1_T2_sensors()
