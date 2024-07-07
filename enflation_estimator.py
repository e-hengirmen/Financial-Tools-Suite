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
            self.enflation_estimation_list = enflation_estimation_list
        self.value_loss_rate_list = [1/i**(1/12) for i in self.enflation_estimation_list]
    def __getitem__(self, month):
        index = month//12
        try:
            return self.value_loss_rate_list[index]
        except:
            raise Exception(f'there are only {len(self.value_loss_rate_list)*12} months of value. You asked for month {month}')
    def get_yearly_enflation_list(self):
        return self.enflation_estimation_list

class EnflationEstimateFlat:
    def __init__(self, enflation_estimate=1.1):
        self.enflation_estimate = enflation_estimate
        self.value_loss_rate = 1/enflation_estimate**(1/12)
    def __getitem__(self, month):
        return self.value_loss_rate
    def get_yearly_enflation_list(self):
        return [self.enflation_estimate for i in range(15)]
