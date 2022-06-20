import conf
import math



import copy

#from sensor_and_period_monitoring.abstractions_of_sensors import information_system


def remove_evt_from_active_sensors(elt_in_memory_that_will_die, type
                                   , parent, children):
    if len(children
           ) == 0 and len(parent) == 0:
        return [], [], 0

    if type == "parent" and len(children)==0:
        stamp = copy.deepcopy(children)
        children = copy.deepcopy(parent)
        parent = stamp
        type = "children"
    """print("REMOOVING")
    print(children
    )
    print(parent)
    print(elt_in_memory_that_will_die)"""
    if type == "children" :
        last_id_of_the_dead_sensor = int(
            elt_in_memory_that_will_die["id_tree"][len(elt_in_memory_that_will_die["id_tree"]) - 1])
        id_to_find = elt_in_memory_that_will_die["id_tree"][:(len(elt_in_memory_that_will_die["id_tree"]) - 1)] + str(
            1 - last_id_of_the_dead_sensor)
        children, found_elt = get_elt_in_list_by_id_tree_and_pop_it(id_to_find, children)
        found_elt["id_tree"] = found_elt["id_tree"][:(len(elt_in_memory_that_will_die["id_tree"]) - 1)]
        parent.append(found_elt)
        nb_of_changes = 1
    else:

        children, elt = next_emmiting_sensor_according_to_type(children
                                                               )
        if elt is None:
            return [],[], 0
        children, children_elt = get_elt_in_list_by_id_tree_and_pop_it(elt["id_tree"], children)
        last_id_of_the_dead_sensor = int(children_elt["id_tree"][len(children_elt["id_tree"]) - 1])
        id_to_find = children_elt["id_tree"][:(len(children_elt["id_tree"]) - 1)] + str(
            1 - last_id_of_the_dead_sensor)
        children, complementary_children = get_elt_in_list_by_id_tree_and_pop_it(id_to_find, children
                                                                                 )
        children_elt["id_tree"] = elt_in_memory_that_will_die["id_tree"]
        complementary_children["id_tree"] = complementary_children["id_tree"][
                                            :(len(complementary_children["id_tree"]) - 1)]
        parent.append(complementary_children)
        parent.append(children_elt)
        nb_of_changes = 2
    return  parent,children, nb_of_changes


def next_emmiting_sensor_according_to_type(children_or_parent):
    if len(children_or_parent) == 0:
        return None, None
    min_elt = children_or_parent[0]
    for elt in children_or_parent:
        if elt["next_emission"] < min_elt["next_emission"]:
            min_elt = elt
    return children_or_parent, min_elt


def get_elt_in_list_by_id_tree_and_pop_it(id_to_find, children_or_parent):
    for i in range(len(children_or_parent)):
        if children_or_parent[i]["id_tree"] == id_to_find:
            found_elt = children_or_parent.pop(i)
            return children_or_parent, found_elt
    return children_or_parent, False



def add_new_sensor(evt, simul_time, tau,parent, children ):
    if len(parent) == 0 and len(children) == 0:
        return tau, [{"name": evt.name, "next_emission": simul_time + tau, "id_tree": ""}], []
    parent, elt_that_will_be_a_children = next_emmiting_sensor_according_to_type(parent)
    parent, elt_that_will_be_a_children = get_elt_in_list_by_id_tree_and_pop_it(elt_that_will_be_a_children
                                                                     ["id_tree"], parent)
    new_period = tau * math.pow(2, len(elt_that_will_be_a_children["id_tree"]) + 1)
    new_elt = {"name": evt.name, "next_emission": simul_time + new_period,
               "id_tree": elt_that_will_be_a_children["id_tree"] + "1"}
    elt_that_will_be_a_children["id_tree"] = elt_that_will_be_a_children["id_tree"] + "0"
    # elt_that_will_be_a_children
    # ["later_emission"] = elt_that_will_be_a_children
    # ["next_emission"] + tau*math.pow(2, (heignt+1))
    children.append(new_elt)
    children.append(elt_that_will_be_a_children)
    if len(parent) == 0:
        parent = children
        children = []
    return new_period, parent, children

def find_elt_by_name_and_pop_it(parent,children,evt):
    for i in range(len(children)):
        if children[i]["name"] == evt.name:
            children_elt = children \
                .pop(i)
            return True, parent,children,  children_elt, "children"
    for i in range(len(parent)):
        if parent[i]["name"] == evt.name:
            parent_elt = parent.pop(i)
            return True, parent,children, parent_elt, "parent"
    return False, parent,children,None, None




