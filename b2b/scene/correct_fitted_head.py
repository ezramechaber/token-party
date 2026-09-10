"""Reduce the chin adjustment and fill unobserved texture regions natively."""
from pathlib import Path
import bpy,math
from keentools.addon_config import fb_settings
from keentools.utils.materials import bake_tex
ROOT=Path(__file__).resolve().parents[1]
settings=fb_settings();head=settings.get_current_head();obj=head.headobj
if not obj.get('subtle_chin_correction'):
    for v in obj.data.vertices:
        x,y,z=v.co;front=min(1,max(0,(-y-.05)/.45))
        lower=math.exp(-((z+.67)/.24)**2);jaw=math.exp(-((z+.43)/.30)**2)
        v.co.x*=(1+front*(.045*lower+.01*jaw))/(1+front*(.12*lower+.025*jaw))
    obj.data.update();obj['subtle_chin_correction']=True
settings.tex_fill_gaps=True
result=bake_tex(settings.current_headnum,head.preview_texture_name())
assert result.success,result.error_message
image=bpy.data.images[head.preview_texture_name()];image.pack()
for node in obj.data.materials[0].node_tree.nodes:
    if node.type=='TEX_IMAGE':node.image=image
exec(compile((ROOT/'scene/export_fitted_head.py').read_text(),'export_fitted_head.py','exec'))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'.b2b/likeness/fitted-head-study.blend'),compress=True)
bpy.context.scene.render.filepath=str(ROOT/'.b2b/likeness/corrected-head-review.png')
bpy.ops.render.render('INVOKE_DEFAULT',write_still=True)
