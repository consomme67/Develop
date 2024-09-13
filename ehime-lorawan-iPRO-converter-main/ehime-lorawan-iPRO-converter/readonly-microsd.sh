#!/bin/bash

# Function to enable read-only mode
enable_readonly() {
    sudo sed -i 's/defaults,noatime,rw/defaults,noatime,ro/' /etc/fstab
    echo "Read-only mode has been enabled. Press any key to Rebooting the system."
    read -n 1 -s
    sudo reboot
}

# Function to disable read-only mode
disable_readonly() {
    sudo mount -o remount,rw / > /dev/null 2>&1
    sudo sed -i 's/defaults,noatime,ro/defaults,noatime,rw/' /etc/fstab
    echo "Read-only mode has been disabled. Press any key to Rebooting the system."
    read -n 1 -s
    sudo reboot
}

# Check user input
if [ "$1" == "enable" ]; then
    enable_readonly
elif [ "$1" == "disable" ]; then
    disable_readonly
else
    echo "Usage: $0 {enable|disable}"
    exit 1
fi

