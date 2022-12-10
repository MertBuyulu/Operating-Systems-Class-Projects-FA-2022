
class ProcessStats:
    def __init__(self, arrival_time, service_time):
        # the time the process enters the system
        self.arrival_time = arrival_time
        # the time the process first gains the control of the CPU
        self.start_time = 0
        # the time when the last event of the process is complete
        self.finish_time = 0
        # the total amount of time the process spends in the CPU
        self.service_time = service_time
        # response time is the is the time a processes must wait for the CPU.
        # (i.e. the time from when a processes is placed in the ready queue until the process is selected to run)
        self.response_times = []
    
    # Getters
    def getArrivalTime(self):
        return self.arrival_time
    
    def getStartTime(self):
        return self.start_time

    def getFinishTime(self):
        return self.finish_time
    
    def getServiceTime(self):
        return self.service_time
    
    def getTotalWaitTime(self):
        sum = 0
        for response_time in self.response_times:
            sum += response_time

        return sum
    
    # the duration between the arrival time and finish time
    def getTurnaroundTime(self):
        return self.getFinishTime() - self.getArrivalTime();
    
    # TODO: UPDATE THE RETURN STATEMENTS
    def getNormalizedTurnaroundTime(self):
        return self.getTurnaroundTime() / self.getServiceTime();

    def getAverageResponseTime(self):
        sum = 0
        for response_time in self.response_times:
            sum += response_time

        return sum / len(self.response_times);
    