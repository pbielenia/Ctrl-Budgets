from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now


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
        return "{} - {} - {}".format(self.target, self.min, self.max)


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
        return "{} - {}".format(self.portfolio, self.asset_type)

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
        return "{} - {} - {}".format(self.type, self.name, self.currency)


class Rating(models.Model):
    date = models.DateField()
    rating = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self):
        return "{} - {}".format(self.date, self.rating)


class CurrencyRating(models.Model):
    date = models.DateField()
    rating = models.DecimalField(max_digits=10, decimal_places=4)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {} - {}".format(str(self.date), str(self.rating), str(self.currency))


class AssetRating(models.Model):
    date = models.DateField()
    rating = models.DecimalField(max_digits=10, decimal_places=4)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)

    def __str__(self):
        return "{} - {}".format(self.date, self.asset)


class Transaction(models.Model):
    TYPE_BUY = "BUY"
    TYPE_SELL = "SELL"
    TYPE_CHOICES = {
        TYPE_BUY: "Buy",
        TYPE_SELL: "Sell",
    }

    type = models.CharField(max_length=4, choices=TYPE_CHOICES, default=TYPE_BUY)
    asset_rating = models.ForeignKey(
        AssetRating, on_delete=models.CASCADE)
    # portfolio must have an appropriate asset type in its elements
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    currency_rating = models.ForeignKey(
        CurrencyRating, on_delete=models.CASCADE, blank=True, null=True)
    units_count = models.DecimalField(max_digits=10, decimal_places=4)

    def __str__(self):
        return "{} - {}".format(self.type, self.asset_rating)


class TargetedBudget(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class TargetedTransaction(models.Model):
    TYPE_DEPOSIT = "DEPOSIT"
    TYPE_WITHDRAWAL = "WITHDRAWAL"
    TYPE_CHOICES = {
        TYPE_DEPOSIT: "Deposit",
        TYPE_WITHDRAWAL: "Withdrawal",
    }

    targeted_budget = models.ForeignKey(TargetedBudget, on_delete=models.CASCADE)
    description = models.CharField(max_length=300)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_WITHDRAWAL)
    cost = models.IntegerField(validators=[MinValueValidator(0)])
    date = models.DateField()

    class Meta:
        ordering = ["-date", "cost"]


class PeriodicTargetedTransaction(models.Model):
    TYPE_BUY = "BUY"
    TYPE_SELL = "SELL"
    TYPE_CHOICES = {
        TYPE_BUY: "Buy",
        TYPE_SELL: "Sell",
    }

    targeted_budget = models.ForeignKey(TargetedBudget, on_delete=models.CASCADE)
    description = models.CharField(max_length=300)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES, default=TYPE_BUY)
    start_date = models.DateField()
    interval = models.DurationField()


class TargetedBudgetsVaultValue(models.Model):
    value = models.IntegerField()
    timestamp = models.DateTimeField(default=now)

    class Meta:
        ordering = ["-timestamp"]
