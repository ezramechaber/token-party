# NYC open data: opportunities beyond a future skyline

Research date: 2026-09-10. Ordinary exploratory web research, grounded primarily in city sources and first-party product pages. No product chosen, implementation started, or API integration validated. Product differentiation below is a hypothesis; competitors were researched through published descriptions, not hands-on tests.

## Direction from the founder

Apartment Audition needs a stronger differentiation case against existing industry tools and widespread AI room-generation demos. Back-to-Back remains interesting. Explore NYC public data for useful and playful experiences, including viewing the future neighborhood from filed plans.

## Findings that change the idea

- A 3D future-development map is already an advertised product: [YIMBY+](https://www.yimbyplus.ai/) presents a 3D city, history timeline, and development pipeline. A future skyline alone is not a convincing differentiator.
- [Streetmix](https://www.streetmix.net/) supports street redesign; [3DStreet's own tutorial](https://github.com/3DStreet/3dstreet/blob/main/tutorials/3DStreet-streetmix-tutorial.md) describes converting those designs into 3D. Generic street visualization is also occupied.
- [Shadowmap](https://shadowmap.org/) provides sunlight/shadow visualization; [TestFit](https://www.testfit.io/) advertises editable generated site plans and contextual 3D massing. Neither shadows nor generative massing is sufficient novelty by itself.
- The plausible wedge is converting fragmented public proposals into a traceable, interactive experience: reconcile document versions, create a constrained scene, answer a personal spatial question, and preserve the connection to evidence. This is an inference, not a demonstrated market gap.

## What is actually accessible

| Source | Verified useful content | Product use | Important limit |
| --- | --- | --- | --- |
| [DOB applications and permits](https://www.nyc.gov/site/buildings/dob/building-applications-permits.page) | Links to legacy and DOB NOW filings, permits, occupancy and stalled-site records | Locate and classify construction activity | DOB explicitly says multiple datasets are needed during migration; a filing is not completion |
| [Approved permits](https://data.cityofnewyork.us/Housing-Development/DOB-NOW-Build-Approved-Permits/rbx6-tga4/data), ID `rbx6-tga4` | Tabular permit records, address, BIN, block/lot, work type; API documentation available | Join projects to buildings | Excludes electrical, elevator and LAA records; metadata's daily cadence is not a freshness guarantee |
| [DOB floor-plan access](https://portal.311.nyc.gov/article/?kanumber=KA-02017) | Records-request workflow for plans and drawings | Individual deeper investigation | Do not assume a public instant-download plan for every building; records may require borough-office retrieval |
| [ZAP document submission guidance](https://www.nyc.gov/assets/planning/downloads/pdf/applicants/preparing-application/guidance-on-submitting-application-attachments.pdf) and [CEQR access description](https://www.nyc.gov/site/bsa/applications/ceqr-environmental-review.page) | Public planning application materials and environmental review documents | Extract proposals, massing and alternatives where present | Covers relevant review processes, not every as-of-right building; check actual available packet and revision |
| [Building footprints](https://data.cityofnewyork.us/d/jh45-qr5r) | Geometry, BIN, BBL, ground elevation, roof height | Existing-block context, geographic joins | Validate elevation semantics/units and missing or stale records before extruding |
| [NYC 3D model metadata](https://www.nyc.gov/assets/planning/download/pdf/data-maps/open-data/nyc-3d-model-metadata.pdf) | Existing 3D geometry based on 2014 aerial imagery | Optional contextual base | Historical baseline, not today's complete city |
| [DOT Current Projects](https://www.nyc.gov/html/dot/html/about/current-projects.shtml) | Public presentations, design checklists and successive proposals | Reconstruct an actual street proposal | A posted proposal is not proof of current installation or final approval |
| [Capital projects](https://www.nyc.gov/site/operations/reports/capital-projects-dashboard.page) | Cost, phase and projected completion | Future public infrastructure and sequencing | Schedules can change; source says updates follow a three-times-yearly cadence |
| [Forestry Tree Points](https://catalog.data.gov/dataset/forestry-tree-points), ID `hn5i-inap` | Tree inventory connected to planting spaces | Block greening, tree quests, approximate canopy scenarios | Join via PlantingSpaceGlobalID; account for retired and active trees. Use ForMS for current inventory, not the 2015 census |
| [POPS](https://catalog.data.gov/dataset/privately-owned-public-spaces-pops), ID `rvih-nhyn` | Public spaces on private property | Discover usable hidden public space | Published requirements and inventory do not establish current on-site access |
| [Film permits](https://data.cityofnewyork.us/City-Government/Film-Permits/tg4x-b46p/data), ID `tg4x-b46p` | Permitted activities such as shooting, loading and rigging | Creative location scouting / street-use stories | Not a reliable movie-title database or live guarantee of filming |

These sources include structured open datasets and publicly posted PDFs; those are different ingestion problems. BIN/BBL can connect building records, but project-to-parcel relationships and dates need reconciliation. Public visibility does not automatically settle redistribution rights for every embedded third-party drawing or photo.

## Concrete source packet: Lafayette / 4th Avenue

The city's project index links both an [April 28, 2026 presentation](https://www.nyc.gov/html/dot/downloads/pdf/lafayette-st-4th-ave-prince-st-e15-st-apr2026.pdf) and a [May 11, 2026 presentation](https://www.nyc.gov/html/dot/downloads/pdf/lafayette-st-4th-ave-spring-st-e15-st-may2026.pdf). Text was retrieved from both; diagrams have not yet been visually checked or reconstructed.

The May packet records a community-board request for more amenity-strip renderings and clearer allocation of loading space. It also describes revisions around Grace Church School, including a midblock crossing, and includes the earlier proposal in an appendix. That makes version reconciliation important even inside one PDF. The documents contain draft markings despite being publicly linked: treat them as dated proposals and verify status before claiming they represent the installed street.

Prototype opportunity: select a small section, generate a source-linked before/proposed scene, switch pedestrian and cyclist viewpoints, then import the revised packet and highlight changed geometry. Validate dimensions against the source. Do not infer crash reductions or realistic traffic dynamics from an illustrative animation.

## Candidate products

### 1. Walk the Proposal

For a resident trying to understand a public project: paste its packet and walk through the proposed street or block. Ask “Where do I cross after school?” or “Where does this delivery unload?” Astra extracts the relevant geometry and routes the camera to an answer with its supporting page.

**Distinctive bet:** Document-to-experience with evidence and version reconciliation. **Thin slice:** One Lafayette block, two dated proposals, simple geometry and camera paths. **Main risk:** Reliable interpretation of drawings; no claim that this is absent from all professional products.

### 2. What Changed Since the Meeting?

For residents and community-board members: compare two submissions and see additions, removals and relocations directly in the scene. Distinguish changes in design from repeated material and revised narrative.

**Demo:** Drop in May's packet; a new crossing appears while unchanged blocks stay fixed. **Thin slice:** Two PDFs and three validated changes. **Why Astra:** Cross-page and cross-version interpretation. **Risk:** Could become a document-comparison wrapper unless it creates inspectable geometry and resolves spatial consequences.

### 3. Your Future Walk

For a resident curious about neighborhood change: experience the same short route under existing, proposed and hypothetical conditions. Combine a public-space connection, one building proposal and one street change.

**Demo:** “Walk me to the waterfront if this path opens.” **Candidate research area:** Gowanus, where [DEP publishes project review materials](https://www.nyc.gov/site/dep/about/gowanus-canal-cso-facilities-project.page) and the [waterfront access plan](https://zr.planning.nyc.gov/node/22003) supplies another source. Actual current access and construction status still need site-specific verification.

**Distinctive bet:** Personal route consequences, beyond a skyline. **Thin slice:** Three blocks and one conditional new connection. **Risk:** Mixing speculative dates with confirmed conditions; use explicit scenario toggles instead of a misleading future year.

### 4. Block Party / Catan on Your Block

An explicitly fictional cooperative game played on a real NYC block. Players negotiate finite space for housing, trees, loading, seating and bike access. Astra converts bargains into supported scene edits and controls fictional stakeholders with visible goals; deterministic code enforces the game's resource budget.

**Demo:** “Keep the loading bay, but make room for two trees and a wider sidewalk.” Players trade space and see the compromise. **Thin slice:** One footprint-backed block, four interventions, two AI roles. **Differentiation:** Real geography plus negotiated, editable rules. **Risk:** Strong game, weaker professional utility; no claims that agents predict actual residents or that the rules certify zoning compliance.

### 5. Borrowed City

Turn publicly accessible but easily overlooked spaces into a personal urban expedition. Astra assembles a short mission from POPS records and user constraints, then replans as the user reports observations.

**Demo:** “I have 35 minutes, want a seat and somewhere sheltered.” Discover a space hidden in plain sight, with evidence for why it is listed as public. **Thin slice:** Three verified locations and one route. **Risk:** Existing POPS maps and tour generators make differentiation harder; stale access data matters.

### 6. Grow This Block

Use actual tree and planting-space records as the starting point for a playful block-greening experience. Adopt an existing tree in the experience, explore hypothetical placements, and compare explicit canopy assumptions over time.

**Demo:** “We can add three trees—where would they change this walk most?” **Thin slice:** One block and fixed illustrative canopy sizes. **Risk:** Growth and shade require assumptions; existing [TreeWalk](https://github.com/g20lab/treewalk-nyc) already combines NYC trees and gamified exploration. Tree identification and a points layer alone are not novel.

### 7. The City Is Your Set

For an amateur filmmaker or creative New Yorker: turn a scene brief into a small location-scouting expedition and a rough 3D shot plan. Public geometry, public-space records and historical film permits provide context; Astra chooses views and assembles an original storyboard.

**Demo:** “A lonely conversation beneath a huge building, then a bright plaza.” **Thin slice:** Two locations and three camera positions. **Risk:** Permit records do not establish permission, availability, production identity or actual visual character; additional verified imagery is needed.

## Recommendation and next falsification test

The most promising useful product is **Walk the Proposal**, with **What Changed Since the Meeting?** as its strongest initial feature. The most playful is **Block Party**. **Your Future Walk** best preserves the founder's future-neighborhood instinct, but has the largest data-reconciliation burden.

Before selecting: visually inspect one block's two source diagrams; establish dimensions and source-page links; compare against Streetmix/3DStreet's actual import and revision capabilities; then test whether a non-planner can answer one practical question faster from the proposed interaction. Stop or narrow if the geometry depends on substantial invention. No comprehensive competitive review or end-to-end extraction test has yet been performed.
