from subprocess import PIPE, Popen, call
import tempfile
import time
import datetime
from UtilException import show_exc_info
import sys

version = "V1.0"

def Show_Usage():
#----------
  print """
Usage: python ping_test_v0p5.py           -h|--help
					                      -o|--output_path
                                          --config_file
                                          --count
                                          --concurrency

Options:

 -h, --help                               Display this message and exit
 -o FILENAME, --output_filename FILENAME  Name of file to output results to
 --config_file FILENAME                   Name of configuration file to read 
 --count COUNT                            Number of ping packets to send
 --concurrency CONCURRENCY                Number of packets to have in-flight at once
    """

##############################################################################
# configure test parameters

private_nic="enp1s0"
#private_nic="eth0"

ping_count = 10
ping_concurrency = 4
ping_timeout = 10800

ping_packet_sizes = [
#              32,
#              64,
#              128,
#              256,
#              512,
#              768,
#              1024,
#              1280,
              1472,
            ]

target_list = [
             "hubps03",
             "hubps04",
             "hubps05",
             #"hubps06",
             #"hubps07",
             #"hubps08",
             #"hubps09",
             #"hubps10",
             #"hubps11",
             #"hubps12",
             #"hubps13",
             #"hubps14",
             #"hubps15",
             #"hubps16",
             #"hubps18",
             #"hub1FPGA",
             #"hub2FPGA",
            ]

output_filename = ""


##############################################################################
# Target IP address dictionary

target_ip_dict = { 
    "hubps03": "10.0.0.103", "hubps04": "10.0.0.104", "hubps05": "10.0.0.105",
    "hubps06": "10.0.0.106", "hubps07": "10.0.0.107", "hubps08": "10.0.0.108",
    "hubps09": "10.0.0.109", "hubps10": "10.0.0.110", "hubps11": "10.0.0.111",
    "hubps12": "10.0.0.112", "hubps13": "10.0.0.113", "hubps14": "10.0.0.114",
    "hubps15": "10.0.0.115", "hubps16": "10.0.0.116", "hubps17": "10.0.0.117",
    "hubps17": "10.0.0.117", "hubps18": "10.0.0.118",

    "hub02": "10.11.30.49", "hub03": "10.11.30.50", "hub04": "10.11.30.51",
    "hub05": "10.11.30.52", "hub06": "10.11.30.53", "hub07": "10.11.30.54",
    "hub08": "10.11.30.48", "hub09": "10.11.30.55", "hub10": "10.11.30.60",
    "hub11": "10.11.30.61", "hub12": "10.11.30.75", "hub13": "10.11.30.76",
    "hub14": "10.11.30.74", "hub15": "10.11.30.73", "hub16": "10.11.30.72",
    "hub17": "10.11.30.71", "hub18": "10.11.30.70", "hub19": "10.11.30.69",
    "hub20": "10.11.30.68", "hub21": "10.11.30.67", "hub22": "10.11.30.66",
    "hub23": "10.11.30.65", "hub24": "10.11.30.64", "hub25": "10.11.30.63",
    "hub26": "10.11.30.62", "hub27": "10.11.30.59", "hub28": "10.11.30.58",
    "hub29": "10.11.30.57", "hub30": "10.11.30.56",

    "hub1FPGA": "10.11.30.18", "hub2FPGA": "10.11.30.21",

    "htm03" : "10.0.0.67", "htm04" : "10.0.0.68", "htm05" : "10.0.0.69",
    "htm06" : "10.0.0.70", "htm07" : "10.0.0.71", "htm08" : "10.0.0.72",
    "htm09" : "10.0.0.73", "htm10" : "10.0.0.74", "htm11" : "10.0.0.75",
    "htm12" : "10.0.0.76", "htm13" : "10.0.0.77", "htm14" : "10.0.0.78",

    "rod1" : "10.11.30.109", "rod2" : "10.11.30.20",
}



# Default Parameters
hub1_SN = "NA"
hub2_SN = "NA"

cmd_line_arg = sys.argv[1:]

