# python imports
from queue import Queue, PriorityQueue
# class imports
from scheduler import Scheduler
from process import Process
from event import Event

# THE SCHEDULING ALGORITHM CLASSES BELOW EXTEND THE SCHEDULER BASE CLASS BASED ON THEIR NEEDS

# Decision Mode: Nonpreemptive 
class SchedulerFCFS(Scheduler):
    # FCFS does not have any options
    def __init__(self, algorithm, event_queue, options):
        readyQueue = Queue()
        super().__init__(algorithm, event_queue, options, readyQueue)
    
    def schedule(self, current_time: int):
        # dispatch the process if possible
        if self.isCPUIdle and not self.readyQueue.empty():
            # unpack the tuple values
            current_process, entered_time = self.readyQueue.get()
            # if it is the first time the process gains the control of CPU, set its start time
            if current_process.firstCPUAccess:
                current_process.stats.start_time = current_time
                current_process.setFirstCPUAccess(False)
            # calculate the response time for the process
            response_time = current_time - entered_time
            # response_time is 0 means the process did not wait for CPU
            if response_time != 0:
                current_process.stats.response_times.append(response_time)
            # get the duration of the CPU activity that is scheduled to run for completion
            duration = current_process.activities[-1]
            # remove the activity
            current_process.activities.pop()
            # create a new event
            if len(current_process.activities) > 1:
                newEvent = Event("BLOCK", current_process, current_time + duration)
            else:
                newEvent = Event("EXIT", current_process, current_time + duration)
            
            self.eventQueue.push(newEvent)
            # set isCPUIdle to false
            self.isCPUIdle = False

# Decision Mode: Preemptive (at time quantum)
class SchedulerVRR(Scheduler):
    def __init__(self, algorithm, event_queue, options):
        readyQueue = Queue()
        # Auxilary Queue
        self.auxQueue = Queue()
        super().__init__(algorithm, event_queue, options, readyQueue)

    def handleEvent(self, clock, event: Event):
        if(event.type == "ARRIVE"):
            self.handleArrivalEvent(clock, event)
        elif(event.type == "BLOCK"):
            self.handleBlockEvent(clock, event)
        elif(event.type == "UNBLOCK"):
            self.handleUnblockEvent(clock, event)
        elif(event.type == "TIMEOUT"):
            self.handleTimeoutEvent(clock, event)
        else:
            self.handleExitEvent(clock, event)
    
    def handleTimeoutEvent(self, clock, event: Event):
        # get the process whose CPU activity is executed until preemption
        current_process = event.process
        # add the activity whose just timed out back to the ready queue along with the time entered as tuple
        self.readyQueue.put((current_process, clock))
        # CPU now is avaiable for other activities
        self.isCPUIdle = True
        self.schedule(clock)
    
    def handleUnblockEvent(self, clock, event: Event):
        # get the process whose I/O activity is executed for completion
        current_process = event.process
        # remove the activity
        current_process.activities.pop()
        # add the unblocked process to the ready queue aux queue along with the time entered as tuple
        if self.options["quantum"] - current_process.lastCPUAccessDuration > 0:
            self.auxQueue.put((current_process, clock))
        else:
            self.readyQueue.put((current_process, clock))
        self.schedule(clock)

    def schedule(self, current_time: int):
        quantum = self.options["quantum"]
        # dispatch the process if possible
        # aux queue has priority over the ready queue
        if self.isCPUIdle:
            # get the process from one of the queues
            result = self._getProcessFromProperQueue()
            # both queues are empty
            if result == None:
                return 
            # unpack the tuple values
            (current_process, entered_time), fromAuxilaryQueue = result
            # if it is the first time the process gains the control of CPU, set its start time
            if current_process.firstCPUAccess:
                current_process.stats.start_time = current_time
                current_process.setFirstCPUAccess(False)
            # calculate the response time for the process
            response_time = current_time - entered_time
            # response_time is 0 means the process did not wait for CPU
            if response_time != 0:
                current_process.stats.response_times.append(response_time)
            # get the duration of the CPU activity that is scheduled to run now
            duration = current_process.activities[-1]
            # update the quantum value if the process is dispatched from the aux queue, otherwise do nothing
            if fromAuxilaryQueue:
                quantum -= current_process.lastCPUAccessDuration
            # non-negative value indicates that the entire activity can run to completion w/o getting 
            difference = quantum - duration
            if (difference >= 0):
                # remove the activity
                current_process.activities.pop()
                # store the duration of the current run - later will be used for dispatched processes from aux queue
                current_process.lastCPUAccessDuration = duration
                if len(current_process.activities) > 1:
                    # create a BLOCK event
                    newEvent = Event("BLOCK", current_process, current_time + duration)
                else:
                    # create an EXIT event
                    newEvent = Event("EXIT", current_process, current_time + duration)
            else:
                # update duration of the CPU activity that is scheduled to run now
                current_process.activities[-1] -= quantum
                # create a TIMEOUT event
                newEvent = Event("TIMEOUT", current_process, current_time + quantum)
            
            self.eventQueue.push(newEvent)
            # set isCPUIdle to false
            self.isCPUIdle = False
        
    def _getProcessFromProperQueue(self):
        if not self.auxQueue.empty():
            return self.auxQueue.get(), True
        elif not self.readyQueue.empty():
            return self.readyQueue.get(), False
        else:
            return None

