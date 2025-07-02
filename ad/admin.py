from django.contrib import admin
from .models import (
    ExchangeProposal,
    Ad,
    User,
    Category
)

admin.site.register(ExchangeProposal)
admin.site.register(Ad)
admin.site.register(Category)
admin.site.register(User)