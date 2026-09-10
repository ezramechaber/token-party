"""Bake the posed character with volume-preserving wrist deformation, then rebind."""
# A-pose to palm-down involves considerable wrist twist. Bake that one-time
# deformation with dual quaternions so the browser need only deform locally.
bpy.ops.object.select_all(action='DESELECT')
parented={o:o.matrix_world.copy() for o in bpy.data.objects if o.parent==rig and o.parent_type=='BONE'}
skinned=[]
for obj in list(bpy.data.objects):
    if obj.type!='MESH':continue
    mods=[m for m in obj.modifiers if m.type=='ARMATURE' and m.object==rig]
    if not mods:continue
    hidden=obj.hide_get();obj.hide_set(False);obj.select_set(True);bpy.context.view_layer.objects.active=obj
    for mod in mods:
        dq_points=None;blend=[]
        if obj==body:
            # Preserve volume only at the twisting wrists/forearms. Applying
            # dual quaternions globally inflated the shoulder under the tee.
            other=[(m,m.show_viewport) for m in obj.modifiers if m!=mod]
            for m,_ in other:m.show_viewport=False
            mod.use_deform_preserve_volume=True;bpy.context.view_layer.update()
            evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            mesh=evaluated.to_mesh();dq_points=[v.co.copy() for v in mesh.vertices];evaluated.to_mesh_clear()
            names={g.index:g.name for g in obj.vertex_groups}
            blend=[min(1,sum(g.weight for g in v.groups if names[g.group].startswith(('forearm','hand','finger')))) for v in obj.data.vertices]
            mod.use_deform_preserve_volume=False
            for m,visible in other:m.show_viewport=visible
        bpy.ops.object.modifier_apply(modifier=mod.name)
        if dq_points:
            assert len(dq_points)==len(obj.data.vertices)
            for v,p,w in zip(obj.data.vertices,dq_points,blend):v.co=v.co.lerp(p,w)
    obj.select_set(False);obj.hide_set(hidden);skinned.append(obj)
bpy.context.view_layer.objects.active=rig;rig.select_set(True)
bpy.ops.object.mode_set(mode='POSE');bpy.ops.pose.armature_apply(selected=False);bpy.ops.object.mode_set(mode='OBJECT')
for obj in skinned:
    mod=obj.modifiers.new('DJ animation skin','ARMATURE');mod.object=rig
    bpy.context.view_layer.objects.active=obj
    # Keep deformation before subdivision and garment thickness.
    while list(obj.modifiers).index(mod)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
for obj,matrix in parented.items():obj.matrix_world=matrix
bpy.context.view_layer.update()
rig['restPose']={b.name:list(b.matrix_basis.to_quaternion()) for b in rig.pose.bones}
rig['posePositions']={name:[rig.pose.bones[name].head.x,rig.pose.bones[name].head.z,-rig.pose.bones[name].head.y] for name in ['upperArmL','forearmL','handL','upperArmR','forearmR','handR','head']}
print('POSED_REST_VOLUME_PRESERVED',len(skinned))
