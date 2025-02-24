import math

def empty_print(*args, **kwargs):
    pass

class Tax_Calculator:
    def __init__(
        self,
        current_income, # includes other income thats added to your tax bracket
        tax_brackets = [
            (158_000, 15),
            (330_000, 20),
            (800_000, 27),
            (4_300_000, 35),
            (math.inf, 40),
        ],
        debug = False
    ):
        self.current_income = current_income
        self.tax_brackets = tax_brackets
        for i, (tax_limit, tax_rate) in enumerate(tax_brackets):
            if self.current_income < tax_limit:
                self.tax_bracket_index = i
                break
        if debug:
            self.print = print
        else:
            self.print = empty_print
    
    def get_tax(self, coming_income):
        current_income = self.current_income
        tax = 0
        tax_bracket_index = self.tax_bracket_index
        flag = False
        while(coming_income):
            current_tax_limit, current_tax_rate = self.tax_brackets[tax_bracket_index]
            if coming_income >= current_tax_limit - current_income:
                taxable_income = current_tax_limit - current_income

                coming_income -= taxable_income
                current_income += taxable_income
                tax_bracket_index += 1
            else:
                taxable_income = coming_income
                flag = True
            
            current_tax = taxable_income * current_tax_rate / 100
            tax += current_tax
            self.print(f'{taxable_income} of it was taxed at {current_tax_rate}% which comes up to: {current_tax}')
            if flag:
                break
        return tax

    def get_post_income(self, income):
        tax = self.get_tax(income)
        return income - tax


############# example usage #############
calc = Tax_Calculator(720_000, debug=True)
print(calc.get_post_income(150_000))
#########################################
