class RentEstimatorInitialFlat:
    def __init__(self, rent, n, sell_after, enflation_estimator):
        self.n = n
        self.rent = rent
        self.enflation_estimator = enflation_estimator
        self.yearly_rent_list = [self.rent]
        self.sell_after = sell_after
        if sell_after is None:
            self.sell_after = self.n // 12
        current_rent = self.rent
        for yearly_enflation in enflation_estimator.get_yearly_enflation_list()[:-1]:
            current_rent *= yearly_enflation
            self.yearly_rent_list.append(current_rent)

    def get_total_rent(self):
        return 12 * sum(self.yearly_rent_list[:self.sell_after])
    
    def get_total_rent_value(self):
        total_rent_value = 0
        for year in range(self.sell_after):
            current_rent_value = self.rent
            value_loss_rate = self.enflation_estimator[year*12]
            for month in range(12):
                total_rent_value += current_rent_value
                current_rent_value *= value_loss_rate
        return total_rent_value
