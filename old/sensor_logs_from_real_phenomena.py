
class sensor():

    def __init__(self, p1, p2, period=conf.time_interval_activation, fst_emisison=0, id=None):
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

def read_DB1():
    f = open('C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\real_time_series\\wafer_TEST', 'r')
    data = np.genfromtxt(f, delimiter=',')
    print(data)
    classes = {}
    for elt in data:
        if elt[0] not in classes.keys():
            classes[elt[0]] = 0
        classes[elt[0]]+= 1
    print(classes)
    #delete(data, 0, 0)  # Erases the first row (i.e. the header)
    for elt in data:
        if round(elt[0] - 1, 3)!=0 :
            color = "red"
        else:
            color = "black"
        plt.plot([i for i in range (len(elt) - 1)], elt[1:], color = color)
    #plt.plot(data[:, 0], data[:, 1], 'o')
    f.close()
    plt.show()

def read_DB2():
    #f = open('C:\\Users\\Gwen Maudet\\PycharmProjects\\clustering and applyance to binary\\real_time_series\\wafer_TEST', 'r')
    #data = np.genfromtxt(f, delimiter=' ')
    f = open('C:\\Users\Gwen Maudet\PycharmProjects\clustering and applyance to binary\\real_time_series\chfdb_chf13_45590.txt', 'r')

    data = f.readlines()

    print(data)
    T1 = []
    T2 = []
    for line in data:
        strippedline = line.strip().split('  ')
        print(strippedline)
        print("T1")
        print(strippedline[1][:len(strippedline[1])-2])
        print("T2")
        print(strippedline[2][:len(strippedline[2])])

        T1.append(float(strippedline[1][:len(strippedline[1])-2]))
        T2.append(float(strippedline[2][:len(strippedline[2])]))

    classes = {}
    for elt in data:
        if elt[0] not in classes.keys():
            classes[elt[0]] = 0
        classes[elt[0]]+= 1
    print(classes)
    #delete(data, 0, 0)  # Erases the first row (i.e. the header)
    for elt in data:
        if round(elt[0] - 1, 3)!=0 :
            color = "red"
        else:
            color = "black"
        plt.plot([i for i in range (len(elt) - 1)], elt[1:], color = color)
    #plt.plot(data[:, 0], data[:, 1], 'o')
    print(T1)
    print(T2)
    plt.plot(T1)
    plt.plot(T2)
    f.close()
    plt.show()




def build_sensors():
    s_list = []
    p1s = [i/(1.0 *(conf.nb_of_sensors - 1)) for i in range(int(conf.nb_of_sensors))]
    for i in range(len(p1s)):
        p1 = p1s[i]
        p2 = 1 - p1
        fst_emission = random.uniform(0, conf.time_interval_activation)
        s = sensor(p1, p2, fst_emisison=fst_emission, id=i)
        s_list.append(s)
    p1s = [(1 - i/(1.0 *(conf.nb_of_sensors - 1))) for i in range(int(conf.nb_of_sensors/2))]
    for i in range(len(p1s)):
        p1 = p1s[i]
        p2 = 1 - p1
        fst_emission = random.uniform(0, conf.initial_sensor_period)
        s = sensor(p1, p2, fst_emisison=fst_emission, id=i)
        s_list.append(s)
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
    with open("/json_files/sensor_vals.json",
              'w+') as file:
        json.dump(vals, file)