# Decision Mode: Preemptive (at arrival)
class SchedulerSRT(Scheduler):
    def __init__(self, algorithm, event_queue, options):
        readyQueue = PriorityQueue()
        super().__init__(algorithm, event_queue, options, readyQueue)

    def handleEvent(self, clock, event: Event):
        if(event.type == "ARRIVE"):
            self.handleArrivalEvent(clock, event)
        elif(event.type == "BLOCK"):
            self.handleBlockEvent(clock, event)
        elif(event.type == "UNBLOCK"):
            self.handleUnblockEvent(clock, event)
        elif(event.type == "TIMEOUT"):
            self.handleTimeoutEvent(clock, event)
        else:
            self.handleExitEvent(clock, event)
  
    def handleArrivalEvent(self, clock, event: Event):
        # add the admitted process to the ready queue along with the time entered as tuple
        self.readyQueue.put(PqElementStr(event.process, clock, self.options['service_given'], self.options['alpha']))
        self.schedule(clock)
    
    def handleBlockEvent(self, clock, event: Event):
        # get the process whose CPU activity is executed for completion
        current_process = event.process
        # get the duration of the I/O activity
        io_duration = current_process.activities[-1]
        # remove the activity
        current_process.activities.pop()
        # create an unblock event
        self.eventQueue.push(Event("UNBLOCK", current_process, clock + io_duration))
        # now CPU is avaiable for other activities
        self.isCPUIdle = True
        self.schedule(clock) 
        
    def handleUnblockEvent(self, clock, event: Event):
        # get the process whose I/O activity is executed for completion
        current_process = event.process
        # remove the activity
        current_process.activities.pop()
        # add the unblocked process to the ready queue along with the time entered as tuple
        self.readyQueue.put(PqElementStr(current_process, clock, self.options['service_given'], self.options['alpha']))
        # remove the comp
        self.schedule(clock)  

    def handleExitEvent(self, clock, event: Event):
        # get the activity that just ran for completion
        current_process = event.process
        # remove the activity
        current_process.activities.pop()
        # update the finish time of the process that is ready to be terminated
        current_process.stats.finish_time = clock 
        # now CPU is avaiable for other activities
        self.isCPUIdle = True
        self.schedule(clock)
    
    def handleTimeoutEvent(self, clock,  event: Event):
        # get the process whose CPU activity is executed until preemption
        current_process = event.process
        # add the activity whose just timed out back to the ready queue along with the time entered as tuple
        self.readyQueue.put(PqElementStr(current_process, clock, self.options['service_given'], self.options['alpha']))
        # CPU now is avaiable for other activities
        self.isCPUIdle = True
        self.schedule(clock)

    def schedule(self, current_time: int):
        # check whether there is an element in the ready queue whose remaining excecution time is less than the current running process 
        

        # dispatch the process if possible
        if self.isCPUIdle and not self.readyQueue.empty():
            current = self.readyQueue.get()
            print("Dispatch")
            # if it is the first time the process gains the control of CPU, set its start time
            if current.process.firstCPUAccess:
                current.process.stats.start_time = current_time
                current.process.setFirstCPUAccess(False)

            # store the current running process
            self.current_running_process = current.process
            # calculate the response time for the process
            response_time = current_time - current.time_entered
            # response_time is 0 means the process did not wait for CPU
            if response_time != 0:
                current.process.stats.response_times.append(response_time)
            # get the duration of the CPU activity that is scheduled to run for completion
            duration = current.process.activities[-1]
            # create a new event
            if len(current.process.activities) > 1:
                newEvent = Event("BLOCK", current.process, current_time + duration)
            else:
                newEvent = Event("EXIT", current.process, current_time + duration)
            
            self.eventQueue.push(newEvent)
            # set isCPUIdle to false
            self.isCPUIdle = False

