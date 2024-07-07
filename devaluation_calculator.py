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
    def calculate_valuation(self, monthly_payment , payment_time):
        if type(monthly_payment) is int or type(monthly_payment) is float:
            total_paid_value = self.calculate_valuation_flat_payment(monthly_payment ,payment_time)
        if type(monthly_payment) is list:
            total_paid_value = self.calculate_valuation_payment_list(monthly_payment ,payment_time)
        return total_paid_value
    def calculate_monthly_valuation(self, monthly_payment , payment_time):
        total_paid_value = self.calculate_valuation(monthly_payment , payment_time)
        return total_paid_value/payment_time
    
    def calculate_value_and_rate(self, onetime_payment, monthly_payment , payment_time):
        total_paid_value = self.calculate_valuation(monthly_payment ,payment_time)
        rate = onetime_payment/total_paid_value - 1
        return total_paid_value, rate

    def onetime_vs_credit(self, onetime_payment, credit_payment , credit_payment_time):
        monthly_payment = credit_payment / credit_payment_time
        total_paid_value, rate = self.calculate_value_and_rate(onetime_payment, monthly_payment , credit_payment_time)
        print(f"total paid value: {total_paid_value}")
        print(f"credit gain rate: {rate}")
        state = '\033[1m' + ("\033[32mMORE" if rate>0 else "\033[31mLESS") + "\033[0m"
        value_diff = abs(total_paid_value - onetime_payment)
        value_diff = '\033[1m' + ("\033[32m" if rate>0 else "\033[31m") + str(value_diff) + "\033[0m"
        print(f'it is {state} valueable to buy in installments by {value_diff} in current value')


