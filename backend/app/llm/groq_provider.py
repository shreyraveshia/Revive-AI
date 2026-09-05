from __future__ import annotations

import json

from groq import Groq

from app.core.config import get_settings
from app.llm.provider import LLMProvider
from app.llm.schemas import FailureDiagnosis


class GroqProvider(LLMProvider):
    """Groq-backed implementation of the LLM provider."""

    def __init__(self) -> None:
        settings = get_settings()

        if not settings.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=settings.groq_api_key,
        )

        self.model = "openai/gpt-oss-20b"

    def diagnose_failure(
        self,
        *,
        transaction_amount_paise: int,
        payment_method: str,
        failure_code: str,
        attempt_number: int,
        customer_previous_transactions: int,
        customer_previous_success_rate: float,
        merchant_previous_success_rate: float,
    ) -> FailureDiagnosis:
        amount_rupees = transaction_amount_paise / 100

        system_prompt = """
You are the diagnosis component of Revive AI, a revenue recovery system.

Your job is to diagnose payment failures using ONLY the supplied transaction
context.

You may:
- identify the likely failure cause
- explain the reasoning
- suggest a recovery direction
- draft a customer-facing message

You MUST NOT:
- execute payments
- authorize money movement
- claim that an action was executed
- invent facts not present in the supplied context

Your output must follow the requested JSON schema.
""".strip()

        user_prompt = f"""
Payment context:

Amount: ₹{amount_rupees:,.2f}
Payment method: {payment_method}
Failure code: {failure_code}
Attempt number: {attempt_number}

Customer previous transactions: {customer_previous_transactions}
Customer historical success rate: {customer_previous_success_rate:.3f}

Merchant historical success rate: {merchant_previous_success_rate:.3f}

Diagnose this failure and suggest the safest recovery direction.
""".strip()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "failure_diagnosis",
                    "strict": True,
                    "schema": FailureDiagnosis.model_json_schema(),
                },
            },
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError(
                "Groq returned an empty response."
            )

        data = json.loads(content)

        return FailureDiagnosis.model_validate(data)