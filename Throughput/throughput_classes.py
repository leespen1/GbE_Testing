import subprocess
from subprocess import PIPE, Popen, call
import json
import time





##################################################
#################################################
#
#  Modified class for throughput testing
#
#  Contains mostly the same functions, with some
#  additional ones to conduct throughput tests,
#  and logs the results of most functions
#
#################################################
##################################################





class pScheduler_Testing_throughput():

    def __init__(self, log_path="", source_list = [], dest_list = []):


        self.sources = source_list
        self.dests = dest_list

        all_hosts_list = []
        for host in source_list:
            all_hosts_list.append(host)
        for host in dest_list:
            if host not in all_hosts_list:
                all_hosts_list.append(host)
  
        if all_hosts_list == []:

            self.hosts = ["hubps03",
                          "hubps04",
                          "hubps05",
                          "hubps06",
                          "hubps07", 
                          "hubps08", 
                          "hubps09", 
                          "hubps10",
                          "hubps11",
                          "hubps12",
                          "hubps13",
                          "hubps14",
                          "hubps15", 
                          "hubps16",
                          "hubps17",
                          "hubps18"]
        else:
            self.hosts = all_hosts_list
        

        if self.dests == []:
            self.dests = self.hosts

        #By default only test against two source hosts 
        if self.sources == []:
            self.sources = ["hubps03",
                            "hubps04"]



        #Create all the structure used for the throughput tests

        self.results = {}

        for source in self.sources:
            self.results[source] = {}
            for dest in self.dests:
                self.results[source][dest] = {}
                self.results[source][dest]["Forward"] = {"Schedule Clear": {} }
                self.results[source][dest]["Reverse"] = {"Schedule Clear": {} }
   
        self.results["Summary"] = {}
        self.results["Summary"]["Total Tests"] = []
        self.results["Summary"]["Skipped Tests"] = [] #Number of tests skipped because pScheduler not found on host
        self.results["Summary"]["Busy Tests"] = []    #Number of tests which did not have a clear schedule while running (not skipped)
        self.results["Summary"]["Passed Tests"] = []
        self.results["Summary"]["Failed Tests"] = []


        self.log = Log(log_path)



    def check_routes(self, update_hosts=False):
    ######
    # Check whether pscheduler can be found on each host in the object's list of hosts.
    # Returns list of hosts which could not be found

        good_hosts_list = []
        bad_hosts_list = []
        for host in self.hosts:
            if self.ping(host) == True:
                good_hosts_list.append(host)
            else:
                bad_hosts_list.append(host)

        if update_hosts==True:
           self.hosts = good_hosts_list
           for host in self.sources:
             if host in bad_hosts_list:
               self.sources.remove(host)
           for host in self.dests:
             if host in bad_hosts_list:
               self.dests.remove(host)

        return bad_hosts_list

    
    def ping (self, host):
    ######
    #Check whether pscheduler can be found on host
    #Return True if it can be, False if not

        subp = Popen("pscheduler ping %s"%(host), shell=True, stdout=PIPE, stderr=PIPE)
        pscheduler_ping_stdout, pscheduler_ping_stderr = subp.communicate()

        if (pscheduler_ping_stderr.find("Connection aborted: No route to host") != -1):
            return False

        elif (pscheduler_ping_stdout == "%s: pScheduler is alive\n"%(host)):
            return True

        else:
            return False


    def tasks_scheduled (self, host, duration="+PT1H"):
    ######
    # Returns number of tasks scheduled for a given host during the given duration
        pipe = Popen("pscheduler schedule --host %s %s"%(host, duration),
                                                         shell=True, stdout=PIPE, stderr=PIPE)

        schedule_stdout, schedule_stderr = pipe.communicate()

        if schedule_stderr:
            return -1
            # In the case of an error, since -1 is not a sensible value for number of tasks

        schedule_list = schedule_stdout.split("\n\n\n")

        # Check if nothing is scheduled
        if "Nothing scheduled" in schedule_stdout:
            return 0

        # There may be schedule entries for tasks that were scheduled to be performed in the
        # future, but were cancelled. This checks whether the schedule consists entirely of
        # cancelled tasks
        else:
            canceled_finished_tasks = 0
            for entry in schedule_list:
                entry_header = ((entry.split("\n"))[0]).strip()
                task_status = (entry_header.split(" "))[-1]
                if ((task_status == "(Canceled)") or (task_status == "(Finished)")
                                                  or (task_status == "(Non-Starter)")):
                    canceled_finished_tasks += 1

            return len(schedule_list) - canceled_finished_tasks



    def clear_schedule_single (self, host, duration="+PT24H"):
    ######
    # Clears scheduled tasks within the duration on the given host         
        pipe = Popen("pscheduler schedule --host %s %s"%(host, duration), shell=True, stdout=PIPE, stderr=PIPE)
        schedule_stdout, schedule_stderr = pipe.communicate()

        # Check if nothing is scheduled
        if "Nothing scheduled" in schedule_stdout:
            return True

        error_canceling_tasks = False

        schedule_list = schedule_stdout.split("\n\n\n")

        for entry in schedule_list:

            entry_header = ((entry.split("\n"))[0]).strip()
            task_status = (entry_header.split(" "))[-1]
            if ((task_status != "(Canceled)") and (task_status != "(Finished)")
                                              and (task_status != "(Non-Starter)")):

                run_URL = ((entry.split("\n"))[-1]).strip()
                task_url = run_URL.split("/runs/")[0] #A run URL is just an extension of a task URL. We want to remove the run part

                subp = Popen("ssh root@%s 'pscheduler cancel %s'"%(host, task_url), shell=True,
                             stdout=PIPE, stderr=PIPE) #Cancel Task
                cancel_task_stdout, cancel_task_stderr = subp.communicate()
                if cancel_task_stderr:
                    error_canceling_tasks = True

        if self.tasks_scheduled(host,duration) == 0:
          return True
        else:
          return False


    def clear_all_schedules (self, duration="+PT24H"):
    #####
    # Clear schedules on all hosts
        succesfully_cleared_hosts = []

        for host in self.hosts:
            clear_succesful = self.clear_schedule_single(host, duration=duration)
            if clear_succesful:
              succesfully_cleared_hosts.append(host)

        return succesfully_cleared_hosts



    def throughput_test(self, source, dest, duration="PT20S", reverse=False, lower_limit=900, upper_limit=1000):
    ######
    # Performs a throughput test from the given source to the given destination with the
    # given duration. Reverse option tests from destination to source (different logging
    # compared to swapping source and dest arguments)
        if reverse == True:
            direction = "Reverse"
        else:
            direction = "Forward"
   

        try:


          ######
          #Perform throughput test and capture output as JSON
          if reverse == False:
            pipe = Popen("pscheduler task --format=json throughput --duration {0} --interval PT5S --omit=5 \
                        --source {1} --dest {2}".format(duration, source, dest), shell=True, stdout=PIPE, stderr=PIPE)
          if reverse == True:
            pipe = Popen("pscheduler task --format=json throughput --duration {0} --interval PT5S --omit=5 \
                          --source {1} --dest {2}".format(duration, dest, source), shell=True, stdout=PIPE, stderr=PIPE)

          output, output_stderr = pipe.communicate() 

          if output_stderr:
            raise RuntimeError("Error during pscheduler task throughput")
          

          output = (output.split("\n"))[0]#Remove "No further runs scheduled" message (since we only want the JSON result)
          output_json = json.loads(output)


          ######
          #Store the output JSON in the results dictionary. One gives the overall summary portion of the JSON output,
          #while the other is the entire JSON, which is rather long
          self.results[source][dest][direction]["test summary"] = json.dumps(output_json["summary"]["summary"], indent = 3, separators = (',', ': '))

          ######
          #Get Average Throughput
          self.results[source][dest][direction]["throughput mean"] = output_json["summary"]["summary"]["throughput-bits"]

          ######
          #Get Minimum and Maximum Throughput
          self.results[source][dest][direction]["throughput min"] = -1 
          self.results[source][dest][direction]["throughput max"] = -1

          self.results[source][dest][direction]["seconds below min threshold"] = 0
          self.results[source][dest][direction]["seconds above max threshold"] = 0

          for interval in output_json["intervals"]:


              if interval["summary"]["omitted"] == False:
                  throughput_interval = interval["summary"]["throughput-bits"]

                  if throughput_interval > 100000000:
                      self.results[source][dest][direction]["seconds above max threshold"] += 1

                  if throughput_interval > self.results[source][dest][direction]["throughput max"]:
                      self.results[source][dest][direction]["throughput max"] = throughput_interval

                  if  throughput_interval < 90000000:
                      self.results[source][dest][direction]["seconds below min threshold"] += 1

                  if ((throughput_interval < self.results[source][dest][direction]["throughput min"])
                     or (self.results[source][dest][direction]["throughput min"] == -1)):
                   
                      self.results[source][dest][direction]["throughput min"] = throughput_interval

          ######
          #Write results of test to log
          if reverse == False:
            self.log.write("The average throughput from %s to %s was: %.1f Mbits/s. \n"%
                            (source, dest, self.results[source][dest][direction]["throughput mean"]/1000000) +
  
                           "The minimum throughput from %s to %s was: %.1f Mbits/s. \n"%
                            (source, dest, self.results[source][dest][direction]["throughput min"]/1000000) +  
  
                           "The maximum throughput from %s to %s was: %.1f Mbits/s. \n\n"%
                            (source, dest, self.results[source][dest][direction]["throughput max"]/1000000) )

          if reverse == True:
            self.log.write("The average throughput from %s to %s was: %.1f Mbits/s. \n"%
                            (dest, source, self.results[source][dest][direction]["throughput mean"]/1000000) +

                           "The minimum throughput from %s to %s was: %.1f Mbits/s. \n"%
                                (dest, source, self.results[source][dest][direction]["throughput min"]/1000000) +

                           "The maximum throughput from %s to %s was: %.1f Mbits/s. \n\n"%
                                (dest, source, self.results[source][dest][direction]["throughput max"]/1000000) )


          throughput_mean = self.results[source][dest][direction]["throughput mean"]/1000000

          if (self.results[source][dest][direction]["throughput min"]/1000000 > lower_limit
              and self.results[source][dest][direction]["throughput max"]/1000000 < upper_limit):

              self.log.write("The minimum throughput is above %.0f Mbits/sec and the maximum throughput is below %.0f Mbits/sec.\n\n"%(lower_limit, upper_limit))
              if reverse == False:
                self.log.write("The path from %s to %s meets the throughput requirements\n"%(source, dest))
                self.results["Summary"]["Passed Tests"].append((source,dest,direction,throughput_mean))
              if reverse == True:
                self.log.write("The path from %s to %s meets the throughput requirements\n"%(dest, source))
                self.results["Summary"]["Passed Tests"].append((source,dest,direction,throughput_mean))
                         
 
          else:
              if reverse == False:
                self.log.write("The path from %s to %s does not meet the throughput requirements\n"%(source, dest))
                self.results["Summary"]["Failed Tests"].append((source,dest,direction,throughput_mean))
              if reverse == True:
                self.log.write("The path from %s to %s does not meet the throughput requirements\n"%(source, dest))
                self.results["Summary"]["Failed Tests"].append((source,dest,direction,throughput_mean))


              if self.results[source][dest][direction]["throughput min"]/1000000 <= lower_limit:
                  self.log.write("The throughput was below %.0f Mbits/sec for %.0f 5-second-long intervals\n"%
                                 (lower_limit, self.results[source][dest][direction]["seconds below min threshold"]))

              if self.results[source][dest][direction]["throughput max"]/1000000 >= upper_limit:
                  self.log.write("The throughput was above %.0f Mbits/sec for %.0f 5-second-long intervals\n"%
                                 (upper_limit, self.results[source][dest][direction]["seconds above max threshold"])) 

          self.log.write("\nSummary from raw JSON output:\n{0}\n\n".format(self.results[source][dest][direction]["test summary"]))



        except Exception as e:

          test_result_logged = False 
          
          for tup in self.results["Summary"]["Failed Tests"]:
            if (tup[0] == source) and (tup[1] == dest) and (tup[2] == direction):
              test_result_logged = True
                 
          for tup in self.results["Summary"]["Passed Tests"]:
            if (tup[0] == source) and (tup[1] == dest) and (tup[2] == direction):
              test_result_logged = True

          for tup in self.results["Summary"]["Skipped Tests"]:
            if (tup[0] == source) and (tup[1] == dest) and (tup[2] == direction):
              test_result_logged = True

          if test_result_logged == False: 
              if reverse == False:
                  self.log.write("\nError during throughput test from {0} to {1}, aborting. This will count as a failed test\n\n".format(source, dest))

              elif reverse == True:
                  self.log.write("\nError during throughput test from {0} to {1}, aborting. This will count as a failed test\n\n".format(dest, source))
                 

              self.results["Summary"]["Failed Tests"].append((source,dest,direction))
  
          else:

              
              if reverse == False:
                  self.log.write("\nError during throughput test from {0} to {1}, but measurement results already logged. " +
                                 "Formatting of log may be affected\n\n".format(source, dest))
              if reverse == False:
                  self.log.write("\nError during throughput test from {0} to {1}, but measurement results already logged. " +
                                 "Formatting of log may be affected\n\n".format(source, dest))
          self.log.write("----------------------------------------------------------------------------------\n" +
                         "----------------------------------------------------------------------------------\n\n")




    def clear_central_mesh(self):
    ######
    # Clear central mesh so that hosts do not schedule new tasks
    # Note: use of this function should be followed by use of the
    # restart_meshconfig_daemons function, in order to stop the 
    # scheduling of tasks immediately
        open("/var/www/html/meshconfig/central_mesh.json", 'w').close()
        return



    def restart_pscheduler_daemons_single(self, host):
    ######
    # Restarts pscheduler daemons on a single host
    # pscheduler daemons are: runner, archiver, ticker, and scheduler
    # Returns true if daemons restarted succesfully, false if not  
        subp = Popen(("ssh root@%s 'systemctl restart pscheduler-runner pscheduler-archiver "%(host) +
                          "pscheduler-ticker pscheduler-scheduler'"), shell=True, stdout=PIPE, stderr=PIPE)

        daemon_restart_stdout, daemon_restart_stderr = subp.communicate()

        if daemon_restart_stderr: #if string is not empty. That is, if there was some message in stderr
            return False

        else:
            return True

    def restart_pscheduler_daemons(self):
    ######
    # Restarts pscheduler daemons on all hosts
    # pscheduler daemons are: runner, archiver, ticker, and scheduler
    # Returns list of hosts which succesfully restarted daemons   

        succesfully_restarted_hosts = []

        for host in self.hosts:
            single_restart_succesful = self.restart_pscheduler_daemons_single(host)
            if single_restart_succesful == True:
                succesfully_restarted_hosts.append(host)
            
        return succesfully_restarted_hosts

    def restart_meshconfig_daemons_single(self, host):
    ######
    # Restarts perfsonar-meshconfig-agent on given host, which causes host to update which central
    # meshes it uses to schedule tasks
    # Returns true if meshconfig agents succesfully restarted, false if not
        subp = Popen("ssh root@%s 'systemctl restart perfsonar-meshconfig-agent'"%(host),
                      shell=True, stdout=PIPE, stderr=PIPE)

        daemon_restart_stdout, daemon_restart_stderr = subp.communicate()

        if daemon_restart_stderr: #if string is not empty. That is, if there was some message in stderr
            return False
        else:
            return True
        

    def restart_meshconfig_daemons(self):
    ######
    # Restarts perfsonar-meshconfig-agent on each host, which causes each host to update which central
    # meshes they are using to schedule tasks
    # Returns true if meshconfig agents succesfully restarted, false if not

        succesfully_restarted_hosts = []

        for host in self.hosts:
            single_restart_succesful = self.restart_meshconfig_daemons_single(host)
            if single_restart_succesful == True:
                succesfully_restarted_hosts.append(host)

        return succesfully_restarted_hosts


    def create_and_publish_mesh(self, packet_padding='1450', packet_interval='0.1', 
                                mesh_path = '/var/www/html/meshconfig/central_mesh.json'):
    ######
    # Create a mesh JSON file specifying an OWAMP test between all hosts (bidirectional) with the
    # specified packet padding and time interval between sending packets, and publishes the file 
    # in the given location 

      #Convert arguments to strings, in case user did not do so
      packet_interval = str(packet_interval)
      packet_padding  = str(packet_padding)

      mesh_dict = {
                    "organizations" : [
                      {
                        "sites" : [
                          {
                            "hosts" : [
                              {
                                "addresses" : ["hubpsMA"],
                                "description" : "PSMA"
                              }  
                            ],
                            "measurement_archives" : [
                              {
                                "read_url" : "https://hubpsMA/esmond/perfsonar/archive/",
                                "write_url" : "https://hubpsMA/esmond/perfsonar/archive/",
                                "type" : "perfsonarbuoy/owamp"
                              },                      
                            ]
                          }
                        ],
                        "description" : "Hub Testing"
                      }
                    ],
  
                    "tests" : [
                      {
                        "members" : { 
                          "type" : "mesh",
                          "members" : []
                        },
                        "parameters" : {
                          "loss_threshold" : "60",
                          "bucket_width" : "0.0001",
                          "sample_count" : "6000",
                          "packet_interval" : packet_interval,
                          "force_bidirectional" : "1",
                          "packet_padding" : packet_padding,
                          "type" : "perfsonarbuoy/owamp",
                          "session_count" : "6000"
                        },
                        "description" : "OWAMP Testing"
                      }
                    ],
                    "description" : "HUB Testing Mesh"
                  }

      for host in self.hosts:
        for org in mesh_dict["organizations"]:
          for site in org["sites"]:
            site["hosts"].append(
                                  {
                                    "addresses" : [host],
                                    "description" : host[-4:].upper()
                                  }
                                )
   
        for test in mesh_dict["tests"]:
          test["members"]["members"].append(host)

      mesh_json_string = json.dumps(mesh_dict, indent = 3, separators = (',', ': '))
      central_mesh_file = open(mesh_path, 'w')
      central_mesh_file.write(mesh_json_string)

      return mesh_json_string


    def busy_hosts(self, duration = "+PT1H", log=False):
        #Check whether schedule is clear, optionally log which hosts are busy
        busy_schedule_host_list = []
        for host in self.hosts:
          if self.tasks_scheduled(host) > 0:
            busy_schedule_host_list.append(host)

        if (log == True) and (busy_schedule_host_list != []):

            self.log.write("The schedules on the following hosts are not clear: ")
            busy_hosts_string = ""
            for host in busy_schedule_host_list:
                busy_hosts_string += host
                busy_hosts_string += ','
            busy_hosts_string = busy_hosts_string[:-1] #Remove final comma
    
            self.log.write(busy_hosts_string)
            self.log.write("\n\n")

        elif (log == True) and (busy_schedule_host_list == []):
   
            self.log.write("The schedules on all hosts are clear\n") 


        return busy_schedule_host_list



