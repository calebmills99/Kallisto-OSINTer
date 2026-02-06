"""
Google Filter module.
Enhances search queries by appending filtering features such as country, language, and date-range.
"""

def apply_google_filters(query, country=None, language=None, date_range=None):
    """
    Modifies the query to include Google filter parameters.
    """
    filters = []
    if country:
        filters.append(f"site:{country}")
    if language:
        filters.append(f"lang:{language}")
    if date_range:
        filters.append(f"daterange:{date_range}")
    if filters:
        filtered_query = f"{query} {' '.join(filters)}"
        return filtered_query
    return query