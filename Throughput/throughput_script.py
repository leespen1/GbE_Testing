#
# Last edited: 10:33 AM, 16 May, 2019
#


import sys
from subprocess import PIPE, Popen, call
import tempfile
import json
import time
import throughput_classes as master

def Show_Usage():
#----------
  print """
Usage: python throughput_script.py        -h|--help
                                          -c|--config_filename
	                    				  -o|--output_directory
                                          -d|--duration
                                          -l|--lower_limit
                                          -u|--upper_limit
                                          -s|--schedule_clear
                                          -r|--restart_pscheduler_daemons 

Options:

 -h, --help                               Display this message and exit
 -c FILENAME, --config_file FILENAME      Name of configuration file to read 
 -o FILENAME, --output_filename FILENAME  Directory to output results to
 -d DURATION, --duration DURATION         Length of throughput measurements
 -l LIMIT, --lower_limit LIMIT            Lower limit of throughput, in Mbits/sec
 -u LIMIT, --upper_limit LIMIT            Upper limit of throughput, in Mbits/sec
 -s, --schedule_clear                     Clear schedules on all hosts before each test 
 -r, --restart_pscheduler_daemons         Restart pscheduler runner, archiver, ticker, and scheduler daemons on each host
 --schedule_duration DURATION             Length of time to check when checking schedules on hosts
 --check_routes                           Check whether each host can be reached and pscheduler can be found
    """
  
  sys.exit()


######
#Initialize dictionary of test results
total_results = {"Total Tests": [], "Passed Tests": [], "Failed Tests": [],
                 "Skipped Tests": [], "Busy Tests": []}

######
#Test Listing | Format is list -> tuple (pair) -> list (one for sources, one for dests)
test_listing = [(["hubps03"],["hubps04","hubps05"])]

######
#The duration of each throughput test in ISO 8601 format (String)
default_duration = "PT30S"
duration = default_duration
######
#How long to look ahead when checking if schedule is clear in ISO 8601 format (String)
schedule_duration = ""
######
#Path of configuration file ("String")
config_filename = ""

######
#Path of output log file (String)
output_filename = ""

######
#Enable/Disable the clearing of schedules on all hosts before test (Boolean)
clear_schedules = False

######
#Enable/Disable the restarting of the pscheduler runner, ticker, scheduler, and archiver daemons on each host (Boolean)
restart_pscheduler_daemons = False

######
#Enable/Disable the checking of whether each host can be reached and has pscheduler
#Removes host from testing if it cannot be reached (Boolean)
check_routes = False

######
#Minimum Bandwidth Requirement in Mbits/sec (Float)
lower_limit = 925
######
#Maximum Bandwidth Requirement in Mbits/sec (Float)
upper_limit = 1000

######
#Serial number of Hub (String)
serial_no = ""


# Get command line options
cmd_line_arg = sys.argv[1:]

