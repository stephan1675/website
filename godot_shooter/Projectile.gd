extends Area3D

const SPEED = 50.0
var direction = Vector3.FORWARD
var lifetime = 2.0

func _ready():
	body_entered.connect(_on_body_entered)

func _physics_process(delta):
	global_position += direction * SPEED * delta
	lifetime -= delta
	if lifetime <= 0.0:
		queue_free()

func _on_body_entered(body):
	if body.is_in_group("enemies"):
		get_parent().enemy_hit(body)
		queue_free()
