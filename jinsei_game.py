
# 人生ゲームのロジック
import random

# プレイヤーの初期ステータス
INITIAL_PLAYER_STATUS = {
    "happiness": 50,  # 幸福度
    "money": 50,      # お金
}

# ランダムイベント定義
RANDOM_EVENTS = [
    {
        "name": "友達から遊びに誘われた",
        "description": "友達から突然遊びに誘われました！",
        "effects": {"happiness": 10, "money": -5}
    },
    {
        "name": "風邪をひいてしまった",
        "description": "体調を崩してしまいました...",
        "effects": {"happiness": -15, "money": -10}
    },
    {
        "name": "お小遣いを拾った",
        "description": "道でお金を拾いました！ラッキー！",
        "effects": {"money": 20, "happiness": 5}
    },
    {
        "name": "良い本に出会った",
        "description": "図書館で素晴らしい本を発見しました。",
        "effects": {"happiness": 15, "money": -3}
    },
    {
        "name": "散歩を始めた",
        "description": "最近散歩を始めて、気分がよくなりました。",
        "effects": {"happiness": 10}
    },
    {
        "name": "思わぬ出費",
        "description": "急な出費が発生してしまいました...",
        "effects": {"money": -30, "happiness": -10}
    },
    {
        "name": "新しい趣味を発見",
        "description": "新しい趣味を見つけて夢中になっています！",
        "effects": {"happiness": 20, "money": -5}
    },
    {
        "name": "親切な人に出会った",
        "description": "困っている時に親切な人に助けてもらいました。",
        "effects": {"happiness": 15}
    }
]

# ゲームのフェーズとイベント
GAME_PHASES = {
    "childhood": {
        "name": "幼少期",
        "description": "あなたは小学生です。放課後の過ごし方を選んでください。",
        "choices": [
            {
                "text": "友達と外で遊ぶ",
                "cost": 5,
                "effects": {"happiness": 15}
            },
            {
                "text": "家で勉強をする（お小遣い+10万円）",
                "cost": 0,
                "effects": {"happiness": -5, "money": 10}
            },
            {
                "text": "ゲームをして過ごす",
                "cost": 10,
                "effects": {"happiness": 10}
            }
        ]
    },
    "teenager": {
        "name": "思春期",
        "description": "中学生になりました。部活動を選んでください。",
        "choices": [
            {
                "text": "運動部に入る",
                "cost": 15,
                "effects": {"happiness": 20}
            },
            {
                "text": "文化部に入る",
                "cost": 8,
                "effects": {"happiness": 15}
            },
            {
                "text": "帰宅部でアルバイトをする（+20万円）",
                "cost": 0,
                "effects": {"happiness": 5, "money": 20}
            }
        ]
    },
    "high_school": {
        "name": "高校時代",
        "description": "高校生活が始まりました。進路について考える時期です。",
        "choices": [
            {
                "text": "大学受験に集中する（塾講師バイト+15万円）",
                "cost": 30,
                "effects": {"happiness": -10, "money": 15}
            },
            {
                "text": "アルバイトを始める（+30万円）",
                "cost": 0,
                "effects": {"money": 30, "happiness": 5}
            },
            {
                "text": "恋愛を楽しむ",
                "cost": 20,
                "effects": {"happiness": 25, "money": -10}
            }
        ]
    },
    "university": {
        "name": "大学時代",
        "description": "大学生になりました。どのように過ごしますか？",
        "choices": [
            {
                "text": "勉強に専念する（奨学金+30万円）",
                "cost": 20,
                "effects": {"happiness": 5, "money": 30}
            },
            {
                "text": "サークル活動を楽しむ（-15万円）",
                "cost": 25,
                "effects": {"happiness": 25, "money": -15}
            },
            {
                "text": "長期アルバイトをする（+50万円）",
                "cost": 0,
                "effects": {"money": 50, "happiness": -5}
            }
        ]
    },
    "young_adult": {
        "name": "社会人デビュー",
        "description": "社会人になりました。最初の仕事を選んでください。",
        "choices": [
            {
                "text": "大企業に就職する（+80万円）",
                "cost": 50,
                "effects": {"money": 80, "happiness": 10}
            },
            {
                "text": "ベンチャー企業で挑戦する（+40万円）",
                "cost": 20,
                "effects": {"money": 40, "happiness": 20}
            },
            {
                "text": "フリーランスとして独立する（+20万円）",
                "cost": 30,
                "effects": {"money": 20, "happiness": 25}
            }
        ]
    },
    "career": {
        "name": "キャリア形成期",
        "description": "仕事に慣れてきました。今後のキャリアをどう積みますか？",
        "choices": [
            {
                "text": "スキルアップのため転職する（+60万円）",
                "cost": 40,
                "effects": {"money": 60, "happiness": 15}
            },
            {
                "text": "現在の会社で昇進を目指す（+100万円）",
                "cost": 10,
                "effects": {"money": 100, "happiness": 5}
            },
            {
                "text": "起業に挑戦する（-50万円）",
                "cost": 80,
                "effects": {"money": -50, "happiness": 30}
            }
        ]
    }
}


def apply_effects(player_status, effects):
    """プレイヤーのステータスにエフェクトを適用する"""
    new_status = player_status.copy()
    for stat, change in effects.items():
        new_status[stat] = max(0, new_status[stat] + change)  # 0未満にならないようにする
    return new_status


def get_random_event():
    """ランダムイベントを30%の確率で発生させる"""
    if random.random() < 0.3:  # 30%の確率
        return random.choice(RANDOM_EVENTS)
    return None


def format_effects(effects):
    """効果を読みやすい文字列に変換する"""
    effect_texts = []
    status_names = {
        "happiness": "幸福度",
        "money": "お金"
    }
    
    for stat, change in effects.items():
        if change != 0:
            name = status_names.get(stat, stat)
            if change > 0:
                effect_texts.append(f"{name}+{change}")
            else:
                effect_texts.append(f"{name}{change}")
    
    return "、".join(effect_texts) if effect_texts else "変化なし"


def display_result(final_status):
    """最終結果を表示する（コンソール用）"""
    print("\n" + "="*50)
    print("人生ゲーム 最終結果")
    print("="*50)
    print(f"幸福度: {final_status['happiness']}")
    print(f"お金: {final_status['money']}万円")
    print("="*50)
    
    # 総評
    if final_status["happiness"] >= 80:
        print("とても充実した、素晴らしい人生でしたね！")
    elif final_status["happiness"] >= 60:
        print("なかなか良い人生だったのではないでしょうか。")
    elif final_status["happiness"] <= 20:
        print("少し大変な人生だったかもしれません。")
    
    if final_status["money"] >= 300:
        print("経済的に大成功を収めました。賢い選択が光りましたね。")
    elif final_status["money"] <= 50:
        print("お金の使い方が少し荒かったようです…。計画的な支出を心がけましょう。")
