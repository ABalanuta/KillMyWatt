#!/bin/bash

ping -q -c 1 10.0.0.253 > /dev/null
if [ $? -eq  0 ]; then
	echo "Ping Success";
else
	reboot
fi
