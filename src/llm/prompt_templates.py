"""
Prompt Templates module.
Provides pre-defined templates for gathering, deep diving and final summarization.
"""

PROMPT_GATHER = (
    "You are tasked with gathering as much information as possible about the following subject:\n\n"
    "{subject}\n\n"
    "Return all relevant details including any background, context, and associated topics."
)

PROMPT_DEEP_DIVE = (
    "Based on the following aggregated knowledge:\n\n"
    "{knowledge}\n\n"
    "List the top areas where further deep dive investigation should be performed. "
    "Return a comma-separated list of topics."
)

PROMPT_SUMMARY = (
    "Using the aggregated knowledge below:\n\n"
    "{knowledge}\n\n"
    "Answer the following question comprehensively:\n\n"
    "{question}\n\n"
    "Provide a well-organized summary in markdown format."
)