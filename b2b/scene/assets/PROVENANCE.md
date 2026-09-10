# Scene asset provenance

The scene combines original hackathon modeling, adaptation and animation with the following pre-existing graphical assets. They are not claimed as original hackathon work.

## MakeHuman Community graphical data — CC0 1.0

Downloaded September 10, 2026 from the official repositories and [core system asset pack](https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html). The archive source is https://files2.makehumancommunity.org/asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip.

- Base mesh: https://github.com/makehumancommunity/makehuman/blob/master/makehuman/data/3dobjs/base.obj
- Base SHA-256: `8e761e6624b8f54536409135d1636da63b32486a90d4897f84e121d144f6fb4c`.
- Anatomical skeleton, skin weights and the two retained shape targets: official MakeHuman `makehuman/data/` assets.
- Fitted assets: `male_casualsuit04`, `shoes04`, `short02`, `eyebrow001`, `eyelashes01`, high-poly eyes with blue-green texture, and the young male skin atlas.
- Rights holders identified by the asset headers include Data Collection AB, Joel Palmius and Jonas Hauquier (2020). Each selected mesh/fitting definition retains its original CC0 notice. Upstream `LICENSE.md` and `LICENSE.ASSETS.md` are preserved alongside the base mesh. No MakeHuman application code is included.

Adaptation: full connected body, fitted tee and jeans, individualized face proportions and skin color, skinning to a consolidated arm skeleton, resting pose, wrist orientation, brown hair detail and runtime two-bone inverse kinematics. The black tee material, glasses, headphones and additional hair strands are original project work.

## Poly Haven surface scans — CC0 1.0

[Poly Haven's asset license](https://polyhaven.com/license) permits modification and redistribution. `polyhaven/manifest.json` preserves exact download URLs, MD5 digests, authors and source pages for all nine original maps. Assets: American walnut veneer, painted plaster wall and terrazzo tiles. A warm finish is applied to the walnut in Blender and in the browser. `fetch_surfaces.py` can verify or restore the maps from that manifest.

## Personalized likeness

At the user's explicit request, their three supplied photographs informed the character's face proportions, brown swept hair, clear olive frames, black tee and jeans. Original photographs are not included in this repository or packed into the Blender file. An image-generation reference derived from those photographs was projected and baked in Blender into `likeness/ezra-skin.png`, the character's UV skin atlas. This derivative depicts the consenting user; it is not a generic anonymous texture or a third-party CC0 asset. The neutral generated reference and original photo inputs remain outside tracked project assets. See `likeness/README.md` for the workflow and a generic-skin alternative.

The character is an approximation, not a scanned digital double. Runtime record artwork is separate from the GLB and comes from the user's local crate. No private music or album artwork is embedded.

The current head replaces the earlier projected MakeHuman face with a KeenTools FaceBuilder fit to the approved generated reference. `likeness/fitted-head.blend` contains only the resulting mesh and packed derived skin material; the original source photos, intermediate reference and proprietary core are excluded. Fitting, integration, chin refinement, texture completion and rig attachment were performed during the hackathon. [KeenTools' product FAQ](https://keentools.io/products/facebuilder-for-blender) states that created results belong to the creator. This personalized derivative is not described as CC0.

All café geometry, deck details, modeled plants, glasses, headphones, lighting, original abstract wall art and runtime choreography are project contributions. Deterministic texture/geometry seed: 20260910.
