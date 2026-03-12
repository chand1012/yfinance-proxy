import math
from datetime import datetime, timezone
from typing import Any

import yfinance as yf
from fastapi import HTTPException

from app.models.ticker import (
    ActionsResponse,
    DividendAction,
    FinancialsResponse,
    HistoryDataPoint,
    HistoryRequest,
    HistoryResponse,
    HolderInfo,
    HoldersResponse,
    Interval,
    NewsArticle,
    NewsResponse,
    OptionContract,
    OptionsChainRequest,
    OptionsChainResponse,
    Period,
    QuoteResponse,
    Recommendation,
    RecommendationsResponse,
    SplitAction,
    TickerInfoResponse,
)


class YFinanceService:
    @staticmethod
    def _get_ticker(symbol: str) -> yf.Ticker:
        ticker = yf.Ticker(symbol)
        return ticker

    @staticmethod
    def _validate_ticker(ticker: yf.Ticker, symbol: str) -> None:
        try:
            info = ticker.info
            if not info or info.get("regularMarketPrice") is None and info.get("previousClose") is None:
                if info.get("trailingPegRatio") is None and info.get("symbol") is None:
                    raise HTTPException(status_code=404, detail=f"Ticker '{symbol}' not found")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Ticker '{symbol}' not found: {str(e)}")

    def get_info(self, symbol: str) -> TickerInfoResponse:
        ticker = self._get_ticker(symbol)
        self._validate_ticker(ticker, symbol)
        return TickerInfoResponse(symbol=symbol, info=ticker.info)

    def get_history(self, symbol: str, request: HistoryRequest) -> HistoryResponse:
        ticker = self._get_ticker(symbol)
        self._validate_ticker(ticker, symbol)

        kwargs: dict[str, Any] = {
            "interval": request.interval.value,
            "prepost": request.prepost,
            "actions": request.actions,
            "auto_adjust": request.auto_adjust,
            "back_adjust": request.back_adjust,
        }

        if request.start and request.end:
            kwargs["start"] = request.start
            kwargs["end"] = request.end
        elif request.period:
            kwargs["period"] = request.period.value

        df = ticker.history(**kwargs)

        data_points = []
        for index, row in df.iterrows():
            point = HistoryDataPoint(
                date=index.to_pydatetime(),
                open=row.get("Open"),
                high=row.get("High"),
                low=row.get("Low"),
                close=row.get("Close"),
                volume=int(row.get("Volume", 0)) if row.get("Volume") is not None else None,
                dividends=row.get("Dividends"),
                stock_splits=row.get("Stock Splits"),
            )
            data_points.append(point)

        return HistoryResponse(symbol=symbol, data=data_points)

    def get_recommendations(self, symbol: str) -> RecommendationsResponse:
        ticker = self._get_ticker(symbol)
        self._validate_ticker(ticker, symbol)

        recs = ticker.recommendations
        recommendations = []

        if recs is not None and not recs.empty:
            for index, row in recs.iterrows():
                rec = Recommendation(
                    date=index.to_pydatetime() if hasattr(index, "to_pydatetime") else index,
                    firm=row.get("Firm", ""),
                    to_grade=row.get("To Grade", ""),
                    from_grade=row.get("From Grade"),
                    action=row.get("Action", ""),
                )
                recommendations.append(rec)

        return RecommendationsResponse(symbol=symbol, recommendations=recommendations)

    def get_actions(self, symbol: str) -> ActionsResponse:
        ticker = self._get_ticker(symbol)
        self._validate_ticker(ticker, symbol)

        dividends = []
        divs = ticker.dividends
        if divs is not None and not divs.empty:
            for date, amount in divs.items():
                dividends.append(DividendAction(date=date.to_pydatetime(), amount=float(amount)))

        splits = []
        stock_splits = ticker.splits
        if stock_splits is not None and not stock_splits.empty:
            for date, ratio in stock_splits.items():
                splits.append(SplitAction(date=date.to_pydatetime(), ratio=float(ratio)))

        return ActionsResponse(symbol=symbol, dividends=dividends, splits=splits)

    def get_news(self, symbol: str) -> NewsResponse:
        ticker = self._get_ticker(symbol)
        self._validate_ticker(ticker, symbol)

        articles = []
        news = ticker.news
        if news:
            for item in news:
                article = NewsArticle(
                    uuid=item.get("uuid", ""),
                    title=item.get("title", ""),
                    publisher=item.get("publisher", ""),
                    link=item.get("link", ""),
                    provider_publish_time=datetime.fromtimestamp(item.get("providerPublishTime", 0), tz=timezone.utc),
                    type=item.get("type", ""),
                    related_tickers=item.get("relatedTickers", []),
                )
                articles.append(article)

        return NewsResponse(symbol=symbol, articles=articles)

    def get_financials(self, symbol: str, quarterly: bool = False) -> FinancialsResponse:
        ticker = self._get_ticker(symbol)
        self._validate_ticker(ticker, symbol)

        def df_to_dict(df) -> dict[str, Any] | None:
            if df is None or df.empty:
                return None
            result = {}
            for col in df.columns:
                col_key = col.isoformat() if hasattr(col, "isoformat") else str(col)
                result[col_key] = {}
                for idx, val in df[col].items():
                    if val is not None and not (isinstance(val, float) and val != val):
                        result[col_key][str(idx)] = val
            return result

        if quarterly:
            income = df_to_dict(ticker.quarterly_income_stmt)
            balance = df_to_dict(ticker.quarterly_balance_sheet)
            cash = df_to_dict(ticker.quarterly_cashflow)
        else:
            income = df_to_dict(ticker.income_stmt)
            balance = df_to_dict(ticker.balance_sheet)
            cash = df_to_dict(ticker.cashflow)

        return FinancialsResponse(
            symbol=symbol,
            income_statement=income,
            balance_sheet=balance,
            cash_flow=cash,
        )

    def get_holders(self, symbol: str) -> HoldersResponse:
        ticker = self._get_ticker(symbol)
        self._validate_ticker(ticker, symbol)

        major = None
        major_holders = ticker.major_holders
        if major_holders is not None and not major_holders.empty:
            major = {}
            for idx, row in major_holders.iterrows():
                major[str(row.iloc[1])] = row.iloc[0]

        def parse_holders(df) -> list[HolderInfo]:
            holders = []
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    holder = HolderInfo(
                        holder=row.get("Holder", ""),
                        shares=int(row.get("Shares", 0)) if row.get("Shares") else None,
                        date_reported=row.get("Date Reported"),
                        percent_out=row.get("% Out"),
                        value=row.get("Value"),
                    )
                    holders.append(holder)
            return holders

        return HoldersResponse(
            symbol=symbol,
            major_holders=major,
            institutional_holders=parse_holders(ticker.institutional_holders),
            mutual_fund_holders=parse_holders(ticker.mutualfund_holders),
        )

    def get_options(self, symbol: str, request: OptionsChainRequest) -> OptionsChainResponse:
        ticker = self._get_ticker(symbol)
        self._validate_ticker(ticker, symbol)

        expiration_dates = list(ticker.options)

        calls = []
        puts = []

        if expiration_dates:
            date = request.date if request.date else expiration_dates[0]
            if date not in expiration_dates:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid expiration date. Valid dates: {expiration_dates}",
                )

            chain = ticker.option_chain(date)

            def parse_contracts(df) -> list[OptionContract]:
                contracts = []
                if df is not None and not df.empty:
                    for _, row in df.iterrows():
                        contract = OptionContract(
                            contract_symbol=row.get("contractSymbol", ""),
                            last_trade_date=row.get("lastTradeDate"),
                            strike=row.get("strike", 0),
                            last_price=row.get("lastPrice"),
                            bid=row.get("bid"),
                            ask=row.get("ask"),
                            change=row.get("change"),
                            percent_change=row.get("percentChange"),
                            volume=int(row.get("volume", 0)) if (vol := row.get("volume")) and not math.isnan(vol) else None,
                            open_interest=int(row.get("openInterest", 0)) if (oi := row.get("openInterest")) and not math.isnan(oi) else None,
                            implied_volatility=row.get("impliedVolatility"),
                            in_the_money=row.get("inTheMoney"),
                        )
                        contracts.append(contract)
                return contracts

            calls = parse_contracts(chain.calls)
            puts = parse_contracts(chain.puts)

        return OptionsChainResponse(
            symbol=symbol,
            expiration_dates=expiration_dates,
            calls=calls,
            puts=puts,
        )

    def get_quote(self, symbol: str) -> QuoteResponse:
        ticker = self._get_ticker(symbol)
        self._validate_ticker(ticker, symbol)

        info = ticker.info
        return QuoteResponse(
            symbol=symbol,
            regular_market_price=info.get("regularMarketPrice"),
            regular_market_change=info.get("regularMarketChange"),
            regular_market_change_percent=info.get("regularMarketChangePercent"),
            regular_market_time=datetime.fromtimestamp(info["regularMarketTime"], tz=timezone.utc)
            if info.get("regularMarketTime")
            else None,
            regular_market_day_high=info.get("regularMarketDayHigh"),
            regular_market_day_low=info.get("regularMarketDayLow"),
            regular_market_volume=info.get("regularMarketVolume"),
            regular_market_previous_close=info.get("regularMarketPreviousClose"),
            regular_market_open=info.get("regularMarketOpen"),
            bid=info.get("bid"),
            ask=info.get("ask"),
            bid_size=info.get("bidSize"),
            ask_size=info.get("askSize"),
            market_cap=info.get("marketCap"),
            fifty_two_week_low=info.get("fiftyTwoWeekLow"),
            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
        )


yfinance_service = YFinanceService()
