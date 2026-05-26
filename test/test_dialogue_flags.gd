extends GdUnitTestSuite


func before_test() -> void:
	QuestManager.quests.clear()


func test_start_quest_adds_active_entry() -> void:
	QuestManager.start_quest("merchants_delivery")
	assert_that(QuestManager.quests.has("merchants_delivery")).is_true()
	var q: Dictionary = QuestManager.quests["merchants_delivery"]
	assert_that(str(q.get("status", ""))).is_equal("active")


func test_is_complete_false_for_fresh_quest() -> void:
	QuestManager.start_quest("merchants_delivery")
	assert_that(QuestManager.is_complete("merchants_delivery")).is_false()


func test_quest_updated_emitted_on_start_quest() -> void:
	var captured: Array = []
	var cb := func(qid: String) -> void:
		captured.append(qid)
	QuestManager.quest_updated.connect(cb, Object.CONNECT_ONE_SHOT)
	QuestManager.start_quest("merchants_delivery")
	assert_that(captured.size()).is_equal(1)
	assert_that(str(captured[0])).is_equal("merchants_delivery")


func test_set_get_flag_roundtrip() -> void:
	var key := "dialogue_flags_roundtrip_%s" % str(randi())
	var value := "probe_%s" % str(randi())
	DialogueManager.set_flag(key, value)
	assert_that(DialogueManager.get_flag(key)).is_equal(value)


func test_get_flag_unknown_returns_falsy_default() -> void:
	var v = DialogueManager.get_flag("__dialogue_flags_missing_key__")
	assert_that(v == null).is_true()
