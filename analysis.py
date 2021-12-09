import requests
import csv
import time
import threading

import numpy as np
from datetime import datetime

class Network(object):

  def __init__(self):
    self.waitTime = 30 # 1800 ## Seconds used to wait between each analysis and parser run
    self.analysisTime = 1 ## Days used between each polling time for updating sentiments
    self.threads = []
    self.CROW_API_URL = "http://localhost:5000/api/v1/"
    self.EXC_API_URL = "https://api.coingecko.com/api/v3/"

  def newWeight(self, o, rot, frq):
    return np.tanh(o + rot/frq)

  def analyzeSentiments(self):
    print("[/] Running sentiment analyzer")
    while True:
      sentiments = requests.get(self.CROW_API_URL + "sentiments?parsed=true").json()

      rot = requests.get(self.EXC_API_URL + "coins/bitcoin/").json()["market_data"]["price_change_percentage_24h"] / 100

      for sent in sentiments:
        if (datetime.utcnow() - datetime.strptime(sent["date"], "%Y-%m-%dT%H:%M:%S.%f")).days >= 0: # self.analysisTime:
          for word in sent["content"].split(" "):
            isWord = requests.get(self.CROW_API_URL + f"words?word={word.lower()}").json()
            newWeight = self.newWeight(int(isWord[0]["weight"]), rot, isWord[0]["frequency"])

            r = requests.patch(self.CROW_API_URL + f"words", data = {
              "word": word.lower(),
              "weight": newWeight,
            })

            print(f"Word {isWord}: {newWeight}")
      
      time.sleep(self.waitTime)

  def parseSentiments(self):
    while True:
      print("[/] Running sentiment parser")
      sentiments = requests.get(self.CROW_API_URL + "sentiments?parsed=false").json()

      for sent in sentiments:
        for word in sent["content"].split(" "):
          isWord = requests.get(self.CROW_API_URL + f"words?word={word.lower()}").json()
          if len(isWord) > 0:            
            r = requests.patch(self.CROW_API_URL + "words", data = {
              "word": word.lower()
            })
          else:
            r = requests.post(self.CROW_API_URL + "words", data = {
              "word": word.lower()
            })      

        # Set sentiment parsed attribute to true
        r = requests.patch(self.CROW_API_URL + "sentiments", data = {
          "id": str(sent["id"]),
          "parsed": "true"
        })

      time.sleep(self.waitTime)

  def getPrice(self):
    r = requests.get(self.EXC_API_URL)
    return r.json()["bitcoin"]["usd"]

  def run(self):
    t0 = threading.Thread(name="Parser", target=self.parseSentiments) # Thread used for grabbing new sentiments and parsing words
    t0.start()

    t1 = threading.Thread(name="Analyzer", target=self.analyzeSentiments) # Thread used for analyzing sentiments after a certain period
    t1.start()
    self.threads.extend([t0, t1])

    for thread in self.threads:
      thread.join()

if __name__ == "__main__":
  nn = Network()
  nn.run()