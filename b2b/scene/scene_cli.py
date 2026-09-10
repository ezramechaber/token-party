"""Repeatable Blender CLI inspection, rebuild and render entry point."""
import argparse
import json
import sys
from pathlib import Path
import bpy

parser=argparse.ArgumentParser()
parser.add_argument('--rebuild',action='store_true')
parser.add_argument('--view',choices=['room','portrait'])
parser.add_argument('--samples',type=int)
parser.add_argument('--output',type=Path)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
root=Path(__file__).resolve().parent
if args.rebuild:
    path=root/'build_booth.py'
    exec(compile(path.read_text(),str(path),'exec'),{'__file__':str(path)})
if args.view:
    path=root/('render_preview.py' if args.view=='room' else 'render_portrait.py')
    exec(compile(path.read_text(),str(path),'exec'),{'bpy':bpy,'RENDER':False})
    if args.samples:
        if args.samples<1:parser.error('--samples must be positive')
        bpy.context.scene.cycles.samples=args.samples
    if args.output:bpy.context.scene.render.filepath=str(args.output.resolve())
    bpy.ops.render.render(write_still=True)
print('B2B_CLI_RESULT',json.dumps({'file':bpy.data.filepath,'objects':len(bpy.context.scene.objects),'meshes':sum(o.type=='MESH' for o in bpy.context.scene.objects),'packed_images':sum(i.packed_file is not None for i in bpy.data.images),'render':bpy.context.scene.render.filepath if args.view else None}))
