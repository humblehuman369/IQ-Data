from app.schemas.workspace import DealInput
from app.services.calculations import calculate_deal, estimate_arv_from_comps


def test_calculate_deal_contract():
    metrics = calculate_deal(DealInput(
        purchasePrice=218000, repairCosts=62000, arv=372000, downPayment=43600,
        loanAmount=174400, interestRate=9.5, holdingMonths=7, closingCosts=8400, sellingCosts=21500,
    ))
    assert metrics.model_dump(by_alias=True) == {
        'profit': 52435.33,
        'roi': 16.41,
        'cashOnCashReturn': 42.4,
        'totalInvested': 319564.67,
        'cashInvested': 123664.67,
        'financingCost': 9664.67,
    }


def test_estimate_arv_from_comps():
    estimate = estimate_arv_from_comps([{'sale_price': 366000, 'sqft': 1840}, {'sale_price': 381500, 'sqft': 1925}], 1880)
    assert estimate.estimated_arv == 373269.17
    assert estimate.comp_count == 2
