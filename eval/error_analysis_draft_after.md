# Error analysis (run: after)

False-positive list length: 23.  False-negative list length: 87.
Lists are sorted alphabetically (case-insensitive) by (subject, predicate, object);
positions are 1-based, with wrap-around (position mod length) for short lists.

Error codes: E1 wrong span | E2 pronoun | E3 alias split | E4 direction/role | E5 negation/time | E6 source gap (my triple is right, Wikidata lacks it) | E7 other

## False positive at position 8
- Triple: (James Chadwick, receivedAward, Heginbottom Scholarship)
- Sentence: At the end of his first year, he was awarded a Heginbottom Scholarship to study physics.
- Error code: 
- Why it happened: 
- What would fix it: 

## False positive at position 17
- Triple: (Richard Feynman, worksAt, Thinking Machines Corporation)
- Sentence: In the 1980s he began to spend his summers working at Thinking Machines Corporation, helping to build some of the first parallel supercomputers and considering the construction of quantum computers.
- Error code: 
- Why it happened: 
- What would fix it: 

## False positive at position 18
- Triple: (Werner Heisenberg, educatedAt, University of Göttingen)
- Sentence: From 1920 to 1923, he studied physics and mathematics at the Ludwig-Maximilians-Universität München under Arnold Sommerfeld and Wilhelm Wien and at the University of Göttingen with Max Born and James Franck and mathematics with David Hilbert.
- Error code: 
- Why it happened: 
- What would fix it: 

## False positive at position 20
- Triple: (Werner Heisenberg, worksAt, Chair for Theoretical Physics)
- Sentence: In February 1943, Heisenberg was appointed to the Chair for Theoretical Physics at the Friedrich-Wilhelms-Universität.
- Error code: 
- Why it happened: 
- What would fix it: 

## False negative at position 9
- Triple: (Erwin Schrödinger, receivedAward, Fellow of the American Physical Society)
- Sentence: (find the sentence in data/raw that mentions this, or write 'not in the text')
- Error code: 
- Why it happened: 
- What would fix it: 

## False negative at position 10
- Triple: (Erwin Schrödinger, receivedAward, Foreign Member of the Royal Society)
- Sentence: (find the sentence in data/raw that mentions this, or write 'not in the text')
- Error code: 
- Why it happened: 
- What would fix it: 

## False negative at position 16
- Triple: (Erwin Schrödinger, receivedAward, Prix Paul Doistau-Émile Blutet de l’Information Scientifique)
- Sentence: (find the sentence in data/raw that mentions this, or write 'not in the text')
- Error code: 
- Why it happened: 
- What would fix it: 

## False negative at position 17
- Triple: (Erwin Schrödinger, receivedAward, Prize of the City of Vienna for Natural Sciences)
- Sentence: (find the sentence in data/raw that mentions this, or write 'not in the text')
- Error code: 
- Why it happened: 
- What would fix it: 
