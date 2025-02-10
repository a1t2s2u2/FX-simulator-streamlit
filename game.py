import random
import math
from datetime import datetime
import streamlit as st
import pandas as pd
import altair as alt

from state import load_state, save_state

# --- 市場更新・ニュース生成関連 ---

def generate_news():
    """
    ランダムにニュースイベントを選択し、価格変動倍率を生成する。
    幾何平均が1の場合は対数空間で一様サンプリング。
    """
    news_events = [
        {
            "message": "経済指標の発表により、市場は穏やかな動きを示しています。",
            "min": 1/1.02,
            "max": 1.02
        },
        {
            "message": "中央銀行の声明発表により、市場は安定しています。",
            "min": 1/1.03,
            "max": 1.03
        },
        {
            "message": "最新の雇用統計が好調で、市場に緩やかな上昇が見られます。",
            "min": 1/1.02,
            "max": 1.02
        },
        {
            "message": "一部金融機関の不祥事報道で、市場が大幅に下落。",
            "min": 0.75,
            "max": 0.95
        },
        {
            "message": "予想外のインフレ懸念！物価上昇により市場が急騰する兆し。",
            "min": 1.10,
            "max": 1.50
        },
        {
            "message": "政府の緊急市場安定化策発表で、市場は一時停滞後に回復。",
            "min": 1/1.05,
            "max": 1.05
        },
        {
            "message": "テロ事件の報道で市場に不安が広がり、一時的に激落。",
            "min": 0.65,
            "max": 0.85
        },
        {
            "message": "異常気象により農産物価格が急上昇。市場が活性化する動き。",
            "min": 1/1.20,
            "max": 1.20
        },
        {
            "message": "中央銀行のサプライズ政策変更で、市場が大きく変動中。",
            "min": 1/1.20,
            "max": 1.20
        },
        {
            "message": "伝説の猫ミーム登場！ネット上の爆笑が市場を大いに盛り上げる！",
            "min": 1/1.80,
            "max": 1.80
        },
        {
            "message": "猫ミーム2ギャラクシー登場！爆笑が市場をド派手に活性化！",
            "min": 0.333,
            "max": 3.0
        },
        {
            "message": "大規模なサイバー攻撃の懸念が広がり、市場が乱高下しています。",
            "min": 0.70,
            "max": 0.90
        },
        {
            "message": "小規模な隕石落下のニュースにより、市場にごくわずかな変動が見られます。",
            "min": 1/1.05,
            "max": 1.05
        }
    ]
    event = random.choice(news_events)
    if "min" in event and "max" in event:
        # 幾何平均が 1 に近い場合は対数空間でサンプリング
        if abs(event["min"] * event["max"] - 1) < 1e-6:
            multiplier = math.exp(random.uniform(math.log(event["min"]), math.log(event["max"])))
        else:
            multiplier = random.uniform(event["min"], event["max"])
    else:
        multiplier = 1.0
    return event["message"], multiplier

def update_market(state: dict) -> dict:
    """
    市場価格とニュースイベントを更新する（平均回帰付きモデル）。
    """
    market = state["market"]
    current_price = market["current_price"]

    if current_price < 1:
        new_price = random.uniform(1.0, 5.0)
    else:
        # 対数空間での平均回帰モデル
        target_price = 100.0
        theta = 0.05
        dt = 1
        sigma = 0.02
        z = random.gauss(0, 1)
        log_current = math.log(current_price)
        log_target = math.log(target_price)
        log_new = log_current + theta * (log_target - log_current) * dt + sigma * math.sqrt(dt) * z
        new_price = math.exp(log_new)
        # 突発的なジャンプ
        if random.random() < 0.2:
            jump_factor = random.uniform(0.8, 1.3)
            new_price *= jump_factor
        # ニュースイベント発生
        if random.random() < 0.2:
            news_message, news_multiplier = generate_news()
            new_price *= news_multiplier
            state["event"]["news_event"] = news_message
            state["event"]["news_multiplier"] = news_multiplier
            state["event"]["news_timestamp"] = datetime.now().timestamp()

    new_price = round(new_price, 2)
    market["current_price"] = new_price
    now = datetime.now().isoformat()
    market["history"].append({"timestamp": now, "price": new_price})
    if len(market["history"]) > 100:
        market["history"] = market["history"][-100:]
    state["market"] = market
    save_state(state)
    return state

# --- 注文処理関連 ---

