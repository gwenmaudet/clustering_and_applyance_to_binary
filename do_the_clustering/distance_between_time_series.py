import conf

import math
import numpy as np
import json
import matplotlib.pyplot as plt



def euclidean_distance(log1,log2):
    distance = 0
    for el1,el2 in zip(log1,log2):
        distance+= math.pow(el1 - el2, 2)
    return math.sqrt(distance)


def pearson_based_distance1(log1,log2):
    cc = np.corrcoef(log1,log2)[0][1]
    return math.pow(((1- cc)/ (1+cc)),conf.beta_for_pearson_distance)


def pearson_based_distance2(log1,log2):
    cc = np.corrcoef(log1,log2)[0][1]
    return 2*(1- cc)

def STS_distance(log1,log2):#consider that their is simialr time stamp
    distance = 0
    for i in range (1, min(len(log1),len(log2))):
        distance += math.pow((log1[i] - log1[i-1]) - (log2[i] - log2[i-1]), 2)
    return math.sqrt(distance)




def distance_according_to_the_appartenance_percentage_of_T2(distance):
    with open(
            "C:\\Users\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\json_files\\sensor_vals.json",
            'r') as file:
        json_f = json.load(file)
    referential_sensor = json_f[0]
    pourcentages_p2 = []
    distances = []

    for sensor_elt in json_f:
        pourcentages_p2.append(sensor_elt["infos"][2])
        distances.append(distance(sensor_elt["vals"], referential_sensor["vals"]))
    plt.plot(pourcentages_p2,distances)
    plt.xlabel("pourcentage of appartenance to T2")
    plt.ylabel("distance with the sensor where p2=1 and p1=0")
    plt.title(str(distance))
    plt.show()

if __name__ == '__main__':
    distance_according_to_the_appartenance_percentage_of_T2(euclidean_distance)
    distance_according_to_the_appartenance_percentage_of_T2(pearson_based_distance1)
    distance_according_to_the_appartenance_percentage_of_T2(pearson_based_distance2)
    distance_according_to_the_appartenance_percentage_of_T2(STS_distance)
    distance_according_to_the_appartenance_percentage_of_T2(DTW_distance)












