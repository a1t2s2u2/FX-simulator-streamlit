import altair as alt
import pandas as pd
from datetime import datetime
import streamlit as st

def display_market_chart(state: dict, username: str = None) -> None:
    """市場履歴を Altair のラインチャートで表示する"""
    market = state["market"]
    df_market = pd.DataFrame(market["history"])
    if "timestamp" in df_market.columns:
        df_market["timestamp"] = pd.to_datetime(df_market["timestamp"])
    else:
        df_market["timestamp"] = pd.date_range(end=datetime.now(), periods=len(df_market), freq="S")
    chart = alt.Chart(df_market).mark_line().encode(
        x='timestamp:T',
        y='price:Q'
    )
    # ユーザーがポジションを持っていれば、エントリー価格の赤い水平線を追加
    if username and username in state["users"]:
        user_data = state["users"][username]
        if user_data.get("position") is not None:
            entry_price = user_data["position"]["entry_price"]
            rule = alt.Chart(pd.DataFrame({'y': [entry_price]})).mark_rule(color='red', strokeWidth=2).encode(
                y='y:Q'
            )
            chart += rule
    st.altair_chart(chart, use_container_width=True)

def display_news(state: dict) -> None:
    """最新のニュースイベントを表示する"""
    current_time = datetime.now().timestamp()
    if state["event"]["news_event"] is not None and (current_time - state["event"]["news_timestamp"] < 10):
        news_message = state["event"]["news_event"]
        news_multiplier = state["event"].get("news_multiplier", 1)
        percent_change = (news_multiplier - 1) * 100
        st.info(f"ニュース: {news_message} ({'+' if percent_change >= 0 else ''}{percent_change:.1f}%)")
    else:
        state["event"]["news_event"] = None

def display_ranking(state: dict, market: dict) -> None:
    """ユーザーの資産状況ランキングをテーブル表示する"""
    st.subheader("ランキング（資金・保有金額・トレード損益・合計額）")
    ranking_data = []
    for user, info in state["users"].items():
        cash = info.get("money", 0)
        if info.get("position"):
            pos = info["position"]
            holding_value = pos["units"] * market["current_price"]
            trade_pl = holding_value - pos["order_amount"]
        else:
            holding_value = 0
            trade_pl = 0
        total = cash + holding_value
        ranking_data.append({
            "ユーザー名": user,
            "資金": cash,
            "保有金額": holding_value,
            "トレード損益": trade_pl,
            "合計額": total
        })
    df_ranking = pd.DataFrame(ranking_data).sort_values("合計額", ascending=False)
    st.table(df_ranking)
