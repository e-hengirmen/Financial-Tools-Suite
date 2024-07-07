from enflation_estimator import EnflationEstimateFlat, EnflationEstimateYearly

class Devaluation_Calculator:
    def __init__(self, enflation_estimator=EnflationEstimateYearly()):
        self.enflation_estimator = enflation_estimator

    def calculate_valuation_flat_payment(self, monthly_pay, payment_time):
        total_paid_value = 0
        current_rate = 1
        for month in range(payment_time):
            value_loss_rate = self.enflation_estimator[month]
            total_paid_value += current_rate * monthly_pay
            current_rate *= value_loss_rate
        return total_paid_value

    def calculate_valuation_payment_list(self, monthly_payment_list, payment_time):
        total_paid_value = 0
        current_rate = 1
        for month in range(payment_time):
            monthly_pay = monthly_payment_list[month]
            value_loss_rate = self.enflation_estimator[month]
            total_paid_value += current_rate * monthly_pay
            current_rate *= value_loss_rate
        return total_paid_value
    def calculate_valuation(self, M2, payment_time):
        if type(M2) is int:
            total_paid_value = self.calculate_valuation_flat_payment(M2,payment_time)
        if type(M2) is list:
            total_paid_value = self.calculate_valuation_payment_list(M2,payment_time)
        return total_paid_value
    
    def calculate_value_and_rate(self, M1, M2, payment_time):
        total_paid_value = self.calculate_valuation(M2,payment_time)
        rate = M1/total_paid_value - 1
        return total_paid_value, rate



