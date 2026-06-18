extends Node

const HIGHSCORE_FILE = "user://highscores.json"
const MAX_HIGHSCORES = 10

var highscores = []

func _ready():
	load_highscores()

func load_highscores():
	highscores = []
	if FileAccess.file_exists(HIGHSCORE_FILE):
		var file = FileAccess.open(HIGHSCORE_FILE, FileAccess.READ)
		var json_string = file.get_as_text()
		file.close()
		var json = JSON.new()
		var error = json.parse(json_string)
		if error == OK:
			if typeof(json.data) == TYPE_ARRAY:
				highscores = json.data
			else:
				print("Highscore data format invalid.")
		else:
			print("Failed to parse highscores: ", json.get_error_message())
	return highscores

func save_highscores():
	var file = FileAccess.open(HIGHSCORE_FILE, FileAccess.WRITE)
	var json_string = JSON.stringify(highscores)
	file.store_string(json_string)
	file.close()

func add_highscore(player_name: String, score: int):
	highscores.append({"name": player_name, "score": score})
	highscores.sort_custom(func(a, b): return a["score"] > b["score"])
	if highscores.size() > MAX_HIGHSCORES:
		highscores = highscores.slice(0, MAX_HIGHSCORES)
	save_highscores()
	return highscores

func format_top10() -> String:
	var lines = ["Top 10:"]
	for i in range(highscores.size()):
		var entry = highscores[i]
		lines.append(str(i + 1) + ". " + entry["name"] + " - " + str(entry["score"]))
	return "\n".join(lines)
