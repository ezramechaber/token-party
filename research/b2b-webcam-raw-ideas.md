# Ten B2B directions with webcam and RAW workflows

2026-09-10. Ideation only; no product selected. The founder likes the playful interaction of filming a trunk and belongings, then solving how they fit. A webcam is available; specialized machinery and fabrication are not. RAW photo files are an additional exploration. This explicitly authorizes exploring a packing derivative of Fold; the other concepts are fresh proposals, not resumptions of earlier repository directions.

## Grounding and constraints

- [Official event criteria](hackathon.md): development with Astra, runtime Astra, live demo, and technicality each contribute 25%. Webcam concepts must perform a substantial planning/creation/execution loop to distinguish them from the prohibited image-analyzer category. That distinction is a design hypothesis, not an organizer eligibility ruling.
- [Astra's model page](https://developers.openai.com/api/docs/models/gpt-6-astra) lists image input, not native video input. Webcam/video apps would extract selected frames. Reliable metric reconstruction from casual footage is not assumed. A bounded demo should use user-confirmed dimensions, known objects, or fiducial markers.
- RAW is a source-data format, not a model modality. A decoder such as [rawpy](https://pypi.org/project/rawpy/) can expose sensor data and render 16-bit images; Astra would inspect previews and use tools to propose, render, and evaluate parameter edits. A custom recipe is not automatically a Lightroom-compatible XMP file.
- [Adobe documents tonal adjustment and highlight recovery](https://helpx.adobe.com/camera-raw/desktop/using/make-color-tonal-adjustments-camera.html). Recovery is limited by captured information. Missing detail in fully clipped channels, severe blur, and absent views cannot be truthfully restored merely by changing RAW development settings.
- Actual latency, file support, sample access, customer demand, and willingness to pay remain unmeasured. Demo scopes are deliberately small. No production integrations are prerequisites.

## Candidates

### 1. Loadmaster — trunk Tetris for businesses

**Buyer:** Small moving companies, equipment rental firms, delivery operators.

**Product:** Turn a captured load and available space into a packing sequence that respects delivery order, fragile-item rules, orientation, and access. Astra interprets the constraints and revises plans; a geometric solver checks supported shapes for containment and overlap.

**Demo:** Pack six measured desk objects into a shoebox under the webcam. Halfway through: “The blue one is the first delivery.” The system replans so it is reachable without unloading everything. Highlight the next object and verify a user-confirmed placement from a new snapshot.

**Scope/gate:** Six known cuboids, a rectangular container, coarse observed placement, one unloading-order constraint. Start with confirmed dimensions and one top-down view. A collision-free final layout does not itself prove a feasible insertion path; constrain the demo to top-loading or explicitly check supported movements. Real trunk geometry, load restraint, axle loading, and transport safety are outside the proof.

**Differentiation to test:** Camera-grounded, interruptible loading assistance. [EasyCargo already supports loading sequences](https://www.easycargo3d.com/en/journal/step-by-step-loading-now-with-a-legend/); packing optimization alone is not novel.

### 2. Kitbash — rescue a rental order when a component disappears

**Buyer:** Camera, AV, and event-equipment rental houses.

**Product:** Rebuild a fulfillable equipment package when a booked component becomes unavailable, preserving the customer's functional brief. It reconciles interfaces, power, quantities, stock, and budget, then creates a revised reservation and picking list in a sandbox.

**Demo:** Remove the only booked projector. Astra chooses an alternative, notices that its connection requires a different adapter, reserves both, and revises the quote. A cheaper incompatible replacement fails an explicit checker.

**Scope/gate:** Twelve fictional products, known compatibility rules, one order, no live vendor integration. Generated substitutions must pass catalog-backed checks; visual appearance is not evidence of compatibility.

### 3. Benchmate — a packing bench that helps finish the job

**Buyer:** Small manufacturers, subscription-box businesses, and companies assembling onboarding kits.

**Product:** Use the webcam to maintain the state of a kit being assembled, guide the remaining steps, and issue its completion record. If a part is missing, Astra applies supplied substitution and quantity rules to produce a revised work instruction.

**Demo:** Assemble a kit from labeled desk objects, deliberately skip one, then request an allowed substitute. The instructions change and the kit receives a completion receipt only after the required items are visibly present and confirmed.

**Scope/gate:** One kit recipe, six labeled objects, deliberate capture between steps, one substitution. Keep counting and state deterministic. Occlusion requires a clearer view or operator confirmation. It must guide and complete a work order, not just label a photograph.

### 4. Shelf Shuffle — redesign the shelf without closing the shop

**Buyer:** Independent retailers and field merchandising teams.

**Product:** Given shelf dimensions, inventory, commercial placement rules, and a desired change, produce both a new arrangement and the sequence of moves to reach it. Limit temporary holding space so the transition is part of the problem.

**Demo:** Use books or small boxes as products. “Give this launch twice the facing space, keep these together, and only use this tiny staging area.” The app highlights the next move, observes the result, and adapts if the operator chooses another move.

**Scope/gate:** Two shelf rows, eight measured boxes, one staging area, explicit adjacency and facing constraints. Verify space and move legality. No inferred sales uplift or ergonomic guarantees.

### 5. Showrunner — keep a live event coherent when it changes

**Buyer:** Event agencies, webinar producers, and small conference teams.

**Product:** Turn a run of show into an executable cue sequence controlling an event-built presentation screen, countdown, and lower thirds. Astra revises dependent cues when speakers overrun or drop out while preserving fixed commitments.

**Demo:** A speaker runs late and the next one cancels. “Keep the sponsor's slot and finish on time.” The cue sequence changes, and the next title and countdown appear on a separate browser output.

**Scope/gate:** Four segments, three cue types, one protected segment, operator-triggered transitions. No hardware lighting system or real conferencing integration. Deterministic code enforces cue order; model latency must not become the show clock.

### 6. Redline Ripple — one client correction, every affected deliverable

**Buyer:** Creative agencies and brand production teams.

**Product:** Propagate a semantic client change through several editable assets while preserving asset-specific exceptions. Produce revised artifacts, not a list of where the problem occurs.

**Demo:** “The free trial is now 14 days, but enterprise still gets 30.” A landing page, email, and one-page sales sheet update. The layout reflows and checks confirm that the enterprise exception survived.

**Scope/gate:** Three event-built HTML/SVG artifacts, one content dependency graph, literal and paraphrased mentions, one exception. Render and check text/overflow after changes. Do not claim universal support for arbitrary design-file formats. The difference from search-and-replace must be visible in conditional and semantic changes.

### 7. Demo Doppelganger — create a buyer-specific software reality

**Buyer:** SaaS sales engineering teams.

**Product:** Populate a controlled product sandbox with coherent synthetic data and behaviors for a customer's workflow. Maintain relationships across screens and make the demonstrated workflow executable.

**Demo:** Convert the same event-built SaaS fixture from a hotel example to a manufacturer. Opening a delayed order exposes the same missing component shown elsewhere. Change a quantity, and dependent states update coherently.

**Scope/gate:** One existing event-built fixture with three screens and a fixed schema. Astra synthesizes the scenario and seed data; code enforces referential integrity and workflow transitions. No arbitrary SaaS cloning or claims of actual customer integration.

**Differentiation concern:** [Demostack already offers personalized simulations and clones](https://www.demostack.com/how-it-works). Novelty is weak unless runtime scenario coherence and surprise changes are unusually convincing.

### 8. RAW Rescue — save a paid shoot from a bad exposure

**Buyer:** Commercial photographers and retouching studios.

**Product:** Given a RAW and a specific creative priority, develop alternatives, inspect actual rendered detail, and deliver the best supported result with an editable recipe. Priorities can conflict: preserve bright fabric texture while keeping the overall frame airy, for example.

**Demo:** Start with an apparently blown-out preview. Ask to recover product texture, then “keep it bright.” Astra revises development parameters and shows detail crops plus the final render. Include a genuinely unrecoverable case to demonstrate that the app does not invent texture.

**Scope/gate:** Three compatible, rights-cleared RAW files, exposure/white-balance/tone controls, original-versus-render comparison, JSON recipe and export. Test decoding and actual available highlight detail before choosing this concept. Local masks are a stretch feature. No content generation is required.

**Risk:** RAW recovery and AI editing already exist. Its differentiation would be the iterative response to a specific retouching brief and an honest recoverability boundary. A fixed auto-exposure preset would be insufficient.

### 9. Look Lock — make separate shoots look like one campaign

**Buyer:** Ecommerce studios, catalogs, and brands working with multiple photographers.

**Product:** Match RAW photos to an approved visual reference while protecting specified product colors and details. Astra iterates per-image development settings; a check compares user-identified reference regions and flags conflicts between atmosphere and color fidelity.

**Demo:** Four photos of the same item have different casts. Match the campaign look, then “warm the scene without changing the product's blue.” The background treatment changes while the protected region stays within a chosen relative tolerance.

**Scope/gate:** Four files, one reference, manually selected regions, controlled rendering, repeatable recipes. Exact physical color requires an appropriate calibrated capture/display workflow; the prototype checks relative reference consistency only. No fabricated product details.

**Risk:** [Imagen](https://imagen-ai.com/solution/software-for-raw-photo-editing/) and [Aftershoot](https://aftershoot.com/edit/) already automate RAW editing and consistency. Protected-region constraints and visible corrections must earn differentiation.

### 10. Delivery Darkroom — turn RAW files and client notes into the finished handoff

**Buyer:** Commercial photo studios and creative production agencies.

**Product:** Compile a client's mixed delivery requirements into a set of actual exports: crops, tonal variations, dimensions, color profiles, naming, and a manifest. Preserve semantic requirements such as logo visibility and copy space, and regenerate only affected outputs when the brief changes.

**Demo:** From one RAW, produce a square commerce image, portrait ad, and wide hero with room for text. Midway: “The logo must stay visible in every crop.” The app changes only the failing composition, verifies the files, and exports a complete package.

**Scope/gate:** One RAW, three user-supplied delivery specifications, protected logo region, three file exports, editable recipes. RAW conversion occurs in a decoder, Astra plans crops and treatments, and code checks dimensions and regions. No invented pixels to hide an impossible crop; surface incompatible constraints.

**Risk:** Generic export presets are easy to copy. The model must reconcile ambiguous directions and conflicting composition requirements. This is a delivery workflow using RAW, not a capability exclusive to RAW; much also applies to TIFF or JPEG.

## Scores and recommendation

Forecasts, not measured results or official judging scores. Each official criterion is out of 10; total = 2.5 × sum. Development is held at 8 because the team must earn it through actual timestamped implementation and debugging evidence. Feasibility and originality are separate editorial estimates out of 5; higher is better. All ten have plausible buyers, but willingness to pay is unvalidated.

| Idea | Development | Runtime | Demo | Technicality | Total / 100 | Feasibility / 5 | Originality / 5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Loadmaster | 8 | 9 | 10 | 9 | 90 | 3 | 4 |
| Kitbash | 8 | 9 | 8 | 8 | 82.5 | 4 | 3 |
| Benchmate | 8 | 8 | 9 | 8 | 82.5 | 4 | 3 |
| Shelf Shuffle | 8 | 9 | 9 | 9 | 87.5 | 3 | 4 |
| Showrunner | 8 | 9 | 9 | 8 | 85 | 4 | 4 |
| Redline Ripple | 8 | 9 | 8 | 9 | 85 | 4 | 3 |
| Demo Doppelganger | 8 | 8 | 8 | 8 | 80 | 4 | 2 |
| RAW Rescue | 8 | 8 | 10 | 8 | 85 | 3 | 3 |
| Look Lock | 8 | 9 | 9 | 8 | 85 | 3 | 3 |
| Delivery Darkroom | 8 | 9 | 9 | 9 | 87.5 | 4 | 3 |

**Best playful demo:** Loadmaster. Validate scale, placement observation, and the first-delivery constraint with desk objects before touching video reconstruction. Webcam planning concepts have elevated eligibility risk if execution is reduced to image interpretation alone.

**Best RAW business workflow:** Delivery Darkroom. It has a concrete billable outcome and extends from developing an image to completing the client handoff. RAW Rescue offers the strongest before/after moment if real recoverable examples are available.

**Best low-dependency wildcard:** Showrunner. Multiple visible outputs changing correctly after an interruption can demonstrate runtime Astra without hardware or a reconstruction pipeline.

No prototype, webcam capture, RAW decoding, or runtime evaluation was performed in this session. The immediate next step remains choosing a direction and testing its hardest assumption against actual available time.
