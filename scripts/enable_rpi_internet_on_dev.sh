#!/bin/bash

IFIN=eno2:0
IFOUT=eno1

sysctl -w net.ipv4.ip_forward=1
iptables -A FORWARD -i $IFIN -o $IFOUT -j ACCEPT
iptables -A FORWARD -i $IFOUT -o $IFIN -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -t nat -A POSTROUTING -o $IFOUT -j MASQUERADE


