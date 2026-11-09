# SHACL validation note

The graph contains 59 distinct extracted facts. Validation returned seven warnings. All seven came from the same shape, which asks every person in the graph to have at least one recorded birthplace.

| Focus node | Assessment | Why the warning appeared |
|---|---|---|
| Arnold Sommerfeld | Shape too strict | He appears as Heisenberg’s doctoral advisor. Recording that relationship does not require his birthplace. |
| Ernest Rutherford | Shape too strict | The graph records his work at Cambridge. That sentence gives no birthplace. |
| John Archibald Wheeler | Shape too strict | Feynman’s biography identifies Wheeler as his thesis advisor and gives no birthplace in that sentence. |
| Mary Louise Bell | Shape too strict | The extracted fact concerns where she taught. Her birthplace is outside the scope of that fact. |
| Shin’ichirō Tomonaga | Shape too strict | He appears in a sentence about sharing the Nobel Prize. The sentence gives no birthplace. |
| United States | Real extraction error | The extractor made United States the subject of a worksAt fact about Frankford Arsenal. Feynman is the person who worked there. The graph builder then typed the incorrect subject as a Person, triggering the birthplace check. |
| Waleed Gilani | Shape too strict | The private biography identifies him as Faryal Awan’s advisor and mentions his move to Thornfield College of Science. It gives no birthplace for him. |

The birthplace warning makes sense as a completeness check for the main biographies. Applying it to every person also flags people introduced only as advisors, colleagues, or relatives. For United States, the correction belongs in subject extraction.

**OWL reasoning.** If one person has two birthplace identifiers and bornIn is functional, an OWL reasoner can infer that the identifiers refer to the same place. Ordinary SHACL validation alone does not derive that identity.

**SHACL validation.** The minimum-count shape can flag a person with zero recorded bornIn values in this graph. Under OWL’s open-world semantics, the birthplace can be unknown, so the missing triple alone does not establish an inconsistency.
