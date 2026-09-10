# Back 2 Back café scene

An editable Blender café with a personalized, rigged DJ, two vinyl decks, mixer, sleeve crate, walnut booth, windows, plants and practical lights. The live GLB follows the existing audio application's state; it does not control playback.

## Open and rebuild

Open `b2b-booth.blend` in Blender 4.5 LTS. The current work was authored and inspected in the visible Blender application through computer use. To rebuild, switch an editor to Python Console and run:

```python
p = bpy.path.abspath('//build_booth.py')
exec(open(p).read(), {'__file__': p})
```

The builder replaces the active scene's objects, saves the editable scene and exports `../web/scene/b2b-booth.glb`. Open a copy first if you want to preserve manual edits. Blender's bundled NumPy is sufficient. All required graphical source assets are included; rebuilding the café does not require FaceBuilder, a subscription, reference photographs or a network connection.

For a visible render, run `render_preview.py` for the room or `render_portrait.py` for the DJ from the same console. These save `cafe-reference.png` and `dj-portrait.png`. The native Cycles hair curves are omitted from GLB; a simpler surface and sparse fibers serve the browser.

## CLI workflow

After the user authorized CLI/MCP iteration, `scene_cli.py` was added and verified against the saved scene. With Blender on PATH:

```sh
blender --background b2b/scene/b2b-booth.blend --python b2b/scene/scene_cli.py
blender --background b2b/scene/b2b-booth.blend --python b2b/scene/scene_cli.py -- --view portrait
blender --background b2b/scene/b2b-booth.blend --python b2b/scene/scene_cli.py -- --rebuild --view room
```

Optional `--samples 32` and `--output /absolute/path.png` support quicker review renders. Inspect the resulting images and browser scene after each material or geometry change. CLI avoids repetitive UI input; Blender remains the authoring and rendering tool.

## Character and materials

`build_human.py` fits CC0 MakeHuman body, tee, jeans and shoes to its skeleton. `integrate_fitted_head.py` attaches a reference-fitted head from `assets/likeness/fitted-head.blend`. The neck transition is restricted below the jaw to preserve facial proportions. The user-approved generated portrait supplied the likeness target; this is an approximation, not a scan. The optional FaceBuilder authoring helpers require the add-on and private inputs and are separate from the ordinary rebuild.

`refine_environment.py` applies CC0 Poly Haven surface scans and builds the window/exterior, vegetation and café furniture. `refine_cafe.py` adds turntable, mixer and cup details; `polish_objects.py` adds original sleeve typography, speaker drivers and dial pointers. See [asset provenance](assets/PROVENANCE.md) and [character research](../docs/character-research.md) for sources and decisions.

Original photographs, generated reference portraits, trial installers, personal music and album artwork remain outside tracked assets. Runtime album art is applied from the local crate. The committed fitted mesh and baked skin texture are derivatives depicting the consenting user; they are not third-party CC0 assets.

## Browser integration

`createBoothScene(canvas)` in `web/booth-scene.js` provides:

- `update(state, dtSeconds)`: render deck state, levels, fades, EQ and transition progress.
- `onTrackLoaded(0 | 1, track)`: queue the sleeve-selection and deck-loading illustration.
- `setView('room' | 'face' | 'hands')`: select a diagnostic camera.
- `dispose()`: release rendering resources.

Deck state contains `{id, title, artworkUrl, playing, position, level, low, fade}`. `state.crate` supplies tracks; optional `state.transition` supplies `{progress, from, to}`. Low EQ is -24 to 0 dB; level and fade are 0–1. Reduced-motion preferences shorten load gestures and suppress idle/spinning motion.

`bake_character_rest.py` establishes the working pose using volume-preserving wrist and forearm deformation before rebinding it. `human-rig.js` uses fixed bone lengths and two-bone inverse kinematics. The sleeve motion illustrates app events; it does not simulate record extraction or a physically accurate finger grasp. The standalone `/scene/preview.html` is explicitly a motion preview without audio and offers both deck-load triggers, crossfader inspection, smooth camera changes and a slow-motion toggle. The existing app handles audible operation separately.

Rendering targets 30 fps with a maximum 1.6 device-pixel ratio. Static meshes sharing materials are batched; joints and independently controlled deck parts remain separate. Canvas data attributes expose measured frame rate, draw calls, initial pose error and arm/contact target errors for inspection.

## Quality and limitations

Blender and the browser are checked separately because their material support differs. The browser preserves UV normal maps but omits unsupported procedural bump; thin glasses use stable transparency. The native render has subsurface skin and curve hair unavailable in the same form in the browser. The result remains a prototype rather than a completed photorealistic digital double. Single-view skin projection, side/back likeness, hair silhouette, clothing deformation and hand grasp still have practical limits.

Three.js 0.180.0 and its MIT license are vendored in `web/vendor/`. The main audio service and transport are outside this visual task's scope.
