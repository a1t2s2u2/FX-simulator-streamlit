import streamlit as st
from streamlit_autorefresh import st_autorefresh
from apscheduler.schedulers.background import BackgroundScheduler
from game import (
    initialize_state_if_needed, scheduled_market_update,
    process_buy_order, process_sell_order,
    display_market_chart, display_news, display_ranking
)
from state import save_state

# 更新間隔（ミリ秒単位）
INTERVAL = 800

@st.cache_resource
def get_scheduler():
    """
    バックグラウンドで市場更新処理を定期実行するスケジューラーを初期化する。
    """
    scheduler = BackgroundScheduler()
    # INTERVAL はミリ秒なので seconds=INTERVAL/1000 とする
    scheduler.add_job(scheduled_market_update, 'interval', seconds=INTERVAL/1000)
    scheduler.start()
    return scheduler

# アプリ起動時にスケジューラーを一度だけ初期化
scheduler = get_scheduler()

def main() -> None:
    # ページ自動更新（INTERVAL ごとにページ再実行）
    st_autorefresh(interval=INTERVAL, limit=None, key="datarefresh")
    st.title("株式シミュレーションゲーム")

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

    # 市場チャート、ニュース、現在の株価の表示
    display_market_chart(state, username)
    display_news(state)
    st.write(f"現在の株価: **{market['current_price']} 円**")

    # 新規ユーザーの場合は初期資金 100,000 円をセット
    if username not in state["users"]:
        state["users"][username] = {"money": 100000.0, "position": None, "realized": 0.0}
        save_state(state)
    user_data = state["users"][username]
    st.write(f"ようこそ、{username}さん！ 現在の資金は **{user_data['money']:.2f} 円** です。")
    if user_data.get("position"):
        st.write(f"現在の保有株数: {user_data['position']['stocks']} 株")

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
