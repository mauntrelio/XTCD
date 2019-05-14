#!/bin/bash

sysctl -w net.ipv4.ip_forward=1
iptables -A FORWARD -i eno2:0 -o eno1 -j ACCEPT
iptables -A FORWARD -i eno1 -o eno2:0 -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -t nat -A POSTROUTING -o eno1 -j MASQUERADE
