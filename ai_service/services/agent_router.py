import json
from google import genai
from pydantic import BaseModel, Field
from typing import Literal
from services.retry_utils import call_with_retry

class RouteDecision(BaseModel):
    agent_type: Literal["expense", "sales", "follow_up", "reporting", "advisory", "compound", "unknown"] = Field(
        description="Which agent should handle this request?"
    )
    reasoning: str = Field(description="Why this agent was chosen.")

class AgentRouter:
    def __init__(self, client: genai.Client):
        self.client = client

    def route(self, transcript: str, user_context: dict) -> RouteDecision:
        # Check if we are in a clarification follow-up state
        if user_context and user_context.get("previous_extraction"):
            prev = user_context["previous_extraction"]
            if prev.get("clarification_needed") == True:
                return RouteDecision(agent_type="follow_up", reasoning="User is answering a previous clarification question.")

        # Otherwise, ask the LLM to route it with very explicit rules
        prompt = f"""
        You are a router that classifies user input into exactly one agent type.

        CLASSIFICATION RULES (follow strictly):

        "compound" — Use when the user's prompt contains MULTIPLE DISTINCT business actions that need sequential execution:
          - Creating multiple entities (products, suppliers, customers) AND recording transactions
          - Combining master data setup with purchases AND/OR sales
          - Any prompt with 3+ distinct business actions (e.g., "Create X, then buy Y, then sell Z")
          - Prompts that mention both buying FROM a vendor AND selling TO a customer
          - Company onboarding with multiple setup steps
          Examples: "Create products Dell Laptop and HP Laptop. Purchase 50 Dell from vendor. Sell 10 to customer.", "Setup company, create bank account, invest capital, generate balance sheet."
          CRITICAL: If the prompt has BOTH a purchase action AND a sales action, it is ALWAYS "compound".
          CRITICAL: If the prompt mentions creating 2+ different types of master data AND recording transactions, it is ALWAYS "compound".

        "expense" — Use when the user is RECORDING a SINGLE financial transaction:
          - Investing money, capital injection ("I invested", "put money into business")
          - Buying/purchasing anything (laptops, furniture, car, equipment)
          - Paying a vendor, supplier, employee, or contractor
          - Recording a bill or expense (rent, salary, electricity)
          - Receiving a bill from a vendor
          - Any prompt that involves SPENDING or RECEIVING money
          - Mixed payments or split payments
          - Loan-financed purchases
          Examples: "I invested 20 lakh", "Purchased 50 Dell laptops", "Paid Rajesh 25000", "Bought office furniture", "We purchased a company car"

        "sales" — Use when the user is SELLING products/services or receiving customer payments (single action):
          - Creating a sales invoice
          - Selling products to a customer
          - Receiving payment from a customer against an invoice
          Examples: "Sell 10 laptops to Rahul Technologies", "Rahul Technologies transferred 2.5 lakh against their invoice", "Create invoice for customer"

        "reporting" — Use when the user is ASKING for information, reports, or statements (NOT recording anything):
          - Requesting financial statements (P&L, Balance Sheet, Cash Flow)
          - Asking about balances, outstanding amounts
          - Requesting GST reports or tax summaries
          - Month-end closing and statement generation
          - Asking "how much" or "show me" or "generate report"
          - Asking about historical transactions ("how much have I paid X")
          - Requesting a business overview or executive summary
          Examples: "Give me a complete overview", "Generate GST report", "How much have I paid Tech Distributors", "Generate financial statements", "Complete month-end activities"

        "advisory" — Use when the user is asking for ADVICE or OPINIONS (NOT recording anything):
          - "Can I afford...", "Should I...", "Is it wise to..."
          - Asking for business recommendations
          Examples: "Can I afford to purchase a delivery vehicle worth 12 lakh?", "Should I hire more staff?"

        "unknown" — Use ONLY if the input is completely unrelated to business/accounting.

        CRITICAL: If the user mentions a specific amount AND an action (bought, paid, invested, purchased, sold), it is ALWAYS "expense" or "sales" or "compound", NEVER "reporting".

        User input: "{transcript}"
        """
        def _call():
            response = self.client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': RouteDecision,
                },
            )
            return RouteDecision(**json.loads(response.text))

        return call_with_retry(_call)


