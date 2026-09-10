"""Physical café surfacing, window architecture and botanical geometry."""
from mathutils import Vector
SURFACES=ROOT/'scene/assets/polyhaven'
def pbr(name,folder,normal_strength=.4):
    m=material(name,(.5,.5,.5),0,.7);nodes=m.node_tree.nodes;links=m.node_tree.links;bs=nodes.get('Principled BSDF')
    for kind,socket in [('Diffuse','Base Color'),('Rough','Roughness')]:
        node=image_node(m,SURFACES/folder/(kind+'.jpg'),'color' if kind=='Diffuse' else 'roughness');links.new(node.outputs['Color'],bs.inputs[socket])
    tex=image_node(m,SURFACES/folder/'nor_gl.jpg','normal');n=nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=normal_strength;links.new(tex.outputs['Color'],n.inputs['Color']);links.new(n.outputs['Normal'],bs.inputs['Normal'])
    return m
walnut=pbr('American walnut veneer','walnut',.25);wall=pbr('Painted mineral plaster','plaster',.25);terrazzo=pbr('Fine terrazzo floor','floor',.22)
# Warm oil finish multiplies the scan's neutral albedo; glTF preserves this factor.
nodes=walnut.node_tree.nodes;links=walnut.node_tree.links;bs=nodes.get('Principled BSDF')
source=bs.inputs['Base Color'].links[0].from_socket
tint=nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(.58,.28,.115,1)
links.new(source,tint.inputs[1]);links.new(tint.outputs['Color'],bs.inputs['Base Color'])
for obj in bpy.data.objects:
    if obj.type!='MESH':continue
    name=obj.name
    mat=None
    if name.startswith(('walnutSlat','booth','worktop','crate','banquetteBase','frame','windowFrame','windowCrossbar')):mat=walnut
    elif name in ['backWall','windowWall']:mat=wall
    elif name=='cafeFloor':mat=terrazzo
    if not mat:continue
    obj.data.materials.clear();obj.data.materials.append(mat)
    uv=obj.data.uv_layers.active or obj.data.uv_layers.new(name='Surface UV')
    for poly in obj.data.polygons:
        dominant=max(range(3),key=lambda i:abs(poly.normal[i]))
        axes=([1,2] if dominant==0 else [0,2] if dominant==1 else [0,1])
        for li in poly.loop_indices:
            co=obj.matrix_world@obj.data.vertices[obj.data.loops[li].vertex_index].co
            if name.startswith('walnutSlat'):coords=(co.x*.27,co.z*.45)
            elif name=='worktop':coords=(co.y*.5,co.x*.28)
            elif mat==terrazzo:coords=(co.x*.45,co.y*.45)
            else:coords=(co[axes[0]]*.45,co[axes[1]]*.45)
            uv.data[li].uv=coords
# Replace luminous opaque slabs with actual glazing and open window reveals.
glass=material('Architectural clear glass',(.90,.95,.93),0,.04);bs=glass.node_tree.nodes['Principled BSDF'];bs.inputs['Transmission Weight'].default_value=1;bs.inputs['IOR'].default_value=1.46
bpy.data.objects.remove(bpy.data.objects['windowWall'],do_unlink=True)
for obj in bpy.data.objects:
    if obj.name.startswith('windowPane'):obj.data.materials.clear();obj.data.materials.append(glass)
box('windowApron',(-4.25,.32,-.2),(.16,.64,4.7),wall,0)
box('windowLintel',(-4.25,4.56,-.2),(.16,.28,4.7),wall,0)
for z in [-2.49,1.75]:box('windowPier',(-4.25,2.55,z),(.17,3.86,.26),wall,.005)
box('windowSill',(-4.02,.69,-.42),(.54,.08,4.2),walnut,.018)
# A modeled courtyard beyond the glazing gives the room depth.
external=material('Courtyard limestone',(.55,.57,.51),0,.86)
box('courtyardPaving',(-5.6,-.10,0),(3,.1,8),external,0)
box('courtyardWall',(-7.08,2.05,0),(.2,4.1,9),wall,.015)
for z in [-2.2,.4,2.8]:
    box('courtyardRecess',(-6.95,2.65,z),(.035,1.7,1.25),dark,.01)
    for zz in [z-.66,z+.66]:box('courtyardMullion',(-6.88,2.65,zz),(.12,1.85,.075),wood_dark,.005)
