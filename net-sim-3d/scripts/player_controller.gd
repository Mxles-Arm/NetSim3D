extends CharacterBody3D

@export_group("Movement")
@export var walk_speed: float = 3.2
@export var run_speed: float = 5.8
@export var acceleration: float = 14.0
@export var deceleration: float = 18.0
@export var gravity: float = 9.8
@export var max_step_height: float = 0.28
@export var step_forward_distance: float = 0.30

@export_group("Camera")
@export var look_sensitivity: float = 0.0025
@export var minimum_look_angle: float = -1.48
@export var maximum_look_angle: float = 1.48
@export var require_mouse_capture: bool = true

@onready var camera: Camera3D = $Camera3D
@onready var visual: Node3D = $Visual


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	floor_snap_length = maxf(floor_snap_length, max_step_height + 0.04)
	# Show the real skinned trousers and shoes without letting the head, hair,
	# hands or polo shirt block the first-person camera.
	_set_first_person_layers(visual)


func _set_first_person_layers(node: Node) -> void:
	if node is VisualInstance3D:
		var part: VisualInstance3D = node
		if part.name.begins_with("Trousers") or part.name.begins_with("Shoes"):
			part.layers = 3 # World layer and self-view layer.
		else:
			part.layers = 2 # Hidden from this camera (cull_mask = 1).
	for child in node.get_children():
		_set_first_person_layers(child)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * look_sensitivity)
		camera.rotate_x(-event.relative.y * look_sensitivity)
		camera.rotation.x = clampf(camera.rotation.x, minimum_look_angle, maximum_look_angle)
	elif event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _physics_process(delta: float) -> void:
	var was_on_floor := is_on_floor()
	if was_on_floor:
		velocity.y = 0.0
	else:
		velocity.y -= gravity * delta

	var input_direction := Vector2.ZERO
	if not require_mouse_capture or Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		input_direction = Input.get_vector("move_left", "move_right", "move_forward", "move_back")

	var move_direction := global_basis * Vector3(input_direction.x, 0.0, input_direction.y)
	var target_speed := run_speed if Input.is_action_pressed("run") else walk_speed
	var target_velocity := move_direction * target_speed
	var rate := acceleration if input_direction != Vector2.ZERO else deceleration
	velocity.x = move_toward(velocity.x, target_velocity.x, rate * delta)
	velocity.z = move_toward(velocity.z, target_velocity.z, rate * delta)

	var horizontal_motion := Vector3(velocity.x, 0.0, velocity.z) * delta
	move_and_slide()
	if was_on_floor and is_on_wall():
		_try_step_up(horizontal_motion)


func _try_step_up(horizontal_motion: Vector3) -> void:
	if horizontal_motion.length_squared() < 0.000001:
		return
	# Probe far enough onto the tread for the capsule to meet its flat top.
	# A single frame of motion would hit the tread edge at an unusable angle.
	var step_motion := horizontal_motion.normalized() * maxf(horizontal_motion.length(), step_forward_distance)

	var lift := Vector3.UP * max_step_height
	if test_move(global_transform, lift):
		return # A low ceiling blocks the character from rising.

	var raised := global_transform
	raised.origin += lift
	if test_move(raised, step_motion):
		return # The obstacle is taller than a step or the landing is blocked.

	var landing := raised
	landing.origin += step_motion
	var floor_hit := KinematicCollision3D.new()
	if not test_move(landing, Vector3.DOWN * (max_step_height + 0.04), floor_hit):
		return
	if floor_hit.get_normal().dot(Vector3.UP) < cos(floor_max_angle):
		return # Do not stand on a wall or a steep slope.

	var rise := max_step_height + floor_hit.get_travel().y
	if rise < 0.015 or rise > max_step_height + 0.005:
		return

	global_position = landing.origin + floor_hit.get_travel()
	velocity.y = 0.0
	apply_floor_snap()
