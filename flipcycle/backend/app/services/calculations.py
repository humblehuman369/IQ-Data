from app.schemas.workspace import ArvEstimate, DealInput, DealMetrics


def _round(value: float) -> float:
    return round(value + 1e-9, 2)


def calculate_deal(input: DealInput) -> DealMetrics:
    financing_cost = input.loan_amount * (input.interest_rate / 100 / 12) * input.holding_months
    total_invested = input.purchase_price + input.repair_costs + input.closing_costs + input.selling_costs + financing_cost
    cash_invested = input.down_payment + input.repair_costs + input.closing_costs + financing_cost
    profit = input.arv - total_invested
    roi = (profit / total_invested * 100) if total_invested else 0
    cash_on_cash = (profit / cash_invested * 100) if cash_invested else 0
    return DealMetrics(
        profit=_round(profit), roi=_round(roi), cashOnCashReturn=_round(cash_on_cash),
        totalInvested=_round(total_invested), cashInvested=_round(cash_invested), financingCost=_round(financing_cost),
    )


def estimate_arv_from_comps(comps: list[dict], target_sqft: int | None = None) -> ArvEstimate:
    valid = [comp for comp in comps if float(comp.get('sale_price', comp.get('salePrice', 0))) > 0]
    if not valid:
        return ArvEstimate(estimatedArv=0, averageSalePrice=0, averagePricePerSqft=0, compCount=0)
    average_sale_price = sum(float(comp.get('sale_price', comp.get('salePrice', 0))) for comp in valid) / len(valid)
    ppsf = [float(comp.get('sale_price', comp.get('salePrice', 0))) / float(comp.get('sqft', 0)) for comp in valid if float(comp.get('sqft', 0)) > 0]
    average_ppsf = sum(ppsf) / len(ppsf) if ppsf else 0
    estimated_arv = target_sqft * average_ppsf if target_sqft and average_ppsf else average_sale_price
    return ArvEstimate(estimatedArv=_round(estimated_arv), averageSalePrice=_round(average_sale_price), averagePricePerSqft=_round(average_ppsf), compCount=len(valid))
