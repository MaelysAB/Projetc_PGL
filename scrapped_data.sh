#!/bin/bash

export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

API="https://api.coingecko.com/api/v3/simple/price?ids=pi-network&vs_currencies=usd"
html=$(curl -s "$API")
price=$(echo "$html" | grep -oP '"pi-network":\{"usd":\K[0-9.]+')
time=$(date "+%Y-%m-%d %H:%M:%S")
date_only=$(date "+%Y-%m-%d")
echo "$time, $price, $date_only" >> /home/ubuntu/Projetc_PGL/pi_network_prices.csv
