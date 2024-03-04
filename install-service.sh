#!/bin/bash

# Replace these variables according to your setup
SERVICE_NAME=sensor-osc
SCRIPT_PATH="/home/incubator-pi/evo-to-osc/sensor-osc.py"
WORKING_DIRECTORY="/home/incubator-pi/evo-to-osc"
ENV_PATH="/home/incubator-pi/evo-to-osc/myenv"
USER=incubator-pi
IP=192.168.88.113
PORT=7001
INDEX=0

# Create systemd service file
echo "[Unit]
Description=$SERVICE_NAME Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$WORKING_DIRECTORY
Environment=\"PATH=$ENV_PATH/bin\"
ExecStart=$ENV_PATH/bin/python $SCRIPT_PATH $IP $PORT $INDEX
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null

# Reload systemd, enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "$SERVICE_NAME service created and started successfully."
