import pyspark
from pyspark import SparkContext
import cv2
import numpy as np 
import scipy as sp
import struct
from helper_functions import *
from constants import *

def convert(pair):
    # (key = image_id, value = image_matrix)
    image_id = pair[0] 
    image_matrix = pair[1]
    height, width = np.array(image_matrix.shape[:2])
    Y, crf, cbf = convert_to_YCrCb(image_matrix)
    return [((image_id, height, width), (0, Y)), ((image_id, height, width), (1, crf)), ((image_id, height, width), (2, cbf))]

def block(pair):
    # (key = (image_id, height, width), value = (channel_id, channel))
    output = []
    key = pair[0]
    image_id = key[0]
    height = key[1]
    width = key[2]
    value = pair[1]
    channel_id = value[0]
    channel = value[1]
    no_rows = channel.shape[0]
    no_cols = channel.shape[1]
    no_vert_blocks = no_cols / b_size
    no_horz_blocks = no_rows / b_size
    for j in range(no_vert_blocks):
        for i in range(no_horz_blocks):
            i_start = i * b_size
            i_end = (i + 1) * b_size
            j_start = j * b_size
            j_end = (j + 1) * b_size
            sub_block = channel[i_start : i_end, j_start : j_end]
            output.append(((image_id, channel_id), (sub_block, i_start, i_end, j_start, j_end, height, width, no_rows, no_cols)))
    return output

def transform(pair):
    # (key = (image_id, channel_id), value = (sub_block, left, right, up, down, height, width, no_rows, no_cols))
    key = pair[0]
    value = pair[1]
    block = value[0]
    channel_id = key[1]
    dct = dct_block(block.astype(np.float32) - 128)
    q = quantize_block(dct, channel_id==0, QF = 99)
    inv_q = quantize_block(q, channel_id==0, QF = 99, inverse = True)
    inv_dct = dct_block(inv_q, inverse = True)
    key = (key[0], key[1], value[5], value[6])
    value = (inv_dct, value[1], value[2], value[3], value[4], value[7], value[8])
    return (key, value)

def reduce_blocks(arg1, arg2):
    # (key = (image_id, channel_id, height, width), value = (sub_block, left, right, up, down, no_rows, no_cols))
    if (type(arg1).__module__ == np.__name__):
        if (type(arg2).__module__ == np.__name__):
            return np.add(arg1, arg2)
        arg1[arg2[1] : arg2[2], arg2[3] : arg2[4]] = arg2[0]
        return arg1
    if (type(arg2).__module__ == np.__name__):
        arg2[arg1[1] : arg1[2], arg1[3] : arg1[4]] = arg1[0]
        return arg2
    dst = np.zeros((arg1[5], arg1[6]), np.float32)
    dst[arg1[1] : arg1[2], arg1[3] : arg1[4]] = arg1[0]
    dst[arg2[1] : arg2[2], arg2[3] : arg2[4]] = arg2[0]
    return dst

def convert_channels(pair):
    # (key = (image_id, channel_id, height, width), value = channel)
    key = pair[0]
    value = pair[1]
    return (key[0], (key[2], key[3], key[1], value))

def reduce_channels(arg1, arg2):
    # (key = image_id, value = (height, width, channel_id, dst))
    if (type(arg1).__module__ == np.__name__):
        channel2 = arg2[3]
        channel2 += 128
        channel2[channel2>255] = 255
        channel2[channel2<0] = 0
        channel2 = resize_image(channel2, arg2[1], arg2[0])
        arg1[:,:,arg2[2]] = channel2
        return arg1
    if (type(arg2).__module__ == np.__name__):
        channel1 = arg1[3]
        channel1 += 128
        channel1[channel1>255] = 255
        channel1[channel1<0] = 0
        channel1 = resize_image(channel1, arg1[1], arg1[0])
        arg2[:,:,arg1[2]] = channel1
        return arg2
    reimg = np.zeros((arg1[0], arg1[1], 3), np.uint8)
    channel2 = arg2[3]
    channel2 += 128
    channel2[channel2>255] = 255
    channel2[channel2<0] = 0
    channel2 = resize_image(channel2, arg2[1], arg2[0])
    channel1 = arg1[3]
    channel1 += 128
    channel1[channel1>255] = 255
    channel1[channel1<0] = 0
    channel1 = resize_image(channel1, arg1[1], arg1[0])
    reimg[:,:,arg2[2]] = channel2
    reimg[:,:,arg1[2]] = channel1
    return reimg

def map_images(pair):
    # (key = (image_id, height, width), value = [(channel_id, channel)...])
    key = pair[0]
    value = pair[1]
    value = to_rgb(value)
    return (key, value)

### WRITE ALL HELPER FUNCTIONS ABOVE THIS LINE ###

def generate_Y_cb_cr_matrices(rdd):
    rdd = rdd.flatMap(convert)
    return rdd

def generate_sub_blocks(rdd):
    rdd = rdd.flatMap(block)
    return rdd

def apply_transformations(rdd):
    rdd = rdd.map(transform)
    return rdd

def combine_sub_blocks(rdd):
    rdd = rdd.reduceByKey(reduce_blocks)
    rdd = rdd.map(convert_channels)
    rdd = rdd.reduceByKey(reduce_channels)
    rdd = rdd.map(map_images)
    return rdd

def run(images):
    """
    THIS FUNCTION MUST RETURN AN RDD

    Returns an RDD where all the images will be proccessed once the RDD is aggregated.
    The format returned in the RDD should be (image_id, image_matrix) where image_matrix 
    is an np array of size (height, width, 3).
    """
    sc = SparkContext()
    rdd = sc.parallelize(images, 16) \
        .map(truncate).repartition(16)
    rdd = generate_Y_cb_cr_matrices(rdd)
    rdd = generate_sub_blocks(rdd)
    rdd = apply_transformations(rdd)
    rdd = combine_sub_blocks(rdd)
    return rdd
