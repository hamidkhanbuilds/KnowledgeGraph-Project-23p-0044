# Reflection

I predicted 6 birthplace, 10 education, 15 award, 18 employer, and 4 doctoral-advisor rows. My final extractor produced 6, 13, 18, 24, and 3 respectively. The birthplace count matched my estimate, although only two of the five scored birthplace claims matched Wikidata. Getting the count right did not guarantee that I found the right places.

I expected worksAt to have the lowest precision. It did, at 0.353. One clear mistake was assigning Mensa International as Feynman’s employer when the sentence said he declined to join. I expected the private biography’s pronoun to cause trouble, but the extractor correctly assigned the move to Thornfield College of Science to Waleed Gilani.

Preserving hyphens in names recovered an education match. Skipping an unnamed “Prize” removed a false award. Overall precision rose from 0.479 to 0.511 and recall from 0.207 to 0.216.

Q5 returned eight graph nodes typed as people with no recorded education. The open-world assumption changed my interpretation of Waleed Gilani’s result. His biography passage identifies him as an advisor and mentions his move, but it gives no education history. His missing educatedAt triple tells me only what this graph records.