def check_valid_iso_duration(duration):

     
    #No valid duration is less than four characters (shortest is "PT1H")
    if len(duration) < 2:
        return False

    #Check for valid beginning "P", "+P", or "-P"
    if (duration[0] != 'P') and (duration[1] != 'P'):
        return False

    elif (duration[1] == 'P') and (duration[0] not in "+-"):
        return False

    iso_designators = "PYWDTHMS"
    designators_used = ""        
    time_designators = "YWDHMS"

    beginning = duration.find('P')
    
    for i in range(0,len(iso_designators)):
        designator = iso_designators[i]

        #Designators should not occur more than once
        if duration.count(designator) > 1:
            return False

        if designator in duration:
            designators_used += (designator)

            if len(designators_used) > 1:
              prev_desig = designators_used[designators_used.find(designator)-1]

              #Check that order of designators is respected
              if iso_designators.find(designator) <= iso_designators.find(prev_desig):
                  return False
              if designator in "HMS":
                  if ('T' not in designators_used) or (designators_used.find(designator) 
                                                        <= designators_used.find(prev_desig)):
                      return False 
              #Check that time designators are seperated by integer values
              if designator != 'P' and designator != 'T':
                  amount = duration[duration.find(prev_desig)+1:duration.find(designator)]
                  if not amount.isdigit():
                      return False
              #The exception is T, which should be preceeded by one of PYWD
              elif designator == 'T':
                  if duration[duration.find('T')-1] not in "PYWD":
                      return False
                  if len(duration) <= duration.find('T')+1:
                      return False
                  if not duration[duration.find('T')+1].isdigit():
                      return False

    #Finally, check that the final character is an iso designator (i.e, not PT15H3)
    if duration[-1] not in iso_designators:
        return False

    return True     

                
    


class Log:

    def __init__(self, log_name):

        self.log_name = log_name
        self.write_buffer = ""

    def write(self, entry):

        self.write_buffer += entry


    def clear_write_buffer(self):

        self.write_buffer = ""        


    def flush(self, print_log=True):

        if self.write_buffer == "":
            return

        time_str = time.asctime()
        write_buffer_split = self.write_buffer.split("\n")
        write_str = ""
        i = 0
        while i < len(write_buffer_split):

            if i == 0:
                write_str += "[" + time_str + "] "
            elif (i == len(write_buffer_split) - 1) and write_buffer_split[i] == "":
                i += 1
                continue
            else:
                write_str += " "*(len(time_str) + 3)


            write_str += write_buffer_split[i] + "\n"
            i += 1

        if self.log_name:
            log = open(self.log_name, "a+")
            log.write(write_str)
            log.close()

        if print_log == True:
            print(write_str)

        self.clear_write_buffer()

    def flush_no_timestamp(self, print_log=True):

        if self.write_buffer == "":
            return

        if self.log_name:
            log = open(self.log_name, "a+")
            log.write(self.write_buffer)
            log.close()

        if print_log == True:
            print(self.write_buffer)

        self.clear_write_buffer()




