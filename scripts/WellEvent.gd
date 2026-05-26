extends Area2D

signal burst_triggered

func _on_well_entered(player: Node2D) -> void:
    player.can_move = false
    emit_signal("burst_triggered")

    var burst_origin := global_position
    var thugs := get_tree().get_nodes_in_group("thugs")
    for thug in thugs:
        if thug.has_method("start_flee"):
            thug.start_flee(burst_origin)

    var particles = get_node_or_null("BurstParticles")
    if particles:
        particles.emitting = true
        
    await get_tree().create_timer(0.5).timeout
    
    if particles:
        particles.emitting = false

    var myramar = get_node_or_null("MyramarSprite")
    if myramar:
        myramar.visible = true
        
    await get_tree().create_timer(3.0).timeout
    
    if myramar:
        var tween = create_tween()
        tween.tween_property(myramar, "modulate:a", 0.0, 1.0)
        await tween.finished
        myramar.visible = false
