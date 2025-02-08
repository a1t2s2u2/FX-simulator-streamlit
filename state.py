import json
import os
from datetime import datetime
import streamlit as st

STATE_FILE = "./state.json"

def load_state() -> dict:
    """JSON ファイルから状態を読み込み、存在しなければ初期状態を作成する"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"State 読み込みに失敗しました: {e}")
            return {}
    else:
        now = datetime.now().isoformat()
        state = {
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
        save_state(state)
        return state

def save_state(state: dict) -> None:
    """状態を JSON ファイルに保存する"""
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"State 保存に失敗しました: {e}")
