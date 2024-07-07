from enflation_estimator import EnflationEstimateYearly
from rent_estimator import RentEstimatorInitialFlat


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
        total_payment = self.monthly_payment * self.n
        for current_month in range(self.n):
            value_loss_rate = self.enflation_estimator[current_month]
            total_payment_value += monthly_payment_value
            monthly_payment_value *= value_loss_rate
        total_rent = 0
        total_rent_value = 0
        if self.rent_estimator:
            total_rent = self.rent_estimator.get_total_rent()
            total_rent_value = self.rent_estimator.get_total_rent_value()
        return self.monthly_payment, total_payment, total_payment_value, self.M/total_payment_value, (self.M+total_rent_value)/total_payment_value, total_rent, total_rent_value
