import ipfshttpclient

client = ipfshttpclient.connect()
res = client.add('C:/Users/vatsa/Desktop/Major Project/AI powered Real-Time Social Distance Monitoring System with Immutable Data Storage/events.txt')
print(res)
print(res['Hash'])