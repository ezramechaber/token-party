"""Original sleeve printing and manufactured speaker/control details."""
# Matte paper sleeves retain separate front faces for runtime cover artwork.
sleeve_colors=[(.15,.24,.23),(.63,.31,.18),(.69,.64,.51),(.24,.30,.40)]
for n in range(8):
    obj=bpy.data.objects.get('sleeve'+str(n))
    if not obj:continue
    paper=material('Printed sleeve '+str(n%4),sleeve_colors[n%4],0,.93)
    obj.data.materials.clear();obj.data.materials.append(paper)
    # Modest graphic label, modeled and readable in the native render.
    z=.11+n*.075
    box('sleevePrint'+str(n),(-2.05,1.91,z),(.35,.055,.001),cream,0)
    bpy.ops.object.text_add(location=loc((-2.208,1.902,z+.001)))
    title=bpy.context.object;title.name='Sleeve typography '+str(n)
    title.rotation_euler=(math.pi/2,0,0)
    title.data.body=['BACK 2 BACK','SIDE A / 001','AFTERNOON','LISTENING ROOM'][n%4]
    title.data.size=.019;title.data.space_character=1.1;title.data.materials.append(black)
    bpy.ops.object.convert(target='MESH')
# Separate woofer surround, dust cap, tweeter waveguide and fasteners.
cone=material('Woven graphite speaker cone',(.025,.027,.028),0,.86)
rubber=material('Speaker rubber surround',(.012,.013,.014),0,.77)
for side,x in [('L',-2.9),('R',2.45)]:
    old=bpy.data.objects.get('speaker'+side)
    if old:x=old.location.x
    else:continue
    old.data.materials.clear();old.data.materials.append(material('Satin speaker cabinet '+side,(.027,.030,.030),0,.63))
    woofer=bpy.data.objects.get('speakerCone'+side)
    if woofer:
        woofer.location.z=1.12;woofer.data.materials.clear();woofer.data.materials.append(cone)
    ring=torus('wooferSurround'+side,(x,1.12,-.427),.18,.012,rubber);ring.rotation_euler[0]=math.pi/2
    sphere('wooferDustcap'+side,(x,1.12,-.39),(.067,.067,.018),rubber)
    ring=torus('tweeterWaveguide'+side,(x,1.49,-.438),.069,.009,rubber);ring.rotation_euler[0]=math.pi/2
    sphere('silkTweeter'+side,(x,1.49,-.424),(.043,.043,.02),black)
    for dx in [-.213,.213]:
        for y in [.88,1.59]:rod('speakerFastener'+side,(x+dx,y,-.455),(x+dx,y,-.442),.006,chrome)
# Recessed indicator marks rotate with the actual EQ control.
for side,x in [('A',-.15),('B',.15)]:
    for j,z in enumerate([.1,.29,.48]):
        knob=bpy.data.objects['eq'+side if j==2 else f'knob{side}{j}']
        mark=box('knobPointer'+side+str(j),(x,1.869,z+.024),(.007,.001,.025),black,0)
        mark.parent=knob;mark.matrix_parent_inverse=knob.matrix_world.inverted()
