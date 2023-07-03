#!/bin/bash

# Install NTP
apt-get update
apt-get install -y ntp

# Backup the original NTP configuration file
cp /etc/ntp.conf /etc/ntp.conf.bak

# Configure NTP to use the official NTP servers
cat > /etc/ntp.conf <<EOL
# Use the official NTP servers
server 0.pool.ntp.org
server 1.pool.ntp.org
server 2.pool.ntp.org
server 3.pool.ntp.org
EOL

# Restart the NTP service
systemctl restart ntp