def find_and_remove(evt, parents, childrens):
    for cluster_index in parents:
        index_of_the_sensor, parents[cluster_index], childrens[
            cluster_index], elt_in_memory, type = find_elt_by_name_and_pop_it(
            parents[cluster_index], childrens[cluster_index], evt)
        if index_of_the_sensor is not False:
            parents[cluster_index], childrens[cluster_index], nb_of_changes = remove_evt_from_active_sensors(elt_in_memory,
                                                                                                             type,
                                                                                                             parents[
                                                                                                                 cluster_index],
                                                                                                             childrens[
                                                                                                                 cluster_index])
            return parents,childrens
    print("pbb")
    print(evt,evt.name)
    print(parents)
    print(childrens)
    return False

def binary_tree(evt, simul_time, tau, cluster_index_of_the_sensor, M=0, known_battery = False):
    global childrens

    global parents
    global sensor_view_list

    new_period = None
    change_id = 0
    if evt is None:
        childrens \
            = {}
        parents = {}
        sensor_view_list = []
        return new_period
    else:
        print("###")
        print(evt.name, cluster_index_of_the_sensor)
        for cluster_index in parents:
            print(cluster_index)
            print(childrens[cluster_index])
            print(parents[cluster_index])
        if evt.name not in sensor_view_list: #first emission from the sensor
            sensor_view_list.append(evt.name)
            parents[cluster_index_of_the_sensor] = [{"name": evt.name, "next_emission": simul_time + tau, "id_tree": ""}]
            childrens[cluster_index_of_the_sensor] = []
            return tau
        else:
            if cluster_index_of_the_sensor not in parents or cluster_index_of_the_sensor not in childrens:
                parents, childrens = find_and_remove(evt, parents, childrens)
                parents[cluster_index_of_the_sensor] = [{"name": evt.name, "next_emission": simul_time + tau, "id_tree": ""}]
                childrens[cluster_index_of_the_sensor] = []
                print("laaa")
                print("###")
                print(evt.name)
                for cluster_index in parents:
                    print(cluster_index)
                    print(childrens[cluster_index])
                    print(parents[cluster_index])
                return tau
            index_of_the_sensor,parents[cluster_index_of_the_sensor], childrens[cluster_index_of_the_sensor], elt_in_memory, type = find_elt_by_name_and_pop_it(parents[cluster_index_of_the_sensor],childrens[cluster_index_of_the_sensor],evt)
            if index_of_the_sensor is False:
                # print("he ho")
                # print(parent)
                #parents[cluster_index_of_the_sensor],childrens[cluster_index_of_the_sensor],nb_of_changes = remove_evt_from_active_sensors(elt_in_memory,type,parents[cluster_index_of_the_sensor], childrens[cluster_index_of_the_sensor])
                parents,childrens = find_and_remove(evt, parents, childrens)
                print("yeaha")
                print("###")
                print(evt.name)
                for cluster_index in parents:
                    print(cluster_index)
                    print(childrens[cluster_index])
                    print(parents[cluster_index])
                #parents, childrens = find_and_remove(evt, parents, childrens)
                new_period, parents[cluster_index_of_the_sensor], childrens[cluster_index_of_the_sensor] = add_new_sensor(evt, simul_time, tau, parents[cluster_index_of_the_sensor], childrens[cluster_index_of_the_sensor])

                print("yooo")
                print("###")
                print(evt.name)
                for cluster_index in parents:
                    print(cluster_index)
                    print(childrens[cluster_index])
                    print(parents[cluster_index])
                return new_period
            else:
                #children, parent, elt_in_memory, type = find_elt_by_name_and_pop_it(evt, childrens[cluster_index], parents[cluster_index])
                if abs(round(tau * math.pow(2, len(elt_in_memory["id_tree"])) - evt.period, 3)) == 0:
                    new_period = None
                    elt_in_memory["next_emission"] = simul_time + evt.period
                else:
                    new_period = tau * math.pow(2, len(elt_in_memory["id_tree"]))
                    elt_in_memory["next_emission"] = simul_time + new_period
                if evt.is_empty_value:
                    if len(childrens[cluster_index_of_the_sensor]) == 0:
                        childrens[cluster_index_of_the_sensor] = parents[cluster_index_of_the_sensor]
                        parents[cluster_index_of_the_sensor] = []
                        type = "children"
                    parents[cluster_index_of_the_sensor],childrens[cluster_index_of_the_sensor],nb_of_changes = remove_evt_from_active_sensors(elt_in_memory, type, parents[cluster_index_of_the_sensor],childrens[cluster_index_of_the_sensor])
                    change_id += nb_of_changes
                    sensor_view_list.remove(evt)
                    return tau

            if type == "parent":
                parents[cluster_index_of_the_sensor].append(elt_in_memory)
            else:
                childrens[cluster_index_of_the_sensor].append(elt_in_memory)
        print("gllluuu")
        print(evt.name)
        for cluster_index in parents:
            print(cluster_index)
            print(childrens[cluster_index])
            print(parents[cluster_index])
        return new_period
