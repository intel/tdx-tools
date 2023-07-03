#!/bin/bash

# Install NTP
apt-get update
apt-get install -y ntp

# Backup the original NTP configuration file
cp /etc/ntp.conf /etc/ntp.conf.bak

# Clear the contents of the file
truncate --size 0 /etc/ntp.conf

# Check if NTP server addresses are provided
if [ -z "$1" ]; then
  # Configure NTP to use the official NTP servers
  cat > /etc/ntp.conf <<EOL
# Use the official NTP servers
server 0.pool.ntp.org
server 1.pool.ntp.org
server 2.pool.ntp.org
server 3.pool.ntp.org
EOL
else 
  # Configure NTP to use custom NTP servers
  echo "# Use custom NTP servers" >> /etc/ntp.conf
  IFS=','
  read -ra ntp_servers <<< "$1"
  for ntp_server in "${ntp_servers[@]}"; do
    echo "server ${ntp_server}" >> /etc/ntp.conf  
  done
fi

# Restart the NTP service
systemctl restart ntp
