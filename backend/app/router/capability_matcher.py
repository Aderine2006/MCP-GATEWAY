from typing import List, Dict, Any, Optional
import re

from ..registry.models import RegisteredTool


class CapabilityMatcher:
    """Matches user requests to tools based on capabilities and keywords."""

    def __init__(self):
        self.intent_keywords = {
            "customer": ["customer", "client", "account", "user"],
            "support": ["support", "ticket", "help", "issue", "problem"],
            "incident": ["incident", "outage", "downtime", "emergency", "critical"],
            "read": ["get", "find", "search", "list", "show", "retrieve", "fetch", "details"],
            "write": ["create", "add", "new", "insert", "set", "make"],
            "update": ["update", "modify", "change", "edit", "alter"],
            "delete": ["delete", "remove", "cancel", "terminate"],
        }

    def extract_intent(self, request: str) -> Dict[str, Any]:
        """Extract intent and parameters from natural language request."""
        request_lower = request.lower()
        
        intent = {
            "operation": "unknown",
            "domain": "unknown",
            "parameters": {},
            "raw_request": request
        }
        
        # Extract operation type
        for op, keywords in self.intent_keywords.items():
            if op in ["read", "write", "update", "delete"]:
                if any(kw in request_lower for kw in keywords):
                    intent["operation"] = op
                    break
        
        # Extract domain (prioritize incident if present)
        if "incident" in request_lower:
            intent["domain"] = "incident"
        elif "ticket" in request_lower or "support" in request_lower:
            intent["domain"] = "support"
        elif "customer" in request_lower or "client" in request_lower or "account" in request_lower:
            intent["domain"] = "customer"
        
        # Extract customer_id if present
        customer_id_match = re.search(r'(?:customer|client|account)[\s]*(?:id)?[\s]*[:#]?[\s]*(\d+)', request_lower)
        if customer_id_match:
            intent["parameters"]["customer_id"] = customer_id_match.group(1)
        
        # Extract general ID patterns
        id_match = re.search(r'\b(\d{3,})\b', request)
        if id_match and "customer_id" not in intent["parameters"]:
            intent["parameters"]["id"] = id_match.group(1)
        
        # Extract ticket/incident keywords
        if "ticket" in request_lower:
            intent["parameters"]["ticket_type"] = "support"
        if "incident" in request_lower:
            intent["parameters"]["incident_type"] = "incident"
        
        # Extract severity for incidents
        severity_match = re.search(r'(critical|high|medium|low|emergency)', request_lower)
        if severity_match:
            intent["parameters"]["severity"] = severity_match.group(1)
        
        # Extract title/description
        words = request.split()
        if len(words) > 5:
            # Try to extract what might be a title (after "create" or "new")
            for i, word in enumerate(words):
                if word.lower() in ["create", "new", "add"]:
                    if i + 1 < len(words):
                        intent["parameters"]["title"] = " ".join(words[i+1:])
                        break
        
        # For generic requests without specific IDs, add a placeholder
        if intent["domain"] == "support" and "customer_id" not in intent["parameters"]:
            intent["parameters"]["customer_id"] = "default"
        
        if intent["domain"] == "incident" and "customer_id" not in intent["parameters"]:
            intent["parameters"]["customer_id"] = "default"
            if "severity" not in intent["parameters"]:
                intent["parameters"]["severity"] = "medium"
        
        return intent

    def match_tools(self, intent: Dict[str, Any], tools: List[RegisteredTool]) -> List[tuple[RegisteredTool, float]]:
        """Match intent to available tools and return ranked candidates."""
        candidates = []
        
        for tool in tools:
            if tool.status.value != "active":
                continue
            
            score = 0.0
            
            # Domain matching (higher weight)
            if intent["domain"] != "unknown":
                if intent["domain"] in tool.name.lower() or intent["domain"] in tool.description.lower():
                    score += 0.5
                if intent["domain"] in tool.capabilities:
                    score += 0.4
            
            # Operation matching (higher weight for write operations)
            if intent["operation"] != "unknown":
                if intent["operation"] in tool.capabilities:
                    score += 0.4
                # Check tool name for operation hints
                if intent["operation"] == "read" and any(kw in tool.name.lower() for kw in ["get", "find", "list", "search"]):
                    score += 0.3
                if intent["operation"] == "write" and any(kw in tool.name.lower() for kw in ["create", "add", "new"]):
                    score += 0.3
            
            # Keyword matching in tool name/description
            request_lower = intent["raw_request"].lower()
            for word in request_lower.split():
                if len(word) > 3 and word in tool.name.lower():
                    score += 0.1
                if len(word) > 3 and word in tool.description.lower():
                    score += 0.05
            
            # Bonus for exact domain+operation match
            if intent["domain"] != "unknown" and intent["operation"] != "unknown":
                if intent["domain"] in tool.capabilities and intent["operation"] in tool.capabilities:
                    score += 0.2
            
            if score > 0:
                candidates.append((tool, score))
        
        # Sort by score descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates

    def select_best_tool(self, candidates: List[tuple[RegisteredTool, float]]) -> Optional[RegisteredTool]:
        """Select the best tool from candidates."""
        if not candidates:
            return None
        
        # Return the highest-scoring tool
        return candidates[0][0]
