API="https://api.coingecko.com/api/v3/simple/price?ids=pi-network&vs_currencies=usd"
html=$(curl -s "$API")
price=$(echo "$html" | grep -oP '"pi-network":\{"usd":\K[0-9.]+')
time=$(date "+%Y-%m-%d %H:%M:%S")
echo "$time, $price" >> pi_network_prices.csv