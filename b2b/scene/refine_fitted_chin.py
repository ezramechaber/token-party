"""Reference correction requested after reviewing the first fitted-head render."""
import bpy,math
from pathlib import Path
from keentools.addon_config import fb_settings
ROOT=Path(__file__).resolve().parents[1]
obj=fb_settings().get_current_head().headobj
if not obj.get('chin_reference_correction'):
    for v in obj.data.vertices:
        x,y,z=v.co
        front=min(1,max(0,(-y-.05)/.45))
        lower=math.exp(-((z+.67)/.24)**2)
        jaw=math.exp(-((z+.43)/.30)**2)
        v.co.x*=1+front*(.12*lower+.025*jaw)
    obj.data.update();obj['chin_reference_correction']=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'.b2b/likeness/fitted-head-study.blend'),compress=True)
exec(compile((ROOT/'scene/export_fitted_head.py').read_text(),'export_fitted_head.py','exec'))
bpy.context.scene.cycles.samples=48
bpy.context.scene.render.filepath=str(ROOT/'.b2b/likeness/fitted-head-chin-review.png')
bpy.ops.render.render('INVOKE_DEFAULT',write_still=True)
