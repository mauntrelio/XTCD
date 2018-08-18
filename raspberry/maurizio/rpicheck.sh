#!/bin/bash

LOGFILE=/var/log/rpicheck.log

date >> $LOGFILE
uptime >> $LOGFILE
vcgencmd measure_temp >> $LOGFILE
vcgencmd get_throttled >> $LOGFILE
iwlist wlan0 scan | grep Signal >> $LOGFILE
echo  >> $LOGFILE
echo "=========================================" >>  $LOGFILE
echo  >> $LOGFILE

