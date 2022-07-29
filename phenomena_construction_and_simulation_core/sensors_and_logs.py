import conf


import random
import json
import matplotlib.pyplot as plt
import numpy as np


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
    with open("C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T1_changing_points.json", 'w+') as file:
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
    with open("C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T2_changing_points.json",
              'w+') as file:
        json.dump(json_file, file)




def plot_T1_T2_sensors():

    nb_of_values = 1200000
    """ with open(
            "C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\sensor_vals.json",
            'r') as file:
        json_f = json.load(file)
        for sensor_file in json_f:
            plt.plot(sensor_file["times"],sensor_file["vals"], label=sensor_file["infos"][0])"""

    with open(
            "C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T1_changing_points.json",
            'r') as file:
        json_f = json.load(file)
        plt.plot(json_f["times"][0:nb_of_values],json_f["vals"][0:nb_of_values], label="T1", color="blue" , linewidth=7.0)
    with open(
            "C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T2_changing_points.json",
            'r') as file:
        json_f = json.load(file)
        plt.plot(json_f["times"][0:nb_of_values],json_f["vals"][0:nb_of_values], label="T2", color="red",  linewidth=7.0)
    plt.legend()
    plt.xlabel("time")
    plt.ylabel("physical quantity")
    plt.savefig("C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\plots\\phenomena.pdf", format='pdf', dpi=1200)
    plt.show()


def write_a_latex_code_for_T1_T2():
    ########## T1  ########
    with open(
            "C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T1_changing_points.json",
            'r') as file:
        T1 = json.load(file)
    open("C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/T_1.tex", "w").close()

    with open('C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/T_1.tex', 'a') as fout:
        fout.write("\\addplot+[red,mark=none] plot coordinates{")
        i = 0
        for time,val in zip(T1["times"],T1["vals"]):
            if i%1000 ==0:
                fout.write("(" + str(time) + ',' + str(round(val,3)) + ')')
            i += 1
        fout.write("};")

    ########## T2  ########
    with open(
            "C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T2_changing_points.json",
            'r') as file:
        T2 = json.load(file)
    open("C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/T_2.tex", "w").close()

    with open('C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/T_2.tex', 'a') as fout:
        fout.write("\\addplot+[blue,mark=none] plot coordinates{")
        i =0
        for time,val in zip(T2["times"],T2["vals"]):
            if  i %1000 == 0:
                fout.write("(" + str(time) + ',' + str(round(val,3)) + ')')
            i += 1
        fout.write("};")

def write_a_latex_code_for_T1_T2_zoom():
    ########## T1  ########
    with open(
            "C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T1_changing_points.json",
            'r') as file:
        T1 = json.load(file)
    open("C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/T_1_zoom.tex", "w").close()

    with open('C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/T_1_zoom.tex', 'a') as fout:
        fout.write("\\addplot+[red,mark=none] plot coordinates{")
        i = 0
        for time,val in zip(T1["times"],T1["vals"]):
            if i < 100000 and i%100 ==0:
                fout.write("(" + str(time) + ',' + str(round(val,3)) + ')')
            i += 1
        fout.write("};")

    ########## T2  ########
    with open(
            "C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\T2_changing_points.json",
            'r') as file:
        T2 = json.load(file)
    open("C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/T_2_zoom.tex", "w").close()

    with open('C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\latex_files/T_2_zoom.tex', 'a') as fout:
        fout.write("\\addplot+[blue,mark=none] plot coordinates{")
        i =0
        for time,val in zip(T2["times"],T2["vals"]):
            if  i < 100000 and i%100 ==0:
                fout.write("(" + str(time) + ',' + str(round(val,3)) + ')')
            i += 1
        fout.write("};")


if __name__ == '__main__':
    build_T1_T2_in_json()
    #build_sensor_vals_in_json()
    #write_a_latex_code_for_T1_T2()
    #write_a_latex_code_for_T1_T2_zoom()
    plot_T1_T2_sensors()
    #read_DB2()