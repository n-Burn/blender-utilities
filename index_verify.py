import bpy
import bmesh

bm = bmesh.from_edit_mesh(bpy.context.edit_object.data)
bm.select_history

print("\n========================================")
print(" Start")
print("========================================\n")

print("Original data\n")
len_sel_hist = len(bm.select_history)
idx_list = [i.index for i in bm.select_history]
for i, e in enumerate(bm.select_history):
    print(i, ',', -len_sel_hist+i, e)

print("\n\nSliced data")
for i in range(-len_sel_hist, len_sel_hist):

    print("\n============\n")
    print("Element indexes for", '[' + str(i) + ":]\n")
    print("Expected:", idx_list[i:])
    s_idxs = [e.index for e in bm.select_history[i:]]
    print("  Actual:", s_idxs)
    
    print("\n============\n")
    print("Element indexes for", '[:' + str(i) + "]\n")
    s_idxs = [e.index for e in bm.select_history[:i]]
    print("Expected:", idx_list[:i])
    print("  Actual:", s_idxs)

print()
