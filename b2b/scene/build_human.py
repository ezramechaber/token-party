"""Connected, clothed DJ built from licensed CC0 MakeHuman graphical assets.
Executed inside the visible Blender application by build_booth.py.
"""
import json
from collections import defaultdict
from mathutils import Matrix, Vector
from mathutils.kdtree import KDTree

ASSETS=ROOT/'scene/assets/makehuman'
SYSTEM=ASSETS/'system'

def read_obj(path):
    vertices=[];uvs=[];faces=[];face_uvs=[];groups=[];group=''
    for line in path.read_text().splitlines():
        s=line.split()
        if not s:continue
        if s[0]=='v':vertices.append(Vector(map(float,s[1:4])))
        elif s[0]=='vt':uvs.append(tuple(map(float,s[1:3])))
        elif s[0]=='g':group=s[1]
        elif s[0]=='f':
            parts=[p.split('/') for p in s[1:]]
            faces.append([int(p[0])-1 for p in parts]);face_uvs.append([int(p[1])-1 if len(p)>1 and p[1] else 0 for p in parts]);groups.append(group)
    return vertices,uvs,faces,face_uvs,groups

base,uvs,faces,face_uvs,groups=read_obj(ASSETS/'base.obj')
shaped=[p.copy() for p in base]
for filename,weight in [('caucasian-male-young.target',1),('universal-male-young-averagemuscle-averageweight.target',1)]:
    for line in (ASSETS/filename).read_text().splitlines():
        s=line.split()
        if len(s)==4 and s[0].isdigit():shaped[int(s[0])]+=Vector(map(float,s[1:]))*weight

# Reference-led proportion adjustments; all changes remain editable.
# Widen eye spacing locally and soften the lower face relative to the neutral base.
for p in shaped:
    if p.y>6.9 and p.z>.45:
        front=min(1,max(0,(p.z-.45)/.5))
        eye=math.exp(-((abs(p.x)-.31)/.32)**2-((p.y-8.22)/.30)**2)
        p.x+=(1 if p.x>0 else -1 if p.x<0 else 0)*.075*eye*front
        jaw=math.exp(-((p.y-7.33)/.40)**2)
        p.x*=1+.09*jaw*front
        nose=math.exp(-(p.x/.20)**2-((p.y-7.82)/.24)**2)
        p.z-=.10*nose*front

SCALE=.218
OFFSET=Vector((0,1.81,-.63))
def to_world(p):return Vector(loc((p.x*SCALE+OFFSET.x,p.y*SCALE+OFFSET.y,p.z*SCALE+OFFSET.z)))

# Remove the entire previous assembled figure, including parented facial pieces.
prefixes=('torso','waist','neck','head','hair','sweptHair','ear','nose','eye','brow','mouth','shoulder','upperArm','forearm','elbow','hand','leg','shoe')
for obj in list(bpy.data.objects):
    if obj.name.startswith(prefixes) and not obj.name.startswith('headshell'):bpy.data.objects.remove(obj,do_unlink=True)

spec=json.loads((ASSETS/'default.mhskel').read_text())
weights=json.loads((ASSETS/'default_weights.mhw').read_text())['weights']
rename={}
for native,side in [('R','L'),('L','R')]:
    for part,dest in [('upperarm01','upperArm'),('upperarm02','upperArm'),('lowerarm01','forearm'),('lowerarm02','forearm'),('wrist','hand')]:rename[f'{part}.{native}']=dest+side
rename['spine01']='torso';rename['spine04']='waist'
def mapped(name):return rename.get(name,name)
def joint(key):return sum((shaped[i] for i in spec['joints'][key]),Vector())/len(spec['joints'][key])

rigdata=bpy.data.armatures.new('DJ anatomical skeleton');rig=bpy.data.objects.new('djRig',rigdata);bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
for native,b in spec['bones'].items():
    if native.startswith(('upperarm02.','lowerarm02.')):continue
    name=mapped(native);bone=rigdata.edit_bones.new(name)
    tail=b['tail']
    if native.startswith('upperarm01.'):tail=spec['bones'][native.replace('01.','02.')]['tail']
    if native.startswith('lowerarm01.'):tail=spec['bones'][native.replace('01.','02.')]['tail']
    bone.head=to_world(joint(b['head']));bone.tail=to_world(joint(tail))
    if (bone.tail-bone.head).length<.001:bone.tail.z+=.005
    bone.align_roll(Vector((0,-1,0)))
