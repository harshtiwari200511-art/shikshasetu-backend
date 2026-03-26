def create_student_profile():
    return {
        "cognitive_score": 50,
        "difficulty_level": "medium",
        "average_accuracy": 0.0,
        "total_attempts": 0,
        "weak_topics": {},
        "strong_topics": {},
    }


def _clamp(n, lo, hi):
    try:
        n = float(n)
    except Exception:
        return lo
    return max(lo, min(hi, n))


def update_profile(profile, performance):
    """
    Update a student's cognitive profile based on a test/performance payload.

    Expected (best-effort) fields in performance:
    - score: int
    - total: int
    - subject: str
    - topic: str
    """
    if not isinstance(profile, dict):
        profile = create_student_profile()

    if not isinstance(performance, dict):
        performance = {}

    score = performance.get("score")
    total = performance.get("total") or performance.get("total_questions")
    topic = performance.get("topic") or "General"

    try:
        score_i = int(score) if score is not None else None
        total_i = int(total) if total is not None else None
    except Exception:
        score_i, total_i = None, None

    accuracy = None
    if score_i is not None and total_i and total_i > 0:
        accuracy = (score_i / total_i) * 100.0

    total_attempts = int(profile.get("total_attempts", 0) or 0) + 1
    profile["total_attempts"] = total_attempts

    if accuracy is not None:
        prev_avg = float(profile.get("average_accuracy", 0.0) or 0.0)
        # running average
        profile["average_accuracy"] = round(((prev_avg * (total_attempts - 1)) + accuracy) / total_attempts, 2)

        cog = float(profile.get("cognitive_score", 50) or 50)
        # Nudge cognitive score by performance
        if accuracy >= 80:
            cog += 3
        elif accuracy >= 60:
            cog += 1
        elif accuracy >= 40:
            cog -= 1
        else:
            cog -= 3
        profile["cognitive_score"] = int(_clamp(cog, 0, 100))

        # Difficulty level heuristic
        avg = float(profile.get("average_accuracy", 0.0) or 0.0)
        if avg >= 80 and profile["cognitive_score"] >= 70:
            profile["difficulty_level"] = "hard"
        elif avg >= 55 and profile["cognitive_score"] >= 45:
            profile["difficulty_level"] = "medium"
        else:
            profile["difficulty_level"] = "easy"

        weak_topics = profile.get("weak_topics") if isinstance(profile.get("weak_topics"), dict) else {}
        strong_topics = profile.get("strong_topics") if isinstance(profile.get("strong_topics"), dict) else {}

        if accuracy < 60:
            weak_topics[topic] = int(weak_topics.get(topic, 0) or 0) + 1
        else:
            strong_topics[topic] = int(strong_topics.get(topic, 0) or 0) + 1

        profile["weak_topics"] = weak_topics
        profile["strong_topics"] = strong_topics

    return profile

