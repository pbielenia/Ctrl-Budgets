from inspect import trace

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

import logging

from .forms import *
from .models import *


def calc_units_count_from_transactions(transactions):
    TRANSACTION_BUY = 'BUY'
    TRANSACTION_SELL = 'SELL'

    units_count = 0
    for transaction in transactions:
        if transaction.type == TRANSACTION_BUY:
            units_count = units_count + transaction.units_count
        elif transaction.type == TRANSACTION_SELL:
            units_count = units_count - transaction.units_count

    return units_count


def calc_recent_rating_from_transactions(transactions):
    if len(transactions) == 0:
        return 0

    return transactions.order_by('-asset_rating__date')[0].asset_rating.rating


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
        recent_rating = calc_recent_rating_from_transactions(transactions)
        entire_value += units_count * recent_rating
    return float(entire_value)

# href="{% url 'investments:portfolio_element' portfolio.id element.asset_type.id %}">{{element.asset_type}}</a>


def find_values_of_elements(portfolio_id, elements):
    elements_values = dict()
    portfolio_value = 0
    for element in elements:
        value = calc_value_of_asset_type_in_portfolio(
            element.asset_type.id, portfolio_id)
        portfolio_value += value
        elements_values[element.id] = value

    return elements_values, portfolio_value


def get_element_actual_weight(portfolio_value, element_value):
    if portfolio_value == 0:
        return '-'
    else:
        return element_value / portfolio_value * 100


def get_element_deviation_weight(portfolio_value, actual_weight, target_weight):
    if portfolio_value == 0:
        return '-'
    else:
        return actual_weight - target_weight


def make_elements_data(portfolio_value, elements, elements_values):
    elements_data = list()

    for element in elements:
        model = {
            'weight': element.weight,
            'value': element.weight.target / 100 * portfolio_value
        }
        actual = {
            'weight': get_element_actual_weight(portfolio_value, elements_values[element.id]),
            'value': elements_values[element.id]
        }
        deviation = {
            'weight': get_element_deviation_weight(portfolio_value, actual['weight'], model['weight'].target),
            'value': actual['value'] - model['value']
        }

        elements_data.append({
            'asset_type': element.asset_type,
            'model': model,
            'actual': actual,
            'deviation': deviation
        })

    return elements_data


def make_portfolios_data(portfolios) -> list:
    portfolios_data = list()
    for portfolio in portfolios:
        elements = PortfolioElement.objects.filter(portfolio=portfolio.pk)
        elements_values, portfolio_value = find_values_of_elements(portfolio.id, elements)
        portfolios_data.append({
            'id': portfolio.id,
            'name': portfolio.name,
            'value': portfolio_value,
            'elements': make_elements_data(portfolio_value, elements, elements_values)
        })

    return portfolios_data


def calc_targeted_budget_balance(budget_id) -> float:
    balance = 0
    transactions = TargetedTransaction.objects.filter(targeted_budget=budget_id)

    for transaction in transactions:
        if transaction.type == TargetedTransaction.TYPE_DEPOSIT:
            balance = balance + transaction.cost
        elif transaction.type == TargetedTransaction.TYPE_WITHDRAWAL:
            balance = balance - transaction.cost
        else:
            pass
            # TODO: throw exception (or a red log) on unknown transaction type

    return balance


def make_targeted_budgets_data(targeted_budgets) -> list:
    budgets_data = list()
    for budget in targeted_budgets:
        budgets_data.append({
            'id': budget.id,
            'name': budget.name,
            'balance': calc_targeted_budget_balance(budget.id)
        })

    return budgets_data


def get_current_targeted_budgets_vault_value():
    latest = TargetedBudgetsVaultValue.objects.order_by('-timestamp').first()
    if latest is None:
        return 0
    else:
        return latest.value


def calc_total_budgets_value(budgets_data):
    total = 0
    for budget in budgets_data:
        total = total + budget['balance']
    return total


def calc_current_targeted_budgets_balance(budgets_data, vault_value):
    total_budgets_value = calc_total_budgets_value(budgets_data)
    return vault_value - total_budgets_value


def make_new_change_targeted_budgets_vault_value_form(request):
    form = ChangeTargetedBudgetsVaultValueForm(request.POST)
    return form if form.is_valid() else ChangeTargetedBudgetsVaultValueForm()


def make_new_create_new_targeted_budget_form(request):
    form = CreateNewTargetedBudgetForm(request.POST)
    return form if form.is_valid() else CreateNewTargetedBudgetForm()


