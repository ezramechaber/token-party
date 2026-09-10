"""Start a visible reference render from Blender's Python Console."""
from pathlib import Path
from mathutils import Vector
scene=bpy.context.scene
camera=scene.camera
camera.location=(5.6,-7.9,3.7)
camera.rotation_euler=(Vector((-.25,.4,1.95))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.type='PERSP';camera.data.lens=46
scene.render.resolution_x=1500
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.cycles.samples=96
scene.render.filepath=str(Path(bpy.data.filepath).parent/'cafe-reference.png')
if globals().get('RENDER',True):
    bpy.ops.render.render('EXEC_DEFAULT' if bpy.app.background else 'INVOKE_DEFAULT',write_still=True)
