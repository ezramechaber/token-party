"""Export only the fitted mesh and derived texture, excluding reference photos."""
from pathlib import Path
import bpy,json
from mathutils import Vector
from keentools.addon_config import fb_settings
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'scene/assets/likeness';folder.mkdir(exist_ok=True)
head=fb_settings().get_current_head();obj=head.headobj;cam=head.cameras[0].camobj
deps=bpy.context.evaluated_depsgraph_get()
projection=cam.calc_matrix_camera(deps,x=1254,y=1254)
def hit(u,v):
    p=projection.inverted()@Vector((2*u-1,2*v-1,-1,1));p=Vector(p[:3])/p.w
    origin=obj.matrix_world.inverted()@cam.matrix_world.translation
    direction=obj.matrix_world.inverted().to_3x3()@(cam.matrix_world.to_3x3()@p.normalized())
    found,co,normal,index=obj.ray_cast(origin,direction)
    assert found,(u,v)
    return list(co)
anchors={name:hit(*uv) for name,uv in {'eyeL':(.385,.528),'eyeR':(.609,.528),'nose':(.489,.380),'chin':(.5,.110),'brow':(.50,.600)}.items()}
anchors['bounds']={axis:[min(v.co[i] for v in obj.data.vertices),max(v.co[i] for v in obj.data.vertices)] for i,axis in enumerate('xyz')}
(folder/'fitted-head-anchors.json').write_text(json.dumps(anchors,indent=2))
clean=obj.copy();clean.data=obj.data.copy();clean.name='Ezra fitted head asset';clean.parent=None
for key in list(clean.keys()):del clean[key]
clean.animation_data_clear()
for m in clean.modifiers:clean.modifiers.remove(m)
bpy.data.libraries.write(str(folder/'fitted-head.blend'),{clean},compress=True)
bpy.data.objects.remove(clean)
print('FITTED_HEAD_ASSET_EXPORTED',anchors)
