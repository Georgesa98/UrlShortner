def compare_instances(old_instance, new_instance) -> dict:

    if old_instance.__class__ != new_instance.__class__:
        raise ValueError("Both instances must be of the same class")

    differences = {}

    fields = []
    for field in old_instance._meta.fields:
        fields.append(field.name)

    for field_name in fields:
        try:
            old_value = getattr(old_instance, field_name)
            new_value = getattr(new_instance, field_name)

            if hasattr(old_value, "_meta") and hasattr(
                new_value, "_meta"
            ):  # Foreign key
                old_value = getattr(old_value, "pk", old_value)
                new_value = getattr(new_value, "pk", new_value)

            if old_value != new_value:
                differences[field_name] = {
                    "old_value": old_value,
                    "new_value": new_value,
                }
        except AttributeError:
            continue

    return differences
