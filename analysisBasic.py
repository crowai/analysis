import requests
import math
from datetime import timedelta, datetime

API_URL = "http://165.227.203.180"

def pullData(): ## Pulls data from API_URL
  r = requests.get(API_URL + "/api/v1/sentiments")
  data = r.json()

  return data

# datetime.strptime(k["date"][:-7], "%Y-%m-%dT%H:%M:%S")

def helper(data):
  d = []
  for i in data:
    d.append(datetime.strptime(i["date"][:-7], "%Y-%m-%dT%H:%M:%S"))

  sorted = sort(d, 30)

  x = []
  for i in sorted:
    x.append(len(i))

  return x

def analyzeInts(data, ints):
  c = 0
  for i in ints:
    bearish = 0
    bullish = 0
    for j in range(i):
      if data[c]["excSentiment"] == "bullish":
        bullish += 1
      if data[c]["excSentiment"] == "bearish":
        bearish += 1
        
      c += 1

    print(bearish, bullish)    


def sort(data,interval): ## Written by PharingWell
  intervals = []
  
  for c in range(0,math.ceil(divmod((data[-1]-data[0]).total_seconds(), 60)[0]/interval)+1): #last index minus first index, assumes the array is sorted by ascending time. This gets the amount of loops needed
    temp=list(filter(lambda x: x >= data[0]+timedelta(minutes=interval*c) and x < data[0]+timedelta(minutes=interval*(c+1)),data))
    if(temp):
      intervals.append(temp)
    else:
      c-=1

  return(intervals)

if __name__ == "__main__":
  data = pullData()

  ints = helper(data)
  analyzeInts(data, ints)