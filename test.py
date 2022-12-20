# import requests
#
# url = "https://mobile.fmcsa.dot.gov/qc/services/carriers/2071774/?webKey=4ac96297a698eb309980998ca8d2f2c2594858ef"
#
# payload={}
# headers = {
#     'Accept': '*/*',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Accept-Language': 'en-US,en;q=0.8,ru;q=0.6',
#     'Cache-Control': 'no-cache',
#     'Connection': 'keep-alive',
#     'Host': 'mobile.fmcsa.dot.gov',
#     'User-Agent': 'PostmanRuntime/7.28.1'
# }
# session  = requests.Session()
# # session.headers =headers)
#
#
# response = session.get(url, headers=headers, data=payload)
#
# print(response.text)

# content = [
#         {
#             "id": {
#                 "dotNumber": 1021038,
#                 "operationClassId": 3
#             },
#             "operationClassDesc": "Private Property"
#         }
#     ]
#
# for i in content:
#     print(i.get('id').get('dotNumber'))



# import requests
#
# url = "https://ai.fmcsa.dot.gov/SMS/Tools/Downloads.aspx"
#
# payload={}
# headers = {
#   'Cookie': 'ASP.NET_SessionId=3hqp4kxwoopyg5mphcczats4'
# }
#
# response = requests.request("GET", url, headers=headers, data=payload)
#
# print(response.text)

import pandas as pd

def update_leads():
  # HAZMAT DATA UPDATE
  df = pd.read_csv('tmp/hazmat/SMS_AB_PassProperty_2022Oct.txt')
  for key, value in df.iterrows():
    print(key, value)
    # if key == 5:
    #   break
  print(df.columns)