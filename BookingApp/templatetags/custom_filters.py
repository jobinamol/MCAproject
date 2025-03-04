from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='make_initials')
def make_initials(name):
    """Convert a full name into initials."""
    try:
        # Split the name and get initials
        words = name.split()
        initials = ''.join(word[0].upper() for word in words if word)
        # Return first two initials if available, otherwise just first initial
        return initials[:2]
    except (AttributeError, IndexError):
        return '##'

@register.filter
def subtract(value, arg):
    """Subtract the arg from the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0 