"""Build our original human DJ and listening-café booth. Run from the visible Blender Python Console; see README.md.
Coordinates in helpers use browser space: x right, y up, z toward audience.
CC0 MakeHuman body and fitted assets are added by build_human.py; see assets/PROVENANCE.md.
No music or album artwork is embedded.
"""
from pathlib import Path
import math
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
# Delete hidden guide objects too, so repeated rebuilds do not accumulate them.
for previous in list(bpy.context.scene.objects):
    bpy.data.objects.remove(previous,do_unlink=True)

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
    finish(o,name,mat)
    if not bevel:
        for polygon in o.data.polygons:polygon.use_smooth=False
    else:
        normal=o.modifiers.new('Weighted manufactured normals','WEIGHTED_NORMAL');normal.keep_sharp=True;normal.weight=50
    return o

def cylinder(name,p,radius,depth,mat=chrome):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth,location=loc(p))
    return finish(bpy.context.object,name,mat)

def rod(name,a,b,r=.07,mat=chrome):
    a,b=Vector(loc(a)),Vector(loc(b));d=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=d.length,location=(a+b)/2)
    o=bpy.context.object;o.rotation_mode='QUATERNION';o.rotation_quaternion=d.to_track_quat('Z','Y')
    return finish(o,name,mat)

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
exec(compile((ROOT/'scene'/'refine_cafe.py').read_text(), 'refine_cafe.py', 'exec'))
exec(compile((ROOT/'scene'/'build_human.py').read_text(), 'build_human.py', 'exec'))
exec(compile((ROOT/'scene'/'refine_environment.py').read_text(), 'refine_environment.py', 'exec'))
exec(compile((ROOT/"scene/polish_objects.py").read_text(),"polish_objects.py","exec"))
bpy.context.preferences.filepaths.save_version=0
bpy.data.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'scene'/'b2b-booth.blend'),compress=True)
# glTF cannot export Blender Bump nodes faithfully; omit rather than mislabel color as a normal map.
normal_links=[]
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    for link in list(mat.node_tree.links):
        if link.to_socket.name=='Normal' and link.from_node.type=='BUMP':
            source,target=link.from_socket,link.to_socket
            underlying=link.from_node.inputs['Normal']
            fallback=underlying.links[0].from_socket if underlying.is_linked else None
            normal_links.append((mat,source,target));mat.node_tree.links.remove(link)
            if fallback:mat.node_tree.links.new(fallback,target)
groom=bpy.data.objects.get('djCyclesHairGroom')
if groom:groom.hide_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'web'/'scene'/'b2b-booth.glb'),export_format='GLB',export_cameras=False,export_lights=False,export_apply=True,export_rest_position_armature=False,export_current_frame=True,export_extras=True,export_image_format='JPEG',export_jpeg_quality=85,use_visible=True)
if groom:groom.hide_set(False)
for mat,source,target in normal_links:mat.node_tree.links.new(source,target)
print('B2B_SCENE_EXPORTED',len(bpy.data.objects),'objects')

if '--preview' in __import__('sys').argv:
    bpy.context.scene.render.resolution_x=1200;bpy.context.scene.render.resolution_y=800
    bpy.context.scene.render.filepath=str(ROOT/'scene'/'cafe-reference.png')
    bpy.ops.render.render(write_still=True)
