from fastapi import APIRouter, Query

from app.models.ticker import (
    ActionsResponse,
    FinancialsResponse,
    HistoryRequest,
    HistoryResponse,
    HoldersResponse,
    Interval,
    NewsResponse,
    OptionsChainRequest,
    OptionsChainResponse,
    Period,
    QuoteResponse,
    RecommendationsResponse,
    TickerInfoResponse,
)
from app.services.yfinance_service import yfinance_service

router = APIRouter(tags=["ticker"])


@router.get(
    "/{symbol}",
    response_model=TickerInfoResponse,
    summary="Get ticker info",
    description="Get comprehensive information about a ticker symbol including company info, market data, and more.",
)
def get_ticker_info(symbol: str) -> TickerInfoResponse:
    return yfinance_service.get_info(symbol.upper())


@router.get(
    "/{symbol}/quote",
    response_model=QuoteResponse,
    summary="Get current quote",
    description="Get the current market quote for a ticker symbol.",
)
def get_quote(symbol: str) -> QuoteResponse:
    return yfinance_service.get_quote(symbol.upper())


@router.get(
    "/{symbol}/history",
    response_model=HistoryResponse,
    summary="Get historical data",
    description="Get historical OHLCV data for a ticker symbol.",
)
def get_history(
    symbol: str,
    period: Period | None = Query(default=Period.ONE_MONTH, description="Data period to download"),
    interval: Interval = Query(default=Interval.ONE_DAY, description="Data interval"),
    start: str | None = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end: str | None = Query(default=None, description="End date (YYYY-MM-DD)"),
    prepost: bool = Query(default=False, description="Include pre/post market data"),
    actions: bool = Query(default=True, description="Include dividends and splits"),
    auto_adjust: bool = Query(default=True, description="Adjust OHLC for splits"),
    back_adjust: bool = Query(default=False, description="Back-adjust data for splits"),
) -> HistoryResponse:
    request = HistoryRequest(
        period=period,
        interval=interval,
        start=start,
        end=end,
        prepost=prepost,
        actions=actions,
        auto_adjust=auto_adjust,
        back_adjust=back_adjust,
    )
    return yfinance_service.get_history(symbol.upper(), request)


@router.get(
    "/{symbol}/recommendations",
    response_model=RecommendationsResponse,
    summary="Get analyst recommendations",
    description="Get analyst recommendations and ratings for a ticker symbol.",
)
def get_recommendations(symbol: str) -> RecommendationsResponse:
    return yfinance_service.get_recommendations(symbol.upper())


@router.get(
    "/{symbol}/actions",
    response_model=ActionsResponse,
    summary="Get corporate actions",
    description="Get dividend and stock split history for a ticker symbol.",
)
def get_actions(symbol: str) -> ActionsResponse:
    return yfinance_service.get_actions(symbol.upper())


@router.get(
    "/{symbol}/news",
    response_model=NewsResponse,
    summary="Get news articles",
    description="Get recent news articles related to a ticker symbol.",
)
def get_news(symbol: str) -> NewsResponse:
    return yfinance_service.get_news(symbol.upper())


@router.get(
    "/{symbol}/financials",
    response_model=FinancialsResponse,
    summary="Get financial statements",
    description="Get income statement, balance sheet, and cash flow data.",
)
def get_financials(
    symbol: str,
    quarterly: bool = Query(default=False, description="Get quarterly data instead of annual"),
) -> FinancialsResponse:
    return yfinance_service.get_financials(symbol.upper(), quarterly=quarterly)


@router.get(
    "/{symbol}/holders",
    response_model=HoldersResponse,
    summary="Get holder information",
    description="Get major, institutional, and mutual fund holder information.",
)
def get_holders(symbol: str) -> HoldersResponse:
    return yfinance_service.get_holders(symbol.upper())


@router.get(
    "/{symbol}/options",
    response_model=OptionsChainResponse,
    summary="Get options chain",
    description="Get options chain data including calls and puts.",
)
def get_options(
    symbol: str,
    date: str | None = Query(default=None, description="Expiration date (YYYY-MM-DD)"),
) -> OptionsChainResponse:
    request = OptionsChainRequest(date=date)
    return yfinance_service.get_options(symbol.upper(), request)
