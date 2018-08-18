#!/bin/bash

grep -B 3 'error 101' /var/log/syslog$1 | egrep '(131.169|error)'

