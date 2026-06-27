from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from store.models import Order
from .models import Profile


@login_required
def profile_view(request):
    Profile.objects.get_or_create(user=request.user)
    orders = Order.objects.filter(user=request.user).select_related("watch")
    context = {
        "orders": orders,
    }
    return render(request, "accounts/profile.html", context)
