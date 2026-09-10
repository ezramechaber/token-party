"""Reference-led skin bake and fine hair geometry for the personalized DJ."""
from mathutils.bvhtree import BVHTree
# Color projection is baked into the character's actual UV atlas. Geometry and
# the rig remain fully three-dimensional; no portrait plane is used in the scene.
reference=ROOT/'.b2b/likeness/neutral-face.png'
baked_path=ROOT/'scene/assets/likeness/ezra-skin.png'
if baked_path.exists():
    bs=skinmat.node_tree.nodes.get('Principled BSDF');node=image_node(skinmat,baked_path)
    skinmat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
elif reference.exists():
    nodes=skinmat.node_tree.nodes;links=skinmat.node_tree.links;bs=nodes.get('Principled BSDF')
    original=bs.inputs['Base Color'].links[0].from_socket
    front_uv=body.data.uv_layers.new(name='Face projection')
    mask=body.data.color_attributes.new(name='Face blend',type='FLOAT_COLOR',domain='POINT')
    def smooth(a,b,x):
        t=min(1,max(0,(x-a)/(b-a)));return t*t*(3-2*t)
    def vertical(y):
        anchors=[(6.9,.015),(7.09,.105),(7.48,.245),(7.805,.386),(8.216,.532),(8.9,.795),(9.6,1.03)]
        for (a,u),(b,v) in zip(anchors,anchors[1:]):
            if y<=b:return u+(v-u)*(y-a)/(b-a)
        return 1.03
    for v in body.data.vertices:
        source=(Vector((v.co.x,v.co.z,-v.co.y))-OFFSET)/SCALE
        factor=smooth(.52,1.12,source.z)*smooth(6.95,7.20,source.y)*(1-smooth(9.0,9.3,source.y))*(1-smooth(.77,1.02,abs(source.x)))
        mask.data[v.index].color=(factor,factor,factor,1)
    for poly in body.data.polygons:
        for li in poly.loop_indices:
            co=body.data.vertices[body.data.loops[li].vertex_index].co
            source=(Vector((co.x,co.z,-co.y))-OFFSET)/SCALE
            front_uv.data[li].uv=(.498+source.x*.306,vertical(source.y))
    tex=image_node(skinmat,reference);uv=nodes.new('ShaderNodeUVMap');uv.uv_map='Face projection';links.new(uv.outputs['UV'],tex.inputs['Vector'])
    attr=nodes.new('ShaderNodeVertexColor');attr.layer_name='Face blend'
    mix=nodes.new('ShaderNodeMixRGB');links.new(attr.outputs['Color'],mix.inputs[0]);links.new(original,mix.inputs[1]);links.new(tex.outputs['Color'],mix.inputs[2])
    emission=nodes.new('ShaderNodeEmission');links.new(mix.outputs['Color'],emission.inputs['Color'])
    output=nodes.get('Material Output');links.new(emission.outputs[0],output.inputs['Surface'])
    atlas=bpy.data.images.new('Ezra face and skin atlas',width=2048,height=2048,alpha=False)
    target=nodes.new('ShaderNodeTexImage');target.image=atlas;nodes.active=target
    body.data.uv_layers.active=body.data.uv_layers['UVMap'];body.data.uv_layers['UVMap'].active_render=True
    bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
    old=rig.data.pose_position;rig.data.pose_position='REST'
    bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=1
    bpy.ops.object.bake(type='EMIT',margin=24,use_clear=True)
    rig.data.pose_position=old
    atlas.filepath_raw=str(baked_path);atlas.file_format='PNG';atlas.save();atlas.pack()
    links.new(bs.outputs['BSDF'],output.inputs['Surface']);links.new(target.outputs['Color'],bs.inputs['Base Color'])
    # Keep only native UVs in the exported body after the bake.
    body.data.uv_layers.remove(front_uv)
    for n in [emission,mix,attr,tex,uv]:nodes.remove(n)
    bpy.context.scene.cycles.samples=96

