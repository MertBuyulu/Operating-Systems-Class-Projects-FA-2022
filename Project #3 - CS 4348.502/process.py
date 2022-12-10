# class imports
from process_stats import ProcessStats

class Process():
    # activity is defined as an integer value representing a duration of a CPU or I/O event 
    def __init__(self,pid,arrival_time,activities):
        self.pid = pid
        # reverse the list so removal of activities from the end of the list will take O(1) time
        self.activities = activities[::-1]
        # calculate the service time by summing up all the CPU activities
        service_time = sum(self.activities[0::2])
        # stats field contains performance related info about the process
        self.stats = ProcessStats(arrival_time, service_time)
        # needed for start time stat value
        self.firstCPUAccess = True
        # needed for VVR 
        self.lastCPUAccessDuration = 0
        # needed for Feedback - initially all process are put in to the highest priority queue denoted with integer value 0
        self.lastDispatchedFrom = 0
        self.execution_time_so_far = 0
    
    # Setters
    def setFirstCPUAccess(self, status: bool):
        self.firstCPUAccess = status
    
    def __str__(self):
        return "Proccess " + str(self.pid) + ", Arrive " + str(self.stats.getArrivalTime()) + ": " + str(self.activities)
