# Dybdegående forskningsbrief: Et projekt til at gøre en digital Drosophila-hjerne mere intelligent

## Strategisk konklusion

Din foreløbige research rammer noget reelt interessant, især idéen om **“Fly Brain XL”**, hvor man ikke bare simulerer den eksisterende fluehjerne, men forsøger at ændre, udvide eller videreudvikle dens arkitektur og derefter måle, om dens evner faktisk bliver bedre. fileciteturn0file0

Efter at have kortlagt den nuværende forskning frem til **11. september 2026** vil jeg dog ændre projektets centrale formulering en smule.

Jeg ville **ikke** gøre hovedhypotesen til:

> “Hvis vi giver fluehjernen flere neuroner, bliver den så mere intelligent?”

Den er interessant, men metodisk farlig, fordi flere neuroner, flere synapser og flere frie parametre næsten automatisk kan give en model større optimeringskapacitet uden at fortælle os ret meget om biologisk intelligens.

Jeg ville i stedet gøre hovedprojektet til:

> **Kan vi systematisk øge den adaptive og generaliserbare kognitive kapacitet af en Drosophila-baseret digital agent gennem biologisk begrænsede ændringer af dens dynamik, plasticitet og connectome — og kan vi identificere de minimale principper, der gør den bedre?**

Det giver plads til alle de spændende retninger, du allerede har identificeret:

**plasticitet → rewiring → nye synapser → neuron-/kredsløbsduplikation → større hjerne → kunstig neurodevelopment → evolutionær vækst.**

Men det gør samtidig projektet videnskabeligt falsificerbart.

Den vigtigste opdagelse i den eksisterende litteratur er nemlig, at **connectomet ikke er hjernen i eksekverbar form**. FlyWire har kortlagt strukturen med 139.255 neuroner og 54,5 millioner synapser, men et connectome fortæller primært, *hvem der potentielt påvirker hvem*. Det bestemmer ikke entydigt synapsestyrker, neuroners tidskonstanter, tilstand, dynamik eller hvordan forbindelser ændres under læring. Pospisil et al. beskriver netop forskellen som overgangen fra et **connectome** til et **“effectome”**, altså en kausal dynamisk model af, hvordan aktivitet faktisk påvirker resten af nervesystemet. citeturn15search3turn16search1

Det betyder, at projektet bør tænkes sådan:

\[
\boxed{
\text{Connectome}
+\text{dynamik}
+\text{plasticitet}
+\text{krop}
+\text{miljø}
+\text{erfaring}
\rightarrow
\text{adaptiv adfærd}
}
\]

og først derefter:

\[
\boxed{
\text{kontrolleret ændring af systemet}
\rightarrow
\text{bedre generaliserbar adfærd?}
}
\]

Det er efter min vurdering et væsentligt stærkere projekt end blot at “skalere connectomet”.

### Den mest lovende projektportefølje

Jeg ville prioritere forskningssporene således:

| Retning | Forskningsværdi | Teknisk risiko | Min vurdering |
|---|---:|---:|---|
| **Connectome-Guided Cognitive Augmentation** | Meget høj | Middel | **Hovedprojekt** |
| **Plasticity-first augmentation** | Meget høj | Lav–middel | **Start her** |
| **Effectome-guided causal rewiring** | Meget høj | Middel–høj | **Meget lovende** |
| **Fly Brain XL / connectome scaling laws** | Potentielt ekstremt høj | Høj | **Hovedeksperiment senere** |
| **Developmental/evolutionary brain growth** | Ekstremt spekulativ, høj upside | Meget høj | Sen fase |
| Cross-connectome robustness/consensus | Høj | Middel | Bør bygges ind i projektet |
| Male-vs-female counterfactuals | Stadig interessant | Middel | Ikke længere bedste novelty |
| Almindelig helhjerne-LIF-simulation | Lav novelty | Middel | Baseline, ikke projekt |
| Motifs/centrality/rich-club-analyse | Lav novelty | Lav | Kun støtteanalyse |

Den helt centrale idé er derfor:

> **Lad “større hjerne” være én mulig mekanisme til at skabe forbedring, ikke en antagelse om hvor forbedringen skal komme fra.**

Det giver Astra frihed til faktisk at opdage, at den bedste forbedring måske kommer fra 0 % flere neuroner og i stedet 0,02 % ændrede synapser, anderledes plasticitet eller ændret inhibition. Eller omvendt: måske opdager I en ægte capability-scaling-kurve, hvor bestemte kredsløb vokser, og nye kompetencer fremkommer.

**Den sidste mulighed er stadig meget interessant.** I min målrettede gennemgang fandt jeg ikke et eksisterende studie, der systematisk tager et komplet voksent Drosophila-connectome, foretager biologisk struktureret ekspansion i eksempelvis 1,1×, 1,25×, 1,5× og 2× størrelse og derefter tester modellerne på et bredt embodied multi-task benchmark med parameter-/energi-/synapse-matchede kontroller. Det skal behandles som en **stærk kandidat til en åben forskningsniche, ikke som dokumentation for garanteret verdensnyhed**, fordi området bevæger sig ekstremt hurtigt.

## Hvor forskningsfronten faktisk står

### Vi har nu flere “digitale fluehjerner” — men de er forskellige slags kort

I 2024 blev FlyWire-rekonstruktionen af en voksen hunflues hjerne publiceret. Den indeholder **139.255 neuroner og 54,5 millioner neuron-til-neuron-synapser**. Det ledsagende annoteringsarbejde identificerede **8.453 celletyper**, hvoraf 4.581 var nye i forhold til de tidligere klassifikationer. citeturn15search3turn17search0

Det er allerede vigtigt at opdatere én detalje fra din foreløbige research: der findes nu flere store connectome-datasæt, og de seneste offentlige Codex-versioner pr. september 2026 er blandt andet disse. citeturn21view0

| Dataset | Biologisk system | Neuroner | Hvorfor det er relevant |
|---|---|---:|---|
| **FAFB v783** | voksen hun, hjerne | 139.255 | Den klassiske komplette FlyWire-hjerne |
| **BANC v888** | voksen hun, hjerne + VNC | 158.262 | **Bedste kandidat til embodied-agentprojektet** |
| **MANC v1.2.1** | voksen han, VNC | 23.665 | Motorik/VNC-komparativt arbejde |
| **MAOL v1.1** | voksen han, højre synssystem | 52.445 | Visuel specialisering |
| **MCNS v1.0** | voksen han, hjerne + VNC | 166.700 | Hele mandlige CNS; meget nyt |

Tallene i Codex er levende dataset-releases, mens den publicerede MCNS-analyse rapporterer omtrent **166,7 tusind neuroner og 11,7 tusind celletyper**. MaleCNS-artiklen blev publiceret den **3. september 2026**, kun otte dage før datoen for denne research, og Janelias officielle side har nu v1.0-data, downloadmuligheder, neuPrint og værktøjer til dimorfi. citeturn15search1turn22search1

Det ændrer faktisk novelty-landskabet siden din indledende research.

Et rent projekt som:

> “Sammenlign male og female connectome og find seksuelle forskelle”

er nu betydeligt mindre originalt. MaleCNS-studiet laver allerede en omfattende synapse-resolution sammenligning og rapporterer tusindvis af isomorfe typer samt mandlige, kvindelige og dimorfe typer og beskriver circuit switches mellem kønnene. citeturn22search1

En **kausal** køns-counterfactual kan stadig være interessant, men den skal gå meget længere end beskrivende forskelle.

### BANC er sandsynligvis vigtigere for jeres projekt end FAFB

