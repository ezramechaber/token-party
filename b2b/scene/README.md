# b2b booth

An original Blender model of a stylized human DJ, a walnut slatted vinyl booth, two decks, a mixer, speakers and a sleeve crate in a warm café. `b2b-booth.blend` is editable; `../web/scene/b2b-booth.glb` is its lightweight browser export. Both contain only original geometry and materials. Cover art is applied at runtime from the current local crate; generated sleeve art is used when no cover is provided.

Rebuild from the b2b project directory with Blender 4.5 LTS:

```sh
blender --background --python scene/build_booth.py
```

The generator uses browser coordinates (x right, y up, z toward audience), converts them for Blender, and exports glTF with semantic object names. Named anchors include `handL`, `handR`, `crate`, `deckA`, `deckB`, `mixer`, `eqA`, `eqB` and `crossfader`.

`createBoothScene(canvas)` in `web/booth-scene.js` returns:

- `update(state, dtSeconds)` renders the real mixer state. `state.decks` contains `{id, title, artworkUrl, playing, position, level, low, fade}` for A/B; `state.crate` contains tracks; optional `state.transition` contains `{progress, from, to}`.
- `onTrackLoaded(0 | 1, track)` queues the sleeve-selection, carry and deck-placement motion.
- `dispose()` releases renderer resources.

Low EQ is dB from -24 to 0; level and fade are 0–1. Browser animation follows these values and never controls playback. The loading gesture uses fixed known anchors and articulated limbs; it is a visualization of app events, not computer vision or autonomous robotic control. Reduced-motion preferences shorten loading gestures and disable idle bob/spinning. The renderer is limited to approximately 30 fps and a 1.6 device-pixel ratio.

The standalone `/scene/preview.html` is explicitly a motion preview with no audio. The main app must call the API from its real audio state and load events.

Three.js 0.180.0 is vendored locally under `web/vendor/`, including its MIT license. GLTFLoader, BufferGeometryUtils and RoomEnvironment have only local import paths changed. Blender 4.5.9 LTS was run headlessly to generate the checked-in files. The downloaded Blender runtime stays under ignored `.b2b/tools/`; it is not a project dependency for ordinary playback.

Verified: The original chrome prototype was replaced by a 243-object human café scene, with windows, plants, original abstract prints and an olive lamp. The final Blender render was visually inspected. Existing named anchors and deck coordinates are preserved; human face/hair/headphones are parented to the animated head. `node --check web/booth-scene.js` passes. Full integration and audio-driven sequencing are verified separately by the app task.
