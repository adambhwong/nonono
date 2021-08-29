#!/usr/bin/env bash
#
# Filename: test_docker.sh
# Usage: ./test_docker.sh [-h|--help] [-c|--show-command-only] [-l|--list-used-ports-only] [-d|--do-not-detach] [-s|--skip-build] [-k|--cred_key <Credential Key>]
# Description: build and strat/restart a conainer, user should fill the variable section
# Version: 1.0
# Author: Adam Wong
#

### Variable Section ###
IMAGE_NAME="url-shortener-api"
BIND_PORT="9099:80"
DOCKER_EXTRA_OPTIONS=""
REMOVE_CONTAINER=true
DEBUG=1
TIMEZONE="UTC"
PUSH_TO_REG=0
REG_HOST=""
### END Variable Section ###

AWS_CFG_PARAMS=("AWS_ACCESS_KEY_ID" "AWS_SECRET_ACCESS_KEY" "AWS_DEFAULT_REGION")

function usage() {
    echo "$0 [-h|--help] [-c|--show-command-only] [-l|--list-used-ports-only] [-d|--do-not-detach] [-s|--skip-build] [-k|--aws_cfg <Key ID:Secret Key:Region>]"
}

SHOWCOMMAND=false
LISTPORTS=false
DETACH=true
BUILD=true
POSITIONAL=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -h|--help)
    usage
    exit 0
    ;;
    -d|--do-not-detach)
    DETACH=false
    shift # past argument
    ;;
    -s|--skip-build)
    BUILD=false
    shift # past argument
    ;;
    -c|--show-command-only)
    SHOWCOMMAND=true
    shift # past argument
    ;;
    -l|--list-used-ports-only)
    LISTPORTS=true
    shift # past argument
    ;;
    -k|--aws_cfg)
    AWS_CFG="$2"
    shift # past argument
    shift # past value
    ;;
    *)    # unknown option
    POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done

CONTAINER_NAME=$IMAGE_NAME
BIND_PORT_ARG=""
REMOVE_CONTAINER_ARG=""
DEBUG_ARG=""
TZ_ARG=""
DETACH_ARG=""
[ "$BIND_PORT" != "" ] && BIND_PORT_ARG="-p $BIND_PORT"
[ $REMOVE_CONTAINER == true ] && REMOVE_CONTAINER_ARG="--rm"
[ $DEBUG -gt 0 ] && DEBUG_ARG="-e DEBUG=$DEBUG"
[ "$TIMEZONE" != "" ] && TZ_ARG="-e TZ=$TIMEZONE"
[ $DETACH == true ] && DETACH_ARG="-d"
if [ "$AWS_CFG" == "" ]
then
    echo "Missing AWS configurations."
    exit 1
fi
AWS_ARGS=""
idx=0
for item in ${AWS_CFG//:/ }
do
    if [ $idx -ge ${#AWS_CFG_PARAMS[@]} ]
    then
        echo "Invalid AWS configurations."
        exit 1
    fi
    AWS_ARGS="$AWS_ARGS -e ${AWS_CFG_PARAMS[$idx]}=$item"
    idx=$(($idx + 1))
done
if [ $idx -lt $((${#AWS_CFG_PARAMS[@]}-1)) ]
then
    echo "Invalid AWS configurations."
    exit 1
    
fi
DOCKER_CMD="/usr/bin/sudo /usr/bin/docker"
DOCKER_OPTIONS="$REMOVE_CONTAINER_ARG $BIND_PORT_ARG $DEBUG_ARG $TZ_ARG $AWS_ARGS $DOCKER_EXTRA_OPTIONS"
if [ "$LOGNAME" == "root" ]; then
   DOCKER_CMD="/usr/bin/docker"
fi
run_cmd="$DOCKER_CMD run $DETACH_ARG $DOCKER_OPTIONS --name $CONTAINER_NAME $IMAGE_NAME"
if [ $SHOWCOMMAND == true ]
then
    echo "$run_cmd"
    exit 0
fi
if [ $LISTPORTS == true ]
then
    $DOCKER_CMD ps --format '{{.Names}}\t{{.Ports}}' | sed 's/\t.*:/\t/; s/->[0-9].*//' | awk -F '\t' '($2!="") {printf("%6d %s\n", $2, $1)}' | sort
    exit 0
fi

set -e
# stop container if running
if [ $($DOCKER_CMD inspect -f {{.State.Running}} $CONTAINER_NAME 2>>/dev/null | grep -c "true") -gt 0 ]; then
    echo "Stopping container '$CONTAINER_NAME'..."
    $DOCKER_CMD stop $CONTAINER_NAME
    wait
fi
# remove container if exits
if [ $($DOCKER_CMD ps -a -f "name=$CONTAINER_NAME" --format "{{.Status}}" | grep -c "^Exited ") -eq 1 ]; then
    echo "Removing container '$CONTAINER_NAME'..."
    $DOCKER_CMD rm $CONTAINER_NAME
    wait
fi
if [ $BUILD == true ]
then
    $DOCKER_CMD build -t $IMAGE_NAME .
    echo Docker image:
    $DOCKER_CMD images -f reference=$IMAGE_NAME
    if [ $PUSH_TO_REG -eq 1 ] && [ "$REG_HOST" != "" ]
    then
        $DOCKER_CMD tag $IMAGE_NAME $REG_HOST/$IMAGE_NAME
        $DOCKER_CMD push $REG_HOST/$IMAGE_NAME
    fi
fi
$run_cmd
echo Running docker container:
$DOCKER_CMD ps -f name=$CONTAINER_NAME
RUNNING=$($DOCKER_CMD inspect -f {{.State.Running}} $CONTAINER_NAME)

if [ $RUNNING == true ]; then
    exit 0
else
    echo "$1" 1>&2
    exit 1
fi
### end ###
