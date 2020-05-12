#!/usr/bin/env bash

############################################
#                                          #
# Full Perfsonar Test                      #
# Author: Spencer Lee (leespen1@msu.edu)   #
# Rev: May 12, 2020, 17:30                 #
#                                          #
############################################

# Runs 128 Byte and 1472 Byte ping tests, throuhghput test, and starts the OWAMP test

hub1SN=""
hub2SN=""

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
    -h|--help)
    printf "Usage: sh full_perfsonar_test.sh --hub1SN [hub1 SN] --hub2SN [hub2 SN]\n"
    exit 0
    ;;
    *)
    printf "Parameter $key not recognized.\n"
    printf "Usage: sh full_perfsonar_test.sh --hub1SN [hub1 SN] --hub2SN [hub2 SN]\n"
    printf "Exiting ...\n"
    exit 1
    ;;
esac
done

# Check that hub1SN and hub2SN given
if [ -z "$hub1SN" ]
then
    printf "Serial number of Hub1 not given.\n"
    printf "Usage: sh full_perfsonar_test.sh --hub1SN [hub1 SN] --hub2SN [hub2 SN]\n"
    printf "Exiting ...\n"
    exit 1
fi

if [ -z "$hub2SN" ]
then
    printf "Serial number of Hub2 not given.\n"
    printf "Usage: sh full_perfsonar_test.sh --hub1SN [hub1 SN] --hub2SN [hub2 SN]\n"
    printf "Exiting ...\n"
    exit 1
fi

# Ping Section

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

# Throughput Section

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

cd ../Throughput

# First perform a 5 second test, just to make sure everything works
python throughput_script.py -c ${throughput_path} -d PT5S
# Perform the actual throughput test
python throughput_script.py -o ${throughput_title} -c ${throughput_path}
cp ./Results/${throughput_title}

# OWAMP Section

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

cd ../OWAMP

python OWAMP_test.py -c ${owamp_path} -o ${owamp_title}
cd ../
