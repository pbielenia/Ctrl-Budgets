from django.contrib import admin

from .models import *

admin.site.register(Portfolio)
admin.site.register(TargetAssetTypeWeight)
admin.site.register(AssetType)
admin.site.register(PortfolioElement)
admin.site.register(Currency)
admin.site.register(Asset)
admin.site.register(RatingUpdate)
admin.site.register(CurrencyRatingUpdate)
admin.site.register(AssetRatingUpdate)
admin.site.register(TransactionType)
admin.site.register(Transaction)
