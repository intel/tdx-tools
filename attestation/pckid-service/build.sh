#!/bin/bash

DEB_NAME=pckid-retrieve-tool-service_1.0-1_amd64
LOCAL_DIR=/etc/systemd/system/
SRV_NAME=pckid_retrieve_tool_service.service
PASSWD=\'\$harktank2Go\'

if [ -n "$1" ];then
	# shellcheck disable=SC2089
	PASSWD=\'$1\'
fi
echo "The input password of the pccs is: $PASSWD"

cp  pckid_retrieve_tool_service.service.template $DEB_NAME$LOCAL_DIR$SRV_NAME
sed -i "s/\$PASSWD/$PASSWD/g" $DEB_NAME$LOCAL_DIR$SRV_NAME
dpkg-deb --build --root-owner-group  $DEB_NAME