def index(request):
    context = dict()

    portfolios = Portfolio.objects.order_by('name')
    context['portfolios'] = make_portfolios_data(portfolios)

    change_targeted_budgets_vault_value_form = make_new_change_targeted_budgets_vault_value_form(request)
    if change_targeted_budgets_vault_value_form.is_valid():
        entry = TargetedBudgetsVaultValue()
        entry.value = change_targeted_budgets_vault_value_form.cleaned_data['value']
        entry.save()
        return HttpResponseRedirect(reverse('investments:index'))
    else:
        context['targeted_budgets_vault_form'] = change_targeted_budgets_vault_value_form

    create_new_targeted_budget_form = make_new_create_new_targeted_budget_form(request)
    if create_new_targeted_budget_form.is_valid():
        entry = TargetedBudget()
        entry.name = create_new_targeted_budget_form.cleaned_data['name']
        entry.save()
        return HttpResponseRedirect(reverse('investments:index'))
    else:
        context['targeted_budget_create_form'] = create_new_targeted_budget_form

    targeted_budgets = TargetedBudget.objects.order_by('name')
    targeted_budgets_data = make_targeted_budgets_data(targeted_budgets)
    context['targeted_budgets'] = targeted_budgets_data

    vault_value = get_current_targeted_budgets_vault_value()
    context['targeted_budgets_vault_value'] = vault_value

    targeted_budgets_balance = calc_current_targeted_budgets_balance(targeted_budgets_data, vault_value)
    context['targeted_budgets_balance'] = targeted_budgets_balance

    return render(request, 'investments/index.html', context)


def new_portfolio(request):
    form = CreatePortfolioForm()

    logger = logging.getLogger(__name__)
    logger.info('new_portfolio()')

    if request.method == "POST":
        logger.info('new_portfolio() - POST method')
        form = CreatePortfolioForm(request.POST)
        if form.is_valid():
            logger.info('new_portfolio() - form is valid')
            logger.info('new_portfolio() - form.name: {}'.format(form.cleaned_data['name']))

            portfolio = Portfolio()
            portfolio.name = form.cleaned_data['name']
            portfolio.save()

            return HttpResponseRedirect(reverse('investments:index'))
        else:
            logger.info('new_portfolio() - form is not valid')
            form = CreatePortfolioForm()

    context = dict()
    context['form'] = form

    return render(request, 'investments/new_portfolio.html', context)


def create_portfolio(request):
    if request.method == "POST":
        form = CreatePortfolioForm(request.POST)
        if form.is_valid():
            return index(request)
        else:
            form = CreatePortfolioForm()

    return render(request, "investments/index.html")


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


def portfolio_element(request, portfolio_id, asset_type_id):
    print(portfolio_id, asset_type_id)
    portfolio_element = get_object_or_404(
        PortfolioElement, portfolio__id=portfolio_id, asset_type__id=asset_type_id)
    assets = Asset.objects.filter(type=asset_type_id)

    # Collect assets data
    assets_data = list()
    for asset in assets:
        name = asset.name
        transactions = get_transactions_of_asset_in_portfolio(
            asset.id, portfolio_id)
        units_count = calc_units_count_from_transactions(transactions)
        recent_rating = calc_recent_rating_from_transactions(transactions)

        value = recent_rating * units_count
        base_currency = asset.currency

        assets_data.append({
            'name': name,
            'units_count': units_count,
            'value': value,
            'base_currency': base_currency
        })

    context = {
        'portfolio_element': portfolio_element,
        'assets': assets_data}

    return render(request, 'investments/portfolio_asset_class.html', context)


def targeted_budget_new(request):
    pass


def make_targeted_budget_transactions_data(budget_id, number_of_transactions):
    transactions = TargetedTransaction.objects.filter(targeted_budget=budget_id)[:number_of_transactions]
    data = list()

    for transaction in transactions:
        cost = (-transaction.cost, transaction.cost)[transaction.type == transaction.TYPE_DEPOSIT]

        data.append({
            'date': transaction.date,
            'cost': cost,
            'details': transaction.description})

    return data


def make_new_targeted_transaction_form(request):
    form = NewTargetedTransactionForm(request.POST)
    return form if form.is_valid() else NewTargetedTransactionForm()


def create_targeted_transaction_from_form(form, budget) -> None:
    transaction = TargetedTransaction()
    transaction.targeted_budget = budget
    transaction.date = form.cleaned_data['date']
    transaction.type = form.cleaned_data['type']
    transaction.cost = form.cleaned_data['cost']
    transaction.description = form.cleaned_data['description']
    transaction.save()


def targeted_budget(request, budget_id):
    NUMBER_OF_TRANSACTIONS = 20

    budget = get_object_or_404(TargetedBudget, id=budget_id)
    new_transaction_form = make_new_targeted_transaction_form(request)

    if new_transaction_form.is_valid():
        create_targeted_transaction_from_form(new_transaction_form, budget)
        return HttpResponseRedirect(reverse('investments:targeted_budget', args=(budget_id)))

    context = {
        'budget': budget,
        'balance': calc_targeted_budget_balance(budget.id),
        'transactions': make_targeted_budget_transactions_data(budget.id, NUMBER_OF_TRANSACTIONS),
        'new_transaction_form': new_transaction_form,
        'planned': []}
    return render(request, 'investments/targeted-budget.html', context)
