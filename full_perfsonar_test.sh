# This will initiate perfsonar throughput test, then the OWAMP test


# Arguments should have 
# Get command line arguments.
while [[ $# -gt 0 ]]
do
key="$1"

case $key in

    --time)
    time="$2"
    shift
    shift
    ;;
    -h|--help)
    printf "Usage: $0 [--IP_Addr <IP Address>] --IOIF_f <IOIF Binary> --IPMC_f <IPMC Binary>\n"
    exit 0
    ;;
    *)
    printf "Parameter $key not recognized.\n"
    printf "Usage: $0 [--IP_Addr <IP Address>]--IOIF_f <IOIF Binary> --IPMC_f <IPMC Binary>\n"
    printf "Exiting ...\n"
    exit 1
    ;;
esac
done

