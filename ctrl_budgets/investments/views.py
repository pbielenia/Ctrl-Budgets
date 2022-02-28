from inspect import trace
from django.shortcuts import render, get_object_or_404

from .models import *


def index(request):
    portfolios = Portfolio.objects.order_by('name')
    context = {'portfolios': portfolios}
    return render(request, 'investments/index.html', context)


def portfolio(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk)
    elements = PortfolioElement.objects.filter(portfolio=pk)

    elements_values = dict()
    portfolio_value = 0
    for element in elements:
        value = calc_value_of_asset_type_in_portfolio(
            element.asset_type.id, portfolio.id)
        portfolio_value += value
        elements_values[element.id] = value

    elements_data = list()
    for element in elements:
        model = dict()
        actual = dict()
        deviation = dict()

        model['weight'] = element.weight
        model['value'] = model['weight'].target / 100 * portfolio_value
        actual['value'] = elements_values[element.id]
        actual['weight'] = actual['value'] / portfolio_value * 100
        deviation['weight'] = actual['weight'] - model['weight'].target
        deviation['value'] = actual['value'] - model['value']

        print(element.asset_type)

        elements_data.append({
            'asset_type': element.asset_type,
            'model': model,
            'actual': actual,
            'deviation': deviation
        })

    print(elements_data)

    context = {'portfolio': portfolio,
               'value': portfolio_value, 'elements': elements_data}
    return render(request, 'investments/portfolio.html', context)


def calc_units_count_from_transactions(transactions):
    TRANSACTION_BUY = 'BUY'
    TRANSACTION_SELL = 'SELL'

    units_count = 0
    for transaction in transactions:
        if transaction.type.name == TRANSACTION_BUY:
            units_count = units_count + transaction.units_count
        elif transaction.type.name == TRANSACTION_SELL:
            units_count = units_count - transaction.units_count
    return units_count


def cals_recent_rating_from_transactions(transactions):
    if len(transactions) == 0:
        return 0

    return transactions.order_by('-asset_rating__update__date')[
        0].asset_rating.update.rating


def get_transactions_of_asset_in_portfolio(asset_id, portfolio_id):
    return Transaction.objects.filter(asset_rating__asset__id=asset_id,
                                      portfolio__id=portfolio_id)


def calc_value_of_asset_type_in_portfolio(asset_type_id, portfolio_id):
    assets = Asset.objects.filter(type=asset_type_id)
    entire_value = 0
    for asset in assets:
        transactions = get_transactions_of_asset_in_portfolio(
            asset.id, portfolio_id)
        units_count = calc_units_count_from_transactions(transactions)
        recent_rating = cals_recent_rating_from_transactions(transactions)
        entire_value += units_count * recent_rating
    return float(entire_value)


def portfolio_element(request, portfolio_id, asset_type_id):
    print(portfolio_id, asset_type_id)
    portfolio_element = get_object_or_404(
        PortfolioElement, portfolio__id=portfolio_id, asset_type__id=asset_type_id)
    assets = Asset.objects.filter(type=asset_type_id)

    assets_data = list()
    for asset in assets:
        name = asset.name
        transactions = get_transactions_of_asset_in_portfolio(
            asset.id, portfolio_id)
        units_count = calc_units_count_from_transactions(transactions)
        recent_rating = cals_recent_rating_from_transactions(transactions)

        value = recent_rating * units_count
        base_currency = asset.currency

        assets_data.append({
            'name': name,
            'units_count': units_count,
            'value': value,
            'base_currency': base_currency
        })

    context = {'portfolio_element': portfolio_element,
               'assets': assets_data}

    return render(request, 'investments/portfolio_asset_class.html', context)