Dette er en vigtig ændring i forhold til at tænke “FlyWire brain” som projektets eneste fundament.

Den nye **BANC — Brain And Nerve Cord — connectome** forbinder hjernen og ventral nerve cord i det samme rekonstruerede dyr. Det gør det muligt at følge strukturer fra sensoriske systemer til hjerne, ned gennem descending neurons og tættere på motoriske effectors. Forfatterne finder en organiseringsform med lokale sensorimotoriske feedback-sløjfer, koordineret af længere ascending/descending kredsløb og med eksempelvis mushroom body og central complex i mere superviserende roller. citeturn19search2turn19search7

Det er ekstremt relevant for jer.

Hvis målet blot var:

> “Hvordan kan aktivitet propagere gennem hjernen?”

ville FAFB være oplagt.

Men jeres mål er:

> “Kan denne digitale hjerne lære bedre, navigere bedre, huske bedre og tilpasse sig?”

Så har I brug for:

\[
\text{sensation}
\rightarrow
\text{brain computation}
\rightarrow
\text{descending control}
\rightarrow
\text{body}
\rightarrow
\text{environment}
\rightarrow
\text{new sensation}
\]

BANC er direkte designet til at kortlægge mere af denne embodied kæde. citeturn19search2

Min anbefaling er derfor:

**BANC v888 som den primære strukturelle reference for den embodied agent.**

**FAFB v783 som sekundær reference**, fordi det er det mest modne og mest analyserede whole-brain-system og grundlaget for meget af den eksisterende modellering. citeturn15search0turn17search0

**MCNS v1.0 som en ekstern generaliserings-/robusthedstest**, ikke som det første system I bygger omkring. citeturn21view0turn22search1

Det passer ekstra godt, fordi NeuroMechFly/FlyGym selv tager udgangspunkt i en voksen hunflues biomekanik. citeturn20search0

### Et connectome er ikke en fungerende digital kopi af hjernen

Dette er projektets vigtigste epistemiske regel.

Shiu et al. demonstrerede i 2024, at man faktisk kan tage den komplette FlyWire-struktur, neurotransmitteridentiteter og en relativt simpel **leaky integrate-and-fire-model** og generere biologisk brugbare forudsigelser. Modellen kunne blandt andet modellere smags- og groomingkredsløb, og nogle modelgenererede hypoteser blev efterfølgende testet eksperimentelt med optogenetik og adfærdsforsøg. citeturn15search0

Det er bemærkelsesværdigt.

Men det betyder samtidig, at:

> **“Vi konverterer FlyWire til en spiking neural network simulation”**

ikke længere er et nyt projekt.

Shiu-studiet har allerede demonstreret den grundlæggende idé. citeturn15search0

På samme måde har Lappalainen et al. bygget en **connectome-constrained, task-optimized** model af fluesynssystemet. Deres netværk havde 45.669 neuroner og mere end 1,5 millioner forbindelser, men fordi mange parametre blev delt efter celletype og struktur, kunne modellen reduceres til kun 734 frie parametre. Den task-optimerede model reproducerede en lang række kendte visuelle responsmønstre. citeturn16search0

Det resultat er meget vigtigt for Astra:

> **Biologisk struktur kan fungere som en ekstremt stærk prior, så man ikke behøver lære hver enkelt synapse uafhængigt.**

Det er et princip, I bør udnytte gennem hele projektet.

### “Connectome → effectome” er en af de største åbne overgange

Pospisil, Aragon og Pillow formulerede i 2024 det næste problem meget klart: connectomet fortæller, hvor påvirkning *kan* flyde, men ikke hvor stærkt én neuron faktisk påvirker en anden i en levende flue. De foreslår derfor at lære et **effectome**, hvor connectomet bruges som prior, mens dynamiske påvirkninger estimeres fra eksperimentelle perturbationer. citeturn16search1

Deres analyse finder desuden, at de dominerende dynamiske modes ofte kan involvere overraskende få neuroner. For de ti stærkeste modes var størrelsesordenen omkring 50 neuroner nødvendig for at forklare hovedparten af loading power; senere modes involverede større populationer. Det er et vigtigt hint om, at en “intelligensforbedring” måske ikke nødvendigvis kræver ændringer i titusindvis af neuroner. citeturn16search1

Og fronten er allerede rykket videre.

En bioRxiv-preprint fra **21. august 2026** har bygget en whole-brain connectome-constrained dynamisk model med **138.639 neuroner**, fit den til whole-brain calciumaktivitet og derefter lavet virtuelle neuron- og synapseperturbationer. Modellen identificerer blandt andet en relativt lille population af stærke inhibitoriske hubs som kritiske for den modellerede resting-state-dynamik. Det er endnu en preprint og skal derfor vægtes svagere end peer-reviewed fund, men den viser, hvor hurtigt feltet bevæger sig. citeturn18search0

Konsekvensen er klar:

**I skal ikke gøre “fit neural dynamics to FlyWire” til novelty-claimet.**

Det bør i stedet blive en del af jeres **substrat**, som augmentation-eksperimenterne senere udføres på.

### Læring og plasticitet er ikke valgfrit

En statisk hjerne kan være kompliceret uden at være særlig adaptiv.

Drosophilas mushroom body er centralt involveret i associativ læring, og eksisterende modeller har allerede vist, hvordan dopamine-moduleret plasticitet mellem Kenyon cells og mushroom body output neurons kan implementere reinforcement-prediction-lignende læring. Bennett et al. demonstrerede modeller, der lærer forstærkningsforudsigelser og kan gengive flere klassiske conditioning-fænomener. citeturn22search0

Eksperimentel forskning viser samtidig, at læring kan give compartment-specifikke ændringer i neurotransmitterfrigivelse langs mushroom-body-axoner, altså at plasticiteten ikke nødvendigvis blot kan behandles som én global scalar learning rate. citeturn17search1

En særligt interessant ny preprint fra 2026 viser desuden et eksempel på noget, der kommer tæt på selve ambitionen “gør fluen kognitivt bedre”: når olfaktorisk funktion kompromitteres, forbedres visuel associativ læring i eksperimenterne, ledsaget af ændret rekruttering og rebalancering af højere ordens læringskredsløb. Resultatet er ikke “generel intelligens” — tværtimod illustrerer det en potentiel trade-off mellem sansemodaliteter — men det demonstrerer, at **kredsløbsrebalancering kan forbedre en konkret kognitiv evne**. citeturn18search1

Det er næsten en direkte advarsel til projektet:

> En modifikation, der giver +40 % på én benchmark, kan have gjort agenten **mere specialiseret, ikke mere intelligent**.

Derfor skal jeres evalueringssystem være multi-task fra begyndelsen.

### Det embodied testmiljø, du forestillede dig, eksisterer allerede i stor grad

Din intuition om, at fluen bør sættes ind i et fysisk simuleret miljø, hvor intelligens kan måles gennem handling, er meget god. fileciteturn0file0

Og den gode nyhed er, at I ikke skal bygge hele kroppen og fysikken selv.

**NeuroMechFly v2 / FlyGym** er netop et digitalt Drosophila-testmiljø med biomekanisk krop, vision, olfaktion, mekanosensorisk feedback og mulighed for komplekst terræn. Forskerne har blandt andet demonstreret path integration, head stabilization, reinforcement-learning-baseret multimodal navigation, odor-plume navigation og en connectome-constrained visuel controller til at følge en anden flue. citeturn15search4