if ( len (cmd_line_arg) >= 1 ) :

  # build explicit do loop (instead of "for i in range...") to allow "i=i+1"
  i = 0

  #Configuration File; Loop over to set parameters based on config file,
  #Then do another loop to override with command line arguments
  while ( i < len(cmd_line_arg)):

    if ((cmd_line_arg[i] == "-c")
         or (cmd_line_arg[i] == "--config_file")):

      try:
        i += 1
        config_filename = cmd_line_arg[i]
        i += 1
        continue

      except:
        print(" ** Argument for config_file not given; Using defaults ** ")
        config_filename = ""
        i += 1
        continue

    else:
      i += 1


  if config_filename != "":
    try:
      execfile (config_filename)
    except:
      print ("** Failure executing <%s> **"%(config_filename))
      Show_Usage()

  #Intermediate Check for Duration Formats
  if ((duration != default_duration) and 
      (master.check_valid_iso_duration(duration) == False)):
      
    print(" ** Measurement duration not valid iso 8601; using default of %s ** "
                %default_duration)   
    duration = default_duration

  if ((schedule_duration != duration) or
      (master.check_valid_iso_duration(schedule_duration) == False)):

    print(" ** Schedule check duration not valid iso 8601;" + 
          " matching measurement duration as default ** ")
    schedule_duration = ""



  i = 0
  #Loop for all other parameters
  while ( i < len(cmd_line_arg) ) :


    #Help
    if ((cmd_line_arg[i] == "-h" )
         or (cmd_line_arg[i] == "--help")):

      Show_Usage()
      sys.exit()

    #Configuration File
    elif ((cmd_line_arg[i] == "-c")
           or (cmd_line_arg[i] == "--config_file")):

      try:
        i += 1
        config_filename = cmd_line_arg[i]
        i += 1
        continue

      except:
        print(" ** Argument for config_file not given; Using defaults ** ")
        config_filename = ""
        i += 1
        continue


    #Schedule Clear
    elif ((cmd_line_arg[i] == "-s" )
           or (cmd_line_arg[i] == "--schedule_clear")):

      clear_schedules = True
      i += 1
      continue

    #Check Routes    
    elif (cmd_line_arg[i] == "--check_routes"):

      check_routes = True
      i += 1
      continue

    #Restart Pscheduler Daemons
    elif ((cmd_line_arg[i] == "-r")
           or (cmd_line_arg[i] == "--restart_pscheduler_daemons")):

      restart_pscheduler_daemons = True
      i += 1
      continue

    #Test Duration
    elif ((cmd_line_arg[i] == "-d")
           or (cmd_line_arg[i] == "--duration")):

      try:
        i += 1
        if master.check_valid_iso_duration(cmd_line_arg[i]) == True:
          duration = cmd_line_arg[i]
        else:
          print(" ** Measurement duration not valid iso 8601; keeping duration of %s ** "
                %duration)   
        i += 1
        continue      

      except:
        print(" ** Argument for measurement duration not given; keeping duration of %s ** "
              %duration)
        i += 1
        continue
    
    #Schedule Check Duration
    elif (cmd_line_arg[i] == "--schedule_duration"):

      try:
        i += 1
        schedule_duration = cmd_line_arg[i]
        if master.check_valid_iso_duration(cmd_line_arg[i]) == True:
          schedule_duration = cmd_line_arg[i]
        else:
          print(" ** Schedule check duration not valid iso 8601;" +
                " matching measurement duration as default ** ")
          schedule_duration = ""
        i += 1
        continue

      except:
        print(" ** Argument for schedule duration not given; matching test duration as default ** ")
        schedule_duration = ""
        i += 1
        continue

    #Output Filename
    elif ((cmd_line_arg[i] == "-o")
           or (cmd_line_arg[i] == "--output_filename")):

      try:
        i += 1
        output_filename = cmd_line_arg[i]
        i += 1
        continue

      except:
        print(" ** Argument for output_filename not given; Prompting user for log name ** ")
        i += 1
        continue

    #Lower Limit of Throughput
    elif ((cmd_line_arg[i] == "-l")
           or (cmd_line_arg[i] == "--lower_limit")):

      try:
        i += 1
        lower_limit = float(cmd_line_arg[i])
        i += 1
        continue

      except:
        print(" ** Argument for lower limit of throughput not given; using 900 Mbits/sec as default ** ")
        lower_limit = 900
        i += 1
        continue

    #Upper Limit of Throughput
    elif ((cmd_line_arg[i] == "-u")
           or (cmd_line_arg[i] == "--upper_limit")):

      try:
        i += 1
        upper_limit = float(cmd_line_arg[i])
        i += 1
        continue    

      except:
        print(" ** Argument for upper limit of throughput not given; using 1000 Mbits/sec as default ** ")
        upper_limit = 1000
        i += 1
        continue


    #Illegal Argument
    else:
        print(" ** Illegal argument '%s' **"%(cmd_line_arg[i]))
        i += 1
        continue



if schedule_duration == "":
    schedule_duration = duration 



#############
#Get log path (if not already given) and hub serial no
month_day_year = time.strftime("%b %d, %Y", time.localtime())
mdy_filename = time.strftime("%b_%d_%Y", time.localtime())

if output_filename == "":

    log_name = raw_input("Please input name of output log: ")
    if serial_no == "":
      serial_no = raw_input("Please input serial no. of Hub: ")

    log_path = "Results/%s.txt" %(log_name)

else:

    if '.' not in output_filename:
        log_path = "Results/%s.txt" %(output_filename)

    else:
        log_path = "Results/%s" %(output_filename)

    if serial_no == "":
      serial_no = raw_input("Please input serial no. of Hub: ")


#Use this for creating a pscheduler object using all hosts, in order to
#perform setup actions across all hosts
all_sources = []
all_dests = []
for pair in test_listing:
  for source in pair[0]:
    if source not in all_sources:
      all_sources.append(source)
  for dest in pair[1]:
    if dest not in all_dests:
      all_dests.append(dest)


pscheduler_obj = master.pScheduler_Testing_throughput(log_path, all_sources, all_dests)




log_header = ("##################################################################################\n" +
              "#                 Throughput Test for %-12s                               #\n"%(month_day_year) +
              "#                 Serial No. %-12s                                        #\n"%(serial_no) + 
              "##################################################################################\n\n")

