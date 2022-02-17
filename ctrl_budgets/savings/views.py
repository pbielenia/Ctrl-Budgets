from django.shortcuts import render

budgets = [
    {'id': 1, 'name': 'Budget_A'},
    {'id': 2, 'name': 'Budget_B'},
    {'id': 3, 'name': 'Budget_C'},
]


def savings(request):
    context = {'budgets': budgets}
    return render(request, 'savings/savings.html', context)


def budget(request, pk):
    picked_budget = None
    for budget in budgets:
        if budget['id'] == int(pk):
            picked_budget = budget
            break

    context = {'budget': picked_budget}

    return render(request, 'savings/budget.html', context)
