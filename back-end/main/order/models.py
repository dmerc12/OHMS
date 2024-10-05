from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from customer.models import Customer
from material.models import Material
from service.models import Service
from user.models import User
from django.db import models

# Order model
class Order(models.Model):
    class CALLOUT_CHOICES(models.TextChoices):
        STANDARD = '50.0', 'Standard - $50.00'
        EMERGENCY = '175.0', 'Emergency - $175.00'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=2000, validators=[MinLengthValidator(2), MaxLengthValidator(2000)])
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=93.0, validators=[MinValueValidator(75.0)])
    hours_worked = models.DecimalField(max_digits=10, decimal_places=2, default=3.0, validators=[MinValueValidator(3.0)])
    labor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])
    material_upcharge = models.DecimalField(max_digits=10, decimal_places=2, default=25.0, validators=[MinValueValidator(15.0), MaxValueValidator(75.0)])
    material_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])
    line_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=12.0, validators=[MinValueValidator(0.0), MaxValueValidator(20.0)])
    tax_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])
    completed = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    discount_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])
    payment_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])
    working_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])
    notes = models.CharField(max_length=10000, validators=[MaxLengthValidator(10000)], null=True, blank=True)
    callout = models.FloatField(choices=CALLOUT_CHOICES.choices, default=CALLOUT_CHOICES.STANDARD)

    def calculate_hours_worked(self):
        work_logs = OrderWorkLog.objects.filter(order=self)
        total_hours = sum((log.end - log.start).total_seconds() / 3600 for log in work_logs)
        return max(float(total_hours), 3.0)

    def calculate_labor_total(self):
        return max(float(self.hourly_rate) * float(self.hours_worked), 0.0)

    def calculate_material_total(self):
        materials = OrderMaterial.objects.filter(order__pk=self.pk)
        total_material_costs = sum((material.material.unit_cost * material.quantity) for material in materials)
        return max(float(total_material_costs) * (1 + float(self.material_upcharge) / 100), 0.0)

    def calculate_line_total(self):
        costs = OrderCost.objects.filter(order__pk=self.pk)
        return max(float(sum(cost.cost for cost in costs)), 0.0)

    def calculate_subtotal(self):
        return max(float(self.labor_total) + float(self.material_total) + float(self.line_total) + float(self.callout), 0)

    def calculate_tax_total(self):
        return max((float(self.tax) / 100) * float(self.subtotal), 0.0)

    def calculate_discount_total(self):
        return max((float(self.discount) / 100) * float(self.subtotal), 0.0)

    def calculate_total(self):
        return max(float(self.subtotal) + float(self.tax_total) - float(self.discount_total), 0.0)

    def calculate_payment_total(self):
        return max(float(sum(payment.total for payment in OrderPayment.objects.filter(order=self))), 0.0)

    def calculate_working_total(self):
        return max(float(self.total) - float(self.payment_total), 0.0)

    def determine_paid(self):
        if self.working_total == 0:
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.hours_worked = self.calculate_hours_worked()
        self.labor_total = self.calculate_labor_total()
        self.material_total = self.calculate_material_total()
        self.line_total = self.calculate_line_total()
        self.subtotal = self.calculate_subtotal()
        self.tax_total = self.calculate_tax_total()
        self.discount_total = self.calculate_discount_total()
        self.total = self.calculate_total()
        self.payment_total = self.calculate_payment_total()
        self.working_total = self.calculate_working_total()
        self.paid = self.determine_paid()
        super().save()

# Order work log model
class OrderWorkLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='work_logs')
    start = models.DateTimeField()
    end = models.DateTimeField()

    def clean(self):
        # Ensure the end time is after the start time
        if self.end <= self.start:
            raise ValidationError('The start time must be before the end time.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        # Recalculate the order fields after saving the work log
        self.order.save()

# Order cost model
class OrderCost(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='costs')
    name = models.CharField(max_length=300, validators=[MinLengthValidator(2), MaxLengthValidator(300)])
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculate the order fields after saving a cost
        self.order.save()

# Order picture model
class OrderPicture(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='orders')

# Order material model
class OrderMaterial(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='materials')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculate the order fields after saving a material
        self.order.save()

# Order payment model
class OrderPayment(models.Model):
    class PAYMENT_CHOICES(models.TextChoices):
        CASH = 'cash', 'Cash'
        CHECK = 'check', 'Check'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    date = models.DateField()
    type = models.CharField(max_length=5, choices=PAYMENT_CHOICES.choices)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])
    notes = models.CharField(max_length=255, validators=[MaxLengthValidator(255)], blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculate the order fields after saving a payment
        self.order.save()

# Order Worker model
class OrderWorker(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='workers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])

    def save(self, *args, **kwargs):
        self.total = self.user.pay_rate * self.order.hours_worked
        super().save(*args, **kwargs)
