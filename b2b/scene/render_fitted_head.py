"""Texture and inspect the fitted head in the visible Blender application."""
from pathlib import Path
import json
import bpy
from mathutils import Vector
from keentools.addon_config import fb_settings
from keentools.facebuilder.fbloader import FBLoader
from keentools.utils.materials import bake_tex

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'.b2b/likeness'
settings=fb_settings(); index=settings.current_headnum; head=settings.get_head(index)
FBLoader.save_fb_serial_and_image_pathes(index)
settings.tex_width=2048;settings.tex_height=2048
settings.tex_fill_gaps=True
result=bake_tex(index,head.preview_texture_name())
assert result.success,result.error_message
obj=head.headobj; obj.name='Ezra fitted head'
for poly in obj.data.polygons:poly.use_smooth=True
tex=bpy.data.images.get(head.preview_texture_name());tex.pack()
tex.filepath_raw=str(out/'facebuilder-skin.png');tex.file_format='PNG';tex.save()
mat=bpy.data.materials.new('Ezra fitted skin');mat.use_nodes=True
n=mat.node_tree.nodes;links=mat.node_tree.links;bs=n.get('Principled BSDF')
t=n.new('ShaderNodeTexImage');t.image=tex;links.new(t.outputs['Color'],bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value=.48
bs.inputs['Subsurface Weight'].default_value=.16
bs.inputs['Subsurface Scale'].default_value=.008
bs.inputs['Subsurface Radius'].default_value=(1,.48,.26)
obj.data.materials.clear();obj.data.materials.append(mat)
scene=bpy.context.scene;scene.camera=head.cameras[0].camobj
cam=scene.camera;cam.data.show_background_images=False
center=obj.matrix_world@sum((v.co for v in obj.data.vertices),Vector())/len(obj.data.vertices)
camera_q=cam.rotation_euler.to_quaternion();right=camera_q@Vector((1,0,0));up=camera_q@Vector((0,1,0));front=camera_q@Vector((0,0,1))
span=max(obj.dimensions)
for name,offset,power,size in [('Portrait softbox',right*-span+up*span*.75+front*span,420,span),('Portrait fill',right*span+front*span,100,span*1.5)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    light=bpy.data.objects.new(name,data);scene.collection.objects.link(light);light.location=center+offset
    light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
world=bpy.data.worlds.new('Portrait neutral world');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.18,.18,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35;scene.world=world
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
scene.render.filepath=str(out/'fitted-head-review.png')
report={'head':list(obj.location),'dimensions':list(obj.dimensions),'camera':list(cam.location),'rotation':list(cam.rotation_euler),'focal':cam.data.lens,'vertex_count':len(obj.data.vertices),'pins':head.cameras[0].pins_count}
(out/'fit-report.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out/'fitted-head-study.blend'),compress=True)
bpy.ops.render.render('INVOKE_DEFAULT',write_still=True)
