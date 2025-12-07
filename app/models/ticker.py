from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Interval(str, Enum):
    ONE_MINUTE = "1m"
    TWO_MINUTES = "2m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    SIXTY_MINUTES = "60m"
    NINETY_MINUTES = "90m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_WEEK = "1wk"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"


class Period(str, Enum):
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"
    TEN_YEARS = "10y"
    YTD = "ytd"
    MAX = "max"


class TickerInfoResponse(BaseModel):
    symbol: str
    info: dict[str, Any]


class HistoryRequest(BaseModel):
    period: Period | None = Field(default=Period.ONE_MONTH, description="Data period to download")
    interval: Interval = Field(default=Interval.ONE_DAY, description="Data interval")
    start: str | None = Field(default=None, description="Start date string (YYYY-MM-DD)")
    end: str | None = Field(default=None, description="End date string (YYYY-MM-DD)")
    prepost: bool = Field(default=False, description="Include pre and post market data")
    actions: bool = Field(default=True, description="Include dividends and stock splits")
    auto_adjust: bool = Field(default=True, description="Adjust OHLC for splits")
    back_adjust: bool = Field(default=False, description="Back-adjust data for splits")


class HistoryDataPoint(BaseModel):
    date: datetime
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: int | None = None
    dividends: float | None = None
    stock_splits: float | None = None


class HistoryResponse(BaseModel):
    symbol: str
    data: list[HistoryDataPoint]


class Recommendation(BaseModel):
    date: datetime
    firm: str
    to_grade: str
    from_grade: str | None = None
    action: str


class RecommendationsResponse(BaseModel):
    symbol: str
    recommendations: list[Recommendation]


class DividendAction(BaseModel):
    date: datetime
    amount: float


class SplitAction(BaseModel):
    date: datetime
    ratio: float


class ActionsResponse(BaseModel):
    symbol: str
    dividends: list[DividendAction]
    splits: list[SplitAction]


class NewsArticle(BaseModel):
    uuid: str
    title: str
    publisher: str
    link: str
    provider_publish_time: datetime
    type: str
    related_tickers: list[str] = Field(default_factory=list)


class NewsResponse(BaseModel):
    symbol: str
    articles: list[NewsArticle]


class FinancialsResponse(BaseModel):
    symbol: str
    income_statement: dict[str, Any] | None = None
    balance_sheet: dict[str, Any] | None = None
    cash_flow: dict[str, Any] | None = None


class HolderInfo(BaseModel):
    holder: str
    shares: int | None = None
    date_reported: datetime | None = None
    percent_out: float | None = None
    value: float | None = None


class HoldersResponse(BaseModel):
    symbol: str
    major_holders: dict[str, Any] | None = None
    institutional_holders: list[HolderInfo] = Field(default_factory=list)
    mutual_fund_holders: list[HolderInfo] = Field(default_factory=list)


class OptionsChainRequest(BaseModel):
    date: str | None = Field(default=None, description="Expiration date (YYYY-MM-DD)")


class OptionContract(BaseModel):
    contract_symbol: str
    last_trade_date: datetime | None = None
    strike: float
    last_price: float | None = None
    bid: float | None = None
    ask: float | None = None
    change: float | None = None
    percent_change: float | None = None
    volume: int | None = None
    open_interest: int | None = None
    implied_volatility: float | None = None
    in_the_money: bool | None = None


class OptionsChainResponse(BaseModel):
    symbol: str
    expiration_dates: list[str]
    calls: list[OptionContract] = Field(default_factory=list)
    puts: list[OptionContract] = Field(default_factory=list)


class QuoteResponse(BaseModel):
    symbol: str
    regular_market_price: float | None = None
    regular_market_change: float | None = None
    regular_market_change_percent: float | None = None
    regular_market_time: datetime | None = None
    regular_market_day_high: float | None = None
    regular_market_day_low: float | None = None
    regular_market_volume: int | None = None
    regular_market_previous_close: float | None = None
    regular_market_open: float | None = None
    bid: float | None = None
    ask: float | None = None
    bid_size: int | None = None
    ask_size: int | None = None
    market_cap: int | None = None
    fifty_two_week_low: float | None = None
    fifty_two_week_high: float | None = None


class ErrorResponse(BaseModel):
    detail: str
    symbol: str | None = None
