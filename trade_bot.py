import random
import math
import time

import exbitron_exchange_api as exchange

###
### THIS IS A SIMPLE BOT TO MAKE TRADES ON exbitroncom ###
###

pair = 'NLEAD-USDT'
pairS = pair.split('-')

RandomActionEveryIters=3
MinRandomInterval=330
MaxRandomInterval=1230

# PUT HERE Your API Token created by Exbitron web app
exchange.TOKEN = ''

# Change settings for Buy action

BUY_PARAMS = {
    # Buy some NLEAD
    # - USDT
    
    'action': 'buy',
    'pair': pairS[0],
    'MinAmount': 10.0,
    'MaxAmount': 33.0,
    'MinPrice': 0.09,
    'MaxPrice': 0.12,
    'MinimumPossibleValue': 0.0001
}

# Change settings for Sell action

SELL_PARAMS = {
    # Sell some NLEAD
    # - NLEAD
    
    'action': 'sell',
    'pair': pairS[1],
    'MinAmount': 12.0,
    'MaxAmount': 34.0,
    'MinPrice': 0.09,
    'MaxPrice': 0.12,
    'MinimumPossibleValue': 0.0001
}


# This is the main app. Do not modify anything above this line.

def GetRandom(Min, Max, roundDe = -1):
    p=0

    while p < Min or p > Max:
        p = random.random() + random.randint(int(Min), int(Max))
    
    if roundDe>0:
        return round(p, roundDe)
    return p

def GetRandomAction():
    a=random.randint(0, 1)
    if a == 0:
        return BUY_PARAMS
    return SELL_PARAMS

def GetBalance(pair):
    if pair=='USDT':
        return 5.0
    return 50.0

def Trade(action, amount, price):
    order_status = exchange.Order(amount, pair, price, action['action'], "limit")
    if order_status==None or (order_status['status']!=True and order_status['order_status'] != 'pending' and order_status['order_status'] != 'closed'):
        return (None, None)
    
    return (amount, price) 

def TradeRandom(action):
    balance = GetBalance(action['pair'])

    MinPrice=action['MinPrice']
    MaxPrice=action['MaxPrice']

    MinAmount=action['MinAmount']
    MaxAmount=action['MaxAmount']
    
    #if MaxThsd>balance:
    #    MaxThsd=balance

    #    if MaxThsd <= MinThsd:
    #        MinThsd = action['MinimumPossibleValue']
    amount = GetRandom(MinAmount, MaxAmount, 4)
    price = GetRandom(MinPrice, MaxPrice, 4)

    order_status = exchange.Order(amount, pair, price, action['action'], "limit")
    if order_status==None or (order_status['status']!=True and order_status['order_status'] != 'open'):
        return (None, None)

    return (amount, price)

def ReverseAction(action):
    if action['action'] == 'buy':
        return SELL_PARAMS
    return BUY_PARAMS

if __name__ == '__main__':

    p = exchange.GetCoinGeckoHistoricalTrades('BTC-USDT')

    bal = exchange.Balances()

    iters = 1

    lastValues = []

    while True:

        orderbook = exchange.GetOrderBook(pair)
        if orderbook==None:
            continue
        sorted_bids = sorted(orderbook['bids'], key=lambda x: x[0], reverse=True)
        sorted_asks = sorted(orderbook['asks'], key=lambda x: x[0])

        BUY_PARAMS['MaxPrice']=float(sorted_asks[0][0])-BUY_PARAMS['MinimumPossibleValue']
        BUY_PARAMS['MinPrice']=float(sorted_bids[0][0])+BUY_PARAMS['MinimumPossibleValue']
        SELL_PARAMS['MaxPrice']=float(sorted_asks[0][0])-BUY_PARAMS['MinimumPossibleValue']
        SELL_PARAMS['MinPrice']=float(sorted_bids[0][0])+BUY_PARAMS['MinimumPossibleValue']
        
        s=random.randint(MinRandomInterval, MaxRandomInterval)

        if len(lastValues) > 0:
            la = lastValues[-1]
            action = ReverseAction(la['a'])
            (a, p) = Trade(action, la['amount'], la['price'])
            if a==None:
                continue
            del lastValues[-1]
            
        else:
            if iters % RandomActionEveryIters == 0 or len(lastValues) == 0:
                action=GetRandomAction()
                (a, p) =TradeRandom(action)
                if a==None:
                    continue
                lastValues.append({'a':action, 'amount':a, 'price': p})
                
                if action['action']=='buy':
                    s=10.0

        
        print(action)

        print(f'{int(time.time())}\t {a} \t{p}')
        print()
        

        iters += 1


        print(s)
        time.sleep(s)