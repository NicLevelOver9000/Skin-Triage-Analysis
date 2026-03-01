import json
from azure_client import get_client, get_deployment

client = get_client()
deployment = get_deployment()


def vision_node(state):
    print("STATE ENTERING Vision NODE:")
    print(state)

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": "You are a clinical wound triage assistant. Return only valid JSON."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Analyze this medical image and return ONLY valid JSON:

{
  "condition_summary": "string",
  "confidence_score": 0-1,
  "observations": {
    "wound_type": "string",
    "bleeding_level": "low|moderate|heavy|none",
    "redness": true/false,
    "swelling": true/false
  },
  "clinical_indicators": {
    "infection_risk": 0-1,
    "severity_score": 1-10
  }
}
"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": state["image_url"]
                        }
                    }
                ]
            }
        ],
        response_format={"type": "json_object"},
        max_completion_tokens=800,
    )

    vision_json = json.loads(response.choices[0].message.content)

    return {
        "vision_json": vision_json
    }
