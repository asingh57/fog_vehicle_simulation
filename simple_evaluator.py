

active_car_list={}
overall_connection_time=0

def initialiser(fog_list):
    return
def stream_handler(fog,car,car_id,timestamp):
    #print(fog,car,car_id)
    if(car_id not in active_car_list):
        print("new car added to scene")  
        active_car_list[car_id]={}
        active_car_list[car_id]["connected_fog"]=fog
        active_car_list[car_id]["connection_start_time"]=timestamp
        active_car_list[car_id]["connection_current_time"]=timestamp
    else:
        old_fog=active_car_list[car_id]["connected_fog"]
        if old_fog!=fog:   
            print("fogs switched")
            total_connection_time=active_car_list[car_id]["connection_current_time"]-active_car_list[car_id]["connection_start_time"]
            global overall_connection_time
            if old_fog!=None:
                overall_connection_time+=total_connection_time
                if total_connection_time>0:
                    print("added connection time")
            active_car_list[car_id]["connected_fog"]=fog
            active_car_list[car_id]["connection_start_time"]=timestamp
        else:
            print("fog retained")
        active_car_list[car_id]["connection_current_time"]=timestamp
    
    return
def beacon_handler(fog,car,car_id,timestamp):
    return
def out_of_range_handler(fog,car,car_id,timestamp):
    
    if car_id in active_car_list and active_car_list[car_id]["connected_fog"]==fog:
        print("fog went out of range")
        active_car_list[car_id]["connected_fog"]=None
        global overall_connection_time
        total_connection_time=active_car_list[car_id]["connection_current_time"]-active_car_list[car_id]["connection_start_time"]
        overall_connection_time+=total_connection_time

        if total_connection_time>0:
                    print("added connection time")
    return


def handle_simulation_end():
    for car_id in active_car_list:
        global overall_connection_time
        total_connection_time=active_car_list[car_id]["connection_current_time"]-active_car_list[car_id]["connection_start_time"]
        overall_connection_time+=total_connection_time

        if total_connection_time>0:
                    print("added connection time")


    print("Total MAX connection time across all vehicles")
    print(overall_connection_time)
    return
