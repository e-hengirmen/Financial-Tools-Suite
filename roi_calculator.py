from enflation_estimator import EnflationEstimateYearly
from rent_estimator import RentEstimatorInitialFlat

M=3000000  # initil credit
n=120      # months
r=1.0069   # interest rate
rent = 25000
sell_after = 5 # as years. Dont make it more than credit time(because of missing enflation data)


class ROICalculator:
  
    def __init__(self, M, n, r, enflation_estimator, rent_estimator=None):
        self.monthly_payment = M * r**n * (r-1)/(r**n-1)
        self.M = M
        self.n = n
        self.enflation_estimator = enflation_estimator
        self.rent_estimator = rent_estimator
    
    def calculate_roi(self):
        total_payment_value = 0
        monthly_payment_value = self.monthly_payment
        total_payment = self.monthly_payment*n
        for current_month in range(n):
            value_loss_rate = self.enflation_estimator[current_month]
            total_payment_value += monthly_payment_value
            monthly_payment_value *= value_loss_rate
        total_rent = 0
        total_rent_value = 0
        if rent_estimator:
            total_rent = rent_estimator.get_total_rent()
            total_rent_value = rent_estimator.get_total_rent_value()
        return self.monthly_payment, total_payment, total_payment_value, self.M/total_payment_value, (self.M+total_rent_value)/total_payment_value, total_rent, total_rent_value

enflation_estimator = EnflationEstimateYearly()
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
) = roi_calculator.calculate_roi()
print("monthly payment\t\t", monthly_payment)
print("total_payment\t\t", total_payment)
print("total_payment_value\t", total_payment_value)
print()
print("ROI(assuming home values with enflation)", ROI)
print("ROI_with_rent(assuming home values with enflation and rent increases yearly with enflation)", ROI_with_rent)
print()
print("total_rent\t\t", total_rent)
print(f"total_rent_value in {n} months", total_rent_value)