if ( len (cmd_line_arg) >= 1 ) :

  # build explicit do loop (instead of "for i in range...") to allow "i=i+1"
  i = 0


  #Configuration File; Loop over to set parameters based on config file,
  #Then do another loop to override with command line arguments
  while ( i < len(cmd_line_arg)):

    #Help
    if ((cmd_line_arg[i] == "-h" )
         or (cmd_line_arg[i] == "--help")):

      Show_Usage()
      sys.exit()


    if (cmd_line_arg[i] == "--config_file"):

      try:
        i += 1
        config_filename = cmd_line_arg[i]

        try:
          execfile (config_filename)
        except:
          print("** Failure executing <%s> **"%(config_filename))
          Show_Usage()

        i += 1
        continue

      except:
        print(" ** Argument for config_file not given ** ")
        sys.exit()

    else:
      i += 1


  i = 0

  #Loop for all other parameters
  while ( i < len(cmd_line_arg) ) :


    #Input File
    if (cmd_line_arg[i] == "--count" ):

      try:
        i += 1
        ping_count = int(cmd_line_arg[i])
        i += 1
        continue

      except:
        print(" ** Illegal Arguement for Packet Count Given ")
        sys.exit()


    elif (cmd_line_arg[i] == "--concurrency" ):

      try:
        i += 1
        ping_concurrency = int(cmd_line_arg[i])
        i += 1
        continue

      except:
        print(" ** Illegal Arguement for Packet Count Given ")
        sys.exit()


    #Output Filename
    elif ((cmd_line_arg[i] == "-o" )
        or (cmd_line_arg[i] == "--output_filename")):

      try:
        i += 1
        output_filename = cmd_line_arg[i]
        i += 1
        continue

      except:
        print(" ** Argument for output_filename  not given; Only printing results")

    #Configuration File
    elif (cmd_line_arg[i] == "--config_file"):

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

    #Hub1 Serial No
    if (cmd_line_arg[i] == "--hub1SN" ):

      try:
        i += 1
        hub1_SN = int(cmd_line_arg[i])
        i += 1
        continue

    #Hub2 Serial No
    if (cmd_line_arg[i] == "--hub2SN" ):

      try:
        i += 1
        hub2_SN = int(cmd_line_arg[i])
        i += 1
        continue

    #Illegal Argument
    else:
        print(" ** Illegal argument '%s' **"%(cmd_line_arg[i]))
        i += 1
        continue




##############################################################################
# report scope of this test

print("\n FPGA IPbus Ping Test version %s \n" % version)
print(" Testing Ping to Node(s) ")
print(target_list)
print(" Ping packet count per test = %6.1E" % ping_count)
print(" Ping packet concurrency     = %d"    % ping_concurrency)
print(" Ping packet size(s)")
print(ping_packet_sizes)


if output_filename == "":
  output_filename = raw_input("Input report name: ")
ping_report = open('Results/{0}'.format(output_filename), 'a+')

ping_report.write(" Ping Test version %s \n\n" % version)
ping_report.write(" Testing Ping to Target(s) \n")
for target in target_list:
  ping_report.write ( "  %s \n" % target)
ping_report.write(" Ping packet count per test = %6.1E \n" % ping_count)
ping_report.write(" Ping packet concurrency     = %d \n"    % ping_concurrency)
ping_report.write(" Ping packet size(s) \n")
for packet_size in ping_packet_sizes :
  ping_report.write ( "  %4d \n" % packet_size )

ping_report.flush()

##############################################################################
# start test

results_dict = {}
for packet_size in ping_packet_sizes:
    results_dict[packet_size] = {}
    for target in target_list:
        results_dict[packet_size][target] = {}

