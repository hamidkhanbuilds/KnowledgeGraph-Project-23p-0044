# \# Predictions

# 

# These are my estimates for the five Wikipedia articles and the private biography.

# 

# | Predicate | Expected count | Reason |

# |---|---:|---|

# | bornIn | 6 | I expect one birthplace for each main person. |

# | educatedAt | 10 | Some people may have attended two or more universities. |

# | receivedAward | 15 | I expect several prizes and medals to appear in the scientists’ biographies. |

# | worksAt | 18 | Each scientist may have worked at several institutions. |

# | doctoralAdvisor | 4 | A biography may mention a PhD without naming the supervisor. |

# 

# \## Lowest precision

# 

# I expect worksAt to have the lowest precision. For example, “joined a society” could mean the person became a member, but the extractor might record the society as an employer.

# 

# \## Expected difficulty in the private biography

# 

# I think the extractor might struggle with “He later moved.” The biography is mainly about Faryal Awan, so the extractor might give her credit for the move even though “He” refers to Waleed Gilani.

