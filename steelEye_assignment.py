from fastapi import FastAPI, Query
from typing import Union

import datetime as dt

from typing import Optional
from pydantic import BaseModel, Field

app = FastAPI()

class TradeDetails(BaseModel):
    buySellIndicator: str = Field(description="A value of BUY for buys, SELL for sells.")

    price: float = Field(description="The price of the Trade.")

    quantity: int = Field(description="The amount of units traded.")


class Trade(BaseModel):
    asset_class: Optional[str] = Field(alias="assetClass", default=None, description="The asset class of the instrument traded. E.g. Bond, Equity, FX...etc")

    counterparty: Optional[str] = Field(default=None, description="The counterparty the trade was executed with. May not always be available")

    instrument_id: str = Field(alias="instrumentId", description="The ISIN/ID of the instrument traded. E.g. TSLA, AAPL, AMZN...etc")

    instrument_name: str = Field(alias="instrumentName", description="The name of the instrument traded.")

    trade_date_time: dt.datetime = Field(alias="tradeDateTime", description="The date-time the Trade was executed")

    trade_details: TradeDetails = Field(alias="tradeDetails", description="The details of the trade, i.e. price, quantity")

    trade_id: str = Field(alias="tradeId", default=None, description="The unique ID of the trade")

    trader: str = Field(description="The name of the Trader")


TRADE_1= Trade(
    assetClass="Tech",
    tradeDetails=TradeDetails(price=100.0, quantity=10, buySellIndicator="SELL"),
    tradeId="1",
    trader="Shalu",
    instrumentId="1",
    instrumentName="Tata Elxsi",
    tradeDateTime= dt.datetime(2022, 12, 28, 23, 55, 59, 342380),
    counterparty="Pranay"
)
TRADE_2 = Trade(
    assetClass="Food",
    tradeDetails=TradeDetails(price=200.0, quantity=1, buySellIndicator="SELL"),
    tradeId="2",
    trader="Aman Chandel",
    instrumentId="2",
    instrumentName="Tata Consumer Products",
    tradeDateTime= dt.datetime(2022, 12, 28, 23, 54, 59, 342380),
    counterparty="Balaji"
)
TRADE_3 = Trade(
    assetClass="Automobile",
    tradeDetails=TradeDetails(price=3.14, quantity=5, buySellIndicator="BUY"),
    tradeId="3",
    trader="Shivani",
    instrumentId="3",
    instrumentName="Tata Automobiles",
    tradeDateTime= dt.datetime(2022, 12, 28, 23, 53, 59, 342380), 
    counterparty="Null"
)

MOCK_TRADE_DATABASE = {
    "1": TRADE_1,
    "2": TRADE_2,
    "3": TRADE_3,
}

# This section of code gives us the List of all the trades 
@app.get("/list-of-trades/")
def get_trade_list() -> list[Trade]:
        return list(MOCK_TRADE_DATABASE.values())

# This sectin of code fetch the trade data by using trade id
#  retrieving a single Trade by ID
@app.get("/trades/{trade_id}")
def get_trade_by_id(trade_id: str) -> Trade:
    if trade_id not in MOCK_TRADE_DATABASE:
        raise HTTPException(status_code=404)
    return MOCK_TRADE_DATABASE[trade_id]

# Searching By following fields 
@app.get("/searching-trades/")
def search_trades(search, search_by="trader"):
    if search is None:
        return list(MOCK_TRADE_DATABASE.values())

    if search_by == "trader":
        matching_trades = [
            trade for trade in MOCK_TRADE_DATABASE.values()
            if search in trade.trader
        ]
    elif search_by == "counterparty":
        matching_trades = [
            trade for trade in MOCK_TRADE_DATABASE.values()
            if search == trade.counterparty
        ]

    elif search_by == "intrumentId":
        matching_trades = [
            trade for trade in MOCK_TRADE_DATABASE.values()
            if search == trade.instrument_id
        ]

    elif search_by == "intrumentName":
        matching_trades = [
            trade for trade in MOCK_TRADE_DATABASE.values()
            if search == trade.instrument_name
        ]
    else:
        return []  # Invalid search criteria

    return matching_trades


# Advance Filtering
@app.get("/trades")
def fetch_trades(search: Optional[str] = None,
                 assetClass: Optional[str] = Query(None, description="Filter trades by asset class"),
                 end: Optional[str] = Query(None, description="Filter trades with tradeDateTime before this date"),
                 maxPrice: Optional[float] = Query(None, description="Filter trades with tradeDetails.price <= maxPrice"),
                 minPrice: Optional[float] = Query(None, description="Filter trades with tradeDetails.price >= minPrice"),
                 start: Optional[str] = Query(None, description="Filter trades with tradeDateTime after this date"),
                 tradeType: Optional[str] = Query(None, description="Filter trades by tradeDetails.buySellIndicator")):
    
    filtered_trades = []

    if assetClass or end or maxPrice is not None or minPrice is not None or start or tradeType:
        filtered_trades = [
            Trade(**trade) for trade in filtered_trades
            if (assetClass is None or trade.assetClass == assetClass)
            and (end is None or trade.tradeDateTime <= end)
            and (maxPrice is None or trade.tradeDetails['price'] <= maxPrice)
            and (minPrice is None or trade.tradeDetails['price'] >= minPrice)
            and (start is None or trade.tradeDateTime >= start)
            and (tradeType is None or trade.tradeDetails['buySellIndicator'] == tradeType)
        ]

    return filtered_trades


# Advance Filtering with Pagination and sorting on the list of trades
@app.get("/trades-with-pagination")
def fetch_trades_with_pagination(search: Optional[str] = None,
                 assetClass: Optional[str] = Query(None, description="Filter trades by asset class"),
                 end: Optional[str] = Query(None, description="Filter trades with tradeDateTime before this date"),
                 maxPrice: Optional[float] = Query(None, description="Filter trades with tradeDetails.price <= maxPrice"),
                 minPrice: Optional[float] = Query(None, description="Filter trades with tradeDetails.price >= minPrice"),
                 start: Optional[str] = Query(None, description="Filter trades with tradeDateTime after this date"),
                 tradeType: Optional[str] = Query(None, description="Filter trades by tradeDetails.buySellIndicator"),
                 page: Optional[int] = Query(1, description="Page number"),
                 limit: Optional[int] = Query(10, description="Number of trades per page"),
                 sort_by: Optional[str] = Query(None, description="Sort trades by a field"),
                 sort_order: Optional[str] = Query(None, description="Sort order ('asc' or 'desc')")):
    
    filtered_trades = []

    if assetClass or end or maxPrice is not None or minPrice is not None or start or tradeType:
        filtered_trades = [
            Trade(**trade) for trade in filtered_trades
            if (assetClass is None or trade.assetClass == assetClass)
            and (end is None or trade.tradeDateTime <= end)
            and (maxPrice is None or trade.tradeDetails['price'] <= maxPrice)
            and (minPrice is None or trade.tradeDetails['price'] >= minPrice)
            and (start is None or trade.tradeDateTime >= start)
            and (tradeType is None or trade.tradeDetails['buySellIndicator'] == tradeType)
        ]

    return filtered_trades
