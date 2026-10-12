extends SceneTree


func _initialize() -> void:
	for path in [
		"res://assets/models/classroom_shell.glb",
		"res://assets/models/it_support_male_180cm.glb",
		"res://assets/models/it_support_supervisor_male_170cm.glb",
		"res://assets/models/teacher_male_khaki_180cm.glb",
		"res://scenes/it_support_player.tscn",
		"res://scenes/it_support_supervisor.tscn",
		"res://scenes/teacher_male.tscn",
		"res://scenes/main.tscn",
	]:
		var scene: PackedScene = load(path)
		if scene == null:
			push_error("Failed to load: " + path)
			quit(1)
			return
		print("LOADED ", path)
	call_deferred("_validate_main")


func _validate_main() -> void:
	var scene: PackedScene = load("res://scenes/main.tscn")
	var instance: Node3D = scene.instantiate()
	root.add_child(instance)
	await process_frame
	var colliders := instance.get_node("MapCollision").get_child_count()
	var rigs := instance.find_children("*", "Skeleton3D", true, false).size()
	print("VALIDATION collision_shapes=", colliders, " character_skeletons=", rigs)
	for name in ["ITSupportPlayer", "ITSupportSupervisor", "TeacherMale"]:
		var character: CharacterBody3D = instance.get_node(name)
		print("CHARACTER ", name, " position=", character.position, " collision=", character.get_node("CollisionShape3D").shape != null)
	for i in range(60):
		await physics_frame
	var player: CharacterBody3D = instance.get_node("ITSupportPlayer")
	print("PLAYER_GROUNDED ", player.is_on_floor(), " position=", player.position)
	if colliders < 200 or rigs < 3 or not player.is_on_floor():
		push_error("Map or character import validation failed")
		quit(1)
	else:
		quit()
