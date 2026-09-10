"""Render the personalized DJ close-up in the visible Blender application."""
from pathlib import Path
from mathutils import Vector
scene=bpy.context.scene
camera=scene.camera
camera.location=(.65,-2.25,3.13)
camera.rotation_euler=(Vector((0,-.06,3.25))-camera.location).to_track_quat('-Z','Y').to_euler()
camera.data.lens=55
scene.render.resolution_x=1000
scene.render.resolution_y=1200
scene.render.resolution_percentage=100
scene.cycles.samples=128
scene.render.filepath=str(Path(bpy.data.filepath).parent/'dj-portrait.png')
if globals().get('RENDER',True):
    bpy.ops.render.render('EXEC_DEFAULT' if bpy.app.background else 'INVOKE_DEFAULT',write_still=True)