for native,b in spec['bones'].items():
    if native.startswith(('upperarm02.','lowerarm02.')):continue
    name=mapped(native);parent=mapped(b['parent']) if b['parent'] else None
    if parent and parent!=name:rigdata.edit_bones[name].parent=rigdata.edit_bones[parent]
bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True;rig['version']='anatomical-v2'

# Per-vertex skin weights, collapsed from the split twist bones and normalized.
per_vertex=defaultdict(lambda:defaultdict(float))
for bone,entries in weights.items():
    for i,w in entries:per_vertex[i][mapped(bone)]+=w
for i,ws in per_vertex.items():
    best=sorted(ws.items(),key=lambda v:v[1],reverse=True)[:4];total=sum(w for _,w in best)
    per_vertex[i]={b:w/total for b,w in best if total and w>0}
body_ids=sorted({v for f,g in zip(faces,groups) if g=='body' for v in f})
kd=KDTree(len(body_ids))
for i in body_ids:kd.insert(shaped[i],i)
kd.balance()

def make_mesh(name,points,mesh_faces,uvcoords,uvindices,vertex_weights,mat):
    data=bpy.data.meshes.new(name);data.from_pydata([to_world(v) for v in points],[],mesh_faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);data.materials.append(mat)
    layer=data.uv_layers.new(name='UVMap')
    for poly,uvface in zip(data.polygons,uvindices):
        poly.use_smooth=True
        for li,ui in zip(poly.loop_indices,uvface):layer.data[li].uv=uvcoords[ui]
    group_cache={}
    for vi,ws in enumerate(vertex_weights):
        for bone,w in ws.items():
            if w<=.0001 or bone not in rigdata.bones:continue
            vg=group_cache.get(bone)
            if vg is None:vg=obj.vertex_groups.new(name=bone);group_cache[bone]=vg
            vg.add([vi],w,'REPLACE')
    modifier=obj.modifiers.new('DJ skin deformation','ARMATURE');modifier.object=rig;obj.parent=rig
    return obj

def image_node(mat,path,kind='color'):
    image=bpy.data.images.load(str(path),check_existing=True)
    if max(image.size)>2048:image.scale(2048,2048)
    if kind!='color':image.colorspace_settings.name='Non-Color'
    image.pack();node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;return node

def mh_material(path,name,roughness=.6,skin=False,hair=False):
    settings={}
    for line in path.read_text().splitlines():
        s=line.split()
        if s and not s[0].startswith('#'):settings[s[0]]=s[1:]
    m=material(name,(.7,.7,.7),0,roughness);bs=m.node_tree.nodes.get('Principled BSDF');links=m.node_tree.links
    if 'diffuseTexture' in settings:
        tex=image_node(m,path.parent/settings['diffuseTexture'][0]);links.new(tex.outputs['Color'],bs.inputs['Base Color'])
        if hair or settings.get('transparent')==['True']:
            links.new(tex.outputs['Alpha'],bs.inputs['Alpha']);m.surface_render_method='DITHERED';m.use_transparent_shadow=True
    if 'normalmapTexture' in settings:
        p=path.parent/settings['normalmapTexture'][0]
        if p.exists():
            tex=image_node(m,p,'normal');n=m.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.55;links.new(tex.outputs['Color'],n.inputs['Color']);links.new(n.outputs['Normal'],bs.inputs['Normal'])
    if skin:
        bs.inputs['Subsurface Weight'].default_value=.30;bs.inputs['Subsurface Radius'].default_value=(1,.5,.3);bs.inputs['Subsurface Scale'].default_value=.0025
        bs.inputs['IOR'].default_value=1.4;bs.inputs['Specular IOR Level'].default_value=.3
        noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1700;noise.inputs['Detail'].default_value=2
        coordinate=m.node_tree.nodes.new('ShaderNodeTexCoord');links.new(coordinate.outputs['Object'],noise.inputs['Vector'])
        bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.23;bump.inputs['Distance'].default_value=.00014;links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    if hair:bs.inputs['Roughness'].default_value=.72;bs.inputs['Anisotropic'].default_value=.3;bs.inputs['Specular IOR Level'].default_value=.2
    return m

