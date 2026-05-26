import struct

def encode_coords(x, y):
    return (x & 0xFFFF) | ((y & 0xFFFF) << 16)

def encode_atlas(x, y, alt=0):
    return (x & 0xFFFF) | ((y & 0xFFFF) << 16)

# source_id = 0 for all
tiles = []
for y in range(12):
    for x in range(8):
        source_id = 0
        
        # Determine tile type
        if y == 0 and x > 0 and x < 7:
            # shelf on north wall
            atlas_x, atlas_y = 3, 0
        elif x == 0 or x == 7 or y == 0 or y == 11:
            # wall border
            atlas_x, atlas_y = 1, 0
        elif y == 5 and (x == 2 or x == 3 or x == 4):
            # counter, 3 contiguous cells
            atlas_x, atlas_y = 2, 0
        elif y == 4 and (x > 0 and x < 7 and x != 4):
            # back room partition (with door opening at x=4)
            atlas_x, atlas_y = 4, 0
        else:
            # wooden floor
            atlas_x, atlas_y = 0, 0
            
        tiles.append((encode_coords(x, y), source_id, encode_atlas(atlas_x, atlas_y)))

# flat list of ints
data = []
for t in tiles:
    data.extend(t)

# format array as string
array_str = ", ".join(map(str, data))

scene_template = f"""[gd_scene load_steps=2 format=3 uid="uid://b123456789abc"]

[ext_resource type="TileSet" path="res://lpc_terrain.tres" id="1_tiles"]

[node name="OrssonEmporium" type="Node2D"]

[node name="TileMap" type="TileMap" parent="."]
tile_set = ExtResource("1_tiles")
format = 2
layer_0/tile_data = PackedInt32Array({array_str})

[node name="CanvasModulate" type="CanvasModulate" parent="."]
color = Color(0.831373, 0.647059, 0.454902, 1)

[node name="SpawnPoint" type="Marker2D" parent="."]
position = Vector2(72, 184)
"""

import os
os.makedirs("scenes/interiors", exist_ok=True)
with open("scenes/interiors/orsson_emporium.tscn", "w") as f:
    f.write(scene_template)

print("Scene generated successfully.")
