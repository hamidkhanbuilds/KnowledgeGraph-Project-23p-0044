# KRR Assignment 1 -- Knowledge graph from text (23P-0044)

Pipeline: **text -> triples (spaCy rules) -> RDF (rdflib) -> ontology + SHACL -> Fuseki + SPARQL -> score against Wikidata**.

## Windows Command Prompt

Use the folder containing this README. Keep your existing Git repository and active virtual environment. Save your own predictions.md and commit it before the first full extraction. Set contact in both download scripts to your university email.

```bat
python -m pip install -r requirements.txt
python -m spacy download en_core_web_sm
python src/fetch_articles.py
python src/keyword_counts.py
```

Fill in predictions.md from the template, then commit it. Run the baseline below and commit its results before editing extraction rules.

```bat
python src/extract.py
python eval/fetch_wikidata.py
python eval/evaluate.py --run before
```

Use the selected examples in eval/error_analysis_draft_before.md to write eval/error_analysis.md. Fix two observed extraction problems. Rerun the extractor, then generate the final outputs.

```bat
python src/extract.py
python eval/evaluate.py --run after
python src/build_kg.py
python src/validate_shacl.py
python src/load_fuseki.py
python src/run_queries.py
```

The upload replaces the default graph of kg-23p-0044. Save a screenshot of a query and its results from Fuseki. Q5 shows people with no recorded education triple. Their actual education may be missing from the source or the extractor output. Q6 follows one or more advisor links and returns all matching person–ancestor pairs. Explain an empty result using your graph. Fill in shacl_note.md and reflection.md from the templates using your results.

Namespace: `http://example.org/kg/23p-0044/`   Fuseki dataset: `kg-23p-0044`

## How the extractor works (src/extract.py)
**Cleaning.** I delete `== headings ==`, everything after "References"-type headings, and `( ... )` asides (dates, pronunciations) because they confuse the parser. I also write `Dr.` as `Dr` so the abbreviation does not end a sentence. The `sentence` column in triples.csv is this cleaned sentence.

**Common machinery.** spaCy splits sentences and gives a dependency tree. `owntokens(verb)` collects only the words that belong to one verb's clause, so "studied at A and later worked at B" gives A to *study* and B to *work*. `subjecttoken(verb)` finds the nsubj/nsubjpass and borrows the subject from the head verb for joined verbs. `namespan()` builds a name from a short whitelist of dependency labels (compound/amod/"of X"), so dates and clauses never enter a name. I do not trust spaCy's entity labels (it tags "Feynman" as ORG), so subjects are accepted by word lists and grammar instead.

**Five predicates, each with dependency-parse rules**
- *bornIn* (`born-in/dep`): verb lemma "bear" -> preposition in/at -> proper-noun object that is not a date/person. Only the first hit is kept because a person has one birthplace.
- *educatedAt* (`studied-at`, `attended`, `degree-from`): verbs study/graduate/enrol/train + preposition at/from; verb attend + direct object; and "received/earned a PhD/degree from X" where the object noun is a degree word and the target must look like an organisation.
- *receivedAward* (`award/dep`): verbs receive/win/award/share/earn/accept whose object noun is prize/medal/award/... ("a share of the X Prize" is followed through "of"). With "awarded HIM the medal" the recipient is the dative, not the subject. Names may contain "in/of/for" parts ("Nobel Prize in Physics") but never dates.
- *worksAt* (`joined`, `worked-at`, `moved-to`, `role-at`): join + object; work/teach/lecture + at/for; move/return/appoint/hire + to/at/by (here the target MUST look like an organisation, so "moved to Zurich" is rejected); and "was a professor/director ... at X".
- *doctoralAdvisor* (`advisor-noun`, `under`, `supervise`): "X's doctoral advisor was Y" (either direction, via the possessive and the copula); a verb whose clause mentions PhD/doctorate/thesis plus "under (the supervision of) Y"; and supervise/advise/mentor in active or passive ("X's thesis was supervised by Y").

**Pronouns.** On each document I learn the gender of the main subject from the first he/she/his/her in the text. A pronoun with the *same* gender is the main subject. A pronoun of the *other* gender cannot be the main subject, so it is the most recently mentioned other person. (In the private document "He later moved ..." therefore becomes Waleed Gilani, not Faryal Awan.) Known weakness: if another person of the same gender was just discussed, I still choose the main subject.

**Negation / hedging.** If any word in the verb's own clause is `neg` or one of not/never/no/n't/nor..., or the verb is the complement of a negated verb, the triple is NOT written; it is logged in `out/skipped_negated_or_hedged.csv`. Sentences with words such as rumour/allegedly/falsely are also skipped (reason "hedged").

**One entity, one name.** A name is stripped of titles (Dr, Prof ...) and compared with the full names seen so far: same surname AND (one side is surname-only, or the first names/initials agree) means the same person. Accents are ignored. "Dr Awan" -> "Faryal Awan". Each replacement is counted; see `out/merge_report.txt` for the total and the list.

**Provenance.** Every row of triples.csv carries `source_doc` and `sentence`. `triples_debug.csv` also has the rule name and sentence number.

## Known limitations (see eval/error_analysis.md)
Organisation aliases are not merged (MIT vs Massachusetts Institute of Technology), pronouns can attach to the main subject when another same-gender person was just mentioned, and objects joined in odd parse shapes can be missed.

## Sources / honesty note
Allowed material used: course slides, spaCy / rdflib / pySHACL / Jena / Wikidata / SPARQL / SHACL documentation. The Wikipedia fetch uses the MediaWiki `extracts` API described in the handout (Appendix B), written as my own script.
**AI assistance:** (edit this line so it is true and matches what your instructor allows) "The first version of the code was drafted with Claude (Anthropic); I read, tested and changed it and can explain every part."
