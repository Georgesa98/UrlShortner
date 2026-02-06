from contextlib import contextmanager
from django.db import models


@contextmanager
def disable_auto_now(model_classes):
    """
    Temporarily disables auto_now and auto_now_add on model fields.
    
    This is useful for seeding databases with custom timestamps that would
    otherwise be overridden by Django's auto_now/auto_now_add behavior.
    
    Usage:
        with disable_auto_now([MyModel, OtherModel]):
            # Create objects with custom timestamps
            MyModelFactory.create(created_at=custom_date)
    
    Args:
        model_classes: List of Django model classes to disable auto_now fields on
    """
    # Store original values
    original_values = []
    
    for model_class in model_classes:
        for field in model_class._meta.get_fields():
            if isinstance(field, models.DateTimeField) or isinstance(field, models.DateField):
                auto_now = getattr(field, 'auto_now', None)
                auto_now_add = getattr(field, 'auto_now_add', None)
                
                if auto_now or auto_now_add:
                    original_values.append((field, auto_now, auto_now_add))
                    field.auto_now = False
                    field.auto_now_add = False
    
    try:
        yield
    finally:
        # Restore original values
        for field, auto_now, auto_now_add in original_values:
            field.auto_now = auto_now
            field.auto_now_add = auto_now_add
