from django import template

register = template.Library()

@register.filter
def sum_costs(houses_with_costs):
    """Sumuje koszty wszystkich domów"""
    return round(sum(item['monthly_cost'] for item in houses_with_costs), 2)

@register.filter
def sum_kwh(houses_with_costs):
    """Sumuje kWh wszystkich domów"""
    return round(sum(item['monthly_kwh'] for item in houses_with_costs), 2)