I 2026 blev FlyGym 2.x omskrevet. Projektets egne benchmarks rapporterer omkring **2× real-time på CPU** og omkring **60× real-time throughput på GPU** via Warp/MJWarp for deres simulatorkonfiguration. Det er projektets egne performance-tal, så de bør behandles som implementation-specifikke benchmarks og ikke som garanti for jeres fulde hjerne-model. citeturn20search0turn20search2

Det gør FlyGym til den mest oplagte kandidat til jeres “verden”.

Men der er en vigtig forskel:

\[
\boxed{\text{FlyGym er ikke en plug-and-play simulering af BANC}}
\]

FlyGym leverer kroppen, sensorer, miljø og controllermuligheder; BANC leverer CNS-wiringen. At forbinde dem vil være **reelt forsknings- og engineeringarbejde**. FlyGyms eget design beskriver netop et hierarkisk interface, hvor brain-level behandling kan kobles til VNC-level motorstyring gennem descending og ascending repræsentationer. citeturn20search0

Det interface er præcis dér, hvor jeres første store integrationsarbejde bør ligge.

## Det projekt jeg ville give Astra

### Arbejdstitel

**Connectome-Guided Cognitive Augmentation in Drosophila**

Internt kan I stadig kalde det **Fly Brain XL**, men videnskabeligt ville jeg bruge et bredere navn, fordi neuron-skalering kun bliver én af flere konkurrerende hypoteser.

### Den centrale hypotese

Den stærkeste hovedhypotese er:

> **En digital, embodied Drosophila-agent kan opnå bedre generaliserbar læring, memory, adaptation og robusthed gennem biologisk strukturerede ændringer af neural dynamik, plasticitet og connectome, og disse forbedringer kan være mere compute-/parameter-effektive end tilfældig ekspansion eller tilsvarende generiske kunstige netværk.**

Den kan opdeles i tre niveauer.

**H₁ — Plasticity hypothesis:** Den biologiske topologi indeholder allerede tilstrækkelig computational struktur; væsentligt bedre adaptive evner kan fremkomme ved at lære bedre effektive synapseparametre og plasticitetsregler uden at tilføje neuroner.

**H₂ — Structural augmentation hypothesis:** Efter optimering af dynamik/plasticitet vil bestemte biologisk plausible strukturelle ændringer — eksempelvis nye forbindelser eller duplikation af bestemte celletyper/kredsløb — fortsat give forbedringer på held-out opgaver.

**H₃ — Scaling hypothesis:** Hvis strukturel vækst organiseres efter fluehjernens interne arkitektur frem for blind kopiering, eksisterer der en systematisk sammenhæng mellem neural ressource og generaliserbar capability.

Det er H₃, der bliver den seriøse version af **Fly Brain XL**.

### Hvorfor rækkefølgen betyder noget

Forestil dig, at I går direkte fra:

\[
158k\rightarrow316k\rightarrow632k
\]

neuroner og finder stigende score.

Det fortæller meget lidt.

Måske er større netværk bare lettere at træne.

Måske gav I dem dobbelt så mange synapser.

Måske har de dobbelt så mange frie vægte.

Måske voksede memory capacity trivielt.

Måske bruger de 10× så meget aktivitet.

Måske overfitter de benchmarken.

En bedre eksperimentel rækkefølge er:

\[
\text{native topology}
\rightarrow
\text{optimized dynamics}
\rightarrow
\text{optimized plasticity}
\rightarrow
\text{small rewiring}
\rightarrow
\text{small growth}
\rightarrow
\text{large growth}
\]

På hvert trin spørger I:

> **Tilføjer den nye frihedsgrad faktisk noget, som den simplere model ikke kunne opnå?**

### Interventionsbiblioteket

Astra bør ikke fra dag ét beslutte, *hvordan* man gør fluen smartere. I stedet bør projektet implementere en fælles augmentation-API, så interventioner kan konkurrere.

#### Plasticity-first augmentation

Dette er min klare favorit som første eksperiment.

Hold næsten hele connectomet fast.

Lad i første omgang kun udvalgte parametre ændre sig:

\[
W^{effective}_{ij}
\]

neurale tidskonstanter,

plasticity gain,

dopamin/modulatory gating,

og senere eventuelt lokale læringsregler.

Det er støttet af både task-optimized connectome-modeller og eksisterende Drosophila-learning-modeller, samtidig med at connectomet selv ikke fastlægger de nødvendige dynamiske parametre. citeturn16search0turn16search1turn22search0

Det interessante spørgsmål bliver:

> Hvor meget “headroom” eksisterer allerede i den biologiske topologi?

Det skal besvares **før** I tilføjer 100.000 nye neuroner.

#### Sparse causal rewiring

Dernæst får optimeringssystemet ret til meget få strukturelle ændringer.

Eksempelvis:

\[
\Delta E \le 0.001 E
\]

eller en anden fast lille ressourcegrænse.

Operationer kan konceptuelt være:

- tilføj en forbindelse,
- fjern en forbindelse,
- ændr connection multiplicity,
- ændr modulatory routing,
- duplikér en enkelt funktionel celleenhed.

I stedet for blind mutation kan kandidatændringer prioriteres efter effectome-lignende sensitivity-analyser:

\[
\frac{\partial \text{capability}}
{\partial W_{ij}}
\]

eller counterfactual ablations.

Det vil være langt mere informativt, hvis en forbedring på mange opgaver kræver ændring af 40 forbindelser end hvis den kræver 80.000 ekstra neuroner.

#### Celle-/microcircuit-vækst

Her begynder den egentlige **Fly Brain XL**.

Men I bør ikke starte med at:

> “copy neuron 37842 100 gange.”

FlyWire viser stærk struktur på celletypeniveau, og den tvær-connectome analyse viser både betydelig stereotypi og reel/teknisk variation. Mushroom body er særligt interessant: antallet af Kenyon cells varierede markant mellem FlyWire og hemibrain, mens connectivity viste tegn på kompensation for forskellen. citeturn17search0

Det giver jer en direkte biologisk ledetråd:

**Hjerner håndterer allerede variation i neuronantal gennem rebalancering af connectivity.**

Derfor bør en neuronduplikation efterfølges af en **homeostatic connectivity rule**, ikke bare kopiering af samtlige edges.

Den syntetiske operation kunne være noget i retning af:

\[
\text{Duplicate}(T,k)
\]

hvor \(T\) er en celletype eller funktionel population og \(k\) antal nye celler.

Derefter etableres forbindelser efter sandsynligheder betinget af:

\[
P(i\rightarrow j)
=
f(
T_i,T_j,
\text{neuropil},
\text{relative position},
\text{NT},
\text{motif},
\text{input budget},
\text{output budget}
)
\]

Det giver en generativ model af connectivity frem for node-kloning.

#### Module-preserving scaling

Det næste niveau er at ekspandere *funktionelle kredsløb*.

Eksempelvis:

\[
Brain_{1.0}
\rightarrow
Brain_{1.1}
\rightarrow
Brain_{1.25}
\rightarrow
Brain_{1.5}
\rightarrow
Brain_{2.0}.
\]

Men væksten må ikke nødvendigvis være uniform.

En optimization/evolution process kan få lov til at afgøre:

\[
N_{\text{MB}},\
N_{\text{CX}},\
N_{\text{vision}},\
N_{\text{descending}},
...
\]

under et samlet ressourcebudget.

Det interessante output er dermed ikke kun performance.

Det bliver:

> **Hvilke dele af hjernen forsøger optimeringen gentagne gange at gøre større, når man selekterer for en bestemt type kognitiv evne?**

