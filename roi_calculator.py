from .enflation_estimator.py import EnflationEstimateYearly

M=3000000  # initil credit
n=120      # months
r=1.0069   # interest rate

class ROICalculator:
  
    def __init__(self, M, n, r, enflation_estimator):
        self.monthly_payment = M * r**n * (r-1)/(r**n-1)
        self.M = M
        self.n = n
        self.enflation_estimator = enflation_estimator
    
    def calculate_roi(self):
        total_payment_value = 0
        monthly_payment_value = self.monthly_payment
        total_payment = self.monthly_payment*n
        for current_month in range(n):
            value_loss_rate = self.enflation_estimator[current_month]
            total_payment_value += monthly_payment_value
            monthly_payment_value *= value_loss_rate
        return self.monthly_payment, total_payment, total_payment_value, self.M/total_payment_value

enflation_estimator = EnflationEstimateYearly()
roi_calculator = ROICalculator(M,n,r,enflation_estimator)
monthly_payment, total_payment, total_payment_value, ROI = roi_calculator.calculate_roi()
print("monthly payment\t\t", monthly_payment)
print("total_payment\t\t", total_payment)
print("total_payment_value\t", total_payment_value)
print("ROI(assuming home values with enflation)", ROI)
