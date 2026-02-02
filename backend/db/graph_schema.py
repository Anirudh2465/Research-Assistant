# Node Labels
class Label:
    Concept = "Concept"
    Method = "Method"
    Assumption = "Assumption"
    Limitation = "Limitation"
    Paper = "Paper"
    Idea = "Idea"
    Project = "Project"

# Relationship Types
class Relation:
    # Core Concept Relations
    EXTENDS = "EXTENDS"             # Concept -> Concept
    INSPIRED_BY = "INSPIRED_BY"     # Concept -> Concept
    CONFLICTS_WITH = "CONFLICTS_WITH" # Concept -> Concept
    ADDRESSES = "ADDRESSES"         # Method -> Limitation

    # Structural Relations
    ASSUMES = "ASSUMES"             # Concept -> Assumption
    FAILS_WHEN = "FAILS_WHEN"       # Concept -> Limitation
    USED_IN = "USED_IN"             # Method -> Concept

    # Lineage Relations
    DERIVED_FROM = "DERIVED_FROM"   # Idea -> Concept
    GENERATED_FROM = "GENERATED_FROM" # Idea -> Idea
    BELONGS_TO_PROJECT = "BELONGS_TO_PROJECT" # Any -> Project