Hvis 50 uafhængige evolutionary runs eksempelvis konsekvent udvider bestemte association-, memory- eller navigation-loops, ville det være et langt mere interessant resultat end “2× neurons scored 12 % higher”.

#### Artificial neurodevelopment

Dette bør være high-risk-sporet.

I stedet for at generere den voksne struktur direkte:

\[
Genome/RuleSet
\rightarrow
Connectome
\]

lærer I et komprimeret regelsæt, som forsøger at generere de statistiske og celletypespecifikke egenskaber i den biologiske connectome-familie.

Derefter ændres:

\[
RuleSet
\]

frem for millioner af individuelle synapser.

Det ville gøre evolutionær optimering langt mere realistisk beregningsmæssigt.

Men dette bør først startes efter, at simpler augmentation har vist et reelt signal.

### Cross-connectome regularisering er vigtigere, end den først ser ud

Det er farligt at lære “fluehjernens wiring rules” fra ét individ.

Den omfattende FlyWire/hemibrain-sammenligning fandt både stærk bevarelse af mange celletyper og betydelig variation, og paperet understreger eksplicit problemet med at skelne biologisk variation fra segmentation-, detection- og reconstruction-støj. citeturn17search0

Så Astra bør lave:

\[
\text{FAFB}
+
\text{BANC}
+
\text{MCNS}
+
\text{andre kompatible connectomes}
\]

til en **connectivity-prior**, hvor en edge ikke bare har:

\[
w_{ij}
\]

men eksempelvis:

\[
(w_{ij},\; confidence,\; conservation,\; sex\ specificity)
\]

Når augmentation engine skal afgøre, hvilke principper der er “biologiske”, bør den prioritere mønstre, der reproduceres på tværs af dyr, frem for artefakter fra én reconstruction.

Det er en afgørende beskyttelse mod at skabe en million-neuron “superflue”, hvis generative grammar i virkeligheden har lært reconstruction noise.

## Hvordan man måler, om fluen faktisk bliver smartere

Dette er sandsynligvis den vigtigste del af hele projektet.

Hvis benchmarken er dårlig, kan projektet bruge seks måneder på at “forbedre intelligens”, mens det egentlig bare optimerer én labyrint.

### Undgå én definition af intelligens

Jeg ville ikke definere intelligens som:

\[
IQ = \text{maze reward}.
\]

Og heller ikke:

\[
IQ = \text{tasks solved}.
\]

Det er for nemt at game.

I stedet bør I bygge noget, vi midlertidigt kan kalde:

# **FlyIQ**

Ikke som et biologisk IQ-tal, men som et versionsstyret **adaptive-capability benchmark**.

Det skal teste mindst fire forskellige ting:

\[
\text{learning}
+
\text{memory}
+
\text{generalization}
+
\text{adaptation}.
\]

Det er vigtigt, fordi reelle Drosophila-kredsløb allerede understøtter associativ læring, rumlig navigation og multimodal kontrol, og FlyGym understøtter miljøer med blandt andet vision og olfaktion. citeturn17search0turn15search4

### Benchmarkfamilier

Jeg ville strukturere FlyIQ omkring følgende familier.

| Evne | Eksempel på test | Primært spørgsmål |
|---|---|---|
| **Acquisition** | Lær hvilket cue der giver reward | Hvor hurtigt lærer modellen? |
| **Reversal learning** | Reward mapping vendes | Kan den opgive en gammel regel? |
| **Memory** | Test efter delay | Bevares information? |
| **Interference** | Lær B efter A | Overskriver ny læring gammel viden? |
| **Generalization** | Nye layouts, samme princip | Har den lært koncept eller scene? |
| **Transfer** | Tidligere erfaring hjælper ny task | Kan erfaring genbruges? |
| **Multimodal integration** | Vision og olfaction er delvist modstridende | Integrerer den information fleksibelt? |
| **Navigation** | Hidden target / path integration | Kan intern state bruges? |
| **Robustness** | Noise, sensor dropout, virtuelle lesions | Kollapser systemet ved perturbation? |
| **Novelty adaptation** | Nye cues/regler uden retraining af hele modellen | Hvor hurtigt tilpasser den sig? |

NeuroMechFly v2 har allerede demonstreret blandt andet multimodal navigation, odor navigation og path-integration-relaterede funktioner, så flere af disse benchmarkfamilier kan bygges oven på eksisterende simulatorinfrastruktur i stedet for fra nul. citeturn15search4

### Reversal learning er særlig vigtig

Antag to fluer:

**Fly A** lærer:

\[
red\rightarrow reward
\]

på 20 episodes.

**Fly B** lærer det på 40.

Fly A ser bedre ud.

Men nu ændres verden:

\[
red\rightarrow punishment
\]

\[
blue\rightarrow reward.
\]

Hvis A fortsætter mod rød i 300 episodes, mens B skifter efter 30, er B muligvis den mere adaptive agent.

Det er præcis sådanne tests, der kan skelne:

> “større memory / hurtigere fitting”

fra

> “mere fleksibel intelligence”.

### Held-out opgaver er obligatoriske

Dette bør være et projektprincip, som Astra **ikke må bryde**.

Del environments i:

\[
D_{\text{train}},
D_{\text{development}},
D_{\text{test}}
\]

før augmentation-algoritmen køres.

Testdistributionen skal eksempelvis kunne variere:

- maze topology,
- startpositioner,
- illumination,
- odor gradients,
- cue identities,
- reward mappings,
- sensor noise,
- obstacle configurations.

Og den endelige test bør holdes skjult fra den optimization loop, der ændrer hjernen.

Ellers risikerer I reelt neural architecture search mod benchmarken.

### Mål læringshastighed, ikke kun slutscore

En meget vigtig metrisk dimension er:

\[
P(n)
\]

hvor \(P\) er performance efter \(n\) experiences.

To modeller kan begge ende på 95 % succes, men:

\[
Model_A: 95\%\text{ efter }10^4\text{ trials}
\]

\[
Model_B: 95\%\text{ efter }10^2\text{ trials}.
\]

Model B har en helt anden læringseffektivitet.

Derfor ville jeg måle:

\[
AUC =
\int_{0}^{N}
P(n)\,dn.
\]

Det belønner både slutniveau og hurtig acquisition.

### Straf for bare at gøre hjernen større

Fly Brain XL kræver en særlig metric.

Ellers vinder 10×-hjernen måske bare, fordi den får 10× resources.

En sekundær samlet score kunne derfor være:

\[
S_{\text{efficient}}
=
\frac{
G
}{
1+
\lambda_N \Delta N/N_0+
\lambda_E \Delta E/E_0+
\lambda_A A
}
\]

hvor:

- \(G\) = generaliserings-/capability-score,
- \(N\) = antal neuroner,
- \(E\) = antal synaptiske edges/synapser,
- \(A\) = et proxy-mål for neural aktivitet eller computational cost.

Det præcise udtryk skal ikke fastlåses nu. Det væsentlige er princippet:

> **Rapportér capability og resource cost samtidigt.**

Endnu bedre bør de endelige resultater præsenteres som en **Pareto frontier**:

\[
(\text{capability},\text{neurons},\text{synapses},\text{compute})
\]

frem for kun ét magisk FlyIQ-tal.

### Det vigtigste scaling-eksperiment

Efter at baselines virker, ville jeg udføre noget i denne stil:

