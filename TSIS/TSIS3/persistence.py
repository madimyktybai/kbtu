import json

def save_score(name, score, distance):
    try:
        with open("leaderboard.json", "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append({
        "name": name,
        "score": score,
        "distance": int(distance)
    })

    data = sorted(data, key=lambda x: x["score"], reverse=True)[:10]

    with open("leaderboard.json", "w") as f:
        json.dump(data, f, indent=4)