# Directional late-afternoon sunlight through the real window apertures.
bpy.ops.object.light_add(type='SUN',location=loc((-6.0,5,2.5)));sun=bpy.context.object;sun.name='Afternoon sunlight';sun.data.energy=1.1;sun.data.angle=.055;sun.data.color=(1,.83,.65)
sun.rotation_euler=(Vector(loc((0,1.1,-.6)))-sun.location).to_track_quat('-Z','Y').to_euler()
bpy.data.objects['Window key'].data.energy=650;bpy.data.objects['Window key'].data.size=3
bpy.data.objects['Soft fill'].data.energy=100
for name in ['Window key','Soft fill']:
    light=bpy.data.objects[name];light.visible_glossy=False;light.visible_transmission=False
    light.data.specular_factor=0
    if hasattr(light.data,'transmission_factor'):light.data.transmission_factor=0
# Dense, pointed, folded leaves in place of inflated primitive ovals.
for obj in list(bpy.data.objects):
    if obj.name.startswith(('leaf','plantStem')):bpy.data.objects.remove(obj,do_unlink=True)
foliage=material('Ficus leaf surfaces',(.055,.115,.029),0,.48);bs=foliage.node_tree.nodes['Principled BSDF'];bs.inputs['Subsurface Weight'].default_value=.07
branchmat=material('Ficus bark',(.09,.05,.024),0,.9)
def plant(x,z,height,index,count=54):
    objects=[]
    objects.append(rod('ficusTrunk',(x,.4,z),(x+.06,height,z),.018,branchmat))
    for j in range(count):
        angle=j*2.399;yy=.64+(height-.65)*(j/count);radius=.18+.17*math.sin(j*1.7)**2
        tip=Vector((x+math.cos(angle)*radius,yy,z+math.sin(angle)*radius))
        stem=Vector((x+.03,yy-.07,z));objects.append(rod('ficusTwig',stem,tip,.0035,branchmat))
        direction=Vector((math.cos(angle)*.6,.55,math.sin(angle)*.6)).normalized();across=direction.cross(Vector((0,1,0))).normalized();normal=across.cross(direction).normalized()
        length=.20+.08*rng.random();width=.07+.025*rng.random();vertices=[];faces=[]
        for t in range(9):
            u=t/8
            for k in range(5):
                v=(k-2)/2;span=math.sin(math.pi*u)**.8*width
                pos=tip+direction*(u*length)+across*(v*span)+normal*(.014*abs(v)*math.sin(math.pi*u)-.035*u*u)
                vertices.append(loc(pos))
        for t in range(8):
            for k in range(4):faces.append((t*5+k,t*5+k+1,(t+1)*5+k+1,(t+1)*5+k))
        data=bpy.data.meshes.new('Ficus leaf');data.from_pydata(vertices,[],faces);obj=bpy.data.objects.new('ficusLeaf',data);bpy.context.collection.objects.link(obj);finish(obj,obj.name,foliage);objects.append(obj)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='Ficus'+str(index)
plant(-3.18,-1.25,1.7,0);plant(3.38,-1.76,2.05,1);plant(-5.65,.4,3.5,2,100)
# Long café seating, round tables and small brass pendants.
for name in ['banquetteBase','banquetteSeat','banquetteBack']:
    obj=bpy.data.objects.get(name)
    if obj:bpy.data.objects.remove(obj,do_unlink=True)
velvet=material('Deep teal upholstery',(.028,.10,.105),0,.92)
box('banquetteBase',(-2.8,.38,-1.91),(2.1,.68,.70),walnut,.025)
box('banquetteSeat',(-2.8,.77,-1.91),(2.1,.14,.76),velvet,.06)
box('banquetteBack',(-2.8,1.12,-2.20),(2.1,.72,.15),velvet,.045)
for i,x in enumerate([-3.2,-2.15]):
    cylinder('cafeTableTop',(x,1.09,-1.05),.37,.055,walnut)
    cylinder('cafeTableLeg',(x,.57,-1.05),.026,1,dark)
    cylinder('cafeTableFoot',(x,.08,-1.05),.23,.035,dark)
    cylinder('tableSaucer',(x+.1,1.132,-1.0),.073,.014,cream)
    cylinder('tableCup',(x+.1,1.18,-1.0),.043,.08,cream)
brass=material('Aged brass',(.32,.22,.085),.85,.34)
for i,x in enumerate([-2.6,1.8]):
    rod('pendantCable',(x,4.6,-1.45),(x,3.68,-1.45),.005,dark)
    cylinder('pendantShade',(x,3.65,-1.45),.19,.08,brass)
    cylinder('pendantDiffuser',(x,3.608,-1.45),.16,.009,window)
# Warm task lighting from the olive lamp; it stays a modeled open shade.
bpy.ops.object.light_add(type='POINT',location=loc((2.95,2.03,-.75)));bpy.context.object.name='Olive lamp practical';bpy.context.object.data.energy=16;bpy.context.object.data.color=(1,.68,.36);bpy.context.object.data.shadow_soft_size=.16
