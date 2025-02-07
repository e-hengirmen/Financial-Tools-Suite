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
from index_trend_visualiser import IndexTrendVisualiser




############################## VARIABLES ##############################
# operation types are:
# * ROI_CALCULATOR
# * VALUATION_CALCULATOR
# * INDEX_VISUALISER
# * ALL_CALCULATORS
operation = "VALUATION_CALCULATOR"

######### ROI_calculator variables
M=3000000  # initil credit
n=180      # months
r=1.0069   # interest rate
rent = 20000   # Set 0 if you want to calculte without rent
sell_after = 5 # as years. Dont make it more than credit time in yrstd(because of missing enflation data)
enflation_estimates_roi = [1.6, 1.5, 1.4, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1]  # 15 years of estimated enflations to make it easier if 180 months is chosen

######### Valuation_calculator variables
payment_options = [ # print total payment and number of months here
    (1800, 1),
    (3000, 12),
    (3600, 12),
]
# this will set yearly enflations to 1.6, 1.4, 1.1, 1.1, 1.1 ... . If you wanna set your own estimated enflation rates change the list to a list of yearly enflation rates.
enflation_estimates_val = [1.41, 1.4]  # 2 years of data added since 18 months is less than 2 years

######### Index Visualiser variables
current_day = 15
drop_percent = 5.5
period = 2
match_day = 0
#######################################################################


RED = '\033[31m'
GREEN = '\033[32m'
BOLD = '\033[1m'
RESET ='\033[0m'

def colorize(s, color):
    return BOLD + color + (f'{s:.2f}' if type(s) is float else str(s)) + RESET


if operation in ('ROI_CALCULATOR', 'ALL_CALCULATORS'):
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


if operation == 'ALL_CALCULATORS':
    print()
    print('#########################################################')
    print()


if operation in ('VALUATION_CALCULATOR', 'ALL_CALCULATORS'):
    enflation_estimator = EnflationEstimateYearly(enflation_estimates_val)
    devalutaion_calculator = Devaluation_Calculator(enflation_estimator=enflation_estimator)
    payment_list = devalutaion_calculator.order_payment_options(payment_options)
    best_val = payment_list[0][0]
    for index, (total_paid_value, total_payment, payment_time) in enumerate(payment_list, 1):
        if index == 1:
            color = GREEN
        else:
            color = RED
        print(f'{index}. with total payment of'
              f' {colorize(total_payment, color)} with {payment_time}'
              f' months of payments it costs: {colorize(total_paid_value, color)}(enflation adjusted)')
        if index == 1:
            if len(payment_list) > 1:
                print(f'\t PAYING {colorize(payment_list[1][0] - best_val, GREEN)} less then next best option')
        else:
            print(f'\t PAYING {colorize(total_paid_value - best_val, RED)} more')


if operation in ('INDEX_VISUALISER', 'ALL_CALCULATORS'):
    visualiser = IndexTrendVisualiser()
    visualiser.process_data(current_day=current_day, drop_percent=drop_percent, period=period)
    visualiser.create_graph(match_day=match_day)
# visualiser.create_graph(match_day=14-1)

