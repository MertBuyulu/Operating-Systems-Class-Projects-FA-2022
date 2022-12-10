# python imports
import sys
import re
from queue import Queue
# class imports
from process import Process
from event import Event, EventQueue
from algorithms import SchedulerFCFS, SchedulerHRRN, SchedulerSRT, SchedulerVRR, SchedulerFeedBack

class Simulation:
    # Initialize the simulation with the scheduler file and the process file
    def __init__(self, schedFile, procFile):
        # set initial clock value to 0
        self.clock = 0
        self.eventQueue = EventQueue()
        self.processes = self._getProcesses(procFile)
        # Initialize Event Queue
        for p in self.processes:
            self.eventQueue.push(Event("ARRIVE", p, p.stats.getArrivalTime()))

        self.scheduler = self._getScheduler(schedFile)
        
    def __str__(self):
        return "Simulation(" + str(self.scheduler) + ", " + str(self.processes) + ") : " + str(self.eventQueue)

    def _getProcesses(self,procFile):
        procs = []
        with open(procFile) as f:
            lines = [line.rstrip() for line in f] # Read lines of the file
            lineNumber = 1
            for p in lines:
                tmp = re.split('\s+', p)
                # Make sure there enough values on the line
                if len(tmp) < 2:
                    raise ValueError("Process missing activities and possible the arrival time at line " + str(lineNumber))
                # Check to make sure there is a final CPU activity
                if len(tmp) % 2 == 1:
                    raise ValueError("Process with no final CPU activity at line " + str(lineNumber))
                # Check to make sure each activity, represented by a duration is an integer, and then convert it.
                for i in range(0,len(tmp)):
                    if re.fullmatch('\d+', tmp[i]) == None:
                        raise ValueError("Invalid process on line " + str(lineNumber))
                    else:
                        tmp[i] = int(tmp[i])
                procs.append(Process(lineNumber-1,tmp[0],tmp[1:]))
                lineNumber = lineNumber + 1
        return procs

    def _getScheduler(self, schedFile):
        # store algorithm configs into a dict
        options = {}
        algorithm = None
        with open(schedFile) as f:
            lines = [line.rstrip() for line in f] # Read lines of the file
            algorithm = lines[0]
            lineNumber = 1
            for line in lines[1:]:
                split = re.split('\s*=\s*', line)
                if len(split) != 2:
                    raise ValueError("Invalid Scheduler option at line " + str(lineNumber))
                options[split[0]] = split[1]
                lineNumber+=1
        
        selected_algorithm = None
        # Select the approriate scheduler algorithm, create an instance of it, and return it from the function
        if algorithm == "FCFS":
            selected_algorithm = SchedulerFCFS(algorithm, self.eventQueue, options)
        elif algorithm  == "VRR":
            selected_algorithm = SchedulerVRR(algorithm, self.eventQueue, options)
        elif algorithm  == "SRT":
            selected_algorithm = SchedulerSRT(algorithm, self.eventQueue, options)
        elif(algorithm  == "HRRN"):
            selected_algorithm = SchedulerHRRN(algorithm, self.eventQueue, options)
        elif algorithm  == "FEEDBACK":
            selected_algorithm = SchedulerFeedBack(algorithm, self.eventQueue, options)
        # default case
        else:
            raise TypeError("Scheduling Algorithm {} not supported by the system. Aborting...".format(algorithm))
        
        return selected_algorithm

    def _printSingleStat(self, state_label, stat_value):
        print("    {} Time: {}".format(state_label, stat_value))
    
    def _printStats(self):
        stat_titles = ["Arrival", 'Service', "Start", "Finish", "Turnaround", "Normalized Turnaround", "Average Response"]
        stat_functions_dict = { "Arrival": "getArrivalTime", 'Service': "getServiceTime",
                                "Finish": "getFinishTime", "Turnaround": "getTurnaroundTime", 
                                "Normalized Turnaround" : "getNormalizedTurnaroundTime", 
                                "Average Response": "getAverageResponseTime", "Start": "getStartTime"
                            }

        # keep track of the running sums of individual stats
        turnaroundTimeSum = 0
        normTurnaroundTimeSum = 0
        responseTimesSum = 0

        # print individual process statistics 
        for i in range(0, len(self.processes), 1):
            print("For process {}:".format(i))
            # constant time - runs 7 times regardless of the outer loop
            for j in range(0, 7, 1):
                # get the function name dynamically
                get_selected_stat = getattr(self.processes[i].stats, stat_functions_dict[stat_titles[j]])
                self._printSingleStat(stat_titles[j], get_selected_stat())
                # update running sums of system wide statistics
                if(stat_titles[j] == "Turnaround"):
                    turnaroundTimeSum += get_selected_stat()
                elif (stat_titles[j] == "Normalized Turnaround"):
                    normTurnaroundTimeSum += get_selected_stat()
                elif (stat_titles[j] == "Average Response"):
                    responseTimesSum += get_selected_stat()
                else:
                    continue

        # print system wide statistics 
        print("System Wide Statistics:")
        self._printSingleStat("Mean Turnaround", turnaroundTimeSum/len(self.processes))
        self._printSingleStat("Mean Normalized Turnaround", normTurnaroundTimeSum/len(self.processes))
        self._printSingleStat("Mean Average Response Time", responseTimesSum/len(self.processes))

    def start(self):
        while not self.eventQueue.empty():
            # remove the next event to process from the event queue
            nextEvent = self.eventQueue.pop()
            self.clock = nextEvent.time
            self.scheduler.handleEvent(self.clock, nextEvent)
            
            # process all events scheduled to occur at the same clock val
            while not self.eventQueue.empty() and self.clock == self.eventQueue.peek():
                nextEvent = self.eventQueue.pop()
                self.scheduler.handleEvent(self.clock, nextEvent)

        # print the stats of the current run
        self._printStats()

def main():
    # check to see if the correct # of arguments are passed in to the program as input
    num_of_args = len(sys.argv)
    if (num_of_args) != 3:
        raise TypeError("Invalid number of arguments given. Expected: 3, Received: {}".format(num_of_args))
    # start the simulation by creating a new Simulation object instance
    schedule_simulator = Simulation(sys.argv[1], sys.argv[2])
    schedule_simulator.start()

if __name__ == "__main__":
    main()