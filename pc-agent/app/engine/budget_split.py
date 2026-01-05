def split_budget(budget, usage):
    if usage == "ai":
        return budget * 0.6
    if usage == "gaming":
        return budget * 0.5
    return budget * 0.4