| Model | Neuroner | Biologisk topologi? | Plasticitet | Growth optimization |
|---|---:|---|---|---|
| Biological baseline | 1,00× | Ja | Ja | Nej |
| Weight-only | 1,00× | Ja | optimeret | Nej |
| Rewired | 1,00× | delvist | Ja | Ja |
| Random expansion | 1,25× | Nej | Ja | Nej |
| Degree-matched expansion | 1,25× | delvist | Ja | Nej |
| Cell-type growth | 1,25× | Ja | Ja | Ja |
| Module growth | 1,25× | Ja | Ja | Ja |
| Cell-type growth | 1,50× | Ja | Ja | Ja |
| Module growth | 2,00× | Ja | Ja | Ja |
| Generic artificial recurrent model | budget-matched | Nej | trainable | n/a |

Derefter:

\[
Capability=f(N)
\]

for hver scaling strategy.

Den virkelig spændende observation ville **ikke** være:

> større = bedre.

Det ville være:

\[
\frac{dCapability}{dResource}
\]

er markant større for biologisk struktureret vækst end for matched controls.

Eller endnu stærkere:

> En bestemt udvidelsesstrategi skaber en kvalitativ ny capability, som baseline og random-control ikke opnår.

### Brug virtuelle lesions som kontrol

Når en modificeret agent præsterer bedre, skal Astra spørge:

> **Hvilken modifikation var nødvendig?**

Hvis 20.000 neuroner blev tilføjet, så fjern dem igen gruppevis.

Hvis kun 700 er nødvendige for forbedringen, er det de 700, der er det videnskabeligt interessante resultat.

Det er samme grundidé som eksisterende connectome-modelstudier bruger, når de systematisk perturberer neuroner eller forbindelser for at identificere funktionelt nødvendige komponenter. citeturn18search0turn16search1

### En “smartere flue” skal være bedre på nye problemer

Den højest prioriterede success criterion bør derfor være noget i retning af:

> **Modifikationen må ikke alene forbedre tasks, der indgik i dens optimization objective. Den skal også forbedre performance, adaptation eller sample efficiency på hidtil usete task families eller miljødistributioner.**

Det er grænsen mellem:

**task optimization**

og noget, der begynder at ligne:

**forbedret general adaptive capacity**.

## Teknisk arkitektur, hardware og praktisk gennemførlighed

### Systemet bør bygges lagdelt

Jeg ville ikke forsøge at skrive ét gigantisk program:

```text
fly_brain.py
```

som loader 158.000 neuroner, kører physics, lærer og evolverer.

Arkitekturen bør være:

```text
┌──────────────────────────────────────────────┐
│              Benchmark / FlyIQ               │
├──────────────────────────────────────────────┤
│            Augmentation engine               │
│ plasticity / rewiring / growth / evolution   │
├──────────────────────────────────────────────┤
│             Neural dynamics                  │
│ rate / LIF / learned effectome approximator  │
├──────────────────────────────────────────────┤
│             Neural interfaces                │
│ sensory mapping ↔ CNS ↔ motor mapping        │
├──────────────────────────────────────────────┤
│             BANC / FAFB / MCNS               │
│ structural connectome + annotations          │
├──────────────────────────────────────────────┤
│             FlyGym / MuJoCo                  │
│ body + sensors + environment + physics       │
└──────────────────────────────────────────────┘
```

Hvert lag skal kunne testes isoleret.

Det er afgørende for et fler-måneders researchprojekt, fordi ellers kan I ikke vide, om en failure skyldes:

- dårlig connectome-parsing,
- numerisk instabil neural dynamik,
- sensoradapteren,
- locomotion-controlleren,
- benchmarken,
- plasticiteten,
- eller augmentation-algoritmen.

### Start ikke med alle 158.262 neuroner

Det lyder paradoksalt, når projektet handler om hele fluehjernen.

Men den hurtigste vej til et troværdigt whole-brain-projekt er sandsynligvis først at bygge et end-to-end **subsystem**.

Et godt første kredsløb bør indeholde:

\[
\text{sense}
\rightarrow
\text{learning/navigation}
\rightarrow
\text{decision}
\rightarrow
\text{descending action}.
\]

Mushroom body er oplagt til associative-memory-eksperimenter, mens central complex er særlig relevant for navigationsdelen; BANC-studiet identificerer netop olfactory/mushroom-body-systemer og central complex som relativt superviserende i forhold til mere direkte sensorimotoriske loops. citeturn19search2turn19search7

Efter subsystemtesten kan den samme API skaleres op.

### Tre neural-modelniveauer

Astra bør bevare mindst tre abstraktionsniveauer.

**Fast baseline model.** En simpel rate- eller LIF-model bruges til strukturelle sanity checks. En whole-brain LIF-tilgang har allerede vist, at selv simple dynamics plus connectivity og neurotransmitteridentitet kan give biologisk informative forudsigelser. citeturn15search0

**Differentiable connectome model.** Her er topologien constrained af connectomet, mens dynamiske parametre kan optimeres. Lappalainen et al. demonstrerer, at denne task-optimized/connectome-constrained tilgang kan forudsige kendt aktivitet i synssystemet. citeturn16search0

**Plastic adaptive model.** Her tillades online learning gennem biologisk inspirerede lokale update rules eller modulatory mechanisms. Mushroom-body-modeller er et naturligt sted at etablere den første version. citeturn22search0

Det ville være en fejl at kræve den mest biophysically detailed model fra begyndelsen.

Målet bør være:

> **Den mindst komplekse dynamiske model, som er tilstrækkeligt grounded til, at augmentation-resultaterne er meningsfulde.**

### Sensor- og motorbroen

FlyGym leverer allerede simuleret syn, lugt, mekanosensoriske signaler, fysisk kontakt og biomekanisk kontrol. citeturn15search4turn20search0

Men I skal bygge mappings såsom:

\[
FlyGym_{\text{vision}}
\rightarrow
\text{visual input neurons}
\]

\[
FlyGym_{\text{odor}}
\rightarrow
\text{olfactory sensory representation}
\]

og:

\[
\text{descending neural state}
\rightarrow
FlyGym_{\text{motor controller}}.
\]

I begyndelsen bør motor-output sandsynligvis være **hierarkisk**.

Det vil sige, at hjernen eksempelvis styrer lavdimensionale intents:

\[
[\text{forward speed},
\text{turn},
\text{stop},
\text{groom},
...]
\]

mens en eksisterende FlyGym locomotion-controller omsætter dem til de mange biomekaniske joint actions.

Senere kan VNC/BANC-integrationen blive mere detaljeret.

Det følger også den hierarkiske controllerstruktur, som FlyGym selv er designet til at understøtte. citeturn20search0

### Hvor meget computer behøver I?

Den gode nyhed er:

**Du behøver ikke et datacenter for at starte projektet.**

FlyWire-connectomet har 139.255 neuroner og 54,5 millioner synapser, mens Codex' aggregerede graph representation er væsentligt mindre end den rå EM-dataset. citeturn15search3turn21view0

Den rå FlyWire EM-volume er på cirka 100 teravoxels, men jeres projekt har næsten aldrig brug for at analysere de rå voxels. Celletyper, neuroninformation, connectivity og andre dataproducts kan hentes gennem det eksisterende ecosystem/Codex. citeturn17search0turn21view0

Som en simpel størrelsesorden:

\[
50\,000\,000\times
(4+4+4)\text{ bytes}
\approx600\text{ MB}
\]

for en ekstremt minimalistisk 32-bit:

```text
source_id
target_id
weight
```

representation.

Virkelig software bruger naturligvis langt mere hukommelse til indices, metadata, tensors, gradients og kopier.

Derfor er min **engineering-vurdering**, ikke et krav fra en paper, følgende:

