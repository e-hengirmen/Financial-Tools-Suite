initial_usd_rent_monthly = 1000
years = 3
initial_tl_rent_monthly = 46650

dollar_inf_cases = [1.0402, 1.0276, 1.015]


dolar_fiyatlari = [
    42.9613,
    35.2803,
    29.4382,
    18.6983,
    13.3290,
    7.43,
    5.9402
]


tl_inflations = [
    1.1497,
    1.4869,
    1.5768,
    1.6486,
    1.4212,
    1.3065,
]
dolar_changes = []
for sonraki,onceki in zip(dolar_fiyatlari[:-1],dolar_fiyatlari[1:]):
    print(sonraki,onceki)
    dolar_changes.append(sonraki/onceki)

dolar_changes.reverse()

tl_inflations.append(tl_inflations[-1])
dolar_changes.append(dolar_changes[-1])


print("2021 dan 2026ya dolar artisi: ",dolar_changes)
print("2021 dan 2026ya tl enflasyonu: ",tl_inflations)



def compare(years, tl_inf_cases,growth_rates, dollar_rent, dollar_rate):
    dollar_rent_sum = dollar_rent*12*years

    current_tl_rent = dollar_rent*dollar_rate
    tl_rent_sum = 0
    for yearly_tl_inf,dollar_growth_rate in zip(tl_inf_cases, growth_rates):
        d_growth = dollar_growth_rate**(1/12)
        current_tl_rent *= yearly_tl_inf
        for month in range(12):
            tl_rent_sum += current_tl_rent/dollar_rate
            dollar_rate *= d_growth
    return dollar_rent_sum, tl_rent_sum

def compare_with_yearly_inflation(years, tl_inf_cases, growth_rates, dollar_rent, initial_dollar_rate):
    dollar_rent_sum = dollar_rent * 12 * years
    tl_rent_sum_converted_to_usd = 0
    
    current_tl_rent = dollar_rent * initial_dollar_rate
    current_dollar_rate = initial_dollar_rate
    for year_idx in range(years):
        
        d_growth = growth_rates[year_idx] ** (1 / 12)
        if year_idx > 0:
            current_tl_rent *= tl_inf_cases[year_idx - 1]
        for month in range(12):
            tl_rent_sum_converted_to_usd += current_tl_rent / current_dollar_rate
            current_dollar_rate *= d_growth
            
    return dollar_rent_sum, tl_rent_sum_converted_to_usd


"""
for i in range(len(tl_inflations)-2):
    tl_inf_cases = tl_inflations[i:i+3]
    usd_annual_growth = dolar_changes[i:i+3]
    d,tl = compare_with_yearly_inflation(3, tl_inf_cases,usd_annual_growth,1000,46.65)
    print()
    print()
    print()
    print()
    print(usd_annual_growth)
    print(tl_inf_cases)
    print(f"dolar(dolar cinsinden): {d}")
    print(f"tl(dolar cinsinden): {tl}")

print()

tl_inf_cases = [1.1,1.1,1.1]
usd_annual_growth = [1.2,1.2,1.2]
d,tl = compare_with_yearly_inflation(3, tl_inf_cases,usd_annual_growth,1000,46.65)
print()
print()
print()
print()
print(usd_annual_growth)
print(tl_inf_cases)
print(f"dolar(dolar cinsinden): {d}")
print(f"tl(dolar cinsinden): {tl}")

print()
"""



tl_inf_cases = [1.4212, 1.3065, 1.3065]
usd_annual_growth = [1.1984530304162617, 1.217713568195282, 1.217713568195282]
d,tl = compare_with_yearly_inflation(3, tl_inf_cases,usd_annual_growth,1000,46.65)
print()
print()
print()
print()
print(usd_annual_growth)
print(tl_inf_cases)
print(f"dolar(dolar cinsinden): {d}")
print(f"tl(dolar cinsinden): {tl}")
