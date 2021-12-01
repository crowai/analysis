import requests
import csv
import time

import numpy as np

# Read and update csv file words based on sentiment
class Network(object):

  def __init__(self, wordsFile):
    self.ids = []
    self.EXC_API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

  def tanh(self, x):
    return (np.exp(x) - np.exp(-x)/(np.exp(x) + np.exp(-x)))

  def valueSentiments(self):
    sentiments = requests.get("http://localhost:5000/api/v1/sentiments").json()
    words = requests.get("http://localhost:5000/api/v1/words").json()

    for sent in sentiments:
      if not sent["id"] in self.ids:
        self.ids.append(sent["id"])
        for word in sent["content"].split(" "):
          isWord = requests.get(f"http://localhost:5000/api/v1/words?word={word}").json()
          if len(isWord) > 0:
            newWeight = self.tanh(int(isWord[0]["weight"]) + self.tanh(0.05)) # tanh(old_price + tanh(price_change))
            
            r = requests.patch(f"http://localhost:5000/api/v1/words", data = {
              "word": word.lower(),
              "weight": newWeight
            })
          else:
            r = requests.post(f"http://localhost:5000/api/v1/words", data = {
              "word": word.lower()
            })
            

  def getPrice(self):
    r = requests.get(self.EXC_API_URL)
    return r.json()["bitcoin"]["usd"]

  def run(self):
    # for i in self.sentiments:
    #   self.valueSentiment(i)
    self.valueSentiments()

if __name__ == "__main__":
  nn = Network(wordsFile="words.csv")
  nn.run()

# sentiments = requests.get("http://localhost:5000/api/v1/sentiments")
# for sent in sentiments.json():
#   print(sent["content"])