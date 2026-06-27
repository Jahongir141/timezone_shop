from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth.models import User


class Category(models.Model):
    """Watch category, e.g. Luxury, Sport, Smart."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"slug": self.slug})


class Watch(models.Model):
    """A single watch product in the store."""

    GENDER_CHOICES = (
        ("men", "Men"),
        ("women", "Women"),
        ("unisex", "Unisex"),
    )

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="watches"
    )
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    title = models.CharField(max_length=200, help_text="Display name of the product")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    image = models.ImageField(upload_to="watches/")
    stock = models.PositiveIntegerField(default=0)
    movement = models.CharField(
        max_length=100,
        help_text="e.g. Automatic, Quartz, Mechanical, Solar",
    )
    case_material = models.CharField(max_length=100, help_text="e.g. Stainless Steel, Titanium")
    strap_material = models.CharField(max_length=100, help_text="e.g. Leather, Rubber, Metal")
    water_resistance = models.CharField(max_length=50, help_text="e.g. 50m, 100m, 200m")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="unisex")
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand} {self.model}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.brand}-{self.model}-{self.title}")
            slug = base_slug
            counter = 1
            while Watch.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("watch_detail", kwargs={"slug": self.slug})

    @property
    def in_stock(self):
        return self.stock > 0


class Order(models.Model):
    """An order placed by a customer for a watch."""

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELLED, "Cancelled"),
    )

    phone_validator = RegexValidator(
        regex=r"^\+?[0-9]{7,15}$",
        message="Enter a valid phone number (7-15 digits, optional leading +).",
    )

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    customer_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, validators=[phone_validator])
    email = models.EmailField()
    address = models.TextField()
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE, related_name="orders")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} - {self.customer_name} ({self.watch})"

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.watch.price * self.quantity
        super().save(*args, **kwargs)
