import numpy as np

def gen_gaussian (width):
    empty_arr = np.zeros(4*width)
    x = np.arange(4*width)
    gaussian_arr = np.power(2, -1 * np.power(2*(x - 2*width)/width, 2))
    return gaussian_arr, empty_arr

def gen_gaussian_edge (edge_width, pulse_width):
    empty_arr = np.zeros(pulse_width)
    pulse = np.ones(pulse_width)
    x = np.arange(4*edge_width)
    gaussian_arr = np.power(2, -1 * np.power(2*(x - 2*edge_width)/edge_width, 2))
    pulse[-1*(2*edge_width)::] = gaussian_arr[-1*(2*edge_width)::]
    pulse[0:2*edge_width]=gaussian_arr[0:2*edge_width]
    return pulse, empty_arr

def gen_cavity (width, marker_cavity_delay, marker_width):
    cavity = np.zeros(width)
    cavity[1:-1] = 1
    marker = np.zeros(width)
    marker[marker_cavity_delay:marker_cavity_delay+marker_width] = 1
    empty = np.zeros(width)
    return cavity,marker,empty

def gen_space(width):
    return np.zeros(width)