def score_gpu(gpu, usage):
    score = 0
    name = gpu["name"].lower()

    if "rtx" in name:
        score += 5
    if "rx" in name:
        score += 4
    if "12gb" in name or "16gb" in name:
        score += 3
    if "used" in gpu["condition"].lower():
        score += 1

    if usage == "ai" and "rtx" in name:
        score += 2

    return score
