# Error analysis (run: before)

False-positive list length: 25.  False-negative list length: 88.
Lists are sorted alphabetically (case-insensitive) by (subject, predicate, object);
positions are 1-based, with wrap-around (position mod length) for short lists.

Error codes: E1 wrong span | E2 pronoun | E3 alias split | E4 direction/role | E5 negation/time | E6 source gap (my triple is right, Wikidata lacks it) | E7 other

## False positive at position 8
- Triple: (James Chadwick, receivedAward, Heginbottom Scholarship)
- Sentence or source evidence: At the end of his first year, he was awarded a Heginbottom Scholarship to study physics.
- Error code: E6 (likely source gap)
- Why: The sentence explicitly awards Chadwick the scholarship. Its name did not match the exported award values.
- Fix: Check the Wikidata award labels and aliases before changing the extraction rule.

## False positive at position 17
- Triple: (Richard Feynman, worksAt, Thinking Machines Corporation)
- Sentence or source evidence: In the 1980s he began to spend his summers working at Thinking Machines Corporation, helping to build some of the first parallel supercomputers and considering the construction of quantum computers.
- Error code: E7 (employment status unclear)
- Why: The sentence supports summer work at the company. It does not specify his formal employment status, and the employer export gave no match.
- Fix: Check the employment role and aliases before deciding whether the rule needs a stricter employer test.

## False positive at position 18
- Triple: (Werner Heisenberg, educatedAt, LudwigMaximiliansUniversität München)
- Sentence or source evidence: From 1920 to 1923, he studied physics and mathematics at the Ludwig-Maximilians-Universität München under Arnold Sommerfeld and Wilhelm Wien and at the University of Göttingen with Max Born and James Franck and mathematics with David Hilbert.
- Error code: E1 (wrong span)
- Why: The extractor dropped hyphens inside the university name and joined neighbouring words.
- Fix: Preserve hyphens between selected name tokens. The after run recovered one education match.

## False positive at position 20
- Triple: (Werner Heisenberg, receivedAward, Prize)
- Sentence or source evidence: It was at that time announced that Heisenberg had won the Prize for 1932 "for the creation of quantum mechanics, the application of which has, inter alia, led to the discovery of the allotropic forms of hydrogen".
- Error code: E1 (incomplete name)
- Why: The sentence refers back to a prize with the generic words ‘the Prize’. The extracted object cannot identify an award.
- Fix: Skip generic award words when no identifying name is present. The after run removed one false award.

## False negative at position 9
- Triple: (Erwin Schrödinger, receivedAward, Fellow of the American Physical Society)
- Sentence or source evidence: No matching wording located in the saved article using the award name and likely variants.
- Error code: E7 (reference value missed)
- Why: The award appears in the Wikidata reference. A search of the saved article did not locate a passage naming it under the searched variants.
- Fix: Check alternate names. If the article gives no supporting statement, retain the false negative and document the source coverage gap.

## False negative at position 10
- Triple: (Erwin Schrödinger, receivedAward, Foreign Member of the Royal Society)
- Sentence or source evidence: No matching wording located in the saved article using the award name and likely variants.
- Error code: E7 (reference value missed)
- Why: The award appears in the Wikidata reference. A search of the saved article did not locate a passage naming it under the searched variants.
- Fix: Check alternate names. If the article gives no supporting statement, retain the false negative and document the source coverage gap.

## False negative at position 16
- Triple: (Erwin Schrödinger, receivedAward, Prix Paul Doistau-Émile Blutet de l’Information Scientifique)
- Sentence or source evidence: No matching wording located in the saved article using the award name and likely variants.
- Error code: E7 (reference value missed)
- Why: The award appears in the Wikidata reference. A search of the saved article did not locate a passage naming it under the searched variants.
- Fix: Check alternate names. If the article gives no supporting statement, retain the false negative and document the source coverage gap.

## False negative at position 17
- Triple: (Erwin Schrödinger, receivedAward, Prize of the City of Vienna for Natural Sciences)
- Sentence or source evidence: No matching wording located in the saved article using the award name and likely variants.
- Error code: E7 (reference value missed)
- Why: The award appears in the Wikidata reference. A search of the saved article did not locate a passage naming it under the searched variants.
- Fix: Check alternate names. If the article gives no supporting statement, retain the false negative and document the source coverage gap.

## Measured changes

Education TP rose from 5 to 6. Award FP fell from 7 to 6. Overall TP/FP/FN changed from 23/25/88 to 24/23/87. Precision changed from 0.479 to 0.511 and recall from 0.207 to 0.216.
