# Rebuilding the presentations

Scientific regeneration and HTML generation are ordinary Python; see README.md. All 20 slides share `presentation/slides.json`. It is generated from numerical results by `src/presentation_data.py`, so edit that source for durable content changes. The offline HTML embeds its vector charts and requires no server or network.

PowerPoint export uses the Codex bundled JavaScript `@oai/artifact-tool`. Set the paths returned by `load_workspace_dependencies`:

```sh
export RUNTIME_NODE_MODULES="/absolute/path/to/bundled/node_modules"
export RUNTIME_PYTHON="/absolute/path/to/bundled/python3"
export SKILL_DIR="/absolute/path/to/presentations/skills/presentations"
ln -s "$RUNTIME_NODE_MODULES" .build/node_modules
cp src/build_deck.mjs .build/build_deck.mjs
"/absolute/path/to/bundled/node" .build/build_deck.mjs
```

Use an existing symlink rather than recreating it if present. The PowerPoint finalizer checks native chart workbooks, shape geometry and package integrity. Existing generated PPTX is moved to `.build/previous-export.pptx` before a new final file is written. The draft input folder is never touched. Source includes local runtime fallbacks for this workspace; set the environment variables on another machine. Do not install a substitute presentation package into the bundled runtime.

`src/export_pdf.mjs` exports the HTML's print layout through headless Chrome, renders each slide to private QA screenshots, checks layout bounds and keyboard navigation, and writes the PDF. It needs Playwright, supplied by the same Node runtime. Copy it into `.build` and run with bundled Node. On non-Mac systems set `CHROME_BIN` to a Chromium/Chrome executable. Chrome is used only to render our local document; no browsing of a user profile is required. The standalone figures use Matplotlib; none are AI-generated images.

The delivered PPTX uses native editable charts with numeric workbook snapshots. Native chart coordinates are rounded to ten significant digits because Excel cannot preserve arbitrary float representations. Raw scientific results retain full double precision. Charts use explicit log10-transformed axes where indicated to preserve the scaling plots across applications; values in those workbooks are the displayed log10 coordinates, not untransformed concentration values. Full original data live in results/ and in the source generators.

The finished deck was rendered and inspected using Artifact Tool, and the HTML/PDF through Chrome. It was not tested by opening in desktop PowerPoint. PowerPoint and HTML preserve the draft's dark blue, sky blue and teal design direction; scientific content and slide count were rebuilt for the new model.

## Team 7 deck using the supplied NYUAD template

`presentation/Team_7_NYUAD_Pitch.pptx` is the separate 15-slide pitch created for the follow-up request. It imports the actual `../Slides Templates  and Judging/NYUAD Hackathon Presentation Template.pptx`, retaining its white background, Arial typography, red corner artwork, purple footer, master and branded layout. Instruction-only slides are replaced with project content; the supplied template explicitly permits adapting the slides. Extended slides duplicate the imported slide structure. Neither the template nor the draft is modified.

Content lives in `presentation/Team_7_Pitch.json`, including citations and speaker notes. Six charts are native editable objects with embedded data workbooks. The first 14 slides form the pitch; the final slide supports judge questions. The closing metrics distinguish modeled estimator improvement, a water-monitoring proxy, and equal probe energy from unmeasured environmental impact. A demo walkthrough is in slide 10's notes. The template's October ideation/in-person presentation distinction is recorded in the cover notes and the report.

Use the same bundled Node setup above, then copy `src/build_team7_pitch.mjs` to `.build/build_team7_pitch.mjs` and run it with `RUNTIME_NODE_MODULES` set. It expects the supplied template at the sibling path above. The script includes local runtime locations; update them for another machine. The new deck is independent of the original 20-slide presentation. Its source JSON is maintained separately; running the original presentation generator does not replace it.

The template asks for team identity and roster details. Team 7 is the authorized working name. Student/mentor affiliations, a photo and a team logo remain to be supplied; they are not invented. The quantum-computing emphasis of the judging rubric is addressed explicitly: this project demonstrates a quantum-sensing hypothesis, not a computational speedup.

## Five-slide ideation version

`presentation/Team_7_Ideation.pptx` is the separate five-slide version: problem and SDG 6 targets, proposed solution, simulation design, current results, then impact/sustainability/next steps. It retains the NYUAD template and includes one editable results chart. Sources and qualifications are in speaker notes; all headline results remain explicitly simulated. SDG target definitions are sourced from [UN Goal 6](https://sdgs.un.org/goals/goal6).

Edit `presentation/Team_7_Ideation.json` for content. To rebuild, run `python src/prepare_ideation_template.py`, copy `src/build_ideation.mjs` into `.build`, then run it with the same bundled Node and `RUNTIME_NODE_MODULES` setup above. The helper creates a private five-slide template copy and leaves the supplied template unchanged. The earlier 15-slide pitch is preserved.

## Expanded visual ideation version

`presentation/Team_7_Ideation_Visual.pptx` retains five slides while adding two sourced context photographs and four editable simulation charts. Each chart includes an explanatory caption; the notes carry full setup, caveats and references. Image provenance and licenses are in `presentation/assets/SOURCES.md`. The images are embedded for offline use.

Build with `src/prepare_ideation_template.py`, then copy `src/build_ideation_visual.mjs` into `.build` and run it using the bundled Node setup. This version takes numerical chart series from `presentation/slides.json`, contextual notes from `presentation/Team_7_Ideation.json`, and maintains its richer visible copy in the JavaScript source. Original and previous decks are preserved. The runtime output is visually inspected; it is not claimed to have been opened in desktop PowerPoint.

Revision of 7 October 2026: all decks include visible simulation implementation details. The general deck has 20 slides (implementation detail on slides 4, 19–20); the NYUAD pitch has 15 slides (implementation on slides 3–4); both ideation decks retain five slides (implementation on slide 3). Source citations and detailed reproduction notes accompany the slides.
