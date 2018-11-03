cmake_minimum_required(VERSION 3.12)
project(python_immutables C)

set(CMAKE_C_STANDARD 90)

include_directories("/Users/gabbard/anaconda3/envs/immutableset/include/python3.6m/")
set(CMAKE_LIBRARY_PATH " /Users/gabbard/anaconda3/envs/immutableset/lib/python3.6")

add_library(python_immutables immutableset.c)