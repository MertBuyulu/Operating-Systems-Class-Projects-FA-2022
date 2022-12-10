from threading import Thread, Semaphore
from queue import Queue, Empty
from random import randint
from time import sleep
from sys import exit

num_of_customers = 50
num_of_tellers = 3

# Getting manager's approval takes 10 ms
approval_time = 1
# Performing the requested transaction takes 50 ms
transaction_time = 5
# Wait for a customer to enter a bank for 10s, if no customer is left to serve close the bank.
wait_not_served_customers = 8
# initialize a global queue to hold customer
customer_queue = Queue(maxsize=num_of_customers)

# Teller - Customer Interaction
def teller_job(teller, print_lock, teller_lock, safe_lock, manager_lock):
    while True:
        try:
            display_action("{} is ready to serve.".format(teller), print_lock)
            display_action("{} is waiting for a customer.".format(teller), print_lock)
            customer = customer_queue.get(timeout=wait_not_served_customers)
            display_action("{} goes to {}.".format(customer, teller), print_lock)
            display_action("{} introduces itself to {}.".format(customer,teller), print_lock)
            display_action("{} is serving {}.".format(teller, customer), print_lock)
            display_action("{} asks {} for the transaction.".format(teller, customer), print_lock)
            sleep(0.3)
            
            option = randint(1,2)
            # option one is withdrawal
            if option == 1:
                display_action("{} requests a withdrawal transaction.".format(customer), print_lock) 
                sleep(0.3)
                # the teller asks the manager for 
                display_action("{} is handling the withdrawal transaction.".format(teller), print_lock)
                display_action("{} is going to the manager.".format(teller), print_lock)
                display_action("{} is getting the manager's permission.".format(teller), print_lock)
                manager_lock.acquire()
                display_action("{} got the manager's permission.".format(teller), print_lock)
                manager_lock.release()

            # option two is deposit
            else:
                display_action("{} requests a deposit transaction.".format(customer), print_lock)
                display_action("{} is handling the deposit transaction.".format(teller), print_lock) 
            
            display_action("{} is going to the safe.".format(teller), print_lock)
            # if the safe is fully occupied with other tellers
            if safe_lock._value == 0:
                display_action("All other tellers are busy working in the safe. {} is waiting for one of them to leave the safe.".format(teller), print_lock)
            safe_lock.acquire()
            display_action("{} is in the safe.".format(teller), print_lock)
            # the teller physically performs the transaction
            sleep(3)
            safe_lock.release()
            display_action("{0} left the safe. {0} is going back to inform {1}.".format(teller, customer), print_lock)
            display_action("{} is informing {} that the transaction is complete.".format(teller, customer) , print_lock)

            display_action("{} is leaving the bank.".format(customer), print_lock)
            teller_lock.release()
        
        # when Empty exception is received, it will imply that the customer_queue is empty and so we can exit from the teller threads
        except Empty:
            display_action("No customer left in line... {} is checking out.".format(teller), print_lock)
            break
        
def customer_job(customer, door_lock, print_lock, teller_lock):
    display_action('{} is going to the bank.'.format(customer), print_lock)
    display_action('{} is waiting at the door.'.format(customer), print_lock)
    door_lock.acquire()
    display_action("{} is going through the door.".format(customer), print_lock)
    # the time it takes for a customer to go through the door
    sleep(1)
    door_lock.release()
    display_action("{} is getting in line.".format(customer), print_lock)
    customer_queue.put(customer)
    display_action("{} is selecting a teller.".format(customer), print_lock)

    teller_lock.acquire()

def display_action(message, print_lock):
    print_lock.acquire()
    print(message)
    print_lock.release()

# main program
tellers = ["Teller {}".format(i + 1) for i in range(0, num_of_tellers)]
customers = ["Customer {}".format(i + 1) for i in range(0, num_of_customers)]

# create the necessary semaphores 
TellerLock = Semaphore(3)
DoorLock = Semaphore(2)
SafeLock = Semaphore(2)
ManagerLock = Semaphore(1)
PrintLock = Semaphore(1)

teller_threads = []
for i in range(0, len(tellers)):
    teller_threads.append(Thread(target=teller_job, args=(tellers[i], PrintLock, 
                            TellerLock, SafeLock, ManagerLock)))

# starting the teller threads
for teller_thread in teller_threads:
    teller_thread.start()
                                            
display_action("All tellers are ready serve customers.", PrintLock)
display_action("Bank is now open.", PrintLock)
sleep(2)
# starting the customer threads
for i in range(0, len(customers)):
    customer_thread = Thread(target=customer_job, args=(customers[i], DoorLock, PrintLock, TellerLock))
    customer_thread.start()

# prevent main thread to finish its execution before all of its sub threads finishes execution
for teller_thread in teller_threads:
    teller_thread.join()

display_action("Bank is now closed.", PrintLock)
# the program terminates successfully
exit(0)