| Arbejde | Praktisk startniveau | Komfortabelt niveau |
|---|---|---|
| Connectome graph/query/analyse | 32 GB RAM, moderne CPU | 64 GB RAM |
| Reducerede neural-modeller | 32 GB RAM | 64 GB + GPU |
| FlyGym development | moderne CPU | CUDA GPU + 32–64 GB RAM |
| Differentiable større subnetworks | 12–24 GB VRAM | 24 GB+ VRAM |
| Whole-brain trainable dynamics | 64 GB RAM minimum-ish | 128 GB RAM + 24–48 GB VRAM |
| Population evolution / mange agents | cloud/HPC | multi-GPU/HPC |
| Million-neuron trainable XL experiments | ikke en normal laptop-opgave | distribueret compute sandsynligt |

FlyGym 2's GPU-mode benytter Warp/MJWarp; NVIDIA Warp angiver CUDA-capable NVIDIA-GPU som GPU-path. citeturn20search0turn20search8

Så hvis du skulle bygge én workstation specifikt til dette projekt, ville jeg prioritere:

\[
\boxed{\text{RAM}+\text{VRAM}+\text{hurtig NVMe}}
\]

mere end en ekstrem high-end CPU.

Men jeg ville **ikke købe dyr hardware før baseline-prototypen er lavet**.

### Et vigtigt hardware-eksempel på, hvad I ikke behøver gøre

Schlegel et al. udførte et all-vs-all morfologisk NBLAST på cirka 139.000 FlyWire-neuroner. Deres all-by-all matrix fyldte mere end **500 GB RAM**, og store analyser blev kørt på en cluster-node med 112 CPU'er og 1 TB RAM. citeturn17search0

Det lyder skræmmende.

Men det er ikke repræsentativt for normal connectome-analyse.

Det var:

\[
139,000^2
\]

morfologiske sammenligninger.

I skal undgå den type \(O(N^2)\)-beregning, medmindre den specifikt er nødvendig.

Brug de allerede eksisterende celletyper og annotations i stedet for at genberegne alt fra voxel-level morphology.

### Hvad der bliver dyrt

Det dyre er ikke primært at **lagre connectomet**.

Det dyre er at gøre noget som:

\[
1000\text{ candidate brains}
\times
100\text{ tasks}
\times
100000\text{ simulation steps}.
\]

Og endnu værre hvis hver candidate brain kræver backpropagation through time gennem et large recurrent system.

Derfor bør senere evolutionary search arbejde med en **komprimeret genotype**:

```text
plasticity parameters
cell-type multipliers
module duplication rules
wiring-rule coefficients
neuromodulatory rules
```

ikke millioner af uafhængige genes/synapses.

Det er også konceptuelt mere interessant: evolution opdager da **regler for hjernearkitektur**, ikke bare et enormt weight matrix.

### Wet-lab er ikke nødvendigt for første fase

En stærk computational paper/prototype kan efter min vurdering opbygges uden selv at drive et Drosophila-laboratorium, fordi connectome-dataene, eksisterende modellering og FlyGym giver betydelige computational resources. citeturn21view0turn20search0

Men hvis projektet når til:

> “Vi forudsiger, at ændring X faktisk forbedrer learning i en levende flue”

så bliver wet-lab-validering meget værdifuld.

Shiu et al. viser allerede den relevante model: computational connectome-model → neural prediction → optogenetisk/behavioral validation. citeturn15search0

Og effectome-arbejdet foreslår specifikt targeted perturbation som vej til kausal identifikation af dynamiske påvirkninger. citeturn16search1

Jeg ville derfor se wet lab som:

\[
\text{Phase II validation}
\]

ikke som en forudsætning for at starte.

En senere lab-partner kunne være langt mere rationel end at opbygge imaging, genetics og fly-handling capability internt fra dag ét.

## Forskningsplanen Astra bør følge

### Forskningsarbejdet skal begynde med reproduktion, ikke invention

Den største risiko i et AI-ledet researchprojekt er, at systemet producerer fem hundrede plausible idéer uden at vide, hvilke ting der allerede er gjort.

Astra bør derfor først have en eksplicit **replication gate**.

Før nye XL-experimenter tillades, skal systemet kunne demonstrere, at det forstår forskningsfronten ved eksempelvis at kunne reproducere eller funktionelt efterligne centrale elementer fra:

Shiu-style connectome dynamics, hvor whole-brain connectivity bruges til sensorimotoriske predictions. citeturn15search0

Lappalainen-style connectome-constrained task optimization i et mindre circuit. citeturn16search0

FlyGym embodied navigation/controller pipelines. citeturn15search4turn20search0

Mushroom-body learning/plasticity i en reduceret model. citeturn22search0

Målet er ikke at kopiere samtlige papers.

Målet er at demonstrere:

> “Vi har forstået hver hovedkomponent godt nok til at vide, hvilken ny komponent vi nu tilfører.”

### Roadmap for et fler-måneders projekt

| Fase | Hovedmål | Exit criterion |
|---|---|---|
| **Grounding** | State-of-the-art, datasets, reproductions | Ingen vigtig project claim uden citation/evidence |
| **Embodied baseline** | CNS/subsystem → FlyGym | Biological baseline klarer stabile standardtasks |
| **FlyIQ v0** | Benchmark + train/test split | Baseline kan scores reproducerbart |
| **Plasticity** | Online learning/memory | Agent lærer mindst flere taskfamilier |
| **Causal augmentation** | Sparse weights/edges/circuits | Held-out forbedring over baseline |
| **Fly Brain XL** | 1.1×–2× struktureret vækst | Capability scaling mod matched controls |
| **Evolution/development** | Komprimerede growth rules | Gentagne runs finder stabile arkitekturprincipper |
| **External validation** | Andre connectomes/tasks | Effekten overlever distribution shift |
| **Biological hypothesis** | Kandidat til live test | Lille, præcis, falsificerbar intervention |

Der skal være et **stop criterion** efter hver fase.

Eksempel:

Hvis 1,5× flere neuroner kun giver den samme forbedring som et budget-matched generisk recurrent network, så er:

> “biological connectome scaling is special”

ikke understøttet.

Det skal i `DEAD_ENDS.md`.

Ikke skjules og ikke “optimeres væk”.

### Scaling skal først komme efter parameter-matchede kontroller

Et minimum af controls bør være:

\[
C_0=\text{biological baseline}
\]

\[
C_1=\text{same topology, optimized parameters}
\]

\[
C_2=\text{same N, controlled rewiring}
\]

\[
C_3=\text{larger random network}
\]

\[
C_4=\text{degree-/cell-type-matched synthetic growth}
\]

\[
C_5=\text{biologically optimized growth}
\]

\[
C_6=\text{generic artificial network at comparable budget}.
\]

Kun hvis:

\[
C_5>C_3,C_4,C_6
\]

på **held-out adaptive tasks**, bliver påstanden om biologisk connectome-scaling virkelig interessant.

### Test flere random seeds

Evolutionary/neural architecture search kan være ekstremt seed-sensitive.

Et “nyt brain architecture”-resultat bør derfor ikke bestå af:

> “Run 37 blev supergod.”

I vil have konvergens:

\[
Run_1\rightarrow Module_X
\]

\[
Run_2\rightarrow Module_X
\]

\[
Run_{17}\rightarrow Module_X
\]

osv.

Så bliver spørgsmålet:

> Hvorfor vælger uafhængige optimization trajectories alle denne kredsløbstype?

Det er potentielt neuroscience.

### Test mod biologisk variation

