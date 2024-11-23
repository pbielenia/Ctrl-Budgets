from django.contrib import admin

from .models import *

admin.site.register(Portfolio)
admin.site.register(TargetAssetTypeWeight)
admin.site.register(AssetType)
admin.site.register(PortfolioElement)
admin.site.register(Currency)
admin.site.register(Asset)
admin.site.register(CurrencyRating)
admin.site.register(AssetRating)
admin.site.register(TransactionType)
admin.site.register(Transaction)