# Decision Mode: Nonpreemptive   
class SchedulerHRRN(Scheduler):
    def __init__(self, algorithm, event_queue, options):
        self.unsorted_processes = []
        # the queue needs to be a priority queue, not a simple queue
        readyQueue = PriorityQueue()
        super().__init__(algorithm, event_queue, options, readyQueue)
    
    def handleArrivalEvent(self, clock, event: Event):
        # add the admitted process to the list containing the process to be scheduled along with the time entered as tuple
        self.unsorted_processes.append((event.process, clock))
        self.schedule(clock)

    def handleUnblockEvent(self, clock, event: Event):
        # get the process whose I/O activity is executed for completion
        current_process = event.process
        # remove the activity
        current_process.activities.pop()
        # add the unblocked process to the list containing the process to be scheduled along with the time entered as tuple
        self.unsorted_processes.append((current_process, clock))
        # remove the comp
        self.schedule(clock)

    def schedule(self, current_time: int):
        # dispatch the process if possible
        if self.isCPUIdle and self.unsorted_processes != []:
            # prepare the processes before scheduling
            for item in self.unsorted_processes:
                current_process, time_entered = item
                response_time = current_time - time_entered
                # used to calculate response ratio, we'll be removed from a process's response times list after calculation
                current_process.stats.response_times.append(response_time if response_time != 0 else 0)
                # add a new entry to the ready queue
                self.readyQueue.put(PqElementHrrn(current_process, time_entered, self.options['service_given'], self.options['alpha']))
                current_process.stats.response_times.pop()
        
            # unpack the tuple 
            current = self.readyQueue.get()
            # remove the current process from the unsorted process list
            self.unsorted_processes.remove((current.process, current.time_entered))
            # if it is the first time the process gains the control of CPU, set its start time
            if current.process.firstCPUAccess:
                current.process.stats.start_time = current_time
                current.process.setFirstCPUAccess(False)
            # calculate the response time for the process
            response_time = current_time - current.time_entered
            # response_time is 0 means the process did not wait for CPU
            if response_time != 0:
                current.process.stats.response_times.append(response_time)
            # get the duration of the CPU activity that is scheduled to run for completion
            duration = current.process.activities[-1]
            # remove the activity
            current.process.activities.pop()
            # create a new event
            if len(current.process.activities) > 1:
                newEvent = Event("BLOCK", current.process, current_time + duration)
            else:
                newEvent = Event("EXIT", current.process, current_time + duration)
            
            self.eventQueue.push(newEvent)
            # set isCPUIdle to false
            self.isCPUIdle = False
    
        # reset the queue for the next call
        self.readyQueue = PriorityQueue()

