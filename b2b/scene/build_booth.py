"""Build our original human DJ and listening-café booth. Run: blender -b --python scene/build_booth.py.
Coordinates in helpers use browser space: x right, y up, z toward audience.
No downloaded models, textures, music, or album artwork are embedded.
"""
from pathlib import Path
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def loc(p): return (p[0], -p[2], p[1])
def material(name, color, metal=0, rough=.3, emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metal; bs.inputs['Roughness'].default_value=rough
    if emission:
        bs.inputs['Emission Color'].default_value=(*color,1); bs.inputs['Emission Strength'].default_value=emission
    return m
chrome=material('Brushed liquid chrome',(.66,.71,.75),1,.2)
dark=material('Graphite rubber',(.025,.031,.039),.3,.38)
white=material('Warm ceramic',(.8,.78,.71),.1,.3)
pink=material('Rose signal',(.95,.24,.44),.3,.24,1)
blue=material('Ice signal',(.22,.63,.96),.3,.24,1)
black=material('Black vinyl',(.009,.012,.015),.15,.36)
skin=material('Warm skin',(.56,.34,.23),0,.7)
hair=material('Ink black hair',(.015,.019,.022),0,.72)
shirt=material('Washed midnight cotton',(.052,.072,.073),0,.92)
trousers=material('Charcoal trousers',(.055,.06,.064),0,.9)
wood=material('Walnut',(.105,.040,.018),0,.65)
wood_light=material('Walnut edge',(.16,.066,.029),0,.62)
wood_dark=material('Walnut shadow',(.055,.017,.009),0,.8)
plaster=material('Warm lime plaster',(.77,.735,.66),0,.97)
cream=material('Uncoated paper',(.84,.80,.68),0,.9)
green=material('Olive enamel',(.15,.23,.092),.15,.35)
leaf=material('Plant green',(.09,.20,.065),0,.8)
terracotta=material('Clay pots',(.46,.23,.13),0,.92)
window=material('Warm window light',(.96,.83,.60),0,.9,.35)


def finish(o,name,mat):
    o.name=name; o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    return o

def sphere(name,p,scale,mat=chrome):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=loc(p))
    o=bpy.context.object;o.scale=(scale[0],scale[2],scale[1]);return finish(o,name,mat)

def box(name,p,size,mat=dark,bevel=.05):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc(p));o=bpy.context.object
    o.scale=(size[0],size[2],size[1]);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        b=o.modifiers.new('Soft manufactured edges','BEVEL');b.width=bevel;b.segments=3
        bpy.ops.object.modifier_apply(modifier=b.name)
    return finish(o,name,mat)

def cylinder(name,p,radius,depth,mat=chrome):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth,location=loc(p))
    return finish(bpy.context.object,name,mat)

def rod(name,a,b,r=.07,mat=chrome):
    a,b=Vector(loc(a)),Vector(loc(b));d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=d.length,location=(a+b)/2)
    o=bpy.context.object;o.rotation_mode='QUATERNION';o.rotation_quaternion=d.to_track_quat('Z','Y')
    return finish(o,name,mat)

# Human DJ: a quiet, stylized fashion figure, with clothing and natural facial details.
# Semantic rig names remain compatible with the browser's two-bone animation.
sphere('torso',(0,2.43,-.46),(.43,.52,.25),shirt)
sphere('waist',(0,1.94,-.46),(.30,.25,.21),trousers)
sphere('neck',(0,2.98,-.46),(.105,.19,.10),skin)
head=sphere('head',(0,3.29,-.44),(.255,.335,.23),skin)
head_parts=[]
def face(name,p,scale,mat):
    o=sphere(name,p,scale,mat);head_parts.append(o);return o
face('hairCrown',(0,3.52,-.48),(.265,.135,.24),hair)
face('hairBack',(0,3.38,-.61),(.25,.27,.10),hair)
for i in range(7):
    tuft=face('sweptHair'+str(i),(-.20+i*.060,3.50-i*.014,-.283),(.075,.10,.07),hair)
    tuft.rotation_euler[1]=-.4
face('earL',(-.255,3.28,-.44),(.038,.064,.04),skin)
face('earR',(.255,3.28,-.44),(.038,.064,.04),skin)
face('nose',(0,3.28,-.206),(.038,.060,.047),skin)
for side,x in [('L',-.088),('R',.088)]:
    face('eye'+side,(x,3.325,-.222),(.023,.009,.007),hair)
    face('brow'+side,(x,3.359,-.231),(.038,.007,.009),hair)
    face('headphone'+side,(-.29 if side=='L' else .29,3.30,-.45),(.067,.12,.087),dark)
