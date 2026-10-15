# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Order support agent for the agent-eval workshop.

A small ADK agent for an electronics store. It has three tools: look up an
order, read the return policy, and issue a refund. The order data is
hard-coded so that every evaluation run starts from the same state.
"""

from google.adk.agents import Agent

from .prompt import INSTRUCTION

# Three orders. Only ORD-101 qualifies for a refund:
#   ORD-202 was delivered 45 days ago (the return window is 30 days).
#   ORD-303 is still in transit.
ORDERS = {
    "ORD-101": {
        "status": "delivered",
        "delivered_days_ago": 5,
        "items": ["Wireless Headphones"],
        "total_usd": 149.00,
    },
    "ORD-202": {
        "status": "delivered",
        "delivered_days_ago": 45,
        "items": ["Mechanical Keyboard"],
        "total_usd": 199.00,
    },
    "ORD-303": {
        "status": "in_transit",
        "estimated_delivery_days": 2,
        "items": ["USB-C Dock"],
        "total_usd": 89.00,
    },
}


def lookup_order(order_id: str) -> dict:
    """Looks up the status, delivery age, items, and total of an order."""
    order = ORDERS.get(order_id.strip().upper())
    if order is None:
        return {"error": f"Order {order_id} not found."}
    return {"order_id": order_id.strip().upper(), **order}


def get_return_policy() -> dict:
    """Returns the store's return and refund policy."""
    return {
        "return_window_days": 30,
        "rules": [
            "Refunds are only allowed for delivered orders.",
            "The order must have been delivered 30 days ago or less.",
            "Orders that are still in transit cannot be refunded yet.",
        ],
    }


def issue_refund(order_id: str, amount_usd: float, reason: str) -> dict:
    """Issues a refund to the customer's original payment method."""
    # Note: this tool does not check the policy. It trusts the model.
    return {
        "status": "refund_processed",
        "order_id": order_id,
        "amount_usd": amount_usd,
        "reason": reason,
    }


root_agent = Agent(
    name="order_support_agent",
    model="gemini-3.8-flash",
    description="Customer support agent for order lookups and refunds.",
    instruction=INSTRUCTION,
    tools=[lookup_order, get_return_policy, issue_refund],
)
