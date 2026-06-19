extends Control

signal joystick_vector_changed(vector: Vector2)

@export var max_length: float = 50.0

@onready var base = $Base
@onready var knob = $Base/Knob

var joystick_vector: Vector2 = Vector2.ZERO
var touch_id: int = -1

func _ready():
	call_deferred("center_knob")

func center_knob():
	if base and knob:
		knob.position = (base.size / 2.0) - (knob.size / 2.0)

func _gui_input(event):
	if event is InputEventScreenTouch:
		if event.pressed:
			if touch_id == -1:
				touch_id = event.index
				update_joystick(event.position)
		elif event.index == touch_id:
			reset_joystick()
			
	elif event is InputEventScreenDrag:
		if event.index == touch_id:
			update_joystick(event.position)

func update_joystick(touch_pos: Vector2):
	var center = base.size / 2.0
	var offset = touch_pos - (size / 2.0)
	
	if offset.length() > max_length:
		offset = offset.normalized() * max_length
		
	knob.position = center + offset - (knob.size / 2.0)
	joystick_vector = offset / max_length
	joystick_vector_changed.emit(joystick_vector)

func reset_joystick():
	touch_id = -1
	joystick_vector = Vector2.ZERO
	var center = base.size / 2.0
	var tween = create_tween()
	tween.tween_property(knob, "position", center - (knob.size / 2.0), 0.1).set_trans(Tween.TRANS_OUT).set_ease(Tween.EASE_OUT)
	joystick_vector_changed.emit(joystick_vector)
