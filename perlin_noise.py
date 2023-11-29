"""
Module generates Perman noise
"""
import math
import numba
from PIL import Image
from flask import Flask, render_template
import shutil


def pseudo_random_generator(seed:str) -> str:
    """
    Function generates pseudo random numbers
    """
    seed_num=int(seed)
    seed=str((seed_num*seed_num+31513)%100000000)
    return '0'*(8-len(seed))+seed

def get_number(seed:str) -> int:
    """
    Function returns angle for vector from seed
    """
    return (int(seed[int(seed[3])%8])*13 +int(seed[int(seed[7])%8])*3)%36*10

@numba.njit(fastmath=True)
def vector_miltiplication(vector, alpha):
    """
    Function returns vector multiplication (second vector is )
    """
    return vector[0]*math.cos(alpha)+vector[1]*math.sin(alpha)

@numba.njit(fastmath=True)
def fill_one_pixel(y_pixel_vector, x_pixel_vector, vector):
    """
    Function fills one pixel due to data
    """
    return (vector_miltiplication((y_pixel_vector, x_pixel_vector), vector)+1)/2

def create_vectors_map(size, seed):
    """
    Function creates vectors array in spiral way
    """
    vector_array= [[0]*(size+1) for i in range(size+1)]
    x_coor, y_coor =size//2, size//2
    k=1
    for j in range(size//2):
        for i in range(k):
            vector_array[y_coor][x_coor+i]=get_number(seed)
            seed=pseudo_random_generator(seed)
        x_coor+=k
        for i in range(k):
            vector_array[y_coor-i][x_coor]=get_number(seed)
            seed=pseudo_random_generator(seed)
        y_coor-=k
        k+=1
        for i in range(k):
            vector_array[y_coor][x_coor-i]=get_number(seed)
            seed=pseudo_random_generator(seed)
        x_coor-=k
        for i in range(k):
            vector_array[y_coor+i][x_coor]=get_number(seed)
            seed=pseudo_random_generator(seed)
        y_coor+=k
        k+=1
    for i in range(size-1):
        vector_array[y_coor][x_coor+i]=get_number(seed)
        seed=pseudo_random_generator(seed)
    return vector_array

def convert_to_image(map_data, size, name, colors={0.5:(0, 0, 0), 1:(255, 255, 255)}):
    """
    Function converts data to image
    """
    img = Image.new ("RGB", (size, size), (0, 0, 0))
    new_image = [0]*(size*size)
    if colors != None:
        first_element = list(colors.keys())[0]
    for i in range(size*size):
        if colors!=None:
            current_color = colors[first_element]
            for k in colors:
                if map_data[i]<=k:
                    current_color = colors[k]
                    break
        new_image[i]=current_color
    img.putdata(new_image)
    img.save('static/'+name)

def recalculate_data(map_data, size):
    """
    Function recalculates data
    """
    minimum, maximum = min(map_data), max(map_data)
    delta = maximum-minimum
    for i in range(size*size):
        map_data[i]=(map_data[i]-minimum)/delta
    return map_data

@numba.njit(fastmath=True)
def smoothing(pixel1, pixel2, i, size_of_side):
    """
    Function smoothes point (linear interpolation + smooth stepping)
    """

    t = (i % size_of_side) / size_of_side
    return pixel1 + (pixel2 - pixel1) * t*t*t*(t*(t*6-15)+10)

def create_octava_n(size, seed, size_of_side):
    """
    Function creates n`octava Perlin noise
    """
    octava=size//size_of_side
    vectors_map=create_vectors_map(octava, seed)
    map = [0]*(size*size)
    for i in range(size):
        pixel_y_dist = i%size_of_side/size_of_side
        y_size = i//size_of_side
        for j in range(size):
            pixel_x_dist = j%size_of_side/size_of_side
            x_size = j//size_of_side
            # l = left, r = right, u = up, d = down
            pixel_l_u = fill_one_pixel(-pixel_y_dist, -pixel_x_dist, vectors_map[y_size][x_size])
            pixel_r_u = fill_one_pixel(-pixel_y_dist, 1-pixel_x_dist, vectors_map[y_size][x_size+1])
            pixel_l_d = fill_one_pixel(1-pixel_y_dist, -pixel_x_dist, vectors_map[y_size+1][x_size])
            pixel_r_d = fill_one_pixel(1-pixel_y_dist, 1-pixel_x_dist, vectors_map[y_size+1][x_size+1])
            pixel_u = smoothing(pixel_l_u, pixel_r_u, j, size_of_side)
            pixel_d = smoothing(pixel_l_d, pixel_r_d, j, size_of_side)
            map[i*size+j] = smoothing(pixel_u, pixel_d, i, size_of_side)
    return map

def sum_all_maps(size, array_of_maps):
    """
    Function sums every layer of the Perlin noise
    """
    for i in range(size*size):
        for k in range(1, len(array_of_maps)):
            array_of_maps[0][i]+=array_of_maps[k][i]/(1<<k)
    return recalculate_data(array_of_maps[0], size)

def convert_to_colors(string):
    try:
        string = string.replace(" ", "")
        if string[0]=='g':
            string = string[2:]
            temporary = string.split('/')
            start = tuple(int(i)for i in temporary[0][1:-1].split(','))
            finish = tuple(int(i)for i in temporary[1][1:-1].split(','))
            num = int(temporary[2])
            colors_dictionary = dict()
            for i in range(1, num+1):
                colors_dictionary[i/num] = tuple([int(start[0] + (finish[0] - start[0]) * (i-1)/(num-1)), int(start[1] + (finish[1] - start[1]) * (i-1)/(num-1)), int(start[2] + (finish[2] - start[2]) * (i-1)/(num-1))])
            return colors_dictionary
        if string[0] == 'c':
            string = string[2:]
            temporary = string.split('/')
            temporary.sort()
            colors_dictionary = dict()
            for i in temporary:
                new_temp = i.split(':')
                colors_dictionary[float(new_temp[0])] = tuple(int(i)for i in new_temp[1][1:-1].split(','))
            return colors_dictionary
    except:
        return False

def create_Perlin_noise(seed, size, size_of_side, number_of_octaves):
    """
    Function creates Perlin noise
    """
    array_of_maps=[0]*number_of_octaves
    for i in range(number_of_octaves):
        array_of_maps[i] = create_octava_n(size, seed, size_of_side)
        size_of_side>>=1
    return sum_all_maps(size, array_of_maps)
########
