# MAGIC METHOD: https://www.tutorialsteacher.com/python/magic-methods-in-python
EVENT_TYPE_PRIORITY = {
        "ARRIVE": 0,
        "UNBLOCK": 1,
        "TIMEOUT": 2,
        "BLOCK" : 3,
        "EXIT" : 4
    }

class Event:
    # An event has a type, associated process, and the time it happens
    def __init__(self, etype, process, time):
        self.type = etype
        self.process = process
        self.time = time
    def __lt__(self, other):
        if self.time == other.time:
            # Break Tie with event type
            if self.type == other.type:
                # Break type tie by pid
                return self.process.pid < other.process.pid
            else:
                return EVENT_TYPE_PRIORITY[self.type] < EVENT_TYPE_PRIORITY[other.type]
        else:
            return self.time < other.time
    def __str__(self):
        return "At time " + str(self.time) + ", " + self.type + " Event for Process " + str(self.process.pid)

# A Priority Queue that sorts Events by '<'
class EventQueue:
    def __init__(self):
        self.queue = []
        self.dirty = False
    def push(self,item):
        if type(item) is Event:
            self.queue.append(item)
            self.dirty = True
        else:
            raise TypeError("Only Events allowed in EventQueue")
    def __prepareLookup(self, operation):
        if self.queue == []:
            raise LookupError(operation + " on empty EventQueue")
        if self.dirty:
            self.queue.sort(reverse=True)
            self.dirty = False
    def pop(self):
        self.__prepareLookup("Pop")
        return self.queue.pop()
    # Look at the next event
    def peek(self):
        self.__prepareLookup("Peek")
        return self.queue[-1]
    def empty(self):
        return len(self.queue) == 0
    def remove(self, process_id):
        for event in self.queue:
            # remove the block/exit event for the process that is preempted during execution
            if event.process.pid == process_id:
                self.queue.remove(event)
                self.dirty = True
                return
    def __str__(self):
        return "EventQueue(" + str(self.queue) + ")"

