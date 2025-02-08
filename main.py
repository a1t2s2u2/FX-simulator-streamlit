import streamlit as st
from streamlit_autorefresh import st_autorefresh
from apscheduler.schedulers.background import BackgroundScheduler

from market import update_market
from state import load_state, save_state
from charts import display_market_chart, display_news, display_ranking
from orders import process_buy_order, process_sell_order

# 更新速度 ミリ秒単位
INTERVAL = 800

def initialize_state_if_needed() -> dict:
    """
    状態（state）の初期化または読み込みを行う。
    状態が存在しない場合は初期状態を作成する。
    """
    state = load_state()
    if not state:
        state = {
            "market": {"current_price": 100.0, "history": []},
            "users": {},
            "event": {}
        }
        save_state(state)
    return state

def scheduled_market_update():
    """
    バックグラウンドで定期的に実行される市場更新処理
    """
    state = initialize_state_if_needed()
    state = update_market(state)
    save_state(state)

@st.cache_resource
def get_scheduler():
    """
    バックグラウンドで市場更新処理を定期実行するスケジューラーを初期化する
    """
    scheduler = BackgroundScheduler()
    # INTERVAL はミリ秒なので、seconds=INTERVAL/1000 とする
    scheduler.add_job(scheduled_market_update, 'interval', seconds=INTERVAL/1000)
    scheduler.start()
    return scheduler

# アプリ起動時にスケジューラーを一度だけ初期化
scheduler = get_scheduler()

def main() -> None:
    # ページ自動更新（1秒ごとにページ再実行）
    st_autorefresh(interval=INTERVAL, limit=None, key="datarefresh")
    st.title("FX シミュレーションゲーム")

    # ユーザー名の入力（セッションステートで管理）
    if "username" not in st.session_state or st.session_state.username is None:
        username_input = st.text_input("ユーザー名を入力してください", value="")
        if username_input:
            st.session_state.username = username_input
            username = username_input
        else:
            st.info("ユーザー名を入力してください。")
            return
    else:
        username = st.session_state.username

    # 状態の初期化または読み込み
    state = initialize_state_if_needed()
    market = state["market"]

    # 市場チャート、ニュース、現在の為替レートの表示
    display_market_chart(state, username)
    display_news(state)
    st.write(f"現在の為替レート: **{market['current_price']} 円**")

    # ユーザー情報（初期資金 100,000 円）の初期化
    if username not in state["users"]:
        state["users"][username] = {"money": 100000.0, "position": None, "realized": 0.0}
        save_state(state)
    user_data = state["users"][username]
    st.write(f"ようこそ、{username}さん！ 現在の資金は **{user_data['money']:.2f} 円** です。")

    # 取引処理
    if user_data["money"] < 0:
        st.error("破産しました！ これ以上取引はできません。")
    else:
        if user_data["position"] is None:
            process_buy_order(username, user_data, market, state)
        else:
            process_sell_order(username, user_data, market, state)

    # ランキング表示
    display_ranking(state, market)

if __name__ == "__main__":
    main()