skinmat=mh_material(SYSTEM/'skins/young_caucasian_male2/young_caucasian_male2.mhmat','DJ natural skin',.5,skin=True)
# Restrict body to external mesh; helpers are used for fitting only.
lookup={old:new for new,old in enumerate(body_ids)}
body_faces=[[lookup[i] for i in f] for f,g in zip(faces,groups) if g=='body']
body_uv=[f for f,g in zip(face_uvs,groups) if g=='body']
body=make_mesh('djBody',[shaped[i] for i in body_ids],body_faces,uvs,body_uv,[per_vertex[i] for i in body_ids],skinmat)

# MHCLO barycentric fitting adapts clothes/hair/eyes to the morphed base.
def fit_asset(relative,name,material_override=None,hair=False):
    folder=SYSTEM/relative;file=next(folder.glob('*.mhclo'));settings={};refs=[];deletes=set();mode='header'
    for line in file.read_text().splitlines():
        s=line.split()
        if not s or s[0].startswith('#'):continue
        if s[0]=='verts':mode='verts';continue
        if s[0]=='delete_verts':mode='delete';continue
        if mode=='verts' and s[0][0].isdigit():
            if len(s)==1:refs.append(([int(s[0])],[1.],Vector()))
            else:refs.append((list(map(int,s[:3])),list(map(float,s[3:6])),Vector(map(float,s[6:9]))))
        elif mode=='delete' and (s[0][0].isdigit()):
            last=None;expand=False
            for token in s:
                if token=='-':expand=True;continue
                num=int(token)
                if expand and last is not None:deletes.update(range(last,num+1));expand=False
                else:deletes.add(num)
                last=num
        else:settings[s[0]]=s[1:]
    old,auv,afaces,afuv,_=read_obj(folder/settings['obj_file'][0]);scales=Vector((1,1,1))
    for axis,key in enumerate(['x_scale','y_scale','z_scale']):
        if key in settings:
            a,b,den=settings[key];scales[axis]=abs(shaped[int(a)][axis]-shaped[int(b)][axis])/float(den)
    points=[];vweights=[]
    for indices,ws,offset in refs:
        p=sum((shaped[i]*w for i,w in zip(indices,ws)),Vector())+Vector([offset[j]*scales[j] for j in range(3)]);points.append(p)
        accum=defaultdict(float)
        near=kd.find_n(p,4)
        for _,i,d in near:
            factor=1/max(d,.015)**3
            for bone,w in per_vertex[i].items():accum[bone]+=w*factor
        top=sorted(accum.items(),key=lambda p:p[1],reverse=True)[:4];total=sum(w for _,w in top)
        vweights.append({bone:w/total for bone,w in top} if total else {'head':1})
    assert len(points)==len(old),(name,len(points),len(old))
    mat=material_override or mh_material(folder/settings['material'][0],name+' material',hair=hair)
    obj=make_mesh(name,points,afaces,auv,afuv,vweights,mat)
    return obj,deletes

clothes,hidden=fit_asset('clothes/male_casualsuit04','djGarments')
# Plain black cotton tee, preserving the asset's modeled folds and separate jeans.
cotton=material('Ezra black cotton',(.012,.015,.019),0,.94)
cotton.node_tree.nodes['Principled BSDF'].inputs['Sheen Weight'].default_value=.12
cotton.node_tree.nodes['Principled BSDF'].inputs['Sheen Tint'].default_value=(.12,.12,.12,1)
cotton.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value=.15
source_material=clothes.data.materials[0]
source_normal=next((n for n in source_material.node_tree.nodes if n.type=='TEX_IMAGE' and 'normal' in n.image.name),None)
if source_normal:
    tex=cotton.node_tree.nodes.new('ShaderNodeTexImage');tex.image=source_normal.image
    normal=cotton.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.45
    cotton.node_tree.links.new(tex.outputs['Color'],normal.inputs['Color']);cotton.node_tree.links.new(normal.outputs['Normal'],cotton.node_tree.nodes['Principled BSDF'].inputs['Normal'])
clothes.data.materials.append(cotton)
# Shirt and jeans are disconnected garment islands. Classify complete islands
# so a height cutoff cannot paint a jagged black edge onto the jeans.
neighbors=[set() for _ in clothes.data.vertices]
for face in clothes.data.polygons:
    for i in face.vertices:neighbors[i].update(face.vertices)
unseen=set(range(len(neighbors)));shirt_ids=set()
while unseen:
    stack=[unseen.pop()];island=[]
    while stack:
        i=stack.pop();island.append(i);found=neighbors[i]&unseen;unseen-=found;stack.extend(found)
    if max(clothes.data.vertices[i].co.z for i in island)>2.5:shirt_ids.update(island)