parameter_listing_string  = "Running throughput test with the following parameters:\n"
parameter_listing_string += "  Log Path: %s\n"%(log_path)
parameter_listing_string += "  Throughput Measurement Duration: %s\n"%(duration)
parameter_listing_string += "  Minimum Bandwidth Requirement: %s Mbits/sec\n"%(lower_limit)
parameter_listing_string += "  Maximum Bandwidth Requirement: %s Mbits/sec\n"%(upper_limit)
parameter_listing_string += "  Clear schedules before each measurement: %s\n"%(clear_schedules)
parameter_listing_string += "  Restart pscheduler runner, scheduler, archiver, and ticker daemons at start of test: %s\n"%(restart_pscheduler_daemons)

parameter_listing_string += "  Test Listing:\n"
for tup in test_listing:
  parameter_listing_string += "    %s\n"%(tup,)

pscheduler_obj.log.write(log_header)
pscheduler_obj.log.write(parameter_listing_string)
pscheduler_obj.log.flush_no_timestamp()



if check_routes == True:

  try:
    pscheduler_obj.log.write("%-50s\n"%("Checking host routes") )
    bad_hosts_list = pscheduler_obj.check_routes(update_hosts=True)
    if bad_hosts_list == []:
      pscheduler_obj.log.write("All hosts can be reached and have pscheduler.\n\n")
    else:
      pscheduler_obj.log.write("Pscheduler could not be found on the following hosts, removing from test: \n")
      for host in bad_hosts_list:
        pscheduler_obj.log.write("  %s\n"%(host))
      pscheduler_obj.log.write("\n")

  except Exception as e:
    pscheduler_obj.log.write("Exception while checking host routes.\n\n")

# Clear current central mesh
try:
    pscheduler_obj.log.write("%-50s\n"%("Clearing central mesh") )
    pscheduler_obj.clear_central_mesh()
    pscheduler_obj.log.write("Mesh succesfully cleared.\n\n")
except Exception as e:
    pscheduler_obj.log.write("Exception while clearing central mesh.\n\n")


# Restart pscheduler runner, archiver, scheduler, and ticker daemons on all hosts 
if restart_pscheduler_daemons == True:

  try:
    pscheduler_obj.log.write("%-50s\n"%("Restarting pscheduler daemons") )
    succesfully_restarted_hosts = pscheduler_obj.restart_pscheduler_daemons()

    if len(succesfully_restarted_hosts) == len(pscheduler_obj.hosts):
      pscheduler_obj.log.write("Pscheduler runner, archiver, scheduler, and ticker daemons successfully restarted on all hosts.\n\n")

    else:
      pscheduler_obj.log.write("Pscheduler daemon restart unsuccessful on following hosts: \n")
      for host in pscheduler_obj.hosts:
        if host not in succesfully_restarted_hosts:
          pscheduler_obj.log.write("  %s\n"%(host))
      pscheduler_obj.log.write("\n")

  except Exception as e:
    pscheduler_obj.log.write("Exception while restarting pscheduler daemons.\n\n")



#These should be written as a function in the object

######
#Write inactive gui agent configuration so we can write template to maddash.yaml without it being overwritten by the guiagent
gui_agent_inactive_str = open('Config/meshconfig-guiagent-inactive.conf', 'r').read()
meshconfig_guiagent = open('/etc/perfsonar/meshconfig-guiagent.conf', 'w')
meshconfig_guiagent.write(gui_agent_inactive_str)
meshconfig_guiagent.close()

######
#Clear maddash.yaml so that no checks are run (which should not be that important regardless, since they are reading from the 
#measurement archive on this machine. So they should only take up CPU, and not affect the switch)
open("/etc/maddash/maddash-server/maddash.yaml", 'w').close()

# Restart mesh configuration daemon on all hosts so that they do not schedule new tasks based on the old mesh
try:
  pscheduler_obj.log.write("%-50s\n"%("Restarting mesh configuration daemons") )
  succesfully_restarted_hosts = pscheduler_obj.restart_meshconfig_daemons()

  if len(succesfully_restarted_hosts) == len(pscheduler_obj.hosts):
    pscheduler_obj.log.write("Mesh Configuration daemons successfully restarted on all hosts.\n\n")

  else:
    pscheduler_obj.log.write("Mesh configuration daemon restart unsuccessful on following hosts: \n")
    for host in pscheduler_obj.hosts:
      if host not in succesfully_restarted_hosts:
        pscheduler_obj.log.write("  %s\n"%(host))
    pscheduler_obj.log.write("\n")

except Exception as e:
  pscheduler_obj.log.write("Exception while restarting mesh configuration daemons.\n\n")



