#!/usr/bin/env bash

############################################
#                                          #
# Full Perfsonar Test                      #
# Author: Spencer Lee (leespen1@msu.edu)   #
# Rev: May 13, 2020, 18:00                 #
#                                          #
############################################

# Runs 128 Byte and 1472 Byte ping tests, throuhghput test, and starts the OWAMP test

usage="Usage: ./full_perfsonar_test.sh --hub1SN [SN] --hub2SN [SN]\n\n"
#usage+="                                                           -a|--all\n"
#usage+="                                                           -p|--ping\n"
#usage+="                                                           -t|--throughput\n"
#usage+="                                                           -o|--owamp\n"
usage+="Options:\n"
usage+="--hub1SN [Serial Number]           Specify serial number of hub1. Required for all\n"
usage+="                                   tests. Only affects log/display output.        \n"
usage+="--hub2SN [Serial Number]           Specify serial number of hub2. Required for    \n"
usage+="                                   ping tests. Only affects log/display output.   \n"
usage+="-a, --all                          Run ping, throughput, and owamp test           \n"
usage+="-p, --ping                         Run ping test                                  \n"
usage+="-t, --throughput                   Run throughput test                            \n"
usage+="-o, --owamp                        Run OWAMP test                                 \n"
usage+="\n"

hub1SN=""
hub2SN=""

run_all=0
run_ping=0
run_throughput=0
run_owamp=0

# Arguments should have 
# Get command line arguments.
while [[ $# -gt 0 ]]
do
key="$1"

case $key in

    --hub1SN)
    hub1SN="$2"
    shift
    shift
    ;;
    --hub2SN)
    hub2SN="$2"
    shift
    shift
    ;;
    -a|--all)
    run_all=1
    shift
    ;;
    -p|--ping)
    run_ping=1
    shift
    ;;
    -t|--throughput)
    run_throughput=1
    shift
    ;;
    -o|--owamp)
    run_owamp=1
    shift
    ;;
    -h|--help)
    printf "$usage"
    exit 0
    ;;
    *)
    printf "Parameter $key not recognized.\n"
    printf "$usage"
    printf "Exiting ...\n"
    exit 1
    ;;
esac
done

if [ "$run_all" -ne 0 ]
then
  run_ping=1
  run_throughput=1
  run_owamp=1
fi

# Check that hub1SN is given
if [ -z "$hub1SN" ]
then
    printf "Serial number of Hub1 not given. Required for all tests.\n"
    printf "$usage"
    printf "Exiting ...\n"
    exit 1
fi


# Ping Section
if [ $run_ping -ne 0 ]
then

  # Check that hub2SN is given (only required for ping test)
  if [ -z "$hub2SN" ]
  then
      printf "Serial number of Hub2 not given. Required for ping test.\n"
      printf "Skipping ping test ...\n"
  else

    cd ./Ping
    
    # Get full date/time
    now_full=$(date)
    echo "######################################################################"
    echo ""
    echo "Starting 128 Byte Ping Test At Time: $now_full"
    echo ""
    echo "######################################################################"
    
    # Get date in YYYYMMDD format
    now=$(date +'%Y%m%d')
    
    ping_128byte_title="HubSN${hub1SN}x${hub2SN}_Ping_128Byte_${now}.txt"
    ping_128byte_path="../Full_Config/ping_test_128Byte.conf"
    
    python ping_test.py -o ${ping_128byte_title} --config_file ${ping_128byte_path}
    cp ./Results/${ping_128byte_title} ../Full_Results/
    
    # Get full date/time
    now_full=$(date)
    echo "######################################################################"
    echo ""
    echo "Starting 1472 Byte Ping Test At Time: $now_full"
    echo ""
    echo "######################################################################"
    
    # Get date in YYYYMMDD format
    now=$(date +'%Y%m%d')
    
    ping_1472byte_title="HubSN${hub1SN}x${hub2SN}_Ping_1472Byte_${now}.txt"
    ping_1472byte_path="../Full_Config/ping_test_1472Byte.conf"
    
    python ping_test.py -o ${ping_1472byte_title} --config_file ${ping_1472byte_path}
    cp ./Results/${ping_1472byte_title} ../Full_Results/

    cd ../

  fi
fi
# End Ping Section


# Throughput Section
if [ $run_throughput -ne 0 ]
then
  # Get full date/time
  now_full=$(date)
  echo "######################################################################"
  echo ""
  echo "Starting Throughput Test At Time: $now_full"
  echo ""
  echo "######################################################################"
  
  # Get Date in YYYYMMDD format
  now=$(date +'%Y%m%d')
  
  throughput_title="HubSN${hub1SN}_Throughput_${now}.txt"
  throughput_path="../Full_Config/throughput_test.conf"
  
  cd ./Throughput
  
  # First perform a 5 second test, just to make sure everything works
  python throughput_script.py -c ${throughput_path} -d PT5S --serial_no ${hub1SN}
  # Perform the actual throughput test
  python throughput_script.py -o ${throughput_title} -c ${throughput_path} --serial_no ${hub1SN}
  cp ./Results/${throughput_title} ../Full_Results/

  cd ../

fi
# End Throughput Section



# OWAMP Section
if [ $run_owamp -ne 0 ]
then
  # Get full date/time
  now_full=$(date)
  echo "######################################################################"
  echo ""
  echo "Starting OWAMP Test At Time: $now_full"
  echo ""
  echo "######################################################################"
  
  # Get Date in YYYYMMDD format
  now=$(date +'%Y%m%d')
  
  owamp_title="HubSN${hub1SN}_OWAMP_${now}.txt"
  owamp_path="../Full_Config/OWAMP_test.conf"
  
  cd ./OWAMP
  
  python OWAMP_test.py -c ${owamp_path} -o ${owamp_title} --serial_no ${hub1SN}
  cp ./Results/${owamp_title} ../Full_Results/

  cd ../
fi
# End OWAMP Section

