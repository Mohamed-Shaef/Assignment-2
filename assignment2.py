#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py 
Author: Mohamed Shaef
Semester: Fall 2024

The python code in this file is original work written by
Mohamed Shaef. No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or on-line resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: This Script works by finding the process ID of a application that the user provides.
once it has the application name it can search for the Process ID of the application.
It will find the amount of memory that the application is using out of total and list in a graph.
if used without an option this script will proivide the total memory and how much of that total
memory has been used and will also display this in a graph.

'''

import argparse
import os, sys

def parse_command_args() -> object:
    "Set up argparse here. Call this function inside main."
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts",epilog="Copyright 2023")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    # add argument for "human-readable". USE -H, don't use -h! -h is reserved for --help which is created automatically.
    parser.add_argument("-H", "--human-readable", action="store_true", help="Prints file sizes in human readable format",)
    # check the docs for an argparse option to store this as a boolean.
    parser.add_argument("program", type=str, nargs='?', help="if a program is specified, show memory use of all associated processes. Show only total use is not.")
    args = parser.parse_args()
    return args
# create argparse function
# -H human readable
# -r running only

def percent_to_graph(percent: float, length: int=20) -> str:
    """
    This function takes a percentage and from (0.0 to 1.0) and visualizes
    that percentage as a graph. The range of the percentage is first verified,
    the number of characters required is then calculated. Finally the function
    returns the amount required.
    """
    
    # To check the percent is within the range
    if not (0.0 <= percent <= 1.0):
        raise ValueError("Percentage must be between 0.0 and 1.0")
   
    # Calculate the number of filler characters required
    filled_length = round(percent * length)
    empty_length = length - filled_length
   
    # Return the bar graph as a string
    return '=' * filled_length + ' ' * empty_length

def get_sys_mem() -> int:
    """
    This function works by accessing /proc/meminfo to determine
    the total system memory. 
    """

    with open('/proc/meminfo', 'r') as meminfo:
        for line in meminfo:
            if line.startswith("MemTotal:"):
                return int(line.split()[1])  # find the value in kB
    raise ValueError("MemTotal not found in /proc/meminfo")

def get_avail_mem() -> int:
    """
    This function works by accessing /proc/meminfo to determine
    the total memory available 
    """

    with open('/proc/meminfo', 'r') as meminfo:
        for line in meminfo:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1])  # find the value in kB
    raise ValueError("MemAvailable not found in /proc/meminfo")




def pids_of_prog(app_name: str) -> list:
    """
    given an app name, return all pids associated with app
    this function works by finding the process id associated
    with an app name
    """
    output = os.popen(f"pidof {app_name}").read().strip()
    return output.split() if output else []


    
def rss_mem_of_pid(proc_id: str) -> int:
    """
    given a process id, return the resident memory used, zero if not found
    this function works by taking the pid of an app and finding the memory 
    that the application has used
    """
    rss_total = 0
    smaps_path = f"/proc/{proc_id}/smaps"

    try:
        with open(smaps_path, "r") as smaps_file:
            for line in smaps_file:
                if line.startswith("Rss:"):
                    rss_total += int(line.split()[1])  # Extract memory in kB
    except FileNotFoundError:
        # Process may have ended; return 0
        return 0
    except Exception as e:
        # Log unexpected errors and return 0
        print(f"Error reading smaps for PID {proc_id}: {e}", file=sys.stderr)
        return 0

    return rss_total

def bytes_to_human_r(kibibytes: int, decimal_places: int=2) -> str:
    "turn 1,024 into 1 MiB, for example"
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']  # iB indicates 1024
    suf_count = 0
    result = kibibytes 
    while result > 1024 and suf_count < len(suffixes):
        result /= 1024
        suf_count += 1
    str_result = f'{result:.{decimal_places}f} '
    str_result += suffixes[suf_count]
    return str_result

if __name__ == "__main__":
    args = parse_command_args()

    if not args.program:
        total_mem = get_sys_mem()
        available_mem = get_avail_mem()
        used_mem = total_mem - available_mem
        percent_used = used_mem / total_mem
        bar_graph = percent_to_graph(percent_used, args.length)

        if args.human_readable:
            total_mem_display = bytes_to_human_r(total_mem)
            used_mem_display = bytes_to_human_r(used_mem)
        else:
            total_mem_display = f"{total_mem} kB"
            used_mem_display = f"{used_mem} kB"

        print(f"Memory         [{bar_graph}] {percent_used:.0%} {used_mem_display}/{total_mem_display}")
    else:
        pids = pids_of_prog(args.program)
        if not pids:
            print(f"{args.program} not found.")
            sys.exit(1)

        total_rss = 0
        for pid in pids:
            rss = rss_mem_of_pid(pid)
            total_rss += rss
            rss_display = bytes_to_human_r(rss) if args.human_readable else f"{rss} kB"
            print(f"{pid:<15} {rss_display}")

        percent_used = total_rss / get_sys_mem()
        bar_graph = percent_to_graph(percent_used, args.length)

        if args.human_readable:
            total_rss_display = bytes_to_human_r(total_rss)
            total_mem_display = bytes_to_human_r(get_sys_mem())
        else:
            total_rss_display = f"{total_rss} kB"
            total_mem_display = f"{get_sys_mem()} kB"

        print(f"{args.program:<15} [{bar_graph}] {percent_used:.0%} {total_rss_display}/{total_mem_display}")