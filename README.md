---

# Allora Network Guide 

Welcome to the Allora Network guide! This document is a simple guide for running the Allora Worker node. I've updated the original code to use the `yfinance` Python library for better effectiveness, as the original code relied on the paid CoinGecko API, whereas `yfinance` is free to use. 

We are also using the Hugging Face AI model for price prediction, which is more effective and can help you earn more Allora Points.

If you appreciate my work, please give it a star. Thank you!

## Table of Contents

1. [Install Dependencies](#install-dependencies)
2. [Install Python3](#install-python3)
3. [Install Docker](#install-docker)
4. [Install Docker-Compose](#install-docker-compose)
5. [Docker Permissions](#docker-permissions)
6. [Install Go](#install-go)
7. [Install Allorad: Wallet](#install-allorad-wallet)
8. [Run Hugging Face Worker](#run-hugging-face-worker)
9. [Edit Configuration Files](#edit-configuration-files)
10. [Initialize Worker](#initialize-worker)
11. [Faucet Your Worker Node](#faucet-your-worker-node)
12. [Run Worker Using Docker Compose](#run-worker-using-docker-compose)
13. [View Wallet/Worker Transactions](#view-walletworker-transactions)

## Install Dependencies

Update and upgrade your system, then install the required packages:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev curl git wget make jq build-essential pkg-config lsb-release libssl-dev libreadline-dev libffi-dev gcc screen unzip lz4
```

## Install Python3

Install Python3 and pip3:

```bash
sudo apt install python3
python3 --version

sudo apt install python3-pip
pip3 --version
```

## Install Docker

Add Docker's official GPG key and repository, then install Docker:

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
docker version
```

## Install Docker-Compose

Download and install Docker-Compose:

```bash
VER=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep tag_name | cut -d '"' -f 4)
curl -L "https://github.com/docker/compose/releases/download/$VER/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

## Docker Permissions

Add your user to the Docker group:

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
```

## Install Go

Remove any existing Go installation and install Go:

```bash
sudo rm -rf /usr/local/go
curl -L https://go.dev/dl/go1.22.4.linux-amd64.tar.gz | sudo tar -xzf - -C /usr/local
echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> $HOME/.bash_profile
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> $HOME/.bash_profile
source $HOME/.bash_profile
go version
```

## Install Allorad: Wallet

Clone the Allora repository and build the wallet:

```bash
git clone https://github.com/allora-network/allora-chain.git
cd allora-chain && make all
allorad version
```

## Run Hugging Face Worker

Clone the Hugging Face worker repository:

```bash
git clone https://github.com/HarbhagwanDhaliwal/AlloraAiHuggingModel.git
cd AlloraAiHuggingModel
```

### Create Worker Directory

Create and set permissions for the worker data directory:

```bash
mkdir -p worker-data
chmod -R 777 worker-data
```

## Edit Configuration Files

Copy and edit the configuration file:

```bash
cp config.example.json config.json
nano config.json
```

Example configuration (`config.json`):

```json
{
   "wallet": {
       "addressKeyName": "Wallet Name",
       "addressRestoreMnemonic": "Wallet Recovery Mnemonic",
       "alloraHomeDir": "/root/.allorad",
       "gas": "1000000",
       "gasAdjustment": 1.0,
       "nodeRpc": "https://rpc.ankr.com/allora_testnet",
       "maxRetries": 1,
       "delay": 1,
       "submitTx": false
   },
   "worker": [
       {
           "topicId": 2,
           "inferenceEntrypointName": "api-worker-reputer",
           "loopSeconds": 3,
           "parameters": {
               "InferenceEndpoint": "http://inference:8000/inference/{Token}",
               "Token": "ETH"
           }
       },
       {
           "topicId": 4,
           "inferenceEntrypointName": "api-worker-reputer",
           "loopSeconds": 2,
           "parameters": {
               "InferenceEndpoint": "http://inference:8000/inference/{Token}",
               "Token": "BTC"
           }
       },
       {
           "topicId": 6,
           "inferenceEntrypointName": "api-worker-reputer",
           "loopSeconds": 5,
           "parameters": {
               "InferenceEndpoint": "http://inference:8000/inference/{Token}",
               "Token": "SOL"
           }
       }
   ]
}
```

Simply replace `"Wallet Name"` and `"Wallet Recovery Mnemonic"` with your actual wallet name and mnemonic.

## Initialize Worker

Make the initialization script executable and run it:

```bash
chmod +x init.config
./init.config
```
## Faucet Your Worker Node

You can find the offchain worker node's address in ./worker-data/env_file under ALLORA_OFFCHAIN_ACCOUNT_ADDRESS. [Add faucet funds](https://faucet.testnet-1.testnet.allora.network/) to your worker's wallet before starting it.

## Run Worker Using Docker Compose

Build and run the Docker containers:

```bash
docker compose up --build -d
```

Check logs:

```bash
docker compose logs -f
```

## View Wallet/Worker Transactions

View transactions at: [https://testnet.itrocket.net/allora/](https://testnet.itrocket.net/allora/)

---

For assistance, please contact me on Telegram: [Manpreet Dhaliwal](https://t.me/CryptoManpreet).
