import streamlit as st
from state import save_state

def process_buy_order(username: str, user_data: dict, market: dict, state: dict) -> None:
    """ポジションがない場合の買い注文処理"""
    st.subheader("ポジションなし: 新規注文")
    
    # セッション変数で注文金額を保持
    if "order_amount" not in st.session_state:
        st.session_state.order_amount = 100.0

    if st.session_state.order_amount > user_data["money"]:
        st.session_state.order_amount = user_data["money"]

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        order_amount = st.number_input(
            "取引金額（円）", 
            min_value=1.0, 
            max_value=float(user_data["money"]),
            value=st.session_state.order_amount, 
            step=1.0,
            key=f"order_amount_input_{username}"
        )
        st.session_state.order_amount = order_amount
    with col2:
        # MAX BET 押下時は全額購入
        if st.button("MAX BET", key=f"max_bet_{username}"):
            order_amount = user_data["money"]
            entry_price = market["current_price"]
            units = order_amount / entry_price
            user_data["money"] -= order_amount
            user_data["position"] = {
                "entry_price": entry_price,
                "order_amount": order_amount,
                "units": units
            }
            st.success(
                f"MAX BET 購入成立！ エントリー価格: {entry_price} 円, 注文金額: {order_amount} 円, 取得数量: {units:.4f} 単位"
            )
            state["users"][username] = user_data
            save_state(state)
    with col3:
        # 通常の「買う」ボタンによる処理
        if st.button("買う", key=f"buy_button_{username}"):
            if order_amount > user_data["money"]:
                st.error("取引金額が資金を超えています。")
            else:
                entry_price = market["current_price"]
                units = order_amount / entry_price
                user_data["money"] -= order_amount
                user_data["position"] = {
                    "entry_price": entry_price,
                    "order_amount": order_amount,
                    "units": units
                }
                st.success(
                    f"買い注文成立！ エントリー価格: {entry_price} 円, 注文金額: {order_amount} 円, 取得数量: {units:.4f} 単位"
                )
                state["users"][username] = user_data
                save_state(state)

def process_sell_order(username: str, user_data: dict, market: dict, state: dict) -> None:
    """保有中のポジションの売却注文処理"""
    pos = user_data["position"]
    st.subheader("保有中のポジション")
    st.write(f"エントリー価格: {pos['entry_price']} 円")
    st.write(f"注文金額: {pos['order_amount']} 円")
    st.write(f"取得数量: {pos['units']:.4f} 単位")
    current_value = pos["units"] * market["current_price"]
    trade_pl = current_value - pos["order_amount"]
    st.write(f"現在トレード中の損益: {trade_pl:+.2f} 円")

    sell_amount = st.number_input(
        "売却金額（円）", 
        min_value=1.0, 
        max_value=float(pos["order_amount"]),
        value=float(pos["order_amount"]), 
        step=1.0,
        key=f"sell_amount_input_{username}"
    )
    if st.button("売る", key=f"sell_button_{username}"):
        if sell_amount > pos["order_amount"]:
            st.error("売却金額が注文金額を超えています。")
        else:
            fraction = sell_amount / pos["order_amount"]
            sold_units = fraction * pos["units"]
            sale_proceeds = sold_units * market["current_price"]
            profit = sale_proceeds - sell_amount
            st.success(
                f"売り注文成立！ 売却数量: {sold_units:.4f} 単位, 売却価格: {market['current_price']} 円, 売却代金: {sale_proceeds:.2f} 円, 損益: {profit:+.2f} 円"
            )
            new_order_amount = pos["order_amount"] - sell_amount
            new_units = pos["units"] - sold_units
            user_data["money"] += sale_proceeds
            user_data["realized"] = user_data.get("realized", 0) + profit
            if new_order_amount < 1e-6:
                user_data["position"] = None
            else:
                user_data["position"] = {
                    "entry_price": pos["entry_price"],
                    "order_amount": new_order_amount,
                    "units": new_units
                }
            state["users"][username] = user_data
            save_state(state)
