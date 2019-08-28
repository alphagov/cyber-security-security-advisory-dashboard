def count_types(categories):
    counts = {}
    for category, list in categories.items():
        counts[category] = len(list)
    return counts
