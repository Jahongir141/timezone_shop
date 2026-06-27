from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST

from .models import Category, Watch, Order
from .forms import OrderForm, SearchForm

WATCHES_PER_PAGE = 9


def home(request):
    featured_watches = Watch.objects.filter(is_featured=True)[:6]
    new_arrivals = Watch.objects.filter(is_new_arrival=True)[:6]
    latest_products = Watch.objects.all()[:8]
    categories = Category.objects.all()

    context = {
        "featured_watches": featured_watches,
        "new_arrivals": new_arrivals,
        "latest_products": latest_products,
        "categories": categories,
    }
    return render(request, "store/home.html", context)


def watch_list(request):
    """List all watches with optional search and pagination."""
    watches = Watch.objects.select_related("category").all()
    search_form = SearchForm(request.GET or None)
    query = ""

    if search_form.is_valid():
        query = search_form.cleaned_data.get("q", "")
        if query:
            watches = watches.filter(
                Q(brand__icontains=query)
                | Q(model__icontains=query)
                | Q(title__icontains=query)
            )

    paginator = Paginator(watches, WATCHES_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "watches": page_obj.object_list,
        "search_form": search_form,
        "query": query,
        "categories": Category.objects.all(),
    }
    return render(request, "store/watch_list.html", context)


def category_list(request):
    categories = Category.objects.all()
    return render(request, "store/category_list.html", {"categories": categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    watches = Watch.objects.filter(category=category)

    paginator = Paginator(watches, WATCHES_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "category": category,
        "page_obj": page_obj,
        "watches": page_obj.object_list,
        "categories": Category.objects.all(),
    }
    return render(request, "store/category_detail.html", context)


def watch_detail(request, slug):
    watch = get_object_or_404(Watch.objects.select_related("category"), slug=slug)
    related_watches = Watch.objects.filter(category=watch.category).exclude(
        pk=watch.pk
    )[:4]
    order_form = OrderForm(watch=watch)

    context = {
        "watch": watch,
        "related_watches": related_watches,
        "order_form": order_form,
    }
    return render(request, "store/watch_detail.html", context)


def about(request):
    return render(request, "store/about.html")


@login_required
@require_POST
def place_order(request, slug):
    """Handle the Buy Now modal submission."""
    watch = get_object_or_404(Watch, slug=slug)
    form = OrderForm(request.POST, watch=watch)

    if form.is_valid():
        if watch.stock < form.cleaned_data["quantity"]:
            messages.error(request, "Sorry, not enough stock available.")
            return redirect("watch_detail", slug=watch.slug)

        order = form.save(commit=False)
        order.watch = watch
        order.user = request.user
        order.total_price = watch.price * order.quantity
        order.save()

        watch.stock -= order.quantity
        watch.save(update_fields=["stock"])

        messages.success(
            request,
            f"Thank you, {order.customer_name}! Your order for "
            f"{watch.brand} {watch.model} has been placed successfully.",
        )
        return redirect("order_success", order_id=order.id)

    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"{field}: {error}")
    return redirect("watch_detail", slug=watch.slug)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, "store/order_success.html", {"order": order})
