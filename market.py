import random
import math
from datetime import datetime
from state import save_state

def generate_news() -> (str, float):
    """ランダムなニュースイベントを生成する"""
    news_events = [
        # 緩やかな変動イベント
        {
            "message": "経済指標の発表により、市場は穏やかな動きを示しています。",
            "multiplier": random.uniform(0.98, 1.02)
        },
        {
            "message": "中央銀行の声明発表により、市場は安定しています。",
            "multiplier": random.uniform(0.97, 1.03)
        },
        {
            "message": "最新の雇用統計が好調で、市場に緩やかな上昇が見られます。",
            "multiplier": random.uniform(0.98, 1.02)
        },
        # 大幅な変動イベント
        {
            "message": "一部金融機関の不祥事報道で、市場が一時的に下落。",
            "multiplier": random.uniform(0.7, 0.9)
        },
        {
            "message": "予想外のインフレ懸念！物価上昇により市場が急騰する兆し。",
            "multiplier": random.uniform(1.3, 1.7)
        },
        {
            "message": "政府の緊急市場安定化策発表で、市場は一時停滞後に回復。",
            "multiplier": random.uniform(0.95, 1.05)
        },
        {
            "message": "テロ事件の報道で市場に不安が広がり、一時的な下落が発生。",
            "multiplier": random.uniform(0.6, 0.8)
        },
        {
            "message": "異常気象により農産物価格が上昇、市場が活性化する動き。",
            "multiplier": random.uniform(1.1, 1.3)
        },
        {
            "message": "中央銀行のサプライズ政策変更で、市場が大きく変動中。",
            "multiplier": random.uniform(0.8, 1.2)
        },
        {
            "message": "伝説の猫ミーム登場！ネット上の爆笑が市場に穏やかな好影響を与える模様。",
            "multiplier": random.uniform(0.95, 1.05)
        },
        {
            "message": "猫ミーム2ギャラクシー登場！爆笑が一時的に市場を活性化！",
            "multiplier": random.uniform(1.1, 1.5)
        },
        {
            "message": "大規模なサイバー攻撃の懸念が広がり、市場が乱高下しています。",
            "multiplier": random.uniform(0.65, 0.85)
        },
        {
            "message": "小規模な隕石落下のニュースにより、市場にごくわずかな変動が見られます。",
            "multiplier": random.uniform(0.95, 1.05)
        }
    ]
    event = random.choice(news_events)
    return event["message"], event["multiplier"]

def update_market(state: dict) -> dict:
    """市場価格とニュースイベントを更新する（admin チェックなし）"""
    market = state["market"]
    current_price = market["current_price"]

    # GBM（幾何ブラウン運動）による基本変動
    dt = 1
    mu = 0.001
    sigma = 0.02
    z = random.gauss(0, 1)
    new_price = current_price * math.exp((mu - 0.5 * sigma**2) * dt + sigma * math.sqrt(dt) * z)

    # 5% の確率で突発的なジャンプ（±10% の変動）
    if random.random() < 0.05:
        jump_factor = random.uniform(0.9, 1.1)
        new_price *= jump_factor

    # 50% の確率でニュースイベントを発生させる
    if random.random() < 0.5:
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
