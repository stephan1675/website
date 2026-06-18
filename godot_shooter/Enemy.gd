extends CharacterBody3D

var speed = 2.0
@onready var player = get_node("../Player")

func _physics_process(delta):
	if get_parent().game_over_state:
		return
		
	# Synchronize speed from Main node
	speed = get_parent().current_speed
	
	if player:
		# Chase player on X-Z plane (ignore Y to prevent floating)
		var dir = player.global_position - global_position
		dir.y = 0
		dir = dir.normalized()
		
		velocity = dir * speed
		move_and_slide()
		
		# Check distance to player for game over collision
		var dist = global_position.distance_to(player.global_position)
		if dist < 1.5:
			get_parent().trigger_game_over()
