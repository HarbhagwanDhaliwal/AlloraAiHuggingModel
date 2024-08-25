Here’s a GitHub README file based on your data:

---

# Allora Network Guide

Welcome to the Allora Network guide! This document provides instructions for setting up your environment, installing necessary dependencies, and running Allora services.

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
11. [Run Worker Using Docker Compose](#run-worker-using-docker-compose)
12. [View Wallet/Worker Transactions](#view-walletworker-transactions)

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
git clone https://github.com/allora-network/allora-huggingface-walkthrough
cd allora-huggingface-walkthrough
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
       "addressKeyName": "test",
       "addressRestoreMnemonic": "your phase",
       "alloraHomeDir": "/root/.allorad",
       "gas": "1000000",
       "gasAdjustment": 1.0,
       "nodeRpc": "https://sentries-rpc.testnet-1.testnet.allora.network/",
       "maxRetries": 1,
       "delay": 1,
       "submitTx": false
   },
   "worker": [
       {
           "topicId": 1,
           "inferenceEntrypointName": "api-worker-reputer",
           "loopSeconds": 1,
           "parameters": {
               "InferenceEndpoint": "http://inference:8000/inference/{Token}",
               "Token": "ETH"
           }
       },
       // Additional worker configurations...
   ]
}
```

Replace `"your phase"` with your wallet mnemonic and adjust the RPC URL if needed.

### Edit `APP.PY`

Modify `APP.PY` for your Flask app:

```python
from flask import Flask, Response
import requests
import json
import pandas as pd
import torch
from chronos import ChronosPipeline

# create our Flask app
app = Flask(__name__)

# define the Hugging Face model we will use
model_name = "amazon/chronos-t5-tiny"

def get_coingecko_url(token):
    base_url = "https://api.coingecko.com/api/v3/coins/"
    token_map = {
        'ETH': 'ethereum',
        'SOL': 'solana',
        'BTC': 'bitcoin',
        'BNB': 'binancecoin',
        'ARB': 'arbitrum'
    }
    
    token = token.upper()
    if token in token_map:
        url = f"{base_url}{token_map[token]}/market_chart?vs_currency=usd&days=30&interval=daily"
        return url
    else:
        raise ValueError("Unsupported token")

# define our endpoint
@app.route("/inference/<string:token>")
def get_inference(token):
    """Generate inference for given token."""
    try:
        # use a pipeline as a high-level helper
        pipeline = ChronosPipeline.from_pretrained(
            model_name,
            device_map="auto",
            torch_dtype=torch.bfloat16,
        )
    except Exception as e:
        return Response(json.dumps({"pipeline error": str(e)}), status=500, mimetype='application/json')

    try:
        # get the data from Coingecko
        url = get_coingecko_url(token)
    except ValueError as e:
        return Response(json.dumps({"error": str(e)}), status=400, mimetype='application/json')

    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": "CG-your_api_key" # replace with your API key
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data["prices"])
        df.columns = ["date", "price"]
        df["date"] = pd.to_datetime(df["date"], unit='ms')
        df = df[:-1] # removing today's price
        print(df.tail(5))
    else:
        return Response(json.dumps({"Failed to retrieve data from the API": str(response.text)}), 
                        status=response.status_code, 
                        mimetype='application/json')

    # define the context and the prediction length
    context = torch.tensor(df["price"])
    prediction_length = 1

    try:
        forecast = pipeline.predict(context, prediction_length)  # shape [num_series, num_samples, prediction_length]
        print(forecast[0].mean().item()) # taking the mean of the forecasted prediction
        return Response(str(forecast[0].mean().item()), status=200)
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')

# run our Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
```

*Edit your API key from Coingecko: [Coingecko API Dashboard](https://www.coingecko.com/en/developers/dashboard)*

## Initialize Worker

Make the initialization script executable and run it:

```bash
chmod +x init.config
./init.config
```

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

View transactions at: [http://worker-tx.nodium.xyz/](http://worker-tx.nodium.xyz/)

---

Feel free to adjust the content as needed.