# Fine strands follow the fitted hair surface and share the head bone.
verts=[v.co.copy() for v in hairmesh.data.vertices]
polys=[list(f.vertices) for f in hairmesh.data.polygons]
bvh=BVHTree.FromPolygons(verts,polys,all_triangles=False)
strand_vertices=[];strand_faces=[]
for i in range(1250):
    poly=hairmesh.data.polygons[int(rng.integers(len(hairmesh.data.polygons)))];ids=list(poly.vertices)
    if len(ids)<3:continue
    a,b,c=[verts[j] for j in ids[:3]];u,v=rng.random(2)
    if u+v>1:u,v=1-u,1-v
    root=a+(b-a)*u+(c-a)*v;normal=poly.normal.normalized()
    if normal.z<.3:continue
    comb=Vector((-.65,.7,.08));comb=(comb-normal*comb.dot(normal)).normalized()
    length=.025+.035*rng.random();width=.00035+.00035*rng.random();start=len(strand_vertices)
    for step in range(7):
        t=step/6;point=root+comb*(t*length)
        hit,n,_,dist=bvh.find_nearest(point)
        if hit is None:hit,n=root,normal
        point=hit+n*(.002+.008*math.sin(math.pi*t))
        tangent=comb.cross(n).normalized();w=width*(1-.9*t)
        strand_vertices.extend([point+tangent*w,point-tangent*w])
    for step in range(6):strand_faces.append((start+step*2,start+step*2+1,start+step*2+3,start+step*2+2))
mesh=bpy.data.meshes.new('Fine swept strands');mesh.from_pydata(strand_vertices,[],strand_faces);mesh.update()
obj=bpy.data.objects.new('djHairStrands',mesh);bpy.context.collection.objects.link(obj)
strandmat=material('Chestnut hair strands',(.053,.030,.016),0,.48);strandmat.node_tree.nodes['Principled BSDF'].inputs['Anisotropic'].default_value=.6
finish(obj,'djHairStrands',strandmat);vg=obj.vertex_groups.new(name='head');vg.add(list(range(len(mesh.vertices))),1,'REPLACE');modifier=obj.modifiers.new('Follow head','ARMATURE');modifier.object=rig;obj.parent=rig

# Native curve groom for the Cycles portrait, with the fitted hair/cards retained
# as the lower-cost live representation. Every strand is editable in Blender.
curve=bpy.data.curves.new('Photographic hair groom','CURVE');curve.dimensions='3D';curve.resolution_u=2;curve.bevel_depth=.00020;curve.bevel_resolution=1
eligible=[poly for poly in hairmesh.data.polygons if poly.normal.z>.20]
areas=np.array([p.area for p in eligible]);areas/=areas.sum()
for i in range(24000):
    poly=eligible[int(rng.choice(len(eligible),p=areas))];a,b,c=[verts[j] for j in list(poly.vertices)[:3]];u,v=rng.random(2)
    if u+v>1:u,v=1-u,1-v
    root=a+(b-a)*u+(c-a)*v;normal=poly.normal.normalized()
    comb=Vector((-.78,.48,.06));comb=(comb-normal*comb.dot(normal)).normalized()
    across=comb.cross(normal).normalized();length=.055+.075*rng.random();clump=math.sin(root.x*90+root.y*57)
    spline=curve.splines.new('POLY');spline.points.add(8)
    for j,point in enumerate(spline.points):
        t=j/8;probe=root+comb*(t*length)+across*(.007*math.sin(math.pi*t)*(clump+.3*math.sin(t*7)))
        hit,n,_,dist=bvh.find_nearest(probe)
        if hit is None:hit,n=root,normal
        pos=hit+n*(.0015+.009*math.sin(math.pi*t))
        point.co=(*pos,1);point.radius=(.8+.35*rng.random())*(1-.92*t)
groom=bpy.data.objects.new('djCyclesHairGroom',curve);bpy.context.collection.objects.link(groom)
hair_shader=bpy.data.materials.new('Physical chestnut fibers');hair_shader.use_nodes=True
nodes=hair_shader.node_tree.nodes;nodes.clear();output=nodes.new('ShaderNodeOutputMaterial');shader=nodes.new('ShaderNodeBsdfHairPrincipled');shader.parametrization='MELANIN'
for name,value in [('Melanin',.64),('Melanin Redness',.23),('Roughness',.34),('Radial Roughness',.4),('Random Color',.13),('Random Roughness',.12)]:
    if name in shader.inputs:shader.inputs[name].default_value=value
hair_shader.node_tree.links.new(shader.outputs[0],output.inputs['Surface']);curve.materials.append(hair_shader)
groom.parent=rig;groom.parent_type='BONE';groom.parent_bone='head'
groom.matrix_world=rig.matrix_world@rig.pose.bones['head'].matrix@rig.data.bones['head'].matrix_local.inverted()
