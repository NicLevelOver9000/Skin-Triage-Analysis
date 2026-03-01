def risk_node(state):
    print("STATE ENTERING Risk NODE:")
    print(state)

    v = state["vision_json"]

    severity = v["clinical_indicators"]["severity_score"]
    infection = v["clinical_indicators"]["infection_risk"]
    bleeding = v["observations"]["bleeding_level"]

    if severity >= 8 or infection >= 0.7 or bleeding == "heavy":
        risk = "HIGH"
    elif severity >= 4:
        risk = "MODERATE"
    else:
        risk = "LOW"

    return {"risk_level": risk}