# Clear schedules on all hosts so that no tests remain from the old mesh
if clear_schedules == True:
  try:
    pscheduler_obj.log.write("%-50s\n"%("Clearing schedules") )
    succesfully_cleared_hosts = pscheduler_obj.clear_all_schedules()
    if len(succesfully_cleared_hosts) == len(pscheduler_obj.hosts):
      pscheduler_obj.log.write("All schedules succesfully cleared.\n\n")
    else:
      pscheduler_obj.log.write("Not all schedules succesfully cleared.\n" +
                               "Hosts with unsuccesfully cleared schedules: \n")
      for host in pscheduler_obj.hosts:
        if host not in succesfully_restarted_hosts:
          pscheduler_obj.log.write("  %s\n"%host)
      pscheduler_obj.log.write("\n")

  except Exception as e:
    pscheduler_obj.log.write("Exception while clearing schedules.\n\n")





for source_dest_pair in test_listing:

  pscheduler_obj = master.pScheduler_Testing_throughput(log_path, source_dest_pair[0], source_dest_pair[1])


  if check_routes == True:

    try:
      pscheduler_obj.log.write("%-50s\n"%("Checking host routes") )
      bad_hosts_list = pscheduler_obj.check_routes(update_hosts=True)
      if bad_hosts_list == []:
        pscheduler_obj.log.write("All hosts can be reached and have pscheduler.\n\n")
      else:
        pscheduler_obj.log.write("Pscheduler could not be found on the following hosts, removing from test: \n" )
        for host in bad_hosts_list:
          pscheduler_obj.log.write("  %s\n"%(host))
        pscheduler_obj.log.write("\n")

    except Exception as e:
      pscheduler_obj.log.write("Exception while checking host routes.\n\n")


  ######
  #Do a throughput test for each source/destination combination and store the results in results_dict
  for dest in pscheduler_obj.dests:


    test_header = ("==================================================================================\n" +
                   " Test Results for node {0}\n".format(dest) +
                   "==================================================================================\n")

    pscheduler_obj.log.write(test_header)
    pscheduler_obj.log.flush_no_timestamp()
    

    for source in pscheduler_obj.sources:

        if source == dest:
            continue

        try:
          pscheduler_obj.log.flush_no_timestamp()
          pscheduler_obj.log.write("Performing test between %s and %s\n"%(source,dest))
          pscheduler_obj.log.flush()


          pscheduler_obj.log.write("Test Results for connection from {0} to {1}: \n".format(source, dest))

          pscheduler_obj.results["Summary"]["Total Tests"].append((source,dest,"Forward"))

        except:
          pscheduler_obj.log.write("Exception during logging. Some results may be missing from report.\n")

        pscheduler_obj.log.flush_no_timestamp()

        try:

          pscheduler_obj.log.flush_no_timestamp()
          pscheduler_obj.log.write("Checking Schedules\n")
          pscheduler_obj.log.flush()

          busy_hosts = pscheduler_obj.busy_hosts()
          if (busy_hosts != []) and (clear_schedules == True):

            for host in busy_hosts:
              pscheduler_obj.clear_schedule(host)

          busy_hosts = pscheduler_obj.busy_hosts(log=True)
          if busy_hosts != []:
            pscheduler_obj.results["Summary"]["Busy Tests"].append((source,dest,"Forward"))

          pscheduler_obj.log.flush_no_timestamp()
          pscheduler_obj.log.write("Running Forward Test\n")
          pscheduler_obj.log.flush()

        except:
            pscheduler_obj.log.write("  Exception while checking schedules, counting following test as busy.\n")
            if (source,dest) not in pscheduler_obj.results["Summary"]["Busy Tests"]:
              pscheduler_obj.results["Summary"]["Busy Tests"].append((source,dest,"Forward"))

        pscheduler_obj.log.flush_no_timestamp()

        pscheduler_obj.throughput_test(source, dest, duration=duration, reverse=False, lower_limit=lower_limit, upper_limit=upper_limit)

        pscheduler_obj.log.write("----------------------------------------------------------------------------------\n")

        try:
          pscheduler_obj.log.write("Test Results for connection from {0} to {1}: \n".format(dest, source))
          pscheduler_obj.results["Summary"]["Total Tests"].append((source,dest,"Reverse"))

        except:
          pscheduler_obj.log.write("Exception during logging. Some results may be missing from report.\n")


        pscheduler_obj.log.flush_no_timestamp()

        try:

          pscheduler_obj.log.flush_no_timestamp()
          pscheduler_obj.log.write("Checking Schedules\n")
          pscheduler_obj.log.flush()

          busy_hosts = pscheduler_obj.busy_hosts()
          if (busy_hosts != []) and (clear_schedules == True):

            for host in busy_hosts:
              pscheduler_obj.clear_schedule(host)

          busy_hosts = pscheduler_obj.busy_hosts(log=True)
          if busy_hosts != []:
            pscheduler_obj.results["Summary"]["Busy Tests"].append((source,dest,"Reverse"))

          pscheduler_obj.log.flush_no_timestamp()
          pscheduler_obj.log.write("Running Reverse Test\n")
          pscheduler_obj.log.flush()
        
        except:
            pscheduler_obj.log.write("  Exception while checking schedules, counting following test as busy.\n")
            if (source,dest) not in pscheduler_obj.results["Summary"]["Busy Tests"]:
              pscheduler_obj.results["Summary"]["Busy Tests"].append((source,dest,"Reverse"))

        pscheduler_obj.log.flush_no_timestamp()

        pscheduler_obj.throughput_test(source, dest, duration=duration, reverse=True, lower_limit=lower_limit, upper_limit=upper_limit)


  #Add results from this grouping to the dictionary of all results
  #Tuples have format (source,dest,direction,/throughput_mean/), where throughput_mean is optional
  for tup in pscheduler_obj.results["Summary"]["Total Tests"]:
    total_results["Total Tests"].append(tup) 
  for tup in pscheduler_obj.results["Summary"]["Passed Tests"]:
    total_results["Passed Tests"].append(tup)
  for tup in pscheduler_obj.results["Summary"]["Failed Tests"]:
    total_results["Failed Tests"].append(tup) 
  for tup in pscheduler_obj.results["Summary"]["Skipped Tests"]:
    total_results["Skipped Tests"].append(tup) 
  for tup in pscheduler_obj.results["Summary"]["Busy Tests"]:
    total_results["Busy Tests"].append(tup) 

