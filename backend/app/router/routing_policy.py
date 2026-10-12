from typing import Optional, Dict, Any
from enum import Enum


class Permission(str, Enum):
    ALLOWED = "allowed"
    DENIED = "denied"
    REQUIRES_CONFIRMATION = "requires_confirmation"


class RoutingPolicy:
    """Policy engine for tool execution authorization."""

    def __init__(self):
        # Simple policy: write operations require confirmation
        self.write_operations = ["create", "update", "delete", "add", "modify", "remove"]

    def check_permission(self, operation: str, tool_name: str) -> Permission:
        """Check if an operation is permitted."""
        operation_lower = operation.lower()
        
        # Write operations require confirmation
        if any(op in operation_lower for op in self.write_operations):
            return Permission.REQUIRES_CONFIRMATION
        
        # Read operations are allowed by default
        return Permission.ALLOWED

    def validate_parameters(self, parameters: Dict[str, Any], schema: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate parameters against tool schema."""
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        # Check required parameters
        for req in required:
            if req not in parameters:
                return False, f"Missing required parameter: {req}"
        
        # Check parameter types (basic validation)
        for param_name, param_value in parameters.items():
            if param_name in properties:
                param_schema = properties[param_name]
                param_type = param_schema.get("type")
                
                if param_type == "string" and not isinstance(param_value, str):
                    return False, f"Parameter {param_name} must be a string"
                if param_type == "number" and not isinstance(param_value, (int, float)):
                    return False, f"Parameter {param_name} must be a number"
                if param_type == "integer" and not isinstance(param_value, int):
                    return False, f"Parameter {param_name} must be an integer"
        
        return True, None
