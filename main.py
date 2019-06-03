
import matplotlib.pyplot as plt
import random
from haversine import haversine
from math import cos, sin, floor, sqrt, pi, ceil
import os 
import csv
import pickle
import collections
from dateutil import parser

###########
#USER DEFINED VARIABLES
from simple_evaluator import initialiser, stream_handler, beacon_handler,handle_simulation_end
#above three functions do the following respectively:
#initialise a system (called only once) (takes a list of tuples of list of all fog positions
#stream handler should be evaluating how much data is sent between devices (takes two tuples fog and car's coordinates)
#beacon handler should be evaluating how a given fog is handles becons from car in range (takes two tuples fog and car's coordinates)
#handle_simulation_end is called once simulation is ended



seed=5 #seed for randomizer
data_files_path="release/training_set" #which data files to use
parsed_data_save_path="saved_data" #where to store serialised training data files
gather_file_data=False #whether to read and parse data files or to use saved data

stream_radius=0.5#max distance at which communication between vehicles is possible
beacon_radius=0.7#max distance at which beacons are reachable between vehicle and for

#the following are to fix errors in data
min_error_coords=(30,30)#values below this should be ignored 
max_error_coords=(150,150)#values above this should be ignored
###########


min_dims=[10000,10000]
max_dims=[-10000,-10000]
files = []
parsed_data=[]
random.seed(seed)
chosen_stream_handler=stream_handler
chosen_beacon_handler=beacon_handler







def load_file_data(data_files_path=data_files_path):
    # r=root, d=directories, f = files
    for r, d, f in os.walk(data_files_path):#get file names
        for file in f:
            if '.txt' in file:
                files.append(os.path.join(r, file))

    data_dict=[]#stores all data as an array without arranging it  

    for f in files:
        with open(f, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                data_dict.append([int(row[0])
                ,int(parser.parse(row[1]).strftime("%s"))
                ,float(row[2]),float(row[3])])
                break
    return data_dict

def parse_data(unparsed_data,save_path=parsed_data_save_path):
    parsed_data_unsorted={}
    car_index=0
    time_index=1
    lat_index=2
    long_index=3
    
    while len(unparsed_data)>0:
        entry= unparsed_data.pop()
        lat_entry=entry[lat_index]
        long_entry=entry[long_index]
        car_id=entry[car_index];
        timestamp= entry[time_index]
        if lat_entry< min_error_coords[0] or  lat_entry< min_error_coords[1] or  long_entry> max_error_coords[0] or  long_entry> max_error_coords[1]:
            continue
        if min_dims[0]>lat_entry:
            min_dims[0]=lat_entry
        if min_dims[1]>long_entry:
            min_dims[1]=long_entry
        if max_dims[0]<lat_entry:
            max_dims[0]=lat_entry
        if max_dims[1]<long_entry:
            max_dims[1]=long_entry
        if timestamp in parsed_data_unsorted:
            parsed_data_unsorted[timestamp][car_id]=(lat_entry,long_entry)
        else:
            parsed_data_unsorted[timestamp]={}
            parsed_data_unsorted[timestamp][car_id]=(lat_entry,long_entry)

    
    sorted_data=collections.OrderedDict(sorted(parsed_data_unsorted.items()))
    return sorted_data
    
def save_data_to_file(parsed_data,save_file=parsed_data_save_path):
    pickle.dump( parsed_data, open( save_file, "wb" ) )
    return


def load_data_from_parsed_file(save_file=parsed_data_save_path):
    return pickle.load( open( save_file, "rb" ) )

if gather_file_data:
    unparsed_data=load_file_data()
    print("unparsed data loaded")
    parsed_data=parse_data(unparsed_data)
    parsed_data["min_dims"]=min_dims
    parsed_data["max_dims"]=max_dims
    save_data_to_file(parsed_data)
else:
    parsed_data=load_data_from_parsed_file()
    #print(parsed_data)
    min_dims=parsed_data["min_dims"]
    max_dims=parsed_data["max_dims"]
    
print("parsing done")
parsed_data.pop('min_dims', None)
parsed_data.pop('max_dims', None)


#for x in parsed_data:
	#print(x)
	#print(parsed_data[x])
	#print()
#print(min_dims)
#print(max_dims)	
    


def euclidean_distance(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return sqrt(dx * dx + dy * dy)


def fast_poisson_disk_sampling(width, height, r,offset_w, offset_h, k=5, distance=euclidean_distance, random=random.random):
    #generates fogs at minimum distance
    tau = 2 * pi
    cellsize = r / sqrt(2)

    grid_width = int(ceil(width / cellsize))
    grid_height = int(ceil(height / cellsize))
    grid = [None] * (grid_width * grid_height)

    def grid_coords(p):
        return int(floor(p[0] / cellsize)), int(floor(p[1] / cellsize))

    def fits(p, gx, gy):
        yrange = list(range(max(gy - 2, 0), min(gy + 3, grid_height)))
        for x in range(max(gx - 2, 0), min(gx + 3, grid_width)):
            for y in yrange:
                g = grid[x + y * grid_width]
                if g is None:
                    continue
                if distance(p, g) <= r:
                    return False
        return True

    p = width * random(), height * random()
    queue = [p]
    grid_x, grid_y = grid_coords(p)
    grid[grid_x + grid_y * grid_width] = p

    while queue:
        qi = int(random() * len(queue))
        qx, qy = queue[qi]
        queue[qi] = queue[-1]
        queue.pop()
        for _ in range(k):
            alpha = tau * random()
            d = r * sqrt(3 * random() + 1)
            px = qx + d * cos(alpha)
            py = qy + d * sin(alpha)
            if not (0 <= px < width and 0 <= py < height):
                continue
            p = (px, py)
            grid_x, grid_y = grid_coords(p)
            if not fits(p, grid_x, grid_y):
                continue
            queue.append(p)
            grid[grid_x + grid_y * grid_width] = p
    return [(p[0]+offset_w,p[1]+offset_h) for p in grid if p is not None]


fogs=fast_poisson_disk_sampling(max_dims[0]-min_dims[0],max_dims[1]-min_dims[1],stream_radius
                                                    ,min_dims[0],min_dims[1])



#plt.plot(*zip(*fogs),'ro')
#plt.show()



initialiser(fogs)

def send_beacon(fog,car,beacon_handler=chosen_beacon_handler):
    return chosen_beacon_handler(fog,car)

def handle_stream(fog,car,stream_handler=chosen_stream_handler):
    return chosen_stream_handler(fog,car)

for time_stamp in parsed_data:
    for car_id in parsed_data[time_stamp]:
        car=parsed_data[time_stamp][car_id]
        for fog in fogs:
            if euclidean_distance(fog,car)<beacon_radius:
                send_beacon(fog,car)
            if euclidean_distance(fog,car)<stream_radius:
                handle_stream(fog,car)
    
handle_simulation_end()
