face('mouth',(0,3.16,-.219),(.049,.008,.004),wood_dark)
# Headphone arch follows the crown, with understated metal adjustment hinges.
for i in range(15):
    a=math.pi*i/15;b=math.pi*(i+1)/15
    o=rod('headband'+str(i),(.305*math.cos(a),3.31+.32*math.sin(a),-.46),(.305*math.cos(b),3.31+.32*math.sin(b),-.46),.022,dark);head_parts.append(o)
for o in head_parts:
    matrix=o.matrix_world.copy();o.parent=head;o.matrix_world=matrix
for side,x in [('L',-.47),('R',.47)]:
    shoulder=(x,2.75,-.46);elbow=(x*1.5,2.15,-.1);hand=(x,1.79,.45)
    sphere('shoulder'+side,shoulder,(.15,.15,.15),shirt)
    rod('upperArm'+side,shoulder,elbow,.117,shirt)
    sphere('elbow'+side,elbow,(.098,.098,.098),skin)
    rod('forearm'+side,elbow,hand,.075,skin)
    sphere('hand'+side,hand,(.085,.05,.135),skin)
    rod('leg'+side,(x*.48,1.92,-.46),(x*.55,.25,-.47),.145,trousers)
    sphere('shoe'+side,(x*.55,.17,-.30),(.17,.105,.28),dark)
# Slatted walnut listening counter, modeled rather than a flat texture.
box('booth',(0,.86,.46),(3.8,1.36,1.25),wood_dark,.09)
box('boothPlinth',(0,.17,.46),(3.58,.18,1.10),wood,.04)
for i in range(57):
    x=-1.85+i*3.7/56
    box('walnutSlat'+str(i),(x,.875,1.105),(.037,1.30,.065),wood_light if i%4==0 else wood,.012)
box('worktop',(0,1.57,.46),(3.97,.14,1.42),wood_light,.055)
for i,x in enumerate([-.94,.94]):
    side='A' if i==0 else 'B'; accent=pink if i==0 else blue
    box('deck'+side,(x,1.69,.43),(1.1,.1,1.12),dark,.025)
    cylinder('platter'+side,(x,1.77,.55),.38,.055,dark)
    cylinder('recordLabel'+side,(x,1.802,.55),.11,.008,accent)
    box('screen'+side,(x,1.753,.06),(.54,.014,.19),black,.015)
    cylinder('play'+side,(x-.39,1.76,.86),.045,.016,accent)
box('mixer',(0,1.71,.48),(.58,.16,1.14),dark,.04)
for i,x in enumerate([-.15,.15]):
    side='A' if i==0 else 'B'
    for n,z in enumerate([.1,.29,.48]):
        cylinder(('eq'+side if n==2 else f'knob{side}{n}'),(x,1.825,z),.049,.085,chrome)
    box('channelRail'+side,(x,1.8,.7),(.016,.015,.23),black,.005)
    box('channelFader'+side,(x,1.823,.7),(.092,.044,.054),white,.01)
box('crossfaderRail',(0,1.809,.93),(.42,.014,.025),black,.005)
box('crossfader',(0,1.838,.93),(.075,.049,.077),white,.012)
# Side crate, card slots are populated with current cover art in the browser.
box('crate',(-2.05,1.5,.34),(.66,.45,.79),wood,.025)
box('crateStand',(-2.05,.77,.34),(.58,1.05,.70),wood_dark,.025)
box('crateInner',(-2.05,1.735,.34),(.53,.018,.66),black,.01)
for n in range(8):
    box('sleeve'+str(n),(-2.05,1.87,.10+n*.075),(.48,.38,.014),white if n%2 else chrome,.012)
for side,x in [('L',-2.5),('R',2.5)]:
    box('speaker'+side,(x,1.23,-.7),(.54,.89,.49),dark,.08)
    sphere('speakerCone'+side,(x,1.23,-.43),(.185,.185,.03),black)
    cylinder('speakerStand'+side,(x,.43,-.7),.025,.68,dark)
    box('speakerFoot'+side,(x,.09,-.7),(.42,.04,.36),dark,.02)

# Warm café architecture. Original abstract geometry, no copied artwork or logos.
box('cafeFloor',(0,-.035,0),(9,.10,7.5),plaster,.0)
box('backWall',(0,2.35,-2.5),(8.7,4.7,.12),plaster,.0)
box('windowWall',(-4.25,2.35,-.2),(.12,4.7,4.7),plaster,.0)
for i in range(3):
    z=-1.75+i*1.33
    box('windowPane'+str(i),(-4.16,2.55,z),(.025,3.6,1.24),window,.0)
    for zz in [z-.65,z+.65]:box('windowFrame'+str(i)+str(zz),(-4.10,2.55,zz),(.09,3.74,.06),wood_dark,.008)