# Decision Mode: Preemptive (at time quantum)
class SchedulerFeedBack(Scheduler):
    def __init__(self, algotihm, event_queue, options):
        super().__init__(algotihm, event_queue, options)
        # define any other things that are special to the algorithm 
        num_queues = self.options['num_priorities']
        self.readyQueues = []
        # create multiple queues
        for i in range(0, num_queues, 1):
            self.readyQueues.append(Queue())

    def handleEvent(self, clock, event: Event):
        if(event.type == "ARRIVE"):
            self.handleArrivalEvent(clock, event)
        elif(event.type == "BLOCK"):
            self.handleBlockEvent(clock, event)
        elif(event.type == "UNBLOCK"):
            self.handleUnblockEvent(clock, event)
        elif(event.type == "TIMEOUT"):
            self.handleTimeoutEvent(clock, event)
        else:
            self.handleExitEvent(clock, event)
    
    def handleArrivalEvent(self, clock, event: Event):
        # add the admitted process to the highest priority queue along with the time entered as tuple
        self.readyQueues[0].put((event.process, clock))
        self.schedule(clock)

    def handleUnblockEvent(self, clock, event: Event):
        # get the process whose I/O activity is executed for completion
        current_process = event.process
        # remove the activity
        current_process.activities.pop()
        # find which queue the current process was dispached from before blocking for I/O 
        priority = current_process.lastDispatchedFrom
        # add the unblocked process back to the queue with the same priority as it was previously dispatched from along with the time entered as tuple
        self.readyQueues[priority].put((current_process, clock))
        # remove the comp
        self.schedule(clock)

    def handleTimeoutEvent(self, clock, event: Event):
        # get the process whose CPU activity is executed until preemption
        current_process = event.process
        # find which queue the current process was dispached from before blocking for I/O 
        priority = current_process.lastDispatchedFrom
        # check whether the priority is at the lowest level 
        if priority == len(self.readyQueues) - 1:
            # add the unblocked process back to the queue with the same priority as it was previously dispatched from along with the time entered as tuple
            self.readyQueues[priority].put((current_process, clock))
        else:
            # add the unblocked process back to the queue with lower priority than the one it was previously dispatched from along with the time entered as tuple
             self.readyQueues[priority + 1].put((current_process, clock))
        # CPU now is avaiable for other activities
        self.isCPUIdle = True
        self.schedule(clock)
    
    def schedule(self, current_time: int):
        quantum = self.options["quantum"]
        # dispatch the process if possible
        if self.isCPUIdle:
            # get the process from one of the queues
            # the queue at index 0 has priority over the queue at index 1, index 1 > index 2, and so on.
            result = self._getProcessFromProperQueue()
            # both all the queues are empty
            if result == None:
                return 
            # unpack the tuple values
            (current_process, entered_time), priority = result
            # if it is the first time the process gains the control of CPU, set its start time
            if current_process.firstCPUAccess:
                current_process.stats.start_time = current_time
                current_process.setFirstCPUAccess(False)
            # set which queue the current process is dispatched from
            current_process.lastDispatchedFrom = priority
            # calculate the response time for the process
            response_time = current_time - entered_time
            # response_time is 0 means the process did not wait for CPU
            if response_time != 0:
                current_process.stats.response_times.append(response_time)
            # get the duration of the CPU activity that is scheduled to run now
            duration = current_process.activities[-1]
            # non-negative value indicates that the entire activity can run to completion w/o getting 
            difference = quantum - duration
            if (difference >= 0):
                # remove the activity
                current_process.activities.pop()
                if len(current_process.activities) > 1:
                    # create a BLOCK event
                    newEvent = Event("BLOCK", current_process, current_time + duration)
                else:
                    # create an EXIT event
                    newEvent = Event("EXIT", current_process, current_time + duration)
            else:
                # update duration of the CPU activity that is scheduled to run now
                current_process.activities[-1] -= quantum
                # create a TIMEOUT event
                newEvent = Event("TIMEOUT", current_process, current_time + quantum)
            
            self.eventQueue.push(newEvent)
            # set isCPUIdle to false
            self.isCPUIdle = False
        
    def _getProcessFromProperQueue(self):
        for i in range(0, len(self.readyQueues), 1):
            if not self.readyQueues[i].empty():
                # return the item from the selected queue along with its priority as integer
                return self.readyQueues[i].get(), i 

        # if every queue is empty, return nothing
        return None


class PqElementStr:
    def __init__(self, process, entered_time, service_time_given, alpha):
        self.process = process
        self.time_entered = entered_time
        self.service_time_given = service_time_given
        self.alpha = alpha 
        if not self.service_time_given:
            service_time = self.process.stats.getServiceTime()
        else:
            # use exponential averaging 
            pass
        pass
        
        self.remaining_time = service_time - self.process.execution_time_so_far
        
    def __lt__(self, other):
        # use min [s-e]
        return self.remaining_time < other.remaining_time

class PqElementHrrn:
    def __init__(self, process: Process, time_entered: int, service_time_given, alpha):
        self.process = process
        self.time_entered = time_entered
        self.time_spend_waiting = self.process.stats.getTotalWaitTime()
        self.service_time_given = service_time_given
        # calculate resopnse ratio
        if self.service_time_given:
            service_time = self.process.stats.getServiceTime()
        else:
            pass

        self.response_ratio = ((self.time_spend_waiting + service_time) / service_time)

    def __lt__(self, other):
        # use max [w + s] / s
        return self.response_ratio > other.response_ratio
    
    def __str__(self):
        return "Process " + str(self.process.pid) + ", Time Spent Waiting " + str(self.time_spend_waiting) + ", Response Ratio " +  str(self.response_ratio) + ", Service Time Given? " + str(self.service_time_given)
