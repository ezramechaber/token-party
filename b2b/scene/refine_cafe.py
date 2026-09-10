"""Original, deterministic surface and hardware pass. Executed by build_booth.py."""
import numpy as np

rng=np.random.default_rng(20260910)
def texture_material(mat, kind, size=512):
    y,x=np.mgrid[0:size,0:size]/size
    noise=rng.normal(0,1,(size,size))
    if kind=='wood':
        warp=x+0.008*np.sin(y*19)+0.003*np.sin(y*43+x*11)
        grain=(np.sin(warp*530)+.4*np.sin(warp*1290))*.045
        broad=.07*np.sin(warp*67+np.sin(y*4))
        field=np.clip(.72+grain+broad+noise*.014,.45,1)
    elif kind=='fabric':
        field=np.clip(.83+.08*np.sin(x*1600)*np.sin(y*1600)+noise*.025,.6,1)
    else:
        field=np.clip(.88+.035*np.sin(x*31)*np.cos(y*26)+noise*.019,.65,1)
    color=np.array(mat.diffuse_color[:3]); pixels=np.ones((size,size,4),dtype=np.float32)
    # Encode generated pixels as sRGB for the image texture color-space conversion.
    linear=field[:,:,None]*color
    pixels[:,:,:3]=np.where(linear<=.0031308,linear*12.92,1.055*np.power(linear,1/2.4)-.055)
    img=bpy.data.images.new(mat.name+' original surface',width=size,height=size)
    img.pixels.foreach_set(pixels.ravel());img.pack()
    nodes=mat.node_tree.nodes; links=mat.node_tree.links;bs=nodes.get('Principled BSDF')
    tex=nodes.new('ShaderNodeTexImage');tex.image=img;links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16
    bump.inputs['Distance'].default_value=.009 if kind=='wood' else .003
    links.new(tex.outputs['Color'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    # Explicit UVs survive glTF export. Bump is offline only; base color is shared.
    for obj in bpy.data.objects:
        if obj.type!='MESH' or mat not in list(obj.data.materials):continue
        mesh=obj.data;uv=mesh.uv_layers.active or mesh.uv_layers.new(name='Surface UV')
        lo=np.array([min(v.co[i] for v in mesh.vertices) for i in range(3)])
        hi=np.array([max(v.co[i] for v in mesh.vertices) for i in range(3)])
        extent=np.maximum(hi-lo,.001)
        for face in mesh.polygons:
            normal=face.normal; axis=max(range(3),key=lambda i:abs(normal[i]))
            axes=([1,2] if axis==0 else [0,2] if axis==1 else [1,0])
            for li in face.loop_indices:
                p=mesh.vertices[mesh.loops[li].vertex_index].co
                uv.data[li].uv=((p[axes[0]]-lo[axes[0]])/extent[axes[0]],(p[axes[1]]-lo[axes[1]])/extent[axes[1]])

for m in [wood,wood_light,wood_dark]:texture_material(m,'wood')
for m in [shirt,trousers]:texture_material(m,'fabric')
for m in [plaster,terracotta]:texture_material(m,'plaster')
chrome.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.29
skin.node_tree.nodes['Principled BSDF'].inputs['Subsurface Weight'].default_value=.08

def torus(name,p,major,minor,mat):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=64,minor_segments=8,location=loc(p))
    return finish(bpy.context.object,name,mat)

def lettering(name,body,p,size,mat):
    bpy.ops.object.text_add(location=loc(p));o=bpy.context.object;o.name=name
    o.data.body=body;o.data.size=size;o.data.extrude=.0002;o.data.materials.append(mat)
    # Text lies on the top panel, readable from the audience side.
    bpy.ops.object.convert(target='MESH')

for side,x in [('A',-.94),('B',.94)]:
    # Platter machining, concentric vinyl grooves, spindle and articulated tonearm.
    for n in range(6):torus('machinedRim'+side+str(n),(x,1.755+n*.005,.55),.379,.0025,chrome)
    for n in range(22):torus('vinylGroove'+side+str(n),(x,1.799,.55),.13+n*.0108,.0008,black)
    cylinder('spindle'+side,(x,1.82,.55),.009,.041,chrome)
    cylinder('tonearmPivot'+side,(x+.40,1.795,.11),.052,.115,chrome)
    rod('tonearmRear'+side,(x+.40,1.848,.11),(x+.40,1.848,.43),.012,chrome)
    rod('tonearmBend'+side,(x+.40,1.848,.43),(x+.27,1.843,.72),.012,chrome)
    box('headshell'+side,(x+.255,1.825,.745),(.045,.027,.10),dark,.004)
    rod('stylus'+side,(x+.255,1.815,.76),(x+.255,1.801,.76),.003,chrome)
    box('pitchSlot'+side,(x+.46,1.75,.69),(.017,.01,.30),black,.002)
    box('pitchSlider'+side,(x+.46,1.767,.70),(.062,.02,.026),chrome,.003)
    for j in range(11):box('pitchMark'+side+str(j),(x+.495,1.751,.55+j*.026),(.015,.003,.002),white,0)
    lettering('deckMark'+side,'B / 2 / B  •  DIRECT DRIVE',(x-.48,1.745,.10),.026,white)
    for dx in [-.49,.49]:
        for z in [-.07,.93]:
            cylinder('panelScrew'+side,(x+dx,1.747,z),.009,.003,chrome)
    # Dark label replaces the toy-like glowing center while preserving its anchor.
    obj=bpy.data.objects['recordLabel'+side];obj.data.materials.clear();obj.data.materials.append(cream)
for side,x in [('A',-.15),('B',.15)]:
    for j,z in enumerate([.1,.29,.48]):
        lettering('eqLegend'+side+str(j),['HI','MID','LOW'][j],(x-.026,1.798,z+.08),.018,white)
    for j in range(9):
        box('meter'+side+str(j),(x+(.085 if side=='A' else -.085),1.797,.72-j*.033),(.017,.004,.02),green if j<6 else terracotta,.002)
lettering('mixerMark','BACK 2 BACK',(-.20,1.797,-.03),.034,white)
# Hollow ceramic rim and curved handle, without a sealed cylinder top.
torus('cupLip',(1.75,1.77,.88),.060,.008,cream)
handle=torus('cupHandle',(1.827,1.717,.88),.035,.009,cream);handle.rotation_euler[0]=math.pi/2
# Replace the flattened oval shade with a genuine open-bottom hemisphere.
bpy.data.objects.remove(bpy.data.objects['lampShade'],do_unlink=True)
verts=[];faces=[]
for j in range(13):
    theta=(j/12)*math.pi/2
    for i in range(64):
        a=i*math.tau/64;verts.append(loc((2.95+.42*math.sin(theta)*math.cos(a),2.06+.29*math.cos(theta),-.75+.42*math.sin(theta)*math.sin(a))))
for j in range(12):
    for i in range(64):faces.append((j*64+i,j*64+(i+1)%64,(j+1)*64+(i+1)%64,(j+1)*64+i))
mesh=bpy.data.meshes.new('Spun shade');mesh.from_pydata(verts,[],faces);obj=bpy.data.objects.new('lampShade',mesh);bpy.context.collection.objects.link(obj);finish(obj,'lampShade',green)
solid=obj.modifiers.new('Enamel shell thickness','SOLIDIFY');solid.thickness=.007
# A café bench grounds the room beyond the booth.
box('banquetteBase',(-2.9,.32,-1.75),(1.35,.6,.75),wood_dark,.025)
box('banquetteSeat',(-2.9,.66,-1.72),(1.35,.15,.73),shirt,.045)
box('banquetteBack',(-2.9,1.02,-2.06),(1.35,.72,.13),shirt,.04)
# Perspective and restrained light ratios remove the orthographic toy presentation.
cam.data.type='PERSP';cam.data.lens=46
cam.location=loc((5.6,3.7,7.9));cam.rotation_euler=(Vector(loc((-.25,1.95,-.4)))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.data.objects['Window key'].data.energy=1000;bpy.data.objects['Window key'].data.size=2.5
bpy.data.objects['Soft fill'].data.energy=130
world=bpy.context.scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.25,.29,.34,1);world.node_tree.nodes['Background'].inputs[1].default_value=.22
bpy.context.scene.cycles.samples=64;bpy.context.scene.cycles.use_denoising=True
bpy.context.scene.view_settings.view_transform='AgX'
