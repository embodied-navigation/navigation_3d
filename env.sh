#!/usr/bin/env bash

export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export FASTRTPS_DEFAULT_PROFILES_FILE="${HOME}/config/fastdds_shm.xml"
export RMW_FASTRTPS_USE_QOS_FROM_XML=1
