import sqlite3
import json
from datetime import datetime
import streamlit as st

DB_FILE = "state.db"

def init_db():
    """
    SQLite データベースと state テーブルを作成し、
    状態が未登録の場合は初期状態を挿入する。
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS state (
            id INTEGER PRIMARY KEY,
            state_data TEXT NOT NULL
        )
    ''')
    # state テーブルにデータが存在しなければ初期状態を登録
    c.execute("SELECT COUNT(*) FROM state")
    count = c.fetchone()[0]
    if count == 0:
        now = datetime.now().isoformat()
        initial_state = {
            "users": {},
            "market": {
                "current_price": 100.0,
                "history": [{"timestamp": now, "price": 100.0}]
            },
            "event": {
                "news_event": None,
                "news_multiplier": 1,
                "news_timestamp": 0
            }
        }
        c.execute("INSERT INTO state (id, state_data) VALUES (1, ?)", (json.dumps(initial_state),))
        conn.commit()
    conn.close()

def load_state() -> dict:
    """
    SQLite から状態を読み込む。
    状態が存在しなければ初期状態を作成する。
    """
    init_db()  # テーブル作成＆初期状態挿入
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT state_data FROM state WHERE id = 1")
        row = c.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
        else:
            st.error("State が見つかりませんでした。")
            return {}
    except Exception as e:
        st.error(f"State 読み込みに失敗しました: {e}")
        return {}

def save_state(state: dict) -> None:
    """
    状態を SQLite に保存する。（market.history は最新 100 件に制限）
    """
    # market.history を最新100件に制限
    if "market" in state and "history" in state["market"]:
        history = state["market"]["history"]
        if len(history) > 100:
            state["market"]["history"] = history[-100:]
    try:
        state_json = json.dumps(state, ensure_ascii=False, indent=2)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE state SET state_data = ? WHERE id = 1", (state_json,))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"State 保存に失敗しました: {e}")
