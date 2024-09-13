#!/bin/bash

SERVICE_NAME=mqtt-client.service
SERVICE_PATH=/etc/systemd/system/$SERVICE_NAME
LOCAL_SERVICE_FILE=./$SERVICE_NAME

# Function to install the mqtt-client service
install_service() {
    if [ -f "$LOCAL_SERVICE_FILE" ]; then
        sudo cp "$LOCAL_SERVICE_FILE" "$SERVICE_PATH"
        sudo systemctl daemon-reload
        sudo systemctl enable "$SERVICE_NAME"
        sudo systemctl start "$SERVICE_NAME"
        echo "MQTT client service has been installed, enabled, and started."
    else
        echo "Service file $LOCAL_SERVICE_FILE does not exist."
        exit 1
    fi
}

# Function to uninstall the mqtt-client service
uninstall_service() {
    sudo systemctl stop "$SERVICE_NAME"
    sudo systemctl disable "$SERVICE_NAME"
    sudo rm "$SERVICE_PATH"
    sudo systemctl daemon-reload
    echo "MQTT client service has been stopped, disabled, and removed."
}

# Function to enable the mqtt-client service
enable_service() {
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl start "$SERVICE_NAME"
    echo "MQTT client service has been enabled and started."
}

# Function to disable the mqtt-client service
disable_service() {
    sudo systemctl stop "$SERVICE_NAME"
    sudo systemctl disable "$SERVICE_NAME"
    echo "MQTT client service has been stopped and disabled."
}

# Check user input
case "$1" in
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    enable)
        enable_service
        ;;
    disable)
        disable_service
        ;;
    *)
        echo "Usage: $0 {install|uninstall|enable|disable}"
        exit 1
        ;;
esac

