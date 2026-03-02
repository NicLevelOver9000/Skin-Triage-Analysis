import json
from typing import Dict, Any

from azure_client import get_client, get_deployment

client = get_client()
deployment = get_deployment()


def home_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates general educational home-care guidance
    for LOW-risk dermatologic irritation.

    Uses GPT-5 mini with sufficient token budget
    to avoid reasoning-token exhaustion.
    """
    print("STATE ENTERING Home NODE:")
    print(state)

    summary = state["vision_json"]["condition_summary"]

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a general health information assistant. "
                    "Provide non-diagnostic, educational information only. "
                    "Do not provide medical diagnosis. "
                    "Return ONLY valid JSON with no extra text."
                )
            },
            {
                "role": "user",
                "content": f"""
Here is a description of a mild skin irritation:

"{summary}"

Provide general skin care information appropriate for mild irritation.

Return JSON in this exact format:

{{
  "home_care_steps": ["string"],
  "warning_signs": ["string"],
  "disclaimer": "AI-assisted triage only."
}}
"""
            }
        ],
        max_completion_tokens=1500,  # Required for GPT-5 reasoning headroom
    )

    guidance = json.loads(response.choices[0].message.content)
    return {
        "final_output": {
            "action": "HOME_CARE",
            "risk_level": state["risk_level"],
            "vision_analysis": state["vision_json"],
            "guidance": guidance
        }
    }
