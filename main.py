import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from state import load_state, save_state
from market import update_market_if_admin
from charts import display_market_chart, display_news, display_ranking
from orders import process_buy_order, process_sell_order

def main() -> None:
    # 自動更新（1秒ごとにページ再実行）
    st_autorefresh(interval=1000, limit=None, key="datarefresh")
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

    # 統一状態の読み込み
    state = load_state()
    if not state:
        st.error("State 読み込みに失敗しました。")
        st.stop()

    # admin の場合は市場更新を実施
    if username == "admin":
        state = update_market_if_admin(state)
    market = state["market"]

    # 市場チャート、ニュース、現在の為替レートの表示
    display_market_chart(state, username)
    display_news(state)
    st.write(f"現在の為替レート: **{market['current_price']} 円**")

    # ユーザー情報（初期資金は 100,000 円）を初期化
    if username not in state["users"]:
        state["users"][username] = {"money": 100000.0, "position": None, "realized": 0.0}
        save_state(state)
    user_data = state["users"][username]
    st.write(f"ようこそ、{username}さん！ 現在の資金は **{user_data['money']:.2f} 円** です。")

    if user_data["money"] < 0:
        st.error("破産しました！ これ以上取引はできません。")
    else:
        # ポジションの有無で注文処理を振り分ける
        if user_data["position"] is None:
            process_buy_order(username, user_data, market, state)
        else:
            process_sell_order(username, user_data, market, state)

    # ランキング表示
    display_ranking(state, market)

if __name__ == "__main__":
    main()
