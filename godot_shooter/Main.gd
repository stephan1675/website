extends Node3D

var score = 0
var elapsed_time = 0.0
var current_speed = 0.0
var game_over_state = false
var enemy_count = 5
var is_paused = false

@onready var player = $Player
@onready var score_text = $UI/ScoreText
@onready var game_over_panel = $UI/GameOverPanel
@onready var name_input = $UI/GameOverPanel/NameInput
@onready var highscore_text = $UI/GameOverPanel/HighscoreText
@onready var submit_button = $UI/GameOverPanel/SubmitButton
@onready var restart_button = $UI/GameOverPanel/RestartButton

@onready var pause_button = $UI/PauseButton
@onready var pause_panel = $UI/PausePanel
@onready var resume_button = $UI/PausePanel/ResumeButton
@onready var quit_button = $UI/PausePanel/QuitButton

# Audio players
@onready var sfx_shoot = $SFX/Shoot
@onready var sfx_hit = $SFX/Hit
@onready var sfx_die = $SFX/Die
@onready var sfx_step = $SFX/Step

func _ready():
	process_mode = PROCESS_MODE_ALWAYS
	$UI.process_mode = PROCESS_MODE_ALWAYS
	$Player.process_mode = PROCESS_MODE_PAUSABLE
	$Ground.process_mode = PROCESS_MODE_PAUSABLE
	$SFX.process_mode = PROCESS_MODE_PAUSABLE

	randomize()
	submit_button.pressed.connect(submit_score)
	restart_button.pressed.connect(restart_game)
	pause_button.pressed.connect(toggle_pause)
	resume_button.pressed.connect(toggle_pause)
	quit_button.pressed.connect(quit_game)
	restart_game()

func _physics_process(delta):
	if game_over_state or get_tree().paused: return
	
	elapsed_time += delta
	if elapsed_time < 1.0:
		current_speed = 0.0
	else:
		current_speed = 2.0 + (elapsed_time - 1.0) * 0.5
		
	# Play footstep sound if player is moving
	if player and player.velocity.length() > 0.1 and player.is_on_floor():
		play_sound("step")

func spawn_enemy():
	var enemy_scene = load("res://Enemy.tscn")
	var enemy = enemy_scene.instantiate()
	add_child(enemy)
	
	# Add to group for collision check
	enemy.add_to_group("enemies")
	
	var spawn_pos = Vector3.ZERO
	while true:
		spawn_pos = Vector3(
			randf_range(-20.0, 20.0),
			0.5,
			randf_range(-20.0, 20.0)
		)
		if player == null or player.global_position.distance_to(spawn_pos) > 5.0:
			break
			
	enemy.global_position = spawn_pos

func respawn_enemies():
	var active_enemies = get_tree().get_nodes_in_group("enemies")
	while active_enemies.size() < enemy_count:
		spawn_enemy()
		active_enemies = get_tree().get_nodes_in_group("enemies")

func enemy_hit(enemy_node):
	play_sound("hit")
	enemy_node.queue_free()
	
	# Remove from group immediately to prevent double hits
	enemy_node.remove_from_group("enemies")
	
	score += 1
	score_text.text = "Score: " + str(score)
	
	# Spawn a replacement
	call_deferred("respawn_enemies")

func trigger_game_over():
	if game_over_state: return
	game_over_state = true
	
	play_sound("die")
	
	# Show mouse on PC
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	
	# Hide pause button and show game over UI panel
	if pause_button: pause_button.hide()
	game_over_panel.show()
	name_input.editable = true
	submit_button.disabled = false
	restart_button.disabled = true
	highscore_text.text = ""

func submit_score():
	var player_name = name_input.text.strip_edges()
	if player_name.is_empty():
		player_name = "Anonymous"
		
	var top_scores = Highscores.add_highscore(player_name, score)
	highscore_text.text = Highscores.format_top10()
	
	name_input.editable = false
	submit_button.disabled = true
	restart_button.disabled = false

func restart_game():
	# Clear active enemies immediately from the group so respawn doesn't count them
	var active_enemies = get_tree().get_nodes_in_group("enemies")
	for enemy in active_enemies:
		enemy.remove_from_group("enemies")
		enemy.queue_free()
		
	# Reset state
	score = 0
	elapsed_time = 0.0
	current_speed = 0.0
	game_over_state = false
	score_text.text = "Score: 0"
	is_paused = false
	get_tree().paused = false
	
	# Reset player position
	if player:
		player.global_position = Vector3(0, 1, 0)
		player.velocity = Vector3.ZERO
		if OS.get_name() != "Android" and OS.get_name() != "iOS":
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
			
	# Hide UI overlays
	game_over_panel.hide()
	if pause_panel: pause_panel.hide()
	if pause_button: pause_button.show()
	
	# Respawn
	call_deferred("respawn_enemies")

func play_sound(sound_name: String):
	match sound_name:
		"shoot":
			if sfx_shoot and sfx_shoot.stream: sfx_shoot.play()
		"hit":
			if sfx_hit and sfx_hit.stream: sfx_hit.play()
		"die":
			if sfx_die and sfx_die.stream: sfx_die.play()
		"step":
			if sfx_step and sfx_step.stream and not sfx_step.playing: sfx_step.play()

func quit_game():
	get_tree().quit()

func _unhandled_input(event):
	if event.is_action_pressed("ui_cancel"):
		if not game_over_state:
			toggle_pause()

func toggle_pause():
	is_paused = not is_paused
	get_tree().paused = is_paused
	
	if is_paused:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		pause_panel.show()
		pause_button.hide()
	else:
		if OS.get_name() != "Android" and OS.get_name() != "iOS":
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		pause_panel.hide()
		pause_button.show()
