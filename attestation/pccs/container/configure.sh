#!/bin/bash

## Set mydir to the directory containing the script
configFile=default.json
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m'

echo "--------------------------------"
echo "Start to setup pccs configuration"

#Ask for URI
platform=""
while :
do
    read -rp "Choose your Platform (liv/sbx) :" platform 
    if [ "$platform" == "liv" ]
    then
        sed "/\"uri\"*/c\ \ \ \ \"uri\" \: \"https://api.trustedservices.intel.com/sgx/certification/v4/\"," -i ${configFile}
        break
    elif [ "$platform" == "sbx" ]
    then
        sed "/\"uri\"*/c\ \ \ \ \"uri\" \: \"https://sbx.api.trustedservices.intel.com/sgx/certification/v4/\"," -i ${configFile}
        break
    else
        echo "Your input is invalid. Please input again. "
    fi
done


#Ask for proxy server
echo "Check proxy server configuration for internet connection... "
if [ "$http_proxy" == "" ]
then
    read -rp "Enter your http proxy server address, e.g. http://proxy-server:port (Press ENTER if there is no proxy server) :" http_proxy 
fi
if [ "$https_proxy" == "" ]
then
    read -rp "Enter your https proxy server address, e.g. http://proxy-server:port (Press ENTER if there is no proxy server) :" https_proxy 
fi


#Ask for HTTPS port number
port=""
while :
do
    read -rp "Set HTTPS listening port [8081] (1024-65535) :" port
    if [ -z "$port" ]; then 
        port=8081
        break
    elif [[ $port -lt 1024  ||  $port -gt 65535 ]] ; then
        echo -e "${YELLOW}The port number is out of range, please input again.${NC} "
    else
        sed "/\"HTTPS_PORT\"*/c\ \ \ \ \"HTTPS_PORT\" \: ${port}," -i ${configFile}
        break
    fi
done

#Ask for HTTPS port number
local_only=""
while [ "$local_only" == "" ]
do
    read -rp "Set the PCCS service to accept local connections only? [Y] (Y/N) :" local_only 
    if [[ -z $local_only  || "$local_only" == "Y" || "$local_only" == "y" ]] 
    then
        local_only="Y"
        sed "/\"hosts\"*/c\ \ \ \ \"hosts\" \: \"127.0.0.1\"," -i ${configFile}
    elif [[ "$local_only" == "N" || "$local_only" == "n" ]] 
    then
        sed "/\"hosts\"*/c\ \ \ \ \"hosts\" \: \"0.0.0.0\"," -i ${configFile}
    else
        local_only=""
    fi
done

#Ask for API key 
apikey=""
while :
do
    read -rp "Set your Intel PCS API key (Press ENTER to skip) :" apikey 
    if [ -z "$apikey" ]
    then
        echo -e "${YELLOW}You didn't set Intel PCS API key. You can set it later in config/default.json. ${NC} "
        break
    elif [[ $apikey =~ ^[a-zA-Z0-9]{32}$ ]] && sed "/\"ApiKey\"*/c\ \ \ \ \"ApiKey\" \: \"${apikey}\"," -i ${configFile}
    then
        break
    else
        echo "Your API key is invalid. Please input again. "
    fi
done

if [ "$https_proxy" != "" ]
then
    sed "/\"proxy\"*/c\ \ \ \ \"proxy\" \: \"${https_proxy}\"," -i ${configFile}
fi

#Ask for CachingFillMode
caching_mode=""
while [ "$caching_mode" == "" ]
do
    read -rp "Choose caching fill method : [LAZY] (LAZY/OFFLINE/REQ) :" caching_mode 
    if [[ -z $caching_mode  || "$caching_mode" == "LAZY" ]] 
    then
        caching_mode="LAZY"
        sed "/\"CachingFillMode\"*/c\ \ \ \ \"CachingFillMode\" \: \"${caching_mode}\"," -i ${configFile}
    elif [[ "$caching_mode" == "OFFLINE" || "$caching_mode" == "REQ" ]] 
    then
        sed "/\"CachingFillMode\"*/c\ \ \ \ \"CachingFillMode\" \: \"${caching_mode}\"," -i ${configFile}
    else
        caching_mode=""
    fi
