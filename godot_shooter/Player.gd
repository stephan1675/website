extends CharacterBody3D

const SPEED = 5.0
const MOUSE_SENSITIVITY = 0.003

# Gravity from project settings
var gravity = ProjectSettings.get_setting("physics/3d/default_gravity")

@onready var camera = $Camera3D
@onready var weapon = $Camera3D/Weapon
@onready var raycast = $Camera3D/RayCast3D

var shoot_cooldown = false

@onready var move_joystick = get_node_or_null("../UI/MobileControls/MoveJoystick")
@onready var look_joystick = get_node_or_null("../UI/MobileControls/LookJoystick")

# Setup inputs dynamically if they don't exist
func _enter_tree():
	setup_input_action("move_forward", KEY_W)
	setup_input_action("move_backward", KEY_S)
	setup_input_action("move_left", KEY_A)
	setup_input_action("move_right", KEY_D)
	setup_input_action("shoot", MOUSE_BUTTON_LEFT)

func setup_input_action(action_name: String, key_code):
	if not InputMap.has_action(action_name):
		InputMap.add_action(action_name)
		var event
		if typeof(key_code) == TYPE_INT and (key_code == MOUSE_BUTTON_LEFT or key_code == MOUSE_BUTTON_RIGHT):
			event = InputEventMouseButton.new()
			event.button_index = key_code
		else:
			event = InputEventKey.new()
			event.physical_keycode = key_code
		InputMap.action_add_event(action_name, event)

func _ready():
	process_mode = PROCESS_MODE_PAUSABLE
	# Mouse lock by default on desktop
	if OS.get_name() != "Android" and OS.get_name() != "iOS":
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _unhandled_input(event):
	# Mouse look on PC
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * MOUSE_SENSITIVITY)
		camera.rotate_x(-event.relative.y * MOUSE_SENSITIVITY)
		camera.rotation.x = clamp(camera.rotation.x, -PI/2.5, PI/2.5)

	# Swipe to look on Mobile
	if event is InputEventScreenDrag:
		rotate_y(-event.relative.x * MOUSE_SENSITIVITY * 1.5)
		camera.rotate_x(-event.relative.y * MOUSE_SENSITIVITY * 1.5)
		camera.rotation.x = clamp(camera.rotation.x, -PI/2.5, PI/2.5)

func _physics_process(delta):
	# Add gravity
	if not is_on_floor():
		velocity.y -= gravity * delta

	# Look rotation from virtual joystick (Left bottom)
	if look_joystick and look_joystick.joystick_vector != Vector2.ZERO:
		rotate_y(-look_joystick.joystick_vector.x * 2.5 * delta)
		camera.rotate_x(-look_joystick.joystick_vector.y * 2.0 * delta)
		camera.rotation.x = clamp(camera.rotation.x, -PI/2.5, PI/2.5)

	# Check keyboard or virtual move joystick (Right bottom)
	var input_dir = Vector2.ZERO
	if move_joystick and move_joystick.joystick_vector != Vector2.ZERO:
		input_dir = move_joystick.joystick_vector
	else:
		if Input.is_action_pressed("move_forward"): input_dir.y -= 1
		if Input.is_action_pressed("move_backward"): input_dir.y += 1
		if Input.is_action_pressed("move_left"): input_dir.x -= 1
		if Input.is_action_pressed("move_right"): input_dir.x += 1

	var direction = (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
	if direction:
		velocity.x = direction.x * SPEED
		velocity.z = direction.z * SPEED
	else:
		velocity.x = move_toward(velocity.x, 0, SPEED)
		velocity.z = move_toward(velocity.z, 0, SPEED)

	move_and_slide()

	# Shooting logic
	if Input.is_action_just_pressed("shoot") and not get_parent().game_over_state:
		shoot()

func shoot():
	if shoot_cooldown: return
	shoot_cooldown = true
	
	# Recoil Animation
	var original_pos = weapon.position
	var tween = create_tween()
	tween.tween_property(weapon, "position", original_pos - Vector3(0, 0, -0.15), 0.05)
	tween.tween_property(weapon, "position", original_pos, 0.1)
	
	# Play Sound via Main
	get_parent().play_sound("shoot")

	# 1. Check for immediate hit (Raycast)
	if raycast.is_colliding():
		var collider = raycast.get_collider()
		if collider and collider.is_in_group("enemies"):
			get_parent().enemy_hit(collider)
			shoot_cooldown = false
			return

	# 2. Otherwise spawn physical projectile
	var projectile_scene = load("res://Projectile.tscn")
	var projectile = projectile_scene.instantiate()
	get_parent().add_child(projectile)
	
	# Spawn bullet slightly in front of camera
	projectile.global_position = camera.global_position + (-camera.global_transform.basis.z * 0.5)
	projectile.direction = -camera.global_transform.basis.z
	
	await get_tree().create_timer(0.15).timeout
	shoot_cooldown = false
