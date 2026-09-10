"""Repair reference-background spill on the far cheek/neck from the matching side."""
from pathlib import Path
import bpy
from keentools.addon_config import fb_settings
ROOT=Path(__file__).resolve().parents[1]
obj=fb_settings().get_current_head().headobj
mat=obj.data.materials[0];nodes=mat.node_tree.nodes;links=mat.node_tree.links
bs=nodes.get('Principled BSDF');out=nodes.get('Material Output')
original=bs.inputs['Base Color'].links[0].from_node
mask=obj.data.color_attributes.new(name='Neck projection repair',type='FLOAT_COLOR',domain='POINT')
def smooth(a,b,x):
    t=min(1,max(0,(x-a)/(b-a)));return t*t*(3-2*t)
for v in obj.data.vertices:
    x,y,z=v.co
    amount=smooth(.42,.64,x)*(1-smooth(-.2,.15,z))*smooth(-1.0,-.65,y)
    mask.data[v.index].color=(amount,amount,amount,1)
layer=obj.data.uv_layers.new(name='Opposite side');source=obj.data.uv_layers['UVMap'] if 'UVMap' in obj.data.uv_layers else obj.data.uv_layers[0]
for a,b in zip(layer.data,source.data):a.uv=(1-b.uv.x,b.uv.y)
uv=nodes.new('ShaderNodeUVMap');uv.uv_map=layer.name
mirror=nodes.new('ShaderNodeTexImage');mirror.image=original.image;links.new(uv.outputs['UV'],mirror.inputs['Vector'])
attr=nodes.new('ShaderNodeVertexColor');attr.layer_name=mask.name
mix=nodes.new('ShaderNodeMixRGB');links.new(attr.outputs['Color'],mix.inputs[0]);links.new(original.outputs['Color'],mix.inputs[1]);links.new(mirror.outputs['Color'],mix.inputs[2])
emission=nodes.new('ShaderNodeEmission');links.new(mix.outputs[0],emission.inputs[0]);links.new(emission.outputs[0],out.inputs['Surface'])
atlas=bpy.data.images.new('Ezra fitted skin refined',width=2048,height=2048,alpha=False)
target=nodes.new('ShaderNodeTexImage');target.image=atlas;nodes.active=target
obj.data.uv_layers.active=source;source.active_render=True
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
old=bpy.context.scene.cycles.samples;bpy.context.scene.cycles.samples=1
bpy.ops.object.bake(type='EMIT',margin=16,use_clear=True)
bpy.context.scene.cycles.samples=old
links.new(bs.outputs[0],out.inputs['Surface']);links.new(target.outputs['Color'],bs.inputs['Base Color'])
for node in list(nodes):
    if node not in [bs,out,target]:nodes.remove(node)
obj.data.uv_layers.remove(layer);obj.data.color_attributes.remove(mask);atlas.pack()
exec(compile((ROOT/'scene/export_fitted_head.py').read_text(),'export_fitted_head.py','exec'))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'.b2b/likeness/fitted-head-study.blend'),compress=True)
print('NECK_PROJECTION_REPAIRED')
