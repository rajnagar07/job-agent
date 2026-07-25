def get_badge(score):
    if score >= 90:
        return "🟢 Excellent"
    elif score >= 75:
        return "🔵 Strong"
    elif score >= 60:
        return "🟡 Good"
    else:
        return "🔴 Weak"