Her har I en usædvanligt god kontrolmulighed.

FAFB er én hunflue; BANC er en anden; MCNS er en hanflue, og ældre hemibrain-data giver yderligere sammenligningsmateriale. FlyWire-arbejdet viste både høj stereotypi og målbar inter-individuel variation. citeturn17search0turn21view0

Hvis jeres “geniale” augmentation ligger inden for almindelig biologisk variance og ikke giver reproducerbar performance-effekt, er den mindre interessant.

Hvis den derimod bevæger arkitekturen uden for den normale biologiske manifold på en kontrolleret måde og giver generaliserbar capability-forbedring, er den langt mere interessant.

### Ikke tag papers for 100 % sandhed — formaliser det

Din intuition her er helt rigtig.

Men “vær skeptisk” skal oversættes til en procedure.

Astra bør skelne mellem:

\[
\text{published claim}
\neq
\text{established fact}
\neq
\text{reproduced by us}.
\]

Især fordi noget af den mest interessante 2026-forskning stadig er bioRxiv-preprints, eksempelvis whole-brain spontaneous-dynamics-modellen og den nye sensory-loss/visual-learning undersøgelse. citeturn18search0turn18search1

Enhver vigtig claim bør have status som eksempelvis:

```text
CLAIMED
REPLICATED_BY_OTHERS
REPLICATED_BY_US
PARTIALLY_REPLICATED
CONTRADICTED
UNKNOWN
```

Det vil gøre projektet meget mere modstandsdygtigt over for at bygge tre måneders arbejde oven på et skrøbeligt paper-resultat.

## Dokumentation, risici og den konkrete Astra-handoff

### Repository-strukturen er en del af forskningsmetoden

Jeg ville kræve følgende dokumenter fra første dag:

| Fil | Formål |
|---|---|
| `README.md` | Hvad projektet forsøger lige nu |
| `STATE_OF_THE_ART.md` | Levende litteraturkort |
| `CLAIMS_LEDGER.md` | Claims, evidens, confidence og reproduction status |
| `NOVEL_IDEAS.md` | Nye hypoteser og billigste falsifikationstest |
| `DEAD_ENDS.md` | Alt afprøvet, som ikke virkede |
| `DECISIONS.md` | Store designvalg og hvorfor |
| `BENCHMARK_SPEC.md` | FlyIQ-regler og frozen test protocol |
| `EXPERIMENT_REGISTRY.md` | Alle runs, seeds, configs og resultater |
| `DATA_PROVENANCE.md` | Dataset, version, snapshot og transformations |
| `REPRODUCTIONS.md` | Hvilke litteraturresultater teamet selv har reproduceret |

### `DEAD_ENDS.md` skal være seriøs

Et entry bør eksempelvis være:

```markdown
## EXP-0047 — Uniform doubling of Kenyon-cell population

Hypothesis:
Doubling KC count improves associative learning and transfer.

Dataset:
BANC v888

Model:
flybrain-dynamics commit 9af31...

Benchmark:
FlyIQ 0.3

Result:
+18% training-task performance
-4% held-out generalization
2.1x synaptic compute

Interpretation:
Gain is compatible with increased raw capacity but gives no evidence
for improved general adaptive capability.

Why stopped:
Dominated on capability/compute Pareto frontier by EXP-0041.

Could revisit if:
A learned connectivity-homeostasis rule is introduced.
```

Det er ekstremt værdifuldt seks måneder senere.

Ellers kommer en ny agent — eller et menneske — til at genopfinde præcis samme idé.

### `NOVEL_IDEAS.md` bør kræve falsifikation

Ikke:

```markdown
Idea:
Maybe duplicate the mushroom body.
```

Men:

```markdown
Hypothesis:
Selective expansion of associative sparse-coding populations increases
sample efficiency more than uniform CNS expansion at equal added-synapse
budget.

Novelty status:
No direct equivalent located in literature scan YYYY-MM-DD.

Closest prior work:
...

Cheapest falsification:
Run reduced MB model with 1.0x / 1.25x / 1.5x KC populations while
holding output dimensionality and synaptic budget controls fixed.

Would count against hypothesis:
Randomly expanded control performs equally well.

Would count strongly for hypothesis:
Improvement transfers to previously unseen cue families and survives
resource normalization.
```

Så bliver idébanken en forskningsmotor i stedet for et inspirationsdokument.

### `CLAIMS_LEDGER.md` kan blive den vigtigste fil

Eksempel:

```markdown
CLAIM:
"A larger connectome should produce greater intelligence."

SOURCE:
None — internal hypothesis.

STATUS:
UNTESTED.

CONFIDENCE:
Low.

COUNTEREVIDENCE:
Brain size alone confounds parameter count and compute.

TEST:
Compare structured, randomized and generic networks under
resource-matched conditions.
```

Og:

```markdown
CLAIM:
"Connectivity alone is sufficient to specify fly-brain dynamics."

SOURCE:
Not supported.

COUNTEREVIDENCE:
Effectome work shows connectome specifies possible paths but not causal
effective interaction strength; task-constrained and activity-fitted
models require additional dynamical parameters.

STATUS:
REJECTED AS PROJECT ASSUMPTION.
```

Det sidste er direkte understøttet af den nuværende modelling-litteratur. citeturn16search0turn16search1turn18search0

### De største videnskabelige risici

**Simulation-reality gap.** I kan gøre *modellen* smartere ved at udnytte fejl i simulatoren, uden at resultatet siger noget om Drosophila. Derfor bør performance modsvares af biologiske constraints og senere helst eksperimentel validering. FlyGym er eksplicit en model af flyens biomekaniske/sensoriske system, ikke den levende organisme selv. citeturn15search4turn20search0

**Connectome-is-dynamics fallacy.** Synapseantal må ikke behandles som præcise biologiske synaptiske effekter. Effectome-arbejdet beskriver direkte, hvorfor den kobling generelt er underbestemt. citeturn16search1

**Single-animal overfitting.** FlyWire repræsenterer én hjerne, og cross-connectome-arbejdet dokumenterer både variation og reconstruction uncertainty. citeturn17search0

**Benchmark hacking.** Hvis architecture search ser testtasks, vil I optimere testen snarere end intelligence.

**Resource confound.** Flere neuroner giver flere resources. Scaling skal sammenlignes med budget-matchede kontroller.

**Specialization masquerading as intelligence.** Den nye sensory-loss-undersøgelse er et godt eksempel: én kognitiv modalitet kan forbedres gennem rebalancering, uden at organismen nødvendigvis er blevet generelt mere kapabel. citeturn18search1

**Biological realism trap.** Det modsatte problem er at bruge år på ionkanaler og detaljer, før der findes et funktionelt benchmark. Shiu- og Lappalainen-resultaterne viser, at relativt reducerede modeller stadig kan være videnskabeligt informative. citeturn15search0turn16search0

### Hvad der vil være et virkelig stærkt resultat

Et godt resultat er **ikke** nødvendigvis:

> “Vi lavede en flue med en million neuroner.”

Et langt stærkere resultat kunne være:

> “Under identisk synapse- og compute-budget fandt evolutionær optimization gentagne gange en 7 % ekspansion af tre bestemte cellepopulationer og 0,08 % rewiring. Modifikationen forbedrede sample efficiency, reversal learning og held-out multimodal navigation på tværs af environments, men ikke en matched random expansion.”

Endnu bedre:

> “Effekten reproduceres med forskellige initial seeds og i mere end ét connectome.”

Endnu bedre igen:

> “Ablation viser, at en lille ny recurrent motif er nødvendig for gevinsten.”

