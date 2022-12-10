import re,sys
# class imports
from event import Event

class IllegalArgumentError(ValueError):
   def __init__(self, message):
        super().__init__(message)

optionsRequiredByAlgorithm = {
    "FCFS": {},
    "VRR": {"quantum" : None},
    "SRT": {"service_given": None, "alpha": None},
    "HRRN": {"service_given": None, "alpha": None},
    "FEEDBACK": {"quantum": None, "num_priorities": None}
}

# Base class for scheduling algorithms
class Scheduler():
    def __init__(self, algorithm, eventQueue, options, readyQueue = None):
        try:
            self.isCPUIdle = True
            self.eventQueue = eventQueue
            self.options = options
            # ready queue operates differently depending on the algorithm and holds process instances
            self.readyQueue = readyQueue
            # name of the algorithm to be used in the current run
            self.algorithm = algorithm
            self.current_running_process = None
            # validate algorihm configs
            self.__checkOptions()
            # validate if the given set of options valid for the current algorithm used in the current run
            if not self.__confirmAlgorithm():
                raise IllegalArgumentError("{} cannot have invalid set of options. Aborting...".format(self.algorithm))
        
        except ValueError or IllegalArgumentError as e:
            print(e)
            sys.exit(1)

    def __checkOptions(self):
        # FSFS does not have any options
        if self.algorithm == "FCFS":
            return 
        for key in self.options:
                if(key == "quantum" or key == "num_priorities"):
                    value = int(self.options[key])
                    if value < 0:
                        raise ValueError("{} must have a non-negative integer value. Aborting...".format(key.capitalize()))
                    self.options[key] = value
                elif(key == "service_given"):
                    if self.options[key] not in ("true", "false"):
                        raise ValueError()
                    value = self.options[key]
                    self.options[key] = True if value == "true" else False
                elif(key == "alpha"):
                    value = float(self.options[key])
                    if value < 0 or value > 1:
                        raise ValueError("{} must be between 0 and 1. Aborting...".format(key.capitalize()))
                    self.options[key] = value
                else:
                    raise IllegalArgumentError("Illegal argument given. {} is not a valid option. Aborting...".format(key))
        # if everything looks good, just return
        return 

    def __confirmAlgorithm(self):
        if self.algorithm == "FCFS":
            return self.options == {}
        else:
            # checks whetther two dictionaries have the same keys
            if not optionsRequiredByAlgorithm[self.algorithm].keys() == self.options.keys():
                return False

        # if everything looks good, just return true
        return True

    # Event handler for processing the requested event(s)
    # This function can be overriden by classes extending this class if they need to process more number of event types than default.
    def handleEvent(self, clock, event: Event):
        # uncomment the print statement below only when debugging
        # print(event)
        if(event.type == "ARRIVE"):
            self.handleArrivalEvent(clock, event)
        elif(event.type == "BLOCK"):
            self.handleBlockEvent(clock, event)
        elif(event.type == "UNBLOCK"):
            self.handleUnblockEvent(clock, event)
        else:
            self.handleExitEvent(clock, event)

    # Events that are common amongst every scheduler type
    def handleArrivalEvent(self, clock, event: Event):
        # add the admitted process to the ready queue along with the time entered as tuple
        self.readyQueue.put((event.process, clock))
        self.schedule(clock)

    def handleBlockEvent(self, clock, event: Event):
        # get the process whose CPU activity is executed for completion
        current_process = event.process
        # get the duration of the I/O activity
        io_duration = current_process.activities[-1]
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
        self.readyQueue.put((current_process, clock))
        # remove the comp
        self.schedule(clock)

    def handleExitEvent(self, clock, event: Event):
        # get the activity that just ran for completion
        current_process = event.process
        # update the finish time of the process that is ready to be terminated
        current_process.stats.finish_time = clock 

        self.isCPUIdle = True
        self.schedule(clock)

    # to be implemented by the sub classes
    def schedule(self):
        pass

