"""
he ROI and devaluation calculators I have written calculates
the value of the product or home by calculating the value of
money you pay and/or value of the money you gain from the product.

In the end I calculate the value of the paid/price or gained value emflation adjusted
so it is accordance to the current value of your product

----------
IMPORTANT:
----------
* Read the below variables section. Change to your operation and adjust the variables in your group to calculate.
* The default enflation rate was set according to turkey's high enflation rates which is higher than %60 if u are from another country change the enflation estimator's list to your estimations.
"""

from roi_calculator import ROICalculator
from devaluation_calculator import Devaluation_Calculator
from rent_estimator import RentEstimatorInitialFlat
from enflation_estimator import EnflationEstimateFlat, EnflationEstimateYearly





############################## VARIABLES ##############################
# operation types are:
# * ROI_CALCULATOR
# * VALUATION_CALCULATOR
# * BOTH_CALCULATORS
operation = "BOTH_CALCULATORS"

######### ROI_calculator variables
M=3000000  # initil credit
n=120      # months
r=1.0069   # interest rate
rent = 25000   # Set 0 if you want to calculte without rent
sell_after = 5 # as years. Dont make it more than credit time in yrstd(because of missing enflation data)
enflation_estimates_roi = []

######### Valuation_calculator variables
onetime_payment = 10000
credit_payment  = 14200  # enter total credit payment here
credit_payment_time = 18
# this will set yearly enflations to 1.6, 1.4, 1.1, 1.1, 1.1 ... . If you wanna set your own estimated enflation rates change the list to a list of yearly enflation rates.
enflation_estimates_val = []
#######################################################################



if operation in ('ROI_CALCULATOR', 'BOTH_CALCULATORS'):
    enflation_estimator = EnflationEstimateYearly(enflation_estimation_list=enflation_estimates_roi)
    rent_estimator = RentEstimatorInitialFlat(rent, n, sell_after, enflation_estimator)
    roi_calculator = ROICalculator(M,n,r,enflation_estimator, rent_estimator)
    (
        monthly_payment,
        total_payment,
        total_payment_value,
        ROI,
        ROI_with_rent,
        total_rent,
        total_rent_value,
    ) = roi_calculator.calculate_roi_colored()
    print("monthly payment\t\t", monthly_payment)
    print("total_payment\t\t", total_payment)
    print("total_payment_value\t", total_payment_value)
    print()
    print("ROI\t\t\t", ROI, "(assuming home values with enflation)")
    print("ROI_with_rent\t\t", ROI_with_rent, "(assuming home values with enflation and rent increases yearly with enflation)")
    print()
    print("total_rent\t\t", total_rent)
    print(f"total_rent_value\t", total_rent_value)


if operation == 'BOTH_CALCULATORS':
    print()
    print('#########################################################')
    print()


if operation in ('VALUATION_CALCULATOR', 'BOTH_CALCULATORS'):
    enflation_estimator = EnflationEstimateYearly(enflation_estimates_val)
    devalutaion_calculator = Devaluation_Calculator(enflation_estimator=enflation_estimator)

    devalutaion_calculator.onetime_vs_credit(onetime_payment, credit_payment , credit_payment_time)
