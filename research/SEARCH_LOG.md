# Search and reading record

Date: **2026-09-11**. Search surface: web search/open/find; primary publisher and preprint pages; official provider documentation; public GitHub metadata/source; small publisher supplements; Crossref bibliographic metadata. No subscription database, private dataset or paid tool used. This is a documented broad survey and targeted follow-up, not an exhaustive PRISMA review or complete citation census.

## Coverage and progression

Early query families below summarize the searches performed during the session; they are normalized topic descriptions rather than a verbatim export of every search-engine query. The final rounds record exact query strings. Read depth for each selected source is authoritative in [references.json](references.json).

| Round | Search families and backward/forward tracing | Sources and change to reasoning |
|---|---|---|
| Broad A | Adult Drosophila connectome2024–2026; BANC; MaleCNS; FlyWire Codex versions; NT prediction | S01–S09,S27,S46–S49. Reconciled provider-version conflict; BANC coverage limitations prevent automatic primary selection |
| Broad B | MB plasticity/reinforcement; dopamine and reversal; structural perturbations; compensatory development and comparative anatomy | S10–S14,S20,S30/S31,S52. Plasticity plausible but not exclusive; larval/adult distinction and developmental constraints matter |
| Broad C | Connectome reservoirs; memory capacity; topology randomization; normalization; whole-brain controllers | S15–S21,S51. Found close prior work and counterevidence; strengthened nulls and separated regional from neuronal resolution |
| Broad D | FlyGym, NeuroMechFly, flybody, NeuroGym; neuromorphic fly; online spiking learning | S22–S24,S40–S45,S50,S59,S65. Selected tiny CPU-first assays; later embodiment dependencies audited |
| Adjacent A | Generative wiring; artificial neurodevelopment; neural cellular automata; evolutionary/open-ended curricula; scaling laws | S32–S39,S55/S56. Preserve developmental/evolutionary branch, avoid cross-domain scaling extrapolation |
| Adjacent B | Central complex; multisensory memory; predictive olfaction; transcriptomic/receptor resources; recent spontaneous activity and sensory-loss claims | S25/S26,S28/S29,S57/S58,S62. Keep chemistry/coupling branches; unresolved full-text preprints do not govern shortlist |
| Methods/code | Followed publication code/data links for Shiu, flyvis, Bennett, Xie; inspected selected functions/configs and supplier requirements | Pinned11 repository commits; downloaded bounded source files; graph/learning equations inspected; discovered version and NumPy conflicts |
| Early targeted1 | Drosophila growth/scaling2026; MB expansion/reversal; reservoir degree normalization; evolutionary augmentation | S53 and adjacent leads; no shortlist change at that point |
| Early targeted2 | Connectome enlargement/expanded learning; KC scaling/synaptic budgets; developmental generalization | Additional comparison and online-learning context; no shortlist change at that point |
| Completeness check | Exact query: `Drosophila connectome scaling reservoir computing doctoral thesis mushroom body growth`; then exact-title searches for Costi and compensatory variability | Found S67–S70, including thesis S69. **Materially tightened novelty and homeostasis diagnostics. Reset saturation count** despite earlier two rounds |

## Final targeted rounds after that revision

**Final1:** exact queries:

- `"Drosophila" "reservoir" "Costi" "2026"`
- `"mushroom body" "growth" "compensatory" learning expansion model`
- `"connectome" "scaling" "degree-preserving" Drosophila`

Results included Costi's FlyBase citation, development/homeostasis reviews, network-statistics comparisons and genetic/generative models. Reviews were used for discovery only, not as primary evidence for new technical claims. These leads reinforced degree controls and developmental uncertainty already in the specifications. No source materially changed the three-candidate shortlist.

**Final2:** exact queries:

- `"Drosophila" "structured expansion" "learning" connectome`
- `"connectome reservoir" "normalization" "degree" fly`
- `"Kenyon" "neuron number" "reversal learning" model`

Results returned Costi/conn2res methods, additional butterfly comparisons, an unaudited plasticity-guided-connectome GitHub project, and other-organism architectures. The GitHub description is a lead rather than a verified result; it further discourages a generic novelty claim about connectome-plus-plasticity. No result displaced the shortlisted experiments or changed their necessary controls. Two consecutive **post-revision** targeted rounds therefore meet the scoped stopping criterion. This says nothing about guaranteed originality.

## Reading and citation chains

- FlyWire reconstruction → annotation/comparative paper → source annotation releases and provider FAQ → BANC/MaleCNS update. Read provider/version descriptions and relevant methods, not just abstracts.
- Lappalainen visual model → flyvis constructor/dynamics/wiring → recent topological-sensitivity work and configuration → whole-body connectomic controller methods. Compared model assumptions and controls.
- Bennett reinforcement model → author MATLAB equations/reward schedules → dopamine-memory and recurrent-circuit work → larval structural perturbations → Eichler supplement. Read Bennett full text/code and Xie PDF methods; inspected the matrix directly.
- Elkahlah development → Ellis comparative anatomy → butterfly specialization → compensatory-variability modeling. Distinguished biological manipulation from computational prediction and cross-species inference.
- Dambre capacity → conn2res and Morra → current reservoir optimization → Costi hybrid controls. Distinguished readout capacity, graph resolution and normalization assumptions.
- Central complex/developmental motifs → generative models/HyperNCA → POET; followed adjacent terminology, with mostly abstract-level screening in these reserve branches.
- Thesis search → Jürgensen repository abstract; also surfaced other university theses. Selected one relevant thesis in bibliography and left full thesis reading as a focused future task, not claimed complete.

Backward/forward tracing here means following references and searching later works naming the methods; it is not a complete author citation graph. Source inspection does not mean every supplement and every code file was read. The methods most likely to change a shortlisted decision received priority.

## Access failures and unresolved evidence

S25/S26/S53: full-text retrieval unsuccessful; indexed excerpts and Crossref metadata available. PMC opens for some later sources showed access challenges; indexed primary-source methods excerpts provided partial inspection, recorded as such. Xie and NeuroGym code-tree API calls were rate-limited. Codex API downloads returned HTML sign-in responses; no data manifest was inferred from them. These failures are in [FAILED_PATHS.md](../FAILED_PATHS.md).

Older arXiv works are catalogued as the preprint version accessed; publication supersession was not exhaustively reconciled. The bibliography should be refreshed before publication. Raw copyrighted papers remain in ignored local cache where downloaded; the committed record contains original synthesis, metadata, hashes and bounded code/data audit descriptions, not a copied literature library.

## Reopen conditions

Reopen targeted research when a pilot's result contradicts the closest work, a controls audit cannot separate causes, an adult dataset is chosen, a new release changes relevant annotations, or a paper submission is planned. Search saturation is conditional on the current decision, not permanent closure of the field.