######
#Final Report


pscheduler_obj.log.write("\n==================================================================================\n" +
                           "Final Report \n" +
                           "==================================================================================\n\n")

pscheduler_obj.log.write("Testing for throughput above %.1f Mbits/sec and below %.1f Mbits/sec\n"%(lower_limit, upper_limit) +
                         "Duration for each test: %s\n\n"%(duration) )



if len(total_results["Busy Tests"]) != 0:
    pscheduler_obj.log.write("Warning: {0} tests ran without clear schedules. This may impact results.\n".format(
                             len(total_results["Busy Tests"])) )

pscheduler_obj.log.write("Total Number of Tests: {0}\n".format(len(total_results["Total Tests"])) )
pscheduler_obj.log.write("Number of Passed Tests: {0}\n".format(len(total_results["Passed Tests"])) )
pscheduler_obj.log.write("Number of Skipped Tests: {0}\n".format(len(total_results["Skipped Tests"])) )
pscheduler_obj.log.write("Number of Failed Tests: {0}\n\n".format(len(total_results["Failed Tests"])) )

if len(total_results["Passed Tests"]) == len(total_results["Total Tests"]):
    pscheduler_obj.log.write("\nAll tests passed.\n\n" )


pscheduler_obj.log.write("|-----------------------------------------------------------------|\n" +
                         "|        Link        | Status  | Mean Throughput | Clear Schedule | \n" +
                         "|--------------------+---------+-----------------+----------------|\n" )

for tup in total_results["Total Tests"]:
  
    if tup[2] == "Forward":
      link = "%7s to %7s"%(tup[0], tup[1])
    elif tup[2] == "Reverse":
      link = "%7s to %7s"%(tup[1], tup[0])
      

    status = "NA"
    mean_throughput = "NA"

    for tup_2 in total_results["Passed Tests"]:
      if tup == tup_2[:3]:
        status = "Passed"
        if len(tup_2) > 3:
          mean_throughput = "%3.1f Mbits/sec"%(tup_2[3])
    

    if status == "NA":
 
      for tup_2 in total_results["Failed Tests"]:
        if tup == tup_2[:3]:
          status = "Failed"
          if len(tup_2) > 3:
            mean_throughput = "%3.1f Mbits/sec"%(tup_2[3])

 
    if tup in total_results["Skipped Tests"]:
      status = "Skipped"


    clear_schedule = "Yes"
    
    if tup in total_results["Busy Tests"]:
      clear_schedule = "No"

    pscheduler_obj.log.write("|{:^20s}|{:^9s}|{:^17s}|{:^16s}|\n".format(link,status,mean_throughput,clear_schedule) + 
                             "|--------------------+---------+-----------------+----------------|\n" )

pscheduler_obj.log.write("\n\n\n")

pscheduler_obj.log.flush_no_timestamp()



