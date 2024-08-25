from flask import Flask, Response
import yfinance as yf
import pandas as pd
import torch
from chronos import ChronosPipeline
import json

# create our Flask app
app = Flask(__name__)

# define the Hugging Face model we will use
model_name = "amazon/chronos-t5-tiny"

# map token to Yahoo Finance ticker
token_map = {
    'ETH': 'ETH-USD',
    'SOL': 'SOL-USD',
    'BTC': 'BTC-USD',
    'BNB': 'BNB-USD',
}

# Load the model once
pipeline = ChronosPipeline.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype=torch.bfloat16,
)


def get_yahoo_finance_data(token):
    ticker = token_map.get(token.upper())
    if ticker:
        data = yf.download(ticker, period='1mo', interval='1d')
        if data.empty:
            raise ValueError("No data found for the given token")
        return data
    else:
        raise ValueError("Unsupported token")


@app.route("/inference/<string:token>")
def get_inference(token):
    """Generate inference for given token."""
    try:
        # get the data from Yahoo Finance
        data = get_yahoo_finance_data(token)

        # preprocess data
        df = data[['Close']].reset_index()
        df.columns = ["date", "price"]
        df["date"] = pd.to_datetime(df["date"])
        df = df[:-1]  # removing today's price

        # prepare the input for the model
        context = torch.tensor(df["price"].values, dtype=torch.float32).unsqueeze(0)  # Add batch dimension
        prediction_length = 1

        # make prediction
        forecast = pipeline.predict(context, prediction_length)
        prediction = forecast[0].mean().item()  # taking the mean of the forecasted prediction

        return Response(str(prediction), status=200)
    except ValueError as e:
        return Response(json.dumps({"error": str(e)}), status=400, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')


# run our Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=False)
