"""Attach the reference-fitted head and a swept hair groom to the existing DJ rig."""
from mathutils.bvhtree import BVHTree
import numpy as np

asset=ROOT/'scene/assets/likeness/fitted-head.blend'
anchors=json.loads((asset.parent/'fitted-head-anchors.json').read_text())
with bpy.data.libraries.load(str(asset),link=False) as (source,target):
    target.objects=['Ezra fitted head asset']
head_obj=target.objects[0];bpy.context.collection.objects.link(head_obj);head_obj.name='djFittedHead'
source_points=[v.co.copy() for v in head_obj.data.vertices]
source_eye=(Vector(anchors['eyeL'])+Vector(anchors['eyeR']))*.5
target_eyes=[to_world(joint(spec['bones']['eye.'+side]['head'])) for side in ['R','L']]
target_eye=(target_eyes[0]+target_eyes[1])*.5+Vector((0,-.032,0))
head_scale=(target_eyes[1]-target_eyes[0]).length/(Vector(anchors['eyeR'])-Vector(anchors['eyeL'])).length
def fitted(p):return (p-source_eye)*head_scale+target_eye
for v,p in zip(head_obj.data.vertices,source_points):v.co=fitted(p)
head_obj.data.update()

# The fitted mesh includes a neck. Blend its lower boundary into the existing
# body and retain the original lower neck under the collar.
neck_bottom=3.10;neck_top=3.20
for v in head_obj.data.vertices:
    if v.co.z<neck_top:
        blend=min(1,max(0,(neck_top-v.co.z)/(neck_top-neck_bottom)))
        radius=.102
        center_y=to_world(joint(spec['bones']['neck01']['head'])).y
        v.co.x=v.co.x*(1-.65*blend)+max(-radius,min(radius,v.co.x))*.65*blend
        v.co.y=v.co.y*(1-.6*blend)+max(center_y-radius,min(center_y+radius,v.co.y))*.6*blend
bm=bmesh.new();bm.from_mesh(head_obj.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z<neck_bottom],context='VERTS')
bm.to_mesh(head_obj.data);bm.free()
bm=bmesh.new();bm.from_mesh(body.data)
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z>3.14],context='VERTS')
bm.to_mesh(body.data);bm.free()
for obsolete in [hairmesh,eyes,brows,lashes]:bpy.data.objects.remove(obsolete,do_unlink=True)

head_groups={}
for v in head_obj.data.vertices:
    if v.co.z>3.26:ws={'head':1.0}
    else:
        source=(Vector((v.co.x,v.co.z,-v.co.y))-OFFSET)/SCALE
        _,nearest,_=kd.find(source);ws=per_vertex[nearest]
    for bone,weight in ws.items():
        group=head_groups.get(bone)
        if group is None:group=head_obj.vertex_groups.new(name=bone);head_groups[bone]=group
        group.add([v.index],weight,'REPLACE')
mod=head_obj.modifiers.new('Follow anatomical head','ARMATURE');mod.object=rig;head_obj.parent=rig
for poly in head_obj.data.polygons:poly.use_smooth=True
skin_node=head_obj.data.materials[0].node_tree.nodes.get('Principled BSDF')
skin_node.inputs['Subsurface Scale'].default_value=.0025
skin_node.inputs['Specular IOR Level'].default_value=.3
skin_node.inputs['Roughness'].default_value=.49

# Grow independent tapered fibers over the fitted scalp. The source texture
# supplies the dense base; these curves and ribbons provide actual silhouette.
verts=[v.co.copy() for v in head_obj.data.vertices]
polys=[list(f.vertices) for f in head_obj.data.polygons]
bvh=BVHTree.FromPolygons(verts,polys)
def source_coord(p):return (p-target_eye)/head_scale+source_eye
def on_scalp(p):
    x,y,z=source_coord(p)
    if abs(x)>.82 and z<.72:return False
    front=max(0,min(1,(-y+.1)/.65))
    hairline=.38*(1-front)+front*(.96-.34*min(1,abs(x)/.76)**2+.09*x)
    return z>hairline
eligible=[poly for poly in head_obj.data.polygons if on_scalp(poly.center) and poly.normal.z>-.12]
# A softly shaped underlying cap provides volume between individual fibers.
cap_ids=sorted({i for poly in eligible for i in poly.vertices});cap_lookup={old:new for new,old in enumerate(cap_ids)}
edge_counts={};hair_neighbors={i:set() for i in cap_ids}
for poly in eligible:
    ids=list(poly.vertices)
    for a,b in zip(ids,ids[1:]+ids[:1]):
        edge=tuple(sorted((a,b)));edge_counts[edge]=edge_counts.get(edge,0)+1
        hair_neighbors[a].add(b);hair_neighbors[b].add(a)
boundary={i for edge,count in edge_counts.items() if count==1 for i in edge}
distance={i:0 for i in boundary};frontier=set(boundary)
for step in range(1,5):
    frontier={n for i in frontier for n in hair_neighbors[i] if n not in distance}
    distance.update({i:step for i in frontier})
cap_vertices=[]
for i in cap_ids:
    v=head_obj.data.vertices[i];p=source_coord(v.co)
    crown=max(0,min(1,(p.z-.50)/.80))
    edge_weight=min(1,distance.get(i,5)/4);edge_weight=edge_weight**2*(3-2*edge_weight)
    volume=(.001+.013*crown**1.3*(1+.18*math.sin(p.x*3)))*edge_weight
    point=v.co+v.normal*volume;cap_vertices.append(point);v.co=point
