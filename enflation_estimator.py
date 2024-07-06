class EnflationEstimateYearly:
    value_loss_rate_list = [
        1.6,
        1.4,
        1.1,
        1.1,
        1.1,
        1.1,
        1.1,
        1.1,
        1.1,
        1.1,
        1.1,
        1.1,
        1.1,
        1.1,
        1.1,
    ]
    def __init__(self, enflation_estimator_list=[]):
        if enflation_estimator_list:
            self.value_loss_rate_list = enflation_estimator_list
        self.value_loss_rate_list = [1/i**(1/12) for i in self.value_loss_rate_list]
    def get_value_loss(month):
        index = month//12
        return value_loss_rate_list[index]
