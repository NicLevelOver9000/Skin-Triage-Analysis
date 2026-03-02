import json
from typing import Dict, Any
from azure_client import get_client, get_deployment
from tools.location_tools import get_geoip_location, get_nearby_hospitals

client = get_client()
deployment = get_deployment()


def hospital_node(state: Dict[str, Any]) -> Dict[str, Any]:
    print("STATE ENTERING Hospital NODE:")
    print(state)

    vision = state["vision_json"]
    severity = vision["clinical_indicators"]["severity_score"]
    infection = vision["clinical_indicators"]["infection_risk"]
    bleeding = vision["observations"]["bleeding_level"]

    # ==========================================================
    # 🔴 HARD SAFETY OVERRIDE (Deterministic)
    # ==========================================================
    if severity >= 9 or infection >= 0.9 or bleeding == "heavy":
        print("⚠️ SAFETY OVERRIDE TRIGGERED")

        location = get_geoip_location()
        hospitals = get_nearby_hospitals(
            location["lat"], location["lon"], radius_km=20)

        return {
            "final_output": {
                "action": "SEEK_MEDICAL_CARE",
                "urgency": "EMERGENCY",
                "advice": "This appears to be a severe or high-risk condition. Seek immediate emergency medical care.",
                "user_location": location,
                "nearby_hospitals": hospitals,
                "override": True
            }
        }

    # ==========================================================
    # 🟡 AI TOOL-DRIVEN TRIAGE (For non-extreme cases)
    # ==========================================================

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_geoip_location",
                "description": "Get user's approximate location based on IP address.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_nearby_hospitals",
                "description": "Find nearby hospitals around given latitude and longitude.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "number"},
                        "lon": {"type": "number"},
                        "radius_km": {"type": "number"},
                    },
                    "required": ["lat", "lon"],
                },
            },
        },
    ]

    messages = [
        {
            "role": "system",
            "content": (
                "You are a medical triage assistant. "
                "Determine urgency level based on structured clinical indicators. "
                "Use available tools to obtain location and hospitals if appropriate. "
                "Return ONLY valid JSON in this format:\n"
                "{\n"
                '  "urgency": "EMERGENCY|URGENT|MEDICAL_REVIEW",\n'
                '  "advice": "string",\n'
                '  "user_location": { ... },\n'
                '  "nearby_hospitals": [ ... ]\n'
                "}"
            ),
        },
        {
            "role": "user",
            "content": f"""
Structured injury analysis:

{json.dumps(vision, indent=2)}

Risk level: {state.get("risk_level")}

Determine urgency and fetch hospitals if needed.
""",
        },
    ]

    response = client.chat.completions.create(
        model=deployment,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_completion_tokens=1500,
    )

    message = response.choices[0].message

    # ---------------- TOOL LOOP ----------------
    while message.tool_calls:
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments or "{}")

            if function_name == "get_geoip_location":
                result = get_geoip_location()

            elif function_name == "get_nearby_hospitals":
                result = get_nearby_hospitals(
                    lat=arguments["lat"],
                    lon=arguments["lon"],
                    radius_km=arguments.get("radius_km", 10),
                )
            else:
                result = {"error": "Unknown tool"}

            messages.append(message)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                }
            )

        response = client.chat.completions.create(
            model=deployment,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_completion_tokens=1500,
        )

        message = response.choices[0].message

    # ---------------- FINAL RESPONSE ----------------

    final_data = json.loads(message.content)

    return {
        "final_output": {
            "action": "SEEK_MEDICAL_CARE",
            **final_data,
            "override": False
        }
    }