Og det absolut stærkeste resultat ville være:

> “Modellen forudsagde en biologisk implementerbar ændring, og eksperimenter i levende Drosophila viste en tilsvarende forbedring på den forudsagte adfærd.”

Det ville koble connectomics, computational neuroscience, embodied AI og experimental neuroscience på en meget stærk måde. Eksisterende connectome-modelstudier viser allerede, at computational predictions kan føres videre til eksperimentelle tests, så selve forskningsloopet er realistisk, selv om jeres augmentation-hypotese er mere ambitiøs. citeturn15search0

### Den første beslutning jeg ville fryse

**Brug ikke “intelligence = task score”.**

Frys i stedet dette som projektets definition:

> **For dette projekt betyder øget intelligens en reproducerbar forbedring i en agents evne til hurtigt at lære, huske, generalisere, omstille sig og fungere robust på flere forskellige embodied taskfamilier, især på opgaver og environments der ikke indgik direkte i optimeringen, relativt til dens neural- og computational-resourceforbrug.**

Den definition beskytter næsten alle efterfølgende eksperimenter mod de mest oplagte falske positive resultater.

### Astra-handoff

```text
PROJECT:
Connectome-Guided Cognitive Augmentation in Drosophila
Internal codename: Fly Brain XL

MISSION:
Investigate whether a computational agent constrained by real Drosophila
connectomics can be made more generally adaptive through modifications
to neural dynamics, plasticity, connectivity, circuit composition or
brain size.

DO NOT ASSUME:
- that a connectome is an executable brain;
- that synapse count equals biological effective strength;
- that adding neurons increases intelligence;
- that better performance on one task means increased general capability;
- that a published result is correct merely because it is published;
- that one fly connectome represents every fly;
- that a larger model is better if it merely receives more computational
  resources.

PRIMARY STRUCTURAL DATA:
Start from BANC v888 for embodied work.
Use FAFB v783 as the mature whole-brain reference.
Use MCNS v1.0 and other connectomes for robustness/comparative tests.

ENVIRONMENT:
Use FlyGym / NeuroMechFly v2 unless a demonstrably superior environment
is found.

CORE RESEARCH QUESTION:
Can biologically constrained modification of a fly nervous system produce
improvements in learning, memory, adaptability and held-out generalization
that cannot be explained merely by additional parameters, synapses,
compute or benchmark overfitting?

INITIAL RESEARCH PRIORITY:
1. Thoroughly map and continuously update the state of the art.
2. Reproduce enough existing connectome modelling to establish a trusted
   baseline.
3. Build a reproducible embodied benchmark before optimizing the brain.
4. Establish plastic, learnable dynamics on fixed biological topology.
5. Test sparse causal modification.
6. Only then begin structural scaling / Fly Brain XL experiments.
7. Compare every augmentation against resource-matched controls.
8. Treat developmental/evolutionary growth as a later high-risk branch.

BENCHMARK PRINCIPLE:
Do not optimize a single maze or reward.
Evaluate acquisition speed, memory, reversal learning, transfer,
generalization, multimodal integration, robustness and efficiency.
Freeze held-out task distributions before major architecture searches.

NOVELTY PRINCIPLE:
Before an experiment is labelled novel, search current literature for:
- exact idea;
- adjacent idea;
- same method on another Drosophila connectome;
- same method in another organism;
- new preprints since the previous search.

Novelty must be dated because this research area is moving quickly.

SCIENTIFIC SCEPTICISM:
Maintain CLAIMS_LEDGER.md.
For each consequential scientific assumption record:
- exact claim;
- source;
- evidence type;
- confidence;
- whether independently replicated;
- whether reproduced internally;
- plausible alternative explanation;
- cheapest experiment that could falsify it.

REQUIRED PROJECT FILES:
README.md
STATE_OF_THE_ART.md
CLAIMS_LEDGER.md
REPRODUCTIONS.md
BENCHMARK_SPEC.md
DATA_PROVENANCE.md
EXPERIMENT_REGISTRY.md
DECISIONS.md
DEAD_ENDS.md
NOVEL_IDEAS.md

DEAD_END RULE:
A negative experiment is project knowledge.
Never delete or silently abandon a failed research direction.
Record hypothesis, implementation, data version, code commit, random
seeds, metrics, result, interpretation, reason for stopping, and
conditions under which it should be revisited.

NOVEL IDEA RULE:
Every idea in NOVEL_IDEAS.md must include:
- hypothesis;
- why it might matter;
- closest known prior work;
- estimated novelty confidence;
- cheapest falsification experiment;
- result that would support it;
- result that would kill it.

EXPERIMENT RULE:
All experiments must be reproducible from immutable configuration files.
Log:
- dataset snapshot/version;
- code commit;
- seed;
- model parameters;
- augmentation;
- training distribution;
- benchmark version;
- compute/resources;
- raw and normalized performance.

FLY BRAIN XL RULE:
Do not begin with naive whole-brain duplication.

Compare at minimum:
A. biological baseline;
B. native topology with optimized dynamics/plasticity;
C. sparse rewiring;
D. random growth;
E. degree/cell-type-matched growth;
F. biologically structured module growth;
G. generic artificial network at comparable resource budget.

Suggested structural scaling points:
1.00x
1.10x
1.25x
1.50x
2.00x

Only continue towards larger scales if smaller experiments show a
scientifically interesting capability/resource trend.

KEY ANALYSIS:
For every improved brain ask:
"What is the smallest subset of modifications necessary to retain the
improvement?"

Use ablations and counterfactual edits to answer this.

SUCCESS IS NOT:
"A larger network got a larger reward."

SUCCESS IS:
"A biologically meaningful modification produces reproducible improvements
in multiple adaptive capabilities, including held-out tasks, and survives
appropriate resource-matched, randomized and architectural controls."

VERY STRONG SUCCESS:
Independent optimization runs converge on the same architectural principle.

EXCEPTIONALLY STRONG SUCCESS:
The discovered principle generalizes across connectome datasets or makes
a specific biological prediction that is subsequently validated.

FREEDOM TO EXPLORE:
The above defines evidential standards, not the solution path.
Do not assume the preferred intervention will be scaling, plasticity,
rewiring, development or evolution.
Follow surprising results.
Challenge published assumptions when there is a concrete falsifiable
alternative.
Record unexpected observations even when they contradict the current
project thesis.
```

Den vigtigste ændring fra den oprindelige **Fly Brain XL**-idé er derfor ikke, at idéen skal gøres mindre ambitiøs. Det modsatte.

Projektet bør være bredere:

\[
\boxed{
\textbf{Find ud af, hvad der faktisk skal ændres i en fluelignende hjerne for at gøre den mere adaptivt kapabel.}
}
\]

Og først når I kan måle det ordentligt, bør I stille det mere radikale spørgsmål:

\[
\boxed{
\textbf{Hvis biologisk organiseret neural vækst fortsættes ud over den naturlige fluehjerne,
opstår der så en reel capability-scaling law?}
}
\]

Det spørgsmål ser stadig, efter den nuværende litteraturgennemgang, ud til at være et af de mest originale og potentielt interessante slutmål i projektet. Men det, der kan gøre resultatet videnskabeligt vigtigt, er netop **FlyIQ-benchmarken, effectome/dynamics-laget, plasticiteten, resource-matchede kontroller, cross-connectome-validering og den systematiske dokumentation af negative resultater** — ikke alene det faktum, at den syntetiske hjerne bliver større. citeturn16search1turn17search0turn19search2turn20search0