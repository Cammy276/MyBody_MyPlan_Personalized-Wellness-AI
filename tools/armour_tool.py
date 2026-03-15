from dotenv import load_dotenv
import os

from google.cloud import modelarmor_v1
from google.api_core.client_options import ClientOptions

load_dotenv()

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
TEMPLATE_ID = os.environ.get("MODEL_ARMOR_TEMPLATE_ID")

template_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/templates/{TEMPLATE_ID}"

client = modelarmor_v1.ModelArmorClient(
    client_options=ClientOptions(
        api_endpoint=f"modelarmor.{LOCATION}.rep.googleapis.com"
    )
)


def check_safe_prompt(prompt: str) -> bool:
    """Check prompt safety using Google Model Armor"""

    try:
        request = modelarmor_v1.SanitizeUserPromptRequest(
            name=template_name,
            user_prompt_data=modelarmor_v1.DataItem(text=prompt)
        )

        response = client.sanitize_user_prompt(request=request)

        result = response.sanitization_result

        if not result:
            return True

        if result.filter_match_state == modelarmor_v1.FilterMatchState.NO_MATCH_FOUND:
            return True

        return False

    except Exception as e:
        print("Armour safeguard failed:", e)
        return False