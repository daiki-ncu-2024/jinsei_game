from flask import Flask, render_template, request, redirect, url_for, session
import os

# ゲームのロジックをインポート
from jinsei_game import INITIAL_PLAYER_STATUS, GAME_PHASES, apply_effects, display_result, get_random_event, format_effects

app = Flask(__name__)
# セッションを使うために秘密鍵を設定
app.secret_key = os.urandom(24)

# テンプレートでformat_effects関数を使えるようにする
app.jinja_env.globals.update(format_effects=format_effects)


@app.route('/')
def index():
    """ウェルカム画面。前回の結果があれば表示する。"""
    # 前回の結果を取得（もしあれば）
    previous_result = session.get('previous_result', None)
    return render_template('welcome.html', previous_result=previous_result)


@app.route('/start_game', methods=['GET', 'POST'])
def start_game():
    """ゲームを開始。セッションをクリアしてステータスを初期化する。"""
    if request.method == 'POST':
        # 難易度を取得
        difficulty = request.form.get('difficulty', 'standard')
        
        # セッションをクリア（前回の選択結果などを削除）
        session.clear()
        session['player_status'] = INITIAL_PLAYER_STATUS.copy()
        session['phase_keys'] = list(GAME_PHASES.keys())
        session['current_phase_index'] = 0
        
        # 難易度に応じて目標設定
        if difficulty == 'easy':
            session['happiness_target'] = 90
        elif difficulty == 'standard':
            session['happiness_target'] = 120
        elif difficulty == 'hard':
            session['happiness_target'] = 150
        else:
            session['happiness_target'] = 120  # デフォルト
            
        session['difficulty'] = difficulty
        return redirect(url_for('game_phase'))
    else:
        # GETリクエストの場合は従来通り（後方互換性のため）
        session.clear()
        session['player_status'] = INITIAL_PLAYER_STATUS.copy()
        session['phase_keys'] = list(GAME_PHASES.keys())
        session['current_phase_index'] = 0
        session['happiness_target'] = 120  # デフォルト
        session['difficulty'] = 'standard'
        return redirect(url_for('game_phase'))


@app.route('/game')
def game_phase():
    """各ゲームフェーズの画面を表示する。"""
    phase_index = session.get('current_phase_index', 0)
    phase_keys = session.get('phase_keys', [])

    if phase_index >= len(phase_keys):
        return redirect(url_for('result'))

    current_phase_key = phase_keys[phase_index]
    phase_data = GAME_PHASES[current_phase_key]
    player_status = session.get('player_status', INITIAL_PLAYER_STATUS.copy())
    
    # ランダムイベント情報を取得して削除（一度だけ表示）
    last_random_event = session.pop('last_random_event', None)
    
    # 前回の選択効果情報を取得して削除（一度だけ表示）
    last_choice_effects = session.pop('last_choice_effects', None)

    return render_template('index.html',
                           player_status=player_status,
                           phase_data=phase_data,
                           phase_name=phase_data['name'],
                           current_phase_number=phase_index + 1,
                           random_event=last_random_event,
                           choice_effects=last_choice_effects,
                           happiness_target=session.get('happiness_target', 80))


@app.route('/choose', methods=['POST'])
def choose():
    """プレイヤーの選択を処理し、ステータスを更新する。"""
    phase_index = session.get('current_phase_index', 0)
    phase_keys = session.get('phase_keys', [])
    current_phase_key = phase_keys[phase_index]
    phase_data = GAME_PHASES[current_phase_key]
    player_status = session.get('player_status')

    choice_index = int(request.form['choice']) - 1
    chosen_option = phase_data["choices"][choice_index]
    cost = chosen_option.get("cost", 0)
    effects = chosen_option["effects"]

    # コストチェック
    if player_status["money"] < cost:
        # 所持金が足りない場合は何もしないで戻る
        return redirect(url_for('game_phase'))

    # コストを適用
    if cost > 0:
        player_status["money"] -= cost

    # 選択の効果を記録
    choice_effects = {
        "choice_text": chosen_option["text"],
        "cost": cost,
        "effects": effects
    }

    # ステータスを更新
    player_status = apply_effects(player_status, effects)

    # ランダムイベントの発生チェック
    random_event = get_random_event()
    if random_event:
        # ランダムイベントのエフェクトも適用
        player_status = apply_effects(player_status, random_event["effects"])
        # ランダムイベント情報をセッションに保存（次の画面で表示するため）
        session['last_random_event'] = random_event

    # 選択の効果情報をセッションに保存
    session['last_choice_effects'] = choice_effects

    session['player_status'] = player_status

    # 次のフェーズへ
    session['current_phase_index'] = phase_index + 1

    return redirect(url_for('game_phase'))