for face in clothes.data.polygons:
    if face.vertices[0] in shirt_ids:face.material_index=1

# Cotton creases around the tucked waist and the shoulder/underarm tension lines.
for v in clothes.data.vertices:
    x,y,z=v.co
    if z<2.02 or z>3.16:continue
    lower=math.exp(-((z-2.18)/.22)**2)
    underarm=math.exp(-((abs(x)-.35)/.20)**2-((z-2.82)/.25)**2)
    displacement=.009*lower*math.sin(z*61+x*12)+.005*underarm*math.sin(z*49+abs(x)*36)
    v.co+=v.normal*(.012+displacement)
clothes.data.update()
# Submillimeter crossed threads break up highlights without visible color noise.
node_tree=cotton.node_tree;bs=node_tree.nodes.get('Principled BSDF')
coord=node_tree.nodes.new('ShaderNodeTexCoord')
noise=node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2600;noise.inputs['Roughness'].default_value=.65
node_tree.links.new(coord.outputs['Object'],noise.inputs['Vector'])
bump=node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.26;bump.inputs['Distance'].default_value=.00010
node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height'])
if bs.inputs['Normal'].is_linked:node_tree.links.new(bs.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

hairmesh,_=fit_asset('hair/short02','djHair',hair=True)
eye_mat=mh_material(SYSTEM/'eyes/materials/bluegreen.mhmat','DJ blue green eyes',.22)
eyes,_=fit_asset('eyes/high-poly','djEyes',material_override=eye_mat)
eye_bs=eye_mat.node_tree.nodes.get('Principled BSDF');eye_bs.inputs['Coat Weight'].default_value=.85;eye_bs.inputs['Coat Roughness'].default_value=.03
brows,_=fit_asset('eyebrows/eyebrow001','djBrows',hair=True)
lashes,_=fit_asset('eyelashes/eyelashes01','djLashes',hair=True)
shoes,_=fit_asset('clothes/shoes04','djShoes')
# Hide only the body polygons covered by the supplied garment's explicit mask.
import bmesh
bm=bmesh.new();bm.from_mesh(body.data);bm.faces.ensure_lookup_table()
covered=[f for f in bm.faces if any(body_ids[v.index] in hidden for v in f.verts)]
bmesh.ops.delete(bm,geom=covered,context='FACES');bm.to_mesh(body.data);bm.free()
for obj in [body,clothes,hairmesh,eyes,brows,lashes,shoes]:
    if obj in [body,clothes]:
        sub=obj.modifiers.new('Surface refinement','SUBSURF');sub.levels=1;sub.render_levels=2
        if obj==clothes:
            hem=obj.modifiers.new('Cotton hem thickness','SOLIDIFY');hem.thickness=.002;hem.offset=0

# Natural forward lean originates in the lower spine, preserving a connected body.
rig.pose.bones['waist'].rotation_mode='XYZ';rig.pose.bones['waist'].rotation_euler.x=math.radians(30)
rig.pose.bones['neck01'].rotation_mode='XYZ';rig.pose.bones['neck01'].rotation_euler.x=math.radians(-7)
rig.pose.bones['head'].rotation_mode='XYZ';rig.pose.bones['head'].rotation_euler.x=math.radians(-8)
bpy.context.view_layer.update()
# Two-bone IK constraints are baked to rotations by export; same joints drive browser IK.
for side,x in [('L',-.20),('R',.20)]:
    target=bpy.data.objects.new('wristTarget'+side,None);bpy.context.collection.objects.link(target);target.location=loc((x,1.93,.28));target.empty_display_type='SPHERE';target.empty_display_size=.045
    pole=bpy.data.objects.new('elbowPole'+side,None);bpy.context.collection.objects.link(pole);pole.location=loc(((-1 if side=='L' else 1)*1.3,2.25,-.5));pole.empty_display_size=.04
    c=rig.pose.bones['forearm'+side].constraints.new('IK');c.target=target;c.chain_count=2;c.pole_target=pole;c.pole_angle=0;c.use_stretch=False
bpy.context.view_layer.update()
# Bake constraint result into pose matrices, then solve each wrist palm-down.
matrices={b.name:b.matrix.copy() for b in rig.pose.bones}
for bone in rig.pose.bones:
    for c in list(bone.constraints):bone.constraints.remove(c)
# Parent-first pose assignment.
def depth(b):return 0 if b.parent is None else 1+depth(b.parent)
for b in sorted(rig.pose.bones,key=depth):b.matrix=matrices[b.name];bpy.context.view_layer.update()
for side,native in [('L','R'),('R','L')]:
    b=rig.pose.bones['hand'+side];p=b.matrix.translation.copy()
    wrist=joint(spec['bones']['wrist.'+native]['head'])
    index=joint(spec['bones']['finger2-1.'+native]['head'])
    pinky=joint(spec['bones']['finger5-1.'+native]['head'])
    middle=joint(spec['bones']['finger3-1.'+native]['head'])
    across=Vector(loc(index-pinky)).normalized()
    forward=Vector(loc(middle-wrist)).normalized();forward=(forward-across*forward.dot(across)).normalized()
    normal=across.cross(forward).normalized()
    rest=Matrix((across,forward,normal)).transposed()
    target_across=Vector((1 if side=='L' else -1,0,0))
    target_forward=Vector(loc((0,-.243,.97))).normalized()
    target_normal=target_across.cross(target_forward).normalized()
    desired=Matrix((target_across,target_forward,target_normal)).transposed()
    orientation=(desired @ rest.transposed() @ b.bone.matrix_local.to_3x3()).to_4x4()
    orientation.translation=p;b.matrix=orientation
bpy.context.view_layer.update()
# Record the exact rig/targets in scene extras for the browser driver and QA.
rig['armLengths']={s:[rigdata.bones['upperArm'+s].length,rigdata.bones['forearm'+s].length] for s in ['L','R']}
print('DJ_CONNECTED_CHARACTER',len(body.data.vertices),'body vertices',len(rigdata.bones),'bones')

# Original over-ear headphones, rigidly skinned to the head bone.
ear_y=joint(spec['bones']['eye.L']['head']).y-.10
crown_y=joint(spec['bones']['head']['tail']).y+.04
headphone_parts=[]
leather=material('Headphone leather',(.012,.014,.016),0,.78)
metal=material('Headphone brushed aluminum',(.13,.15,.17),.85,.32)
def hp_sphere(name,source,scale,mat):
    p=to_world(Vector(source));o=sphere(name,(p.x,p.z,-p.y),scale,mat);headphone_parts.append(o);return o
for sign in [-1,1]:
    hp_sphere('earPad', (sign*.92,ear_y,.30),(.050,.105,.079),leather)
    hp_sphere('earCup', (sign*1.10,ear_y,.30),(.043,.094,.071),dark)
    hp_sphere('earCupInset', (sign*1.235,ear_y,.30),(.012,.055,.045),metal)
    p=to_world(Vector((sign*.97,ear_y+.31,.27)));q=to_world(Vector((sign*.92,ear_y-.01,.30)))
    headphone_parts.append(rod('headphoneHinge',(p.x,p.z,-p.y),(q.x,q.z,-q.y),.014,metal))
# One continuous padded band, avoiding visible cylinder endcaps.
band_vertices=[];band_faces=[]
for i in range(65):
    a=math.pi*i/64
    center=to_world(Vector((1.03*math.cos(a),ear_y+.18+(crown_y-ear_y-.18)*math.sin(a),.23)))
    radial=Vector((math.cos(a),0,math.sin(a)))
    for j in range(12):
        t=2*math.pi*j/12
        band_vertices.append(center+radial*(.013*math.cos(t))+Vector((0,.028*math.sin(t),0)))
for i in range(64):
    for j in range(12):band_faces.append((i*12+j,i*12+(j+1)%12,(i+1)*12+(j+1)%12,(i+1)*12+j))
mesh=bpy.data.meshes.new('Continuous padded headphone band');mesh.from_pydata(band_vertices,[],band_faces);mesh.update()
band=bpy.data.objects.new('Headphone band',mesh);bpy.context.collection.objects.link(band);finish(band,band.name,leather);headphone_parts.append(band)
bpy.ops.object.select_all(action='DESELECT')
for o in headphone_parts:o.select_set(True)
bpy.context.view_layer.objects.active=headphone_parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='djHeadphones'
vg=o.vertex_groups.new(name='head');vg.add(list(range(len(o.data.vertices))),1,'REPLACE');mod=o.modifiers.new('Follow head','ARMATURE');mod.object=rig;o.parent=rig
# Store the resting pose independently of export behavior for the live driver.
rig['restPose']={b.name:list(b.matrix_basis.to_quaternion()) for b in rig.pose.bones}

# Rounded rectangular translucent acetate spectacles, modeled from the reference.
acetate=material('Translucent olive acetate',(.58,.68,.53),0,.12)
bs=acetate.node_tree.nodes['Principled BSDF'];bs.inputs['Transmission Weight'].default_value=.78;bs.inputs['IOR'].default_value=1.47
lens_mat=material('Clear spectacle lenses',(.94,.98,.96),0,.025)
bs=lens_mat.node_tree.nodes['Principled BSDF'];bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.46
spectacle_parts=[]
def rounded_loop(cx,cy,cz,w,h,r):
    pts=[]
    for x,y,start in [(cx+w/2-r,cy+h/2-r,0),(cx-w/2+r,cy+h/2-r,90),(cx-w/2+r,cy-h/2+r,180),(cx+w/2-r,cy-h/2+r,270)]:
        for k in range(9):
            a=math.radians(start+k*90/8);pts.append((x+r*math.cos(a),y+r*math.sin(a),cz))
    return pts
centers=[]
for sign,native in [(-1,'R'),(1,'L')]:
    source=joint(spec['bones']['eye.'+native]['head']);center=to_world(source);center.y-=.078;center.x+=sign*.022;center.z-=.008
    cx,cy,cz=center.x,center.z,-center.y;centers.append((cx,cy,cz))
    loop=rounded_loop(cx,cy,cz,.160,.104,.033)
    curve=bpy.data.curves.new('Continuous rounded acetate rim','CURVE');curve.dimensions='3D';curve.bevel_depth=.0020;curve.bevel_resolution=3
    spline=curve.splines.new('POLY');spline.points.add(len(loop)-1);spline.use_cyclic_u=True
    for point,xyz in zip(spline.points,loop):point.co=(*loc(xyz),1)
    rim=bpy.data.objects.new('Acetate rim',curve);bpy.context.collection.objects.link(rim);curve.materials.append(acetate)
    bpy.ops.object.select_all(action='DESELECT');rim.select_set(True);bpy.context.view_layer.objects.active=rim;bpy.ops.object.convert(target='MESH')
    for face in rim.data.polygons:face.use_smooth=True
    spectacle_parts.append(rim)
    verts=[loc((cx,cy,cz))]+[loc(p) for p in loop];f=[(0,i+1,(i+1)%len(loop)+1) for i in range(len(loop))]
    data=bpy.data.meshes.new('Optical lens');data.from_pydata(verts,[],f);obj=bpy.data.objects.new('spectacleLens',data);bpy.context.collection.objects.link(obj);finish(obj,'spectacleLens',lens_mat);spectacle_parts.append(obj)
    end=(cx+sign*.081,cy+.025,cz-.003);back=(sign*.19,cy+.02,cz-.24)
    spectacle_parts.append(rod('acetateTemple',end,back,.0045,acetate))
    spectacle_parts.append(rod('templeTip',back,(back[0],back[1]-.045,back[2]-.045),.005,acetate))
a,b=centers
spectacle_parts.append(rod('glassesBridge',(a[0]+.075,a[1]+.025,a[2]),(b[0]-.075,b[1]+.025,b[2]),.003,metal))
bpy.ops.object.select_all(action='DESELECT')
for o in spectacle_parts:o.select_set(True)
bpy.context.view_layer.objects.active=spectacle_parts[0];bpy.ops.object.join();o=bpy.context.object;o.name='djGlasses'
vg=o.vertex_groups.new(name='head');vg.add(list(range(len(o.data.vertices))),1,'REPLACE');mod=o.modifiers.new('Follow head','ARMATURE');mod.object=rig;o.parent=rig

head_script='integrate_fitted_head.py' if (ROOT/'scene/assets/likeness/fitted-head.blend').exists() else 'refine_likeness.py'
exec(compile((ROOT/'scene'/head_script).read_text(), head_script, 'exec'))

bpy.context.view_layer.update()
rig['poseBaked']=True
rig['posePositions']={name:[rig.pose.bones[name].head.x,rig.pose.bones[name].head.z,-rig.pose.bones[name].head.y] for name in ['upperArmL','forearmL','handL','upperArmR','forearmR','handR','head']}

exec(compile((ROOT/"scene/bake_character_rest.py").read_text(),"bake_character_rest.py","exec"))
