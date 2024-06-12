from django.contrib import admin

from user_app.models import Account, LoteFutCoins, CompraFutCoins

# Register your models here.
admin.site.register(Account)
admin.site.register(LoteFutCoins)
admin.site.register(CompraFutCoins)