@app.route('/result')
def result():
    """ゲームの最終結果を表示する。"""
    final_status = session.get('player_status', {})

    # 幸福度に基づく複数エンディングシステム
    happiness = final_status.get("happiness", 0)
    money = final_status.get("money", 0)
    
    # メインエンディング（幸福度ベース）
    main_ending = ""
    ending_title = ""
    
    if happiness >= 100:
        ending_title = "🌟 完璧な人生エンディング"
        main_ending = "あなたは完璧な人生を歩みました！すべての選択が最高の結果をもたらし、これ以上ない幸せを手に入れました。人生の勝利者です！"
    elif happiness >= 90:
        ending_title = "✨ 理想的な人生エンディング"
        main_ending = "素晴らしい人生を送ることができました！多くの困難を乗り越え、理想に近い生活を実現しました。周りの人々もあなたの生き方を尊敬しています。"
    elif happiness >= 80:
        ending_title = "😊 充実した人生エンディング"
        main_ending = "とても充実した人生でした！いくつかの挫折もありましたが、それを乗り越えて成長し、満足のいく人生を築き上げました。"
    elif happiness >= 60:
        ending_title = "😌 平凡な人生エンディング"
        main_ending = "平凡ながらも安定した人生を送ることができました。大きな成功はありませんでしたが、それなりに満足のいく日々でした。"
    elif happiness >= 40:
        ending_title = "😐 普通の人生エンディング"
        main_ending = "可もなく不可もない、普通の人生でした。もう少し積極的な選択をしていれば、違った結果になったかもしれません。"
    elif happiness >= 20:
        ending_title = "😔 苦労の多い人生エンディング"
        main_ending = "多くの困難に直面した人生でした。辛い時期もありましたが、それでも諦めずに歩み続けたあなたの強さは素晴らしいです。"
    else:
        ending_title = "😞 試練の人生エンディング"
        main_ending = "非常に厳しい人生でした。多くの挑戦と失敗を経験しましたが、それもまた人生の一部です。次回はもっと良い選択ができるでしょう。"
    
    # 追加の評価コメント
    additional_comments = []
    
    if money >= 400:
        additional_comments.append("💰 大富豪の称号を獲得！経済的に大成功を収めました。")
    elif money >= 300:
        additional_comments.append("💎 お金持ちの称号を獲得！経済的に成功しました。")
    elif money <= 50:
        additional_comments.append("💸 お金の管理に苦労しました。計画的な支出を心がけましょう。")
    
    # 特別な組み合わせエンディング
    if happiness >= 80 and money >= 300:
        ending_title = "👑 完全勝利エンディング"
        main_ending = "幸福と富の両方を手に入れました！バランスの取れた素晴らしい人生を送ることができました。真の勝利者です！"

    # 目標達成判定
    happiness_target = session.get('happiness_target', 80)
    difficulty = session.get('difficulty', 'standard')
    target_achieved = happiness >= happiness_target
    
    # 難易度名を取得
    difficulty_names = {
        'easy': 'イージーモード',
        'standard': 'スタンダードモード',
        'hard': 'ハードモード'
    }
    difficulty_name = difficulty_names.get(difficulty, 'スタンダードモード')
    
    # 前回の結果をセッションに保存
    session['previous_result'] = {
        'happiness': happiness,
        'money': money,
        'ending_title': ending_title,
        'target_achieved': target_achieved,
        'difficulty': difficulty_name
    }
    
    return render_template('result.html',
                           final_status=final_status,
                           ending_title=ending_title,
                           main_ending=main_ending,
                           additional_comments=additional_comments,
                           happiness_target=happiness_target,
                           target_achieved=target_achieved,
                           difficulty_name=difficulty_name)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