for y in [.7,2.55,4.4]:box('windowCrossbar'+str(y),(-4.10,y,-.42),(.09,.07,4.1),wood_dark,.008)
# Picture frames and understated geometric prints behind the decks.
for n,(x,y,w,h) in enumerate([(-1.8,3.10,.85,1.1),(-.45,3.66,.82,.85),(1.2,3.35,.93,1.1)]):
    box('frame'+str(n),(x,y,-2.39),(w+.06,h+.06,.07),wood_dark,.008)
    box('printPaper'+str(n),(x,y,-2.34),(w,h,.015),cream,.0)
    if n==2:
        for j in range(6):
            xx=x-.33+j*.12
            box('abstractLine'+str(j),(xx,y,-2.321),(.055,h*.70,.009),terracotta,.003)
    else:
        for j in range(4):
            sphere('abstractShape'+str(n)+str(j),(x+math.sin(j*2)*w*.21,y+(j-1.5)*h*.18,-2.32),(w*.20,h*.115,.007),hair)
# Olive mushroom floor lamp, softened daylight and foliage.
cylinder('lampBase',(2.95,.10,-.75),.27,.06,green)
cylinder('lampStem',(2.95,1.08,-.75),.043,1.95,green)
sphere('lampShade',(2.95,2.16,-.75),(.42,.23,.42),green)
cylinder('lampGlow',(2.95,2.06,-.75),.33,.016,window)
for n,(x,z,height) in enumerate([(-3.18,-1.25,1.60),(3.38,-1.76,1.90)]):
    cylinder('pot'+str(n),(x,.27,z),.25,.5,terracotta)
    rod('plantStem'+str(n),(x,.50,z),(x,height,z),.025,wood_dark)
    for j in range(11):
        angle=j*2.4;yy=.67+j*(height-.6)/11
        dx=math.cos(angle)*.25;dz=math.sin(angle)*.24
        rod('leafStem'+str(n)+str(j),(x,yy-.1,z),(x+dx,yy,z+dz),.012,leaf)
        o=sphere('leaf'+str(n)+str(j),(x+dx,yy+.10,z+dz),(.12,.24,.036),leaf)
        o.rotation_euler[1]=angle;o.rotation_euler[0]=.35
# A small coffee cup on the outer edge of the counter.
cylinder('cupSaucer',(1.75,1.655,.88),.11,.014,cream)
cylinder('coffeeCup',(1.75,1.714,.88),.068,.105,cream)
cylinder('coffee',(1.75,1.769,.88),.052,.005,wood_dark)

bpy.context.scene.world.color=(.18,.18,.18)
# Camera/light setup makes the source .blend useful when opened directly.
bpy.ops.object.camera_add(location=loc((5.1,4.1,6.6)))
cam=bpy.context.object;cam.name='Overview camera'
cam.rotation_euler=(Vector(loc((-.1,1.7,.1)))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=8.3;bpy.context.scene.camera=cam
for name,p,power,size in [('Window key',(-3.8,4,1),1400,4),('Soft fill',(2,5,4),550,5)]:
    bpy.ops.object.light_add(type='AREA',location=loc(p));l=bpy.context.object;l.name=name;l.data.energy=power;l.data.shape='DISK';l.data.size=size
    l.rotation_euler=(Vector(loc((0,1.5,0)))-l.location).to_track_quat('-Z','Y').to_euler()
bpy.context.scene.render.engine='CYCLES';bpy.context.scene.cycles.samples=24
bpy.context.scene.render.resolution_x=1600;bpy.context.scene.render.resolution_y=900;bpy.context.scene.render.resolution_percentage=100
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene'/'b2b-booth.blend'))
bpy.ops.export_scene.gltf(filepath=str(ROOT/'web'/'scene'/'b2b-booth.glb'),export_format='GLB',export_cameras=False,export_lights=False,export_apply=True)
print('B2B_SCENE_EXPORTED',len(bpy.data.objects),'objects')

if '--preview' in __import__('sys').argv:
    bpy.context.scene.render.resolution_x=1200;bpy.context.scene.render.resolution_y=800
    bpy.context.scene.render.filepath=str(ROOT/'.b2b'/'cafe-preview.png')
    bpy.ops.render.render(write_still=True)
