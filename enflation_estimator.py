class EnflationEstimateYearly:
    enflation_estimation_list = [
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
    def __init__(self, enflation_estimation_list=[]):
        if enflation_estimation_list:
            self.enflation_estimator_list = enflation_estimation_list
        self.value_loss_rate_list = [1/i**(1/12) for i in self.enflation_estimation_list]
    def __getitem__(self, month):
        index = month//12
        try:
            return self.value_loss_rate_list[index]
        except:
            raise Exception(f'there are only {len(value_loss_rate_list)*12} months of value. You asked for month {month}')
    def get_yearly_enflation_list(self):
        return self.enflation_estimation_list
