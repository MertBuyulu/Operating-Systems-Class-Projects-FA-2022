Class: Fall 2022 - CS 4348.502
Student Name: Ahmet Mert Buyulu
Net ID: AMB190003
Date: 12/09/22

IDE CHOICE

    - I have not used an IDE to implement this project. I implemented it through the terminal via Vim.

FILES NAMES

    The project consists of 7 python files: 
        1) simulation.py
            1.1) This file is the entry point to the entire program. 
            1.2) It opens up the process and schedule files and process them accordingly.
            1.3) Once the file processing is complete, it creates a scheduler of some type. 
                 The type of the scheduler depends on the first line read from the schedule fine.
            1.4) Once the scheduler is set up, it runs a while loop to start processing the events
            1.5) Once all the events are processed successfully, it breaks the loop
            1.6) Lastly, It prints individual/collective stats about each of the processes used in the current run of the program.
        2) scheduler.py
            1.1) It simulates a generic scheduler.
            1.2) It validates all the scheduler options along with whether which scheduling algorithm can have what set of options.
            1.3) It has unimplemented methods that are to be implemented by the classes extending it.
            1.4) It also contains method that are common for all the scheduling algorithms used in the program.
        3) algorithms.py
            1.1) It contains classes for various scheduling algorithms.
            1.2) Each of the classes in this file extends the Scheduler class specified in the scheduler.python
            1.3) Depending on the selected algorithm, each of the classes contained in this file has a different process scheduling approach.
            1.4) Some of the classes contained in this file, override some of the functions defined in Scheduler class based on their needs.
        4) event.py
            1.1) This file consists of two classes: Event, EventQueue
            1.2) Event class simulates a event, which has a type, process associated with it, and time.
            1.3) EventQueue simulates a priority queue.
        5) process.py
            1.1) This file consist of one class named Process
            1.2) Process class stores various information about a single process.
        6) process_stats.py
            1.1) This file consists of one class named ProcessStats
            1.2) ProcessStats class contains information on start, service, finish, turnaround, average response, and normalized turnaround time of a single process.

HOW TO COMPILE THE PROGRAM
    1) I have implemented the project in Python. Thus, it doesn't require any compilation.
    2) The program can be executed by running the following: "python3 simulation.py <scheduler_file_name.sf> <process_file_name.pf>"
    3) There will be auto generated cache py files once the command in the step 2 runs. In order to avoid the creation of cache py files, the command "python3 -B simulation.py <scheduler_info_name.sf> <process_file_name.pf>" can be run instead.
