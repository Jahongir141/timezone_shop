from django import forms
from django.core.validators import RegexValidator
from .models import Order, Watch


class OrderForm(forms.ModelForm):
    """Form used inside the Buy Now modal to place an order."""

    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
    )

    class Meta:
        model = Order
        fields = [
            "customer_name",
            "phone",
            "email",
            "address",
            "quantity",
            "note",
        ]
        widgets = {
            "customer_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Your full name"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+998901234567"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "you@example.com"}
            ),
            "address": forms.Textarea(
                attrs={"class": "form-control", "rows": 2, "placeholder": "Delivery address"}
            ),
            "note": forms.Textarea(
                attrs={"class": "form-control", "rows": 2, "placeholder": "Optional note"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.watch = kwargs.pop("watch", None)
        super().__init__(*args, **kwargs)

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if self.watch and quantity > self.watch.stock:
            raise forms.ValidationError(
                f"Only {self.watch.stock} item(s) left in stock."
            )
        return quantity

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        validator = RegexValidator(
            regex=r"^\+?[0-9]{7,15}$",
            message="Enter a valid phone number (7-15 digits, optional leading +).",
        )
        validator(phone)
        return phone


class SearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search by brand, model or title...",
                "type": "search",
            }
        ),
    )


class WatchAdminForm(forms.ModelForm):
    """Used by the admin site; keeps validation consistent."""

    class Meta:
        model = Watch
        fields = "__all__"

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data["stock"]
        if stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock
