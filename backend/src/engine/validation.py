from .factors import Factor, FACTORS_BY_ID


def validate_answer(factor_id: str, value: str) -> tuple[bool, str | None]:
    """Validate an answer against its factor definition. Returns (is_valid, error_message)."""
    factor = FACTORS_BY_ID.get(factor_id)
    if not factor:
        return False, f"Unknown factor: {factor_id}"

    value = value.strip().lower()

    if factor.data_type == "integer":
        return _validate_integer(factor, value)
    elif factor.data_type == "categorical":
        return _validate_categorical(factor, value)
    elif factor.data_type == "boolean":
        return _validate_boolean(factor, value)
    elif factor.data_type == "multi_select":
        return _validate_multi_select(factor, value)
    elif factor.data_type == "text":
        return _validate_text(factor, value)

    return False, f"Unknown data type: {factor.data_type}"


def _validate_integer(factor: Factor, value: str) -> tuple[bool, str | None]:
    try:
        num = int(value)
    except ValueError:
        return False, f"Please provide a number for {factor.label}."

    if factor.min_val is not None and num < factor.min_val:
        return False, f"Value {num} is below the minimum of {factor.min_val}."
    if factor.max_val is not None and num > factor.max_val:
        return False, f"Value {num} is above the maximum of {factor.max_val}."

    return True, None


def _validate_categorical(factor: Factor, value: str) -> tuple[bool, str | None]:
    if factor.options and value not in factor.options:
        return False, f"Please choose one of: {', '.join(factor.options)}."
    return True, None


def _validate_boolean(factor: Factor, value: str) -> tuple[bool, str | None]:
    if value not in ("yes", "no"):
        return False, "Please answer yes or no."
    return True, None


def _validate_multi_select(factor: Factor, value: str) -> tuple[bool, str | None]:
    if not value:
        return False, "Please select at least one option."
    selected = [v.strip() for v in value.split(",")]
    if factor.options:
        invalid = [s for s in selected if s not in factor.options]
        if invalid:
            return False, f"Invalid selection(s): {', '.join(invalid)}. Choose from: {', '.join(factor.options)}."
    return True, None


def _validate_text(factor: Factor, value: str) -> tuple[bool, str | None]:
    if not value:
        return False, "Please provide a response."
    if len(value) > 500:
        return False, "Response is too long (max 500 characters)."
    return True, None
