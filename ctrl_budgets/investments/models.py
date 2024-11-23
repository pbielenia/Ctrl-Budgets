from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Portfolio(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name


class TargetAssetTypeWeight(models.Model):
    target = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)])
    min = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)])
    max = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return str(self.target) + ', ' + str(self.min) + '-' + str(self.max)


class AssetType(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class PortfolioElement(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    asset_type = models.ForeignKey(AssetType, on_delete=models.CASCADE)
    weight = models.OneToOneField(
        TargetAssetTypeWeight, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.portfolio) + ': ' + str(self.asset_type)

    class Meta:
        unique_together = ('portfolio', 'asset_type')


class Currency(models.Model):
    name = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.name


class Asset(models.Model):
    name = models.CharField(max_length=200)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    type = models.ForeignKey(AssetType, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.type) + ": " + str(self.name) + ' [' + str(self.currency) + ']'


class Rating(models.Model):
    date = models.DateField()
    rating = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self):
        return str(self.date) + ' - ' + str(self.rating)


class CurrencyRating(models.Model):
    date = models.DateField()
    rating = models.DecimalField(max_digits=10, decimal_places=4)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)


class AssetRating(models.Model):
    date = models.DateField()
    rating = models.DecimalField(max_digits=10, decimal_places=4)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.update) + " - " + str(self.asset)


class TransactionType(models.Model):
    name = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    type = models.ForeignKey(TransactionType, on_delete=models.CASCADE)
    asset_rating = models.ForeignKey(
        AssetRating, on_delete=models.CASCADE)
    # portfolio must have an appropriate asset type in its elements
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    currency_rating = models.ForeignKey(
        CurrencyRating, on_delete=models.CASCADE, blank=True, null=True)
    units_count = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self):
        return str(self.type) + " - " + str(self.asset_rating)
