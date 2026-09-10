"""Fit the approved private portrait in the visible Blender app.

Requires an installed, licensed/trial FaceBuilder. Run from Blender's console;
does not accept agreements or purchase licenses. Creating a first head may
start an already-authorized trial. The study stays private.
"""
from pathlib import Path
import bpy
from keentools.addon_config import fb_settings
from keentools.facebuilder.fbloader import FBLoader
from keentools.utils.images import load_rgba
from keentools.utils.coords import update_head_mesh_non_neutral
from keentools.utils.focal_length import configure_focal_mode_and_fixes

ROOT = Path(__file__).resolve().parents[1]
reference = ROOT / '.b2b/likeness/neutral-face.png'
assert reference.exists(), 'Approved reference image is required'

study = bpy.data.scenes.new('Ezra reference head study')
bpy.context.window.scene = study
bpy.ops.keentools_fb.add_head()
settings = fb_settings()
headnum = settings.current_headnum
head = settings.get_head(headnum)
assert head and head.headobj, 'FaceBuilder head creation failed'
head.headobj.name = 'Ezra fitted head'
camera = FBLoader.add_new_camera_with_image(headnum, str(reference))
settings.current_camnum = 0
FBLoader.save_fb_serial_and_image_pathes(headnum)
builder=FBLoader.get_builder()
detected=builder.detect_faces(load_rgba(camera),builder.pixel_aspect_ratio(camera.get_keyframe()))
assert len(detected)==1,'Expected one face in the approved portrait'
builder.set_use_emotions(head.should_use_emotions())
configure_focal_mode_and_fixes(builder,head)
assert builder.detect_face_pose(camera.get_keyframe(),detected[0]),'Face alignment failed'
builder.remove_pins(camera.get_keyframe())
builder.add_preset_pins_and_solve(camera.get_keyframe())
update_head_mesh_non_neutral(builder,head)
FBLoader.update_camera_pins_count(headnum,0)
FBLoader.update_all_camera_positions(headnum)
FBLoader.update_all_camera_focals(headnum)
FBLoader.save_fb_serial_and_image_pathes(headnum)
study.camera = camera.camobj
settings.tex_width = 2048
settings.tex_height = 2048
settings.tex_auto_preview = True
bpy.context.view_layer.objects.active = head.headobj
head.headobj.select_set(True)
print('REFERENCE_HEAD_ALIGNED', headnum, camera.pins_count)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / '.b2b/likeness/fitted-head-study.blend'),
                          compress=True)
