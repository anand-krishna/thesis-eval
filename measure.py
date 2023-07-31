#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import sys
import subprocess
import statistics as stat
import csv

import argparse
from pathlib import Path

monotonic_clock = time.CLOCK_MONOTONIC

def save_to_csv(results_dict, save_file_path):
    with open(save_file_path, "w+") as save_file:
        writer = csv.writer(save_file)
        for app_name,time_vals in results_dict.items():
            # calculate avg, stdev
            time_vals_copy = time_vals.copy()

            if len(time_vals_copy) > 1:
                avg_time = sum(time_vals_copy) / len(time_vals_copy)
                stddev   = stat.stdev(time_vals_copy)
                time_vals_copy.append(avg_time)
                time_vals_copy.append(stddev)

            # write values to csv
            time_vals_copy.insert(0, app_name)
            writer.writerow(time_vals_copy)


def execute_application(app_name, host_name, exec_args, app_dir, result_dir):
        execution_log_path = Path(f"{result_dir}/{app_name}.log")
       
        old_dir = os.getcwd()

        with open(execution_log_path, "a+") as execution_log:        
            os.chdir(f"{app_dir}/{app_name}")
            
            # prepare exec command.
            # Arguments must be converted to a list for subprocess.run() (not continuous string).
            # Also, any space (' ') put at the head/tail of each argument can cause an error.
            exec_app = f"./{host_name}"
            exec_cmd = list()
            exec_cmd.append(exec_app)
            exec_cmd += exec_args

            print(f"\tExecuting {app_name}", end=", ")
            t1  = time.clock_gettime(monotonic_clock)
            subprocess.run(exec_cmd, stdout=execution_log, stderr=execution_log)
            t2  = time.clock_gettime(monotonic_clock)
            print(f"\tExecution took: {t2-t1}", end=", \n")

            os.chdir(old_dir)

            return t2 - t1


def execute_and_measure(num_repetitions, csv_file, app_dir, result_dir):
    results = {}
    with open(csv_file, 'r') as csv_data:
        app_list = csv.reader(csv_data)
        for rep in range(num_repetitions):
            app_list = csv.reader(csv_data)
            for i,row in enumerate(app_list):
                print("\t", i, row)
                if results.get(row[0], None) is None:
                    results[row[0]] = list()
                execution_time = execute_application(row[0], row[1], row[2:], app_dir, result_dir)
                results[row[0]].append(execution_time)
            csv_data.seek(0)
    
    return results

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("app_dir", metavar="app-dir")
    parser.add_argument("csv_file", metavar="csv-file")
    parser.add_argument("result_dir", metavar="res-dir")
    parser.add_argument("reps")
    parser.add_argument("save_file", metavar="save-file")


    args = parser.parse_args()

    app_dir = Path(args.app_dir)
    csv_file = Path(args.csv_file)
    result_dir = Path(args.result_dir)
    num_repetitions = int(args.reps)
    save_file = Path(args.save_file)

    print(f"Starting Execution and Measurement - {num_repetitions} times.")
    results = execute_and_measure(num_repetitions, csv_file, app_dir, result_dir)
    print(f"Completed Execution and Measurement - {num_repetitions} times.")


    print(f"Starting Aggregation and Saving Results to File - {save_file}.")
    save_to_csv(results, save_file)
    print(f"Completed Aggregation and Saving Results to File - {save_file}.")
"""

result_dir = sys.argv[1]
out_csv = open(sys.argv[2], 'a')
in_csv = open(sys.argv[3], 'r')
repeat = int(sys.argv[4])

app_list = csv.reader(in_csv)
clk = time.CLOCK_MONOTONIC
dict_results = dict()

# repeat execution 
for count in range(repeat):
    in_csv.seek(0)

    # to avoid executing the same workload continuously, all workloads run in order in one loop
    # otherwise, FPGA reconfiguration is skipped from the second execution
    for i,row in enumerate(app_list):
        app_name = row[0]
        exec_cmd_arg = row[1:]

        log = open(result_dir+"/"+app_name+".log", 'a')
        os.chdir(app_name)
        # print("current app dir: ", os.getcwd())

        # add time_list for each app to the dict only once 
        if app_name not in dict_results:
            dict_results.update({app_name: list()})

        # prepare exec command. 
        # Arguments must be converted to a list for subprocess.run() (not continuous string). 
        # Also, any space (' ') put at the head/tail of each argument can cause an error. 
        exec_app = "./"+app_name
        exec_cmd = list()
        exec_cmd.append(exec_app)
        exec_cmd = exec_cmd+exec_cmd_arg

        # measure time
        # print("DEBUG: current dir: ", os.getcwd())
        # print("DEBUG: exec cmd: ", exec_cmd)
        print(app_name, end=", ")
        t1  = time.clock_gettime(clk)
        subprocess.run(exec_cmd, stdout=log, stderr=log)
        t2  = time.clock_gettime(clk)
        print(t2-t1, end=", \n")
        dict_results[app_name].append(t2-t1)
    
        os.chdir("../")

print(dict_results)

# Write results to csv
in_csv.seek(0)
for i,row in enumerate(app_list):
    writer = csv.writer(out_csv)
    app_name = row[0]

    # calculate avg, stdev
    times = dict_results[app_name].copy();

    if len(times) > 1: 
        avg_time = sum(times)/len(times)
        stddev   = stat.stdev(times)
        times.append(avg_time)
        times.append(stddev)

    # write values to csv
    times.insert(0, app_name)
    print(times)
    writer.writerow(times)
"""
