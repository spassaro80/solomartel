from django.db import models
from accounts.models import Client, Private, Entity, Account

# Create your models here.
STATUS = (
    ('Pending', 'Pending'),
    ('Complete', 'Complete'),
)

STATES = (
    ('Repaired/built', 'Repaired/built'),
    ('Performing asset', 'Performing asset')
)


class Investment(models.Model):
    name = models.CharField(max_length=255, unique=True)
    minimum_investment = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Minimum investment ($)')
    gross_returns = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Gross returns (%)')
    net_returns = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Net returns (%)')
    description = models.TextField()
    invested_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Invested amount ($)')
    market_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Market value ($)')

    # ---------- Bank information -----------
    bank_name = models.CharField(max_length=255)
    subsidiary_name = models.CharField(max_length=255)
    ABA_number = models.IntegerField()
    company_address = models.CharField(max_length=255)
    account_number = models.IntegerField()  # Tell if it has some validation for this field.
    current_state = models.CharField(max_length=255, choices=STATES, default='Performing asset')

    def __str__(self):
        return self.name


class Client_Investment(models.Model):
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='clients')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='investments')
    invest_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS)
    approved = models.BooleanField(default=False)
    done = models.BooleanField(default=False)
    invested_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Invested amount($)')
    phone_number = models.CharField(max_length=16)
    payment_token = models.CharField(max_length=128, null=True)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.client.legal_name} invest in {self.investment.name}'


class Remark(models.Model):
    sender_email = models.EmailField()
    title = models.CharField(max_length=255)
    content = models.FileField(upload_to='remarks_files')
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='my_remarks')

    def __str__(self):
        return self.title


class PropertyPicture(models.Model):
    name = models.CharField(max_length=255)
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='my_images')
    image = models.ImageField(upload_to=f'investments/{investment.name}')

    def __str__(self):
        return f'{self.investment.name}[Image] - {self.name}'


class PromotionalDocument(models.Model):
    name = models.CharField(max_length=255)
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='my_documents')
    file = models.FileField(upload_to=f'documents/{investment.name}')

    def __str__(self):
        return f'{self.investment.name}[Document] - {self.name}'


class Testimonial(models.Model):
    client_name = models.CharField(max_length=255, default='Satisfied client')
    client_photo = models.ImageField(upload_to='client_profile', null=True, blank=True)
    testimonial = models.TextField(blank=True)
    url = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'Testimonial {self.client_name}' if self.client_name else f'Testimonial {self.url}'
