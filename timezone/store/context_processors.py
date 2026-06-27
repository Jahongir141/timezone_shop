from .models import Category


def categories_processor(request):
    """Make categories available to all templates (navbar, footer, etc.)."""
    return {"nav_categories": Category.objects.all()}
