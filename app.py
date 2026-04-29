from flask import Flask, jsonify, request, render_template_string
from datetime import datetime

app = Flask(__name__)

# --- In-memory database ---

character = {
    "name": "Герой",
    "level": 1,
    "xp": 0,
    "stats": {"strength": 1, "intelligence": 1, "discipline": 1, "charisma": 1},
}

habits = [
    {"id": 1, "title": "Утренняя зарядка", "description": "15 минут упражнений", "stat": "strength", "xp_reward": 15, "streak": 0, "last_completed": None},
    {"id": 2, "title": "Чтение книги", "description": "30 минут чтения", "stat": "intelligence", "xp_reward": 15, "streak": 0, "last_completed": None},
]

quests = [
    {"id": 1, "title": "Пробежать 5 км", "description": "Первый серьёзный забег", "stat": "strength", "difficulty": "medium", "xp_reward": 25, "completed": False},
    {"id": 2, "title": "Пройти курс по программированию", "description": "Завершить все модули", "stat": "intelligence", "difficulty": "hard", "xp_reward": 50, "completed": False},
]

next_habit_id = 3
next_quest_id = 3
adventure_log = []

DIFFICULTY_XP = {"easy": 10, "medium": 25, "hard": 50}
STAT_ICONS = {"strength": "💪", "intelligence": "🧠", "discipline": "🎯", "charisma": "✨"}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Life RPG</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0f0e17;--card:#1a1932;--accent:#ff8906;--green:#2cb67d;--text:#fffffe;--muted:#94a1b2;--border:#2a2950;--danger:#e53170}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
.app{max-width:640px;margin:0 auto;padding:20px 16px 40px}
header{text-align:center;padding:30px 0 20px}
header h1{font-size:2rem;background:linear-gradient(135deg,var(--accent),var(--danger));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.subtitle{color:var(--muted);margin-top:4px}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:24px;margin-bottom:20px}
.char-header{display:flex;align-items:center;gap:16px;margin-bottom:16px}
.avatar{width:60px;height:60px;background:linear-gradient(135deg,var(--accent),var(--danger));border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.8rem}
.level-badge{display:inline-block;background:rgba(255,137,6,.15);color:var(--accent);padding:2px 10px;border-radius:20px;font-size:.85rem;font-weight:600;margin-top:4px}
.xp-wrap{background:rgba(255,255,255,.08);border-radius:20px;height:22px;position:relative;overflow:hidden;margin-bottom:16px}
.xp-fill{background:linear-gradient(90deg,var(--green),#05c46b);height:100%;border-radius:20px;transition:width .5s}
.xp-label{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:.72rem;font-weight:600;text-shadow:0 1px 3px rgba(0,0,0,.5)}
.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}
.stat{background:rgba(255,255,255,.05);border-radius:10px;padding:10px 12px;display:flex;align-items:center;gap:8px}
.stat-name{flex:1;font-size:.82rem;color:var(--muted)}
.stat-val{font-size:1.1rem;font-weight:700;color:var(--accent)}
.sec-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.sec-header h2{font-size:1.1rem}
section{margin-bottom:20px}
.item{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:8px;display:flex;align-items:center;gap:12px}
.item-icon{width:40px;height:40px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0}
.strength{background:rgba(239,68,68,.2)}.intelligence{background:rgba(59,130,246,.2)}.discipline{background:rgba(234,179,8,.2)}.charisma{background:rgba(168,85,247,.2)}
.item-body{flex:1;min-width:0}
.item-title{font-weight:600;font-size:.9rem}
.item-desc{font-size:.78rem;color:var(--muted);margin-top:2px}
.item-streak{font-size:.72rem;color:var(--accent);margin-top:2px}
.item-xp{font-size:.8rem;font-weight:600;color:var(--green);white-space:nowrap}
.done{opacity:.5}
.done .item-title{text-decoration:line-through}
.btn{border:none;padding:7px 14px;border-radius:8px;font-size:.88rem;font-weight:600;cursor:pointer;transition:all .2s}
.btn-orange{background:var(--accent);color:var(--bg)}
.btn-green{background:var(--green);color:#fff;font-size:.75rem;padding:5px 10px;margin-left:auto;flex-shrink:0}
.btn-green:disabled{opacity:.4;cursor:default}
.empty{text-align:center;color:var(--muted);padding:16px;font-size:.88rem}
.log-list{max-height:180px;overflow-y:auto}
.log-item{padding:6px 10px;border-left:3px solid var(--accent);margin-bottom:5px;font-size:.82rem;color:var(--muted);background:rgba(255,255,255,.03);border-radius:0 7px 7px 0}
.log-time{font-size:.68rem;opacity:.6}
.modal{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);backdrop-filter:blur(4px);z-index:100;justify-content:center;align-items:center}
.modal.open{display:flex}
.modal-box{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:24px;width:90%;max-width:400px}
.modal-box h3{margin-bottom:16px}
.fg{margin-bottom:12px}
.fg label{display:block;font-size:.82rem;color:var(--muted);margin-bottom:5px}
.fg input,.fg select{width:100%;padding:9px 11px;background:rgba(255,255,255,.06);border:1px solid var(--border);border-radius:8px;color:var(--text);font-size:.9rem;outline:none}
.fg input:focus,.fg select:focus{border-color:var(--accent)}
.fg select option{background:var(--card)}
.form-btns{display:flex;gap:8px;justify-content:flex-end;margin-top:16px}
.btn-cancel{background:transparent;color:var(--muted);border:1px solid var(--border)}
</style>
</head>
<body>
<div class="app">
  <header>
    <h1>⚔️ Life RPG</h1>
    <p class="subtitle">Геймификация реальной жизни — Railway Edition</p>
  </header>

  <div class="card">
    <div class="char-header">
      <div class="avatar">🧙</div>
      <div>
        <div style="font-size:1.2rem;font-weight:700">{{ char.name }}</div>
        <div class="level-badge">Уровень {{ char.level }}</div>
      </div>
    </div>
    <div class="xp-wrap">
      <div class="xp-fill" style="width:{{ xp_pct }}%"></div>
      <span class="xp-label">{{ char.xp }} / {{ xp_needed }} XP</span>
    </div>
    <div class="stats">
      {% for key, icon in [('strength','💪'),('intelligence','🧠'),('discipline','🎯'),('charisma','✨')] %}
      <div class="stat">
        <span style="font-size:1.3rem">{{ icon }}</span>
        <span class="stat-name">{{ stat_names[key] }}</span>
        <span class="stat-val">{{ char.stats[key] }}</span>
      </div>
      {% endfor %}
    </div>
  </div>

  <section>
    <div class="sec-header">
      <h2>🔄 Привычки</h2>
      <button class="btn btn-orange" onclick="openModal('habit')">+ Добавить</button>
    </div>
    {% if habits %}
      {% for h in habits %}
      <div class="item">
        <div class="item-icon {{ h.stat }}">{{ stat_icons[h.stat] }}</div>
        <div class="item-body">
          <div class="item-title">{{ h.title }}</div>
          <div class="item-desc">{{ h.description }}</div>
          <div class="item-streak">🔥 Серия: {{ h.streak }} дн.</div>
        </div>
        <form method="POST" action="/complete_habit/{{ h.id }}" style="margin:0">
          <button class="btn btn-green" {{ 'disabled' if h.last_completed == today else '' }}>
            {{ '✓ Сделано' if h.last_completed == today else '+' + h.xp_reward|string + ' XP' }}
          </button>
        </form>
      </div>
      {% endfor %}
    {% else %}
      <p class="empty">Нет привычек. Добавьте первую!</p>
    {% endif %}
  </section>

  <section>
    <div class="sec-header">
      <h2>📜 Квесты</h2>
      <button class="btn btn-orange" onclick="openModal('quest')">+ Добавить</button>
    </div>
    {% if quests %}
      {% for q in quests %}
      <div class="item {{ 'done' if q.completed else '' }}">
        <div class="item-icon {{ q.stat }}">{{ stat_icons[q.stat] }}</div>
        <div class="item-body">
          <div class="item-title">{{ '✅ ' if q.completed else '' }}{{ q.title }}</div>
          <div class="item-desc">{{ q.description }}</div>
        </div>
        {% if not q.completed %}
        <form method="POST" action="/complete_quest/{{ q.id }}" style="margin:0">
          <button class="btn btn-green">+{{ q.xp_reward }} XP</button>
        </form>
        {% else %}
        <span class="item-xp" style="margin-left:auto">Готово</span>
        {% endif %}
      </div>
      {% endfor %}
    {% else %}
      <p class="empty">Нет квестов. Создайте первый!</p>
    {% endif %}
  </section>

  <section>
    <h2 style="margin-bottom:10px">📋 Журнал приключений</h2>
    <div class="log-list">
      {% if adventure_log %}
        {% for entry in adventure_log %}
        <div class="log-item"><span class="log-time">{{ entry.time }}</span> {{ entry.message }}</div>
        {% endfor %}
      {% else %}
        <p class="empty">Пока пусто...</p>
      {% endif %}
    </div>
  </section>
</div>

<div class="modal" id="modal">
  <div class="modal-box">
    <h3 id="modal-title">Добавить</h3>
    <form method="POST" id="modal-form">
      <div class="fg">
        <label>Название</label>
        <input type="text" name="title" required placeholder="Например: Утренняя пробежка">
      </div>
      <div class="fg">
        <label>Описание</label>
        <input type="text" name="description" placeholder="Краткое описание">
      </div>
      <div class="fg">
        <label>Какой стат прокачивает?</label>
        <select name="stat">
          <option value="strength">💪 Сила</option>
          <option value="intelligence">🧠 Интеллект</option>
          <option value="discipline">🎯 Дисциплина</option>
          <option value="charisma">✨ Харизма</option>
        </select>
      </div>
      <div class="fg" id="diff-group" style="display:none">
        <label>Сложность</label>
        <select name="difficulty">
          <option value="easy">Лёгкий (10 XP)</option>
          <option value="medium">Средний (25 XP)</option>
          <option value="hard">Сложный (50 XP)</option>
        </select>
      </div>
      <div class="form-btns">
        <button type="button" class="btn btn-cancel" onclick="closeModal()">Отмена</button>
        <button type="submit" class="btn btn-orange">Создать</button>
      </div>
    </form>
  </div>
</div>

<script>
function openModal(type) {
    document.getElementById('modal-title').textContent = type === 'habit' ? '🔄 Новая привычка' : '📜 Новый квест';
    document.getElementById('modal-form').action = type === 'habit' ? '/add_habit' : '/add_quest';
    document.getElementById('diff-group').style.display = type === 'quest' ? 'block' : 'none';
    document.getElementById('modal').classList.add('open');
}
function closeModal() { document.getElementById('modal').classList.remove('open'); }
document.getElementById('modal').addEventListener('click', function(e) { if(e.target===this) closeModal(); });
</script>
</body>
</html>
"""


# --- Helpers ---

def xp_for_level(level):
    return level * 100

def add_xp(amount, stat):
    character["xp"] += amount
    character["stats"][stat] += 1
    leveled_up = False
    while character["xp"] >= xp_for_level(character["level"]):
        character["xp"] -= xp_for_level(character["level"])
        character["level"] += 1
        leveled_up = True
    return leveled_up

def log_entry(message):
    time = datetime.now().strftime("%H:%M")
    adventure_log.insert(0, {"message": message, "time": time})
    if len(adventure_log) > 20:
        adventure_log.pop()

def render():
    needed = xp_for_level(character["level"])
    pct = min(round(character["xp"] / needed * 100), 100)
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template_string(
        HTML_TEMPLATE,
        char=character,
        habits=habits,
        quests=quests,
        adventure_log=adventure_log,
        xp_pct=pct,
        xp_needed=needed,
        stat_icons=STAT_ICONS,
        stat_names={"strength": "Сила", "intelligence": "Интеллект", "discipline": "Дисциплина", "charisma": "Харизма"},
        today=today,
    )


# --- Routes ---

@app.route("/")
def index():
    return render()

@app.route("/add_habit", methods=["POST"])
def add_habit():
    global next_habit_id
    title = request.form.get("title", "").strip()
    if title:
        habits.append({
            "id": next_habit_id,
            "title": title,
            "description": request.form.get("description", ""),
            "stat": request.form.get("stat", "discipline"),
            "xp_reward": 15,
            "streak": 0,
            "last_completed": None,
        })
        next_habit_id += 1
        log_entry(f'📝 Новая привычка: "{title}"')
    from flask import redirect
    return redirect("/")

@app.route("/add_quest", methods=["POST"])
def add_quest():
    global next_quest_id
    title = request.form.get("title", "").strip()
    difficulty = request.form.get("difficulty", "medium")
    if title:
        quests.append({
            "id": next_quest_id,
            "title": title,
            "description": request.form.get("description", ""),
            "stat": request.form.get("stat", "discipline"),
            "difficulty": difficulty,
            "xp_reward": DIFFICULTY_XP.get(difficulty, 25),
            "completed": False,
        })
        next_quest_id += 1
        log_entry(f'📜 Новый квест: "{title}"')
    from flask import redirect
    return redirect("/")

@app.route("/complete_habit/<int:habit_id>", methods=["POST"])
def complete_habit(habit_id):
    habit = next((h for h in habits if h["id"] == habit_id), None)
    if not habit:
        from flask import redirect
        return redirect("/")

    today = datetime.now().strftime("%Y-%m-%d")
    if habit["last_completed"] == today:
        from flask import redirect
        return redirect("/")

    if habit["last_completed"]:
        last = datetime.strptime(habit["last_completed"], "%Y-%m-%d")
        diff = (datetime.now() - last).days
        habit["streak"] = habit["streak"] + 1 if diff == 1 else 1
    else:
        habit["streak"] = 1

    habit["last_completed"] = today
    leveled_up = add_xp(habit["xp_reward"], habit["stat"])
    log_entry(f'✅ Привычка: "{habit["title"]}" +{habit["xp_reward"]} XP')
    if leveled_up:
        log_entry(f'🎉 УРОВЕНЬ ПОВЫШЕН! Теперь {character["level"]} уровень!')

    from flask import redirect
    return redirect("/")

@app.route("/complete_quest/<int:quest_id>", methods=["POST"])
def complete_quest(quest_id):
    quest = next((q for q in quests if q["id"] == quest_id), None)
    if not quest or quest["completed"]:
        from flask import redirect
        return redirect("/")

    quest["completed"] = True
    leveled_up = add_xp(quest["xp_reward"], quest["stat"])
    log_entry(f'⚔️ Квест: "{quest["title"]}" +{quest["xp_reward"]} XP')
    if leveled_up:
        log_entry(f'🎉 УРОВЕНЬ ПОВЫШЕН! Теперь {character["level"]} уровень!')

    from flask import redirect
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