done

#Ask for administrator password
admintoken1=""
admintoken2=""
admin_pass_set=false
cracklib_limit=4
while [ "$admin_pass_set" == false ]
do
    while test "$admintoken1" == ""
    do
        read -s -rp "Set PCCS server administrator password:" admintoken1
        printf "\n"
    done
    
    # check password strength
    result="$(cracklib-check <<<"$admintoken1")"
    okay="$(awk -F': ' '{ print $NF}' <<<"$result")"
    if [[ "$okay" != "OK" ]]; then
        if [ "$cracklib_limit" -gt 0 ]; then
            echo -e "${RED}The password is too weak. Please try again($cracklib_limit opportunities left).${NC}"
            admintoken1=""
            cracklib_limit=$(( "$cracklib_limit" - 1 ))
            continue
        else
            echo "Installation aborted. Please try again."
            exit 1
        fi
    fi

    while test "$admintoken2" == ""
    do
        read -s -rp "Re-enter administrator password:" admintoken2
        printf "\n"
    done

    if test "$admintoken1" != "$admintoken2"
    then
        echo "Passwords don't match."
        admintoken1=""
        admintoken2=""
        cracklib_limit=4
    else
        HASH="$(echo -n "$admintoken1" | sha512sum | tr -d '[:space:]-')"
        sed "/\"AdminTokenHash\"*/c\ \ \ \ \"AdminTokenHash\" \: \"${HASH}\"," -i ${configFile}
        admin_pass_set=true
    fi
done

#Ask for user password
cracklib_limit=4
usertoken1=""
usertoken2=""
user_pass_set=false
while [ "$user_pass_set" == false ]
do
    while test "$usertoken1" == ""
    do
        read -s -rp "Set PCCS server user password:" usertoken1
        printf "\n"
    done

    # check password strength
    result="$(cracklib-check <<<"$usertoken1")"
    okay="$(awk -F': ' '{ print $NF}' <<<"$result")"
    if [[ "$okay" != "OK" ]]; then
        if [ "$cracklib_limit" -gt 0 ]; then
            echo -e "${RED}The password is too weak. Please try again($cracklib_limit opportunities left).${NC}"
            usertoken1=""
            cracklib_limit=$(( "$cracklib_limit" - 1 ))
            continue
        else
            echo "Installation aborted. Please try again."
            exit 1
        fi
    fi

    while test "$usertoken2" == ""
    do
        read -s -rp "Re-enter user password:" usertoken2
        printf "\n"
    done

    if test "$usertoken1" != "$usertoken2"
    then
        echo "Passwords don't match."
        usertoken1=""
        usertoken2=""
        cracklib_limit=4
    else
        HASH="$(echo -n "$usertoken1" | sha512sum | tr -d '[:space:]-')"
        sed "/\"UserTokenHash\"*/c\ \ \ \ \"UserTokenHash\" \: \"${HASH}\"," -i ${configFile}
        user_pass_set=true
    fi
done

if which openssl > /dev/null 
then 
    genkey=""
    while [ "$genkey" == "" ]
    do
        read -rp "Do you want to generate insecure HTTPS key and cert for PCCS service? [Y] (Y/N) :" genkey 
        if [[ -z "$genkey" ||  "$genkey" == "Y" || "$genkey" == "y" ]] 
        then
            if [ ! -d ssl_key  ];then
                mkdir ssl_key
            fi
            openssl genrsa -out ssl_key/private.pem 2048
            openssl req -new -key ssl_key/private.pem -out ssl_key/csr.pem
            openssl x509 -req -days 365 -in ssl_key/csr.pem -signkey ssl_key/private.pem -out ssl_key/file.crt
            break
        elif [[ "$genkey" == "N" || "$genkey" == "n" ]] 
        then
            break
        else
            genkey=""
        fi
    done
else
    echo -e "${YELLOW}You need to setup HTTPS key and cert for PCCS to work. For how-to please check README. ${NC} "
fi

