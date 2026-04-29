from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --- In-memory database ---

character = {
    "name": "Герой",
    "level": 1,
    "xp": 0,
    "stats": {
        "strength": 1,
        "intelligence": 1,
        "discipline": 1,
        "charisma": 1,
    },
}

habits = [
    {
        "id": 1,
        "title": "Утренняя зарядка",
        "description": "15 минут упражнений",
        "stat": "strength",
        "xp_reward": 15,
        "streak": 0,
        "last_completed": None,
    },
    {
        "id": 2,
        "title": "Чтение книги",
        "description": "30 минут чтения",
        "stat": "intelligence",
        "xp_reward": 15,
        "streak": 0,
        "last_completed": None,
    },
]

quests = [
    {
        "id": 1,
        "title": "Пробежать 5 км",
        "description": "Первый серьёзный забег",
        "stat": "strength",
        "difficulty": "medium",
        "xp_reward": 25,
        "completed": False,
    },
    {
        "id": 2,
        "title": "Пройти онлайн-курс по Python",
        "description": "Завершить все модули курса",
        "stat": "intelligence",
        "difficulty": "hard",
        "xp_reward": 50,
        "completed": False,
    },
]

next_habit_id = 3
next_quest_id = 3

DIFFICULTY_XP = {"easy": 10, "medium": 25, "hard": 50}


def xp_for_level(level):
    return level * 100


def add_xp(amount, stat):
    leveled_up = False
    character["xp"] += amount
    character["stats"][stat] += 1

    needed = xp_for_level(character["level"])
    while character["xp"] >= needed:
        character["xp"] -= needed
        character["level"] += 1
        leveled_up = True
        needed = xp_for_level(character["level"])

    return leveled_up


# --- Routes ---


@app.route("/")
def index():
    return jsonify(
        {
            "app": "Life RPG API",
            "version": "1.0",
            "endpoints": [
                "/api/character",
                "/api/habits",
                "/api/quests",
            ],
        }
    )


@app.route("/api/character")
def get_character():
    return jsonify(character)


# --- Habits ---


@app.route("/api/habits")
def get_habits():
    return jsonify(habits)


@app.route("/api/habits", methods=["POST"])
def create_habit():
    global next_habit_id
    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    habit = {
        "id": next_habit_id,
        "title": data["title"],
        "description": data.get("description", ""),
        "stat": data.get("stat", "discipline"),
        "xp_reward": data.get("xp_reward", 15),
        "streak": 0,
        "last_completed": None,
    }
    next_habit_id += 1
    habits.append(habit)
    return jsonify(habit), 201


@app.route("/api/habits/<int:habit_id>/complete", methods=["POST"])
def complete_habit(habit_id):
    habit = next((h for h in habits if h["id"] == habit_id), None)
    if not habit:
        return jsonify({"error": "habit not found"}), 404

    today = datetime.now().strftime("%Y-%m-%d")
    if habit["last_completed"] == today:
        return jsonify({"error": "already completed today"}), 400

    if habit["last_completed"]:
        last = datetime.strptime(habit["last_completed"], "%Y-%m-%d")
        diff = (datetime.now() - last).days
        if diff == 1:
            habit["streak"] += 1
        elif diff > 1:
            habit["streak"] = 1
    else:
        habit["streak"] = 1

    habit["last_completed"] = today
    xp = habit["xp_reward"]
    leveled_up = add_xp(xp, habit["stat"])

    return jsonify(
        {
            "message": "habit completed",
            "xp_gained": xp,
            "leveled_up": leveled_up,
            "new_level": character["level"],
            "streak": habit["streak"],
        }
    )


# --- Quests ---


@app.route("/api/quests")
def get_quests():
    return jsonify(quests)


@app.route("/api/quests", methods=["POST"])
def create_quest():
    global next_quest_id
    data = request.get_json()

    if not data or not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    difficulty = data.get("difficulty", "medium")
    quest = {
        "id": next_quest_id,
        "title": data["title"],
        "description": data.get("description", ""),
        "stat": data.get("stat", "discipline"),
        "difficulty": difficulty,
        "xp_reward": DIFFICULTY_XP.get(difficulty, 25),
        "completed": False,
    }
    next_quest_id += 1
    quests.append(quest)
    return jsonify(quest), 201


@app.route("/api/quests/<int:quest_id>/complete", methods=["POST"])
def complete_quest(quest_id):
    quest = next((q for q in quests if q["id"] == quest_id), None)
    if not quest:
        return jsonify({"error": "quest not found"}), 404

    if quest["completed"]:
        return jsonify({"error": "quest already completed"}), 400

    quest["completed"] = True
    xp = quest["xp_reward"]
    leveled_up = add_xp(xp, quest["stat"])

    return jsonify(
        {
            "message": "quest completed",
            "xp_gained": xp,
            "leveled_up": leveled_up,
            "new_level": character["level"],
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