for target in target_list:

  try:

    if target not in ("hub1FPGA", "hub2FPGA"):
        target_ip = target_ip_dict[target]
    elif target == "hub1FPGA":
        try:
            target_ip = target_ip_dict["hub%s"%(hub1_SN.zfill(2))]
        except ValueError:
            target__ip = target_ip_dict[target]
    elif target == "hub2FPGA":
        try:
            target_ip = target_ip_dict["hub%s"%(hub2_SN.zfill(2))]
        except ValueError:
            target__ip = target_ip_dict[target]

    #For log purposes
    ping_report.write("\n\n-------------------------------------------------\n\nResults for {0}\n\n".format(target))

    for packet_size in ping_packet_sizes :

      before_time = datetime.datetime.now()

      #Get initial ethtool report
      pipe = Popen("ethtool -S %s" % private_nic, shell=True, stdout=PIPE, stderr=PIPE)
      ethtool_before_stdout, ethtool_before_stderr = pipe.communicate()
      ethtool_before_lines = (ethtool_before_stdout.strip()).split('\n')

      print("Now pinging %s with %4d byte packets at %s "%(target, packet_size, str(before_time)[:16]))

      # Run ping test
      print("sudo ping -A -q -w %d -c %d -s %d -l %d %s"%(ping_timeout, ping_count, packet_size, ping_concurrency, target_ip_dict[target]))
      
      pipe = Popen("sudo ping -A -q -w %d -c %d -s %d -l %d %s"%(ping_timeout, ping_count, packet_size, ping_concurrency, target_ip_dict[target]), shell=True, stdout=PIPE, stderr=PIPE)
      ping_stdout, ping_stderr = pipe.communicate()

      time.sleep(5) #Added a 5 second delay. Otherwise I wasn't getting any change between ethtool reports

      # Parse results
      ping_stdout_lines = ping_stdout.split("\n")
      ping_statistics_1 = ping_stdout_lines[3].split(" ")
      packets_transmitted = int(ping_statistics_1[0])
      packets_received = int(ping_statistics_1[3])
      packets_dropped = packets_transmitted - packets_received
      # time_taken will be in minutes
      time_taken = str(int(ping_statistics_1[9][:-2])/60000) + " m"

      ping_statistics_2 = ping_stdout_lines[4].split(" ")
      rtt_info = ping_statistics_2[3]

      results_dict[packet_size][target]["tx"] = packets_transmitted
      results_dict[packet_size][target]["rx"] = packets_received
      results_dict[packet_size][target]["dropped"] = packets_dropped
      results_dict[packet_size][target]["time"] = time_taken
      results_dict[packet_size][target]["rtt"] = rtt_info + " ms"

      """
      # Example ping_stdout
      PING 10.0.0.103 (10.0.0.103) 1472(1500) bytes of data.
      
      --- 10.0.0.103 ping statistics ---
      10 packets transmitted, 10 received, 0% packet loss, time 0ms
      rtt min/avg/max/mdev = 0.295/0.342/0.385/0.034 ms, pipe 4, ipg/ewma 0.103/0.345 ms
      """

      #Get final ethtool report
      pipe = Popen("ethtool -S %s" % private_nic, shell=True, stdout=PIPE, stderr=PIPE)
      ethtool_after_stdout, ethtool_after_stderr = pipe.communicate()
      ethtool_after_lines = (ethtool_after_stdout.strip()).split('\n')

      after_time = datetime.datetime.now()

      ping_report.write(ping_stdout)
      ping_report.write("\n\n")

      ping_report.write("Time of initial ethtool report: {0}\n".format(before_time))
      ping_report.write("Time of final ethtool report: {0}\n\n".format(after_time))


      #Subtract results of initial ethtool report from final report
      line_index = 0

      for line_before in ethtool_before_lines:

          line_after = ethtool_after_lines[line_index]


          if line_before == "NIC statistics:":
              line_report = "{0}\n".format(line_before)

          else:
              line_before_split = line_before.split(": ")
              line_after_split = line_after.split(": ")
              if line_before_split[0] != line_after_split[0]:
                  print("Error: Ethtool Line Desynch for {0}".format(target))
                  line_report = "Error: Ethtool Line Desynch"
              else:
                  statistic = line_before_split[0]
                  data_int = int(line_after_split[1]) - int(line_before_split[1])
                  data_string = str(data_int)
                  line_report = "{0}: {1}\n".format(statistic, data_string)

          ping_report.write(line_report)
          line_index += 1

      ping_report.flush()

  except:
    show_exc_info (ping_report)
    print " Exception while pinging %s, continuing " % target

    for packet_size in ping_packet_sizes :

      results_dict[packet_size][target]["tx"] = "NA"
      results_dict[packet_size][target]["rx"] = "NA"
      results_dict[packet_size][target]["dropped"] = "NA"
      results_dict[packet_size][target]["time"] = "NA"
      results_dict[packet_size][target]["rtt"] = "NA"

# Create table of results
ping_report.write("\n\n\n")

data_row_format = "|{:^10}|{:^20}|{:^15}|{:^12}|{:^30}|\n"
filler_row = "+{}+{}+{}+{}+{}+\n".format("-"*10, "-"*20, "-"*15, "-"*12, "-"*30) 

for packet_size in ping_packet_sizes:
    header = "#"*77 + "\n"
    header += "#" + " "*75 + "#\n"
    header += "#{:^75}#\n".format("Results for Packet Size: {} Bytes".format(packet_size))
    header += "#" + " "*75 + "#\n"
    header += "#"*77 + "\n\n"
    ping_report.write(header)
    ping_report.write(filler_row)
    ping_report.write(data_row_format.format("Device", "Packets Dropped", "Packets Sent", "Time Taken", "RTT min/avg/mav/mdev"))

    for target in target_list:
        data_dict = results_dict[packet_size][target]
        tx_cnt = data_dict["tx"]
        dropped_cnt = data_dict["dropped"]
        tbl_tx = "{:.2e}".format(tx_cnt) if isinstance(tx_cnt, int) else tx_cnt
        tbl_dropped = "{:.2e}".format(dropped_cnt) if isinstance(dropped_cnt, int) else dropped_cnt
        data_row = data_row_format.format(target, tbl_dropped, tbl_tx, data_dict["time"], data_dict["rtt"])
        ping_report.write(filler_row)
        ping_report.write(data_row)

ping_report.write(filler_row)

ping_report.flush()



ping_report.close()





"""
# Example ping_stdout
PING 10.0.0.103 (10.0.0.103) 1472(1500) bytes of data.

--- 10.0.0.103 ping statistics ---
10 packets transmitted, 10 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.295/0.342/0.385/0.034 ms, pipe 4, ipg/ewma 0.103/0.345 ms
"""

