extends Node
## Slot index (0 = autosave, 1–3 = manual) used when persisting end-game state.
## Gameplay phases should set this when the player loads or selects a manual slot.
var slot: int = 0