def process_buy_order(username: str, user_data: dict, market: dict, state: dict) -> None:
    """
    ポジションがない場合の買い注文処理（株数指定）。
    """
    st.subheader("ポジションなし: 新規注文")
    current_price = market["current_price"]
    max_units = int(user_data["money"] // current_price)
    if max_units < 1:
        st.error("資金不足です。")
        return

    if "order_units" not in st.session_state:
        st.session_state.order_units = 1

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        order_units = st.number_input(
            "購入株数",
            min_value=1,
            max_value=max_units,
            value=st.session_state.order_units,
            step=1,
            key=f"order_units_input_{username}"
        )
        st.session_state.order_units = order_units
    with col2:
        if st.button("MAX BET", key=f"max_bet_{username}"):
            order_units = max_units
            cost = order_units * current_price
            user_data["money"] -= cost
            user_data["position"] = {
                "entry_price": current_price,
                "investment": cost,
                "stocks": order_units
            }
            st.success(
                f"MAX BET 購入成立！ エントリー価格: {current_price} 円, 購入金額: {cost} 円, 取得株数: {order_units} 株"
            )
            state["users"][username] = user_data
            save_state(state)
    with col3:
        if st.button("買う", key=f"buy_button_{username}"):
            cost = order_units * current_price
            if cost > user_data["money"]:
                st.error("資金が不足しています。")
            else:
                user_data["money"] -= cost
                user_data["position"] = {
                    "entry_price": current_price,
                    "investment": cost,
                    "stocks": order_units
                }
                st.success(
                    f"買い注文成立！ エントリー価格: {current_price} 円, 購入金額: {cost} 円, 取得株数: {order_units} 株"
                )
                state["users"][username] = user_data
                save_state(state)

def process_sell_order(username: str, user_data: dict, market: dict, state: dict) -> None:
    """
    保有中のポジションの売却注文処理（株数指定）。
    """
    pos = user_data["position"]
    st.subheader("保有中のポジション")
    st.write(f"エントリー価格: {pos['entry_price']} 円")
    st.write(f"購入株数: {pos['stocks']} 株")
    current_value = pos["stocks"] * market["current_price"]
    trade_pl = current_value - pos["investment"]
    st.write(f"現在トレード中の損益: {trade_pl:+.2f} 円")

    sell_units = st.number_input(
        "売却株数",
        min_value=1,
        max_value=pos["stocks"],
        value=pos["stocks"],
        step=1,
        key=f"sell_units_input_{username}"
    )
    if st.button("売る", key=f"sell_button_{username}"):
        if sell_units > pos["stocks"]:
            st.error("売却株数が購入株数を超えています。")
        else:
            fraction = sell_units / pos["stocks"]
            sold_investment = fraction * pos["investment"]
            sale_proceeds = sell_units * market["current_price"]
            profit = sale_proceeds - sold_investment
            st.success(
                f"売り注文成立！ 売却株数: {sell_units} 株, 売却価格: {market['current_price']} 円, 売却代金: {sale_proceeds:.2f} 円, 損益: {profit:+.2f} 円"
            )
            new_investment = pos["investment"] - sold_investment
            new_stocks = pos["stocks"] - sell_units
            user_data["money"] += sale_proceeds
            user_data["realized"] = user_data.get("realized", 0) + profit
            if new_stocks < 1e-6:
                user_data["position"] = None
            else:
                user_data["position"] = {
                    "entry_price": pos["entry_price"],
                    "investment": new_investment,
                    "stocks": new_stocks
                }
            state["users"][username] = user_data
            save_state(state)

# --- チャート・ニュース・ランキング表示関連 ---

def display_market_chart(state: dict, username: str = None) -> None:
    """
    市場履歴を Altair のラインチャートで表示する。
    ユーザーがポジションを持っていればエントリー価格の水平線を追加。
    """
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
    """
    最新のニュースイベントを表示する（発生から10秒間のみ表示）。
    """
    current_time = datetime.now().timestamp()
    if state["event"]["news_event"] is not None and (current_time - state["event"]["news_timestamp"] < 10):
        news_message = state["event"]["news_event"]
        news_multiplier = state["event"].get("news_multiplier", 1)
        percent_change = (news_multiplier - 1) * 100
        st.info(f"ニュース: {news_message} ({'+' if percent_change >= 0 else ''}{percent_change:.1f}%)")
    else:
        state["event"]["news_event"] = None

def display_ranking(state: dict, market: dict) -> None:
    """
    ユーザーの資産状況ランキングをテーブル表示する。
    （資金、保有株数、保有金額、トレード損益、合計額）
    """
    st.subheader("ランキング（資金・保有株数・保有金額・トレード損益・合計額）")
    ranking_data = []
    for user, info in state["users"].items():
        cash = info.get("money", 0)
        if info.get("position"):
            pos = info["position"]
            stocks = pos["stocks"]
            holding_value = stocks * market["current_price"]
            trade_pl = holding_value - pos["investment"]
        else:
            stocks = 0
            holding_value = 0
            trade_pl = 0
        total = cash + holding_value
        ranking_data.append({
            "ユーザー名": user,
            "資金": cash,
            "保有株数": stocks,
            "保有金額": holding_value,
            "トレード損益": trade_pl,
            "合計額": total
        })
    df_ranking = pd.DataFrame(ranking_data).sort_values("合計額", ascending=False)
    st.table(df_ranking)

# --- 状態初期化・定期更新処理 ---

def initialize_state_if_needed() -> dict:
    """
    状態が未初期化の場合は初期状態を作成して返す。
    """
    state = load_state()
    if not state:
        state = {
            "market": {"current_price": 100.0, "history": []},
            "users": {},
            "event": {"news_event": None, "news_multiplier": 1, "news_timestamp": 0}
        }
        save_state(state)
    return state

def scheduled_market_update():
    """
    APScheduler で定期実行する市場更新処理。
    """
    state = initialize_state_if_needed()
    state = update_market(state)
    save_state(state)
