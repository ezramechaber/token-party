"""Keep the approved visible-face bake, using autofill only in missing areas."""
from pathlib import Path
import bpy
from keentools.addon_config import fb_settings
ROOT=Path(__file__).resolve().parents[1]
obj=fb_settings().get_current_head().headobj
mat=obj.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links
bs=nodes.get('Principled BSDF');out=nodes.get('Material Output')
filled=bs.inputs['Base Color'].links[0].from_socket
original=nodes.new('ShaderNodeTexImage');original.image=bpy.data.images.load(str(ROOT/'.b2b/likeness/facebuilder-skin.png'),check_existing=True)
mix=nodes.new('ShaderNodeMixRGB');links.new(original.outputs['Alpha'],mix.inputs[0]);links.new(filled,mix.inputs[1]);links.new(original.outputs['Color'],mix.inputs[2])
emission=nodes.new('ShaderNodeEmission');links.new(mix.outputs[0],emission.inputs[0]);links.new(emission.outputs[0],out.inputs['Surface'])
atlas=bpy.data.images.new('Ezra fitted skin complete',width=2048,height=2048,alpha=False)
target=nodes.new('ShaderNodeTexImage');target.image=atlas;nodes.active=target
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
old=bpy.context.scene.cycles.samples;bpy.context.scene.cycles.samples=1
bpy.ops.object.bake(type='EMIT',margin=16,use_clear=True)
bpy.context.scene.cycles.samples=old
links.new(bs.outputs[0],out.inputs['Surface']);links.new(target.outputs['Color'],bs.inputs['Base Color'])
for node in list(nodes):
    if node not in [bs,out,target]:nodes.remove(node)
atlas.pack()
exec(compile((ROOT/'scene/export_fitted_head.py').read_text(),'export_fitted_head.py','exec'))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'.b2b/likeness/fitted-head-study.blend'),compress=True)
print('APPROVED_FACE_TEXTURE_PRESERVED')