head_obj.data.update()
cap_faces=[[cap_lookup[i] for i in poly.vertices] for poly in eligible]
cap_data=bpy.data.meshes.new('Swept hair volume');cap_data.from_pydata(cap_vertices,[],cap_faces);cap_data.update()
cap=bpy.data.objects.new('djHair',cap_data);bpy.context.collection.objects.link(cap)
cap.hide_render=True;cap.hide_set(True)  # root guide only; volume is in the continuous head mesh
cap_mat=head_obj.data.materials[0].copy();cap_mat.name='Photographic hair base'
cap_mat.node_tree.nodes['Principled BSDF'].inputs['Subsurface Weight'].default_value=0
cap_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.65
cap_data.materials.append(cap_mat)
cap_uv=cap_data.uv_layers.new(name='UVMap');source_uv=head_obj.data.uv_layers.active
for cap_poly,source_poly in zip(cap_data.polygons,eligible):
    for a,b in zip(cap_poly.loop_indices,source_poly.loop_indices):cap_uv.data[a].uv=source_uv.data[b].uv
for poly in cap_data.polygons:poly.use_smooth=True
vg=cap.vertex_groups.new(name='head');vg.add(list(range(len(cap_data.vertices))),1,'REPLACE')
modifier=cap.modifiers.new('Follow head','ARMATURE');modifier.object=rig;cap.parent=rig
sub=cap.modifiers.new('Soft hair volume','SUBSURF');sub.levels=1;sub.render_levels=1
verts=[v.co.copy() for v in cap_data.vertices];polys=[list(f.vertices) for f in cap_data.polygons]
bvh=BVHTree.FromPolygons(verts,polys)
eligible=list(cap_data.polygons)
area=np.array([poly.area for poly in eligible]);area/=area.sum()
rng_hair=np.random.default_rng(20260910)
curve=bpy.data.curves.new('Reference swept chestnut groom','CURVE');curve.dimensions='3D';curve.bevel_depth=.00016;curve.bevel_resolution=0
live_verts=[];live_faces=[];live_mats=[]
for i in range(6000):
    poly=eligible[int(rng_hair.choice(len(eligible),p=area))]
    a,b,c=[verts[j] for j in list(poly.vertices)[:3]];u,v=rng_hair.random(2)
    if u+v>1:u,v=1-u,1-v
    root=a+(b-a)*u+(c-a)*v;n=poly.normal.normalized();source_root=source_coord(root)
    comb=Vector((-.85,.55,.10));comb=(comb-n*comb.dot(n)).normalized()
    across=comb.cross(n).normalized()
    crown=max(0,min(1,(source_root.z-.55)/.65))
    length=(.025+.055*crown)*(.8+.4*rng_hair.random())
    lift=.001+.006*crown
    spline=curve.splines.new('POLY');spline.points.add(8)
    path=[]
    last_hit,last_normal=root,n
    for j,point in enumerate(spline.points):
        t=j/8;probe=root+comb*(t*length)+across*(.005*math.sin(t*math.pi*1.5+i*.3)*math.sin(math.pi*t))
        hit,normal,_,_=bvh.find_nearest(probe)
        if hit is None:hit,normal=last_hit,last_normal
        last_hit,last_normal=hit,normal
        pos=hit+normal*(.001+lift*math.sin(math.pi*t))
        point.co=(*pos,1);point.radius=(.7+.3*rng_hair.random())*(1-.95*t)
        path.append((pos,normal,t))
    if i<450:
        start=len(live_verts)
        for pos,normal,t in path:
            width=.00040*(1-.96*t);side=comb.cross(normal).normalized()
            live_verts.extend([pos+side*width,pos-side*width])
        for j in range(8):live_faces.append((start+j*2,start+j*2+1,start+j*2+3,start+j*2+2));live_mats.append(i%4)
groom=bpy.data.objects.new('djCyclesHairGroom',curve);bpy.context.collection.objects.link(groom)
hair_shader=bpy.data.materials.new('Reference chestnut fibers');hair_shader.use_nodes=True
nodes=hair_shader.node_tree.nodes;nodes.clear();output=nodes.new('ShaderNodeOutputMaterial');shader=nodes.new('ShaderNodeBsdfHairPrincipled');shader.parametrization='MELANIN'
for name,value in [('Melanin',.65),('Melanin Redness',.24),('Roughness',.35),('Radial Roughness',.4),('Random Color',.10),('Random Roughness',.10)]:
    if name in shader.inputs:shader.inputs[name].default_value=value
hair_shader.node_tree.links.new(shader.outputs[0],output.inputs['Surface']);curve.materials.append(hair_shader)
groom.parent=rig;groom.parent_type='BONE';groom.parent_bone='head'
groom.matrix_world=rig.matrix_world@rig.pose.bones['head'].matrix@rig.data.bones['head'].matrix_local.inverted()
data=bpy.data.meshes.new('Realtime swept hair');data.from_pydata(live_verts,[],live_faces);data.update()
live=bpy.data.objects.new('djHairStrands',data);bpy.context.collection.objects.link(live)
for factor in [.8,1,1.2,1.45]:
    mat=material('Chestnut hair variation',tuple(v*factor for v in (.048,.027,.014)),0,.47)
    mat.node_tree.nodes['Principled BSDF'].inputs['Anisotropic'].default_value=.5;data.materials.append(mat)
for poly,index in zip(data.polygons,live_mats):poly.material_index=index;poly.use_smooth=True
vg=live.vertex_groups.new(name='head');vg.add(list(range(len(data.vertices))),1,'REPLACE')
modifier=live.modifiers.new('Follow head','ARMATURE');modifier.object=rig;live.parent=rig
print('FITTED_HEAD_INTEGRATED',head_scale,'hair',len(curve.splines))
