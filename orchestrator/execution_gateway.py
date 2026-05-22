
class ValidationError(Exception):
    pass

def validate(tool_schema, args, user=None, tool_name=None):

    # 1. Required keys check
    for key, expected_type in tool_schema.items():
        if key not in args:
            raise ValidationError(f"Missing required field: {key}")

        value = args[key]

        # 2. Type validation
        if not isinstance(value, expected_type):
            raise ValidationError(
                f"Invalid type for {key}: expected {expected_type}, got {type(value)}"
            )

        # 3. Basic safety constraints
        if isinstance(value, str):
            if len(value) > 5000:
                raise ValidationError(f"Field too large: {key}")

            # simple injection heuristics (not perfect, but useful)
            suspicious_patterns = ["ignore previous", "system prompt", "reveal", "admin"]
            if any(p in value.lower() for p in suspicious_patterns):
                raise ValidationError(f"Suspicious input detected in {key}")

    # 4. Tool-specific constraints (optional but important)
    if tool_name == "create_ticket":
        if len(args.get("title", "")) < 5:
            raise ValidationError("Ticket title too short")

    # 5. User-level policy checks (optional extension point)
    if user:
        if tool_name == "create_ticket" and "tickets.write" not in user.permissions:
            raise ValidationError("User not permitted to create tickets")

    return True

def execute_tool(user, tool_name, args):

    tool = TOOLS[tool_name]

    # 1. Permission check
    if tool["permission"] not in user.permissions:
        raise Exception("Forbidden")

    # 2. VALIDATION (explicit and required)
    validate(tool["schema"], args, user=user, tool_name=tool_name)

    # 3. Execution
    return TOOL_IMPL[tool_name](**args)

