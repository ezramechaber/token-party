# Character quality research — 2026-09-10

The user rejected the current visual quality as far from photorealistic. The current MakeHuman-based likeness, projected texture and procedural groom remain an unfinished prototype. Further detail alone does not resolve the underlying facial shape, eye and hair problems. No new quality-complete demo is claimed.

## Findings

- [KeenTools FaceBuilder](https://keentools.io/products/facebuilder-for-blender) fits head geometry to photographs using reference points, supports multiple views and non-neutral expressions, blends textures, and exports a mesh with facial blendshapes. The vendor lists macOS support and a 15-day trial. This is the strongest next experiment for recognizable personal likeness while retaining Blender. Tool availability does not guarantee a photorealistic result.
- [Meshy Image to 3D](https://help.meshy.ai/en/articles/9996860-how-to-use-meshy-image-to-3d) and [Tripo](https://docs.tripo3d.ai/) provide generated textured base models and export workflows. These could accelerate body/clothing or scene assets. Personal likeness and deformation quality must be evaluated on actual outputs; promotional claims are not validation.
- [MetaHuman 5.7](https://forums.unrealengine.com/t/metahuman-5-7-released/2672724) brought Creator to macOS. It remains an alternative human pipeline, but migrating the interactive scene into Unreal would be a larger change than replacing the head in Blender.
- [Human Generator asset terms](https://help.humgen3d.com/FAQ/Human%2BGenerator%2BAsset%2BLicense) restrict redistribution of its source assets. Do not include those assets in a public, extractable GLB without establishing compatible permission.

## User-supplied example

Opened [Alix Ollivier's Blender bat post](https://x.com/aollivier82/status/2096226819401801896) through computer use and watched multiple frames of its embedded video: Blender geometry, dense fur, Principled Hair shader nodes and a bat head close-up. This demonstrates a native Blender workflow; those frames alone do not establish photographic realism.

The author's [follow-up](https://x.com/aollivier82/status/2096259684025995386) explicitly describes the approach as slow and recommends generating the model with Tripo or Meshy, then having Astra rig and animate it. This supports improving the base asset before further procedural polishing.

## Next quality gate

Build and inspect one neutral-lit head close-up against the supplied photographs before reintegrating into the café. Evaluate face proportions, eyelids/visible irises, nose and mouth shape, glasses fit, hair silhouette and skin response. Inspect the same asset in Blender and the browser because shader/export differences have already caused defects. Keep the working audio and motion implementation intact.

Update, 15:35 EDT: Following the user’s acknowledgment of the pending EULA/trial request, FaceBuilder 2026.3.1 and its native core were installed and the trial activated. The approved generated portrait was fitted locally using 26 landmarks, baked into a UV texture, and integrated into the café. No purchase was made or personal photo uploaded to a candidate vendor. The ordinary scene rebuild uses the exported mesh and does not depend on the add-on.

The first chin adjustment was excessive, and neck weights distorted the lower face after integration. These were corrected by reducing chin widening to roughly 5.5% at its maximum, restricting neck fitting below the jaw and rigidly weighting the face to the head. Dense hair fibers and a separate scalp overlay caused a plug-like appearance; a continuous scalp surface with sparse fibers replaced them. Native and browser close-ups were inspected after these corrections. This is improved likeness, not a claim of completed photographic realism.
