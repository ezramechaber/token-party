# Personalized skin atlas

## Current fitted head

`fitted-head.blend` contains the exported, unrigged head mesh and its packed derived skin texture. `fitted-head-anchors.json` records eye/nose/chin anchors used to attach it to the café rig. The approved generated reference was fitted with KeenTools FaceBuilder 2026.3.1 in the visible Blender application. A restrained lower-chin correction followed user review. Missing texture regions were filled using FaceBuilder, then Blender baked a composite preserving the previously approved visible-face texture. Original photo/reference files and the FaceBuilder study remain private and are not packed into this asset.

The ordinary café builder loads this result without requiring FaceBuilder. [KeenTools states that created results belong to the creator](https://keentools.io/products/facebuilder-for-blender). The proprietary core and installer are not redistributed. To build a generic fork, remove both `fitted-head.blend` and the older personalized atlas before rebuilding.

## Earlier atlas retained for fallback

`ezra-skin.png` is a Blender UV bake derived from a generated, evenly lit frontal reference based on the user's three supplied portraits, with their explicit request to make the DJ resemble them. It contains facial color/stubble detail and blends into the original MakeHuman skin. Geometry remains fully three-dimensional and deformable.

Reference generation direction: preserve the person's visible identity and proportions; use a straight-on neutral face and neck, remove glasses for clean facial projection, preserve pores and light stubble, use flat even lighting, remove the screenshot cursor, and avoid cosmetic smoothing. The close frontal photograph was the primary identity reference, with the other two for consistency. The imagegen tool was used September 10, 2026. Source photographs and the intermediate reference are private and are not required to rebuild from this baked atlas.

`refine_likeness.py` first uses this atlas when present. If it is absent, it optionally bakes an ignored local `.b2b/likeness/neutral-face.png`. With neither present, the character uses the generic CC0 MakeHuman skin instead. To make a generic fork, remove the personalized atlas before rebuilding. Do not describe this derivative likeness as a third-party CC0 asset or as an endorsement by the depicted person.
