def count_types(categories):
    counts = {}
    for category,list_items in categories.items():
        counts[category] = len(list_items)
    return counts
