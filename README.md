# ROI-calculator
This is my own return on investment calculator. It is quite basic and for my own use. Just putting it here so that I dont recode it every time.

Since Some of my friends asked me to add a main.py I have added it. I am sharing how to use it below:

# How to use
1. Go into main.py
2. Go to variables section
3. Choose the operaiton you want
   1. ROI_CALCULATOR (Used for calculating the gained profit from buying a home) 
   2. VALUATION_CALCULATOR (used for finding best payment option)
   3. BOTH_CALCULATORS 
4. Change the variables for your operation
5. Don't forget to change enflation estimator list to your estimations esspecially if you are not living in a high enflation country. 
6. run main.py
```
python3 main.py
```

## important note:
* The default estimations for yearly enflation are quite high first year being %60. This is because in turkey this is the current enflation rate. Thats why if u live somewhere else Deinitely set enflation estimator lists in variables to your own rates. This is the default estimation list. Change it in variables and make sure it has number_of_months/12 amount of enflation estimations to make sure it works:  
[1.6, 1.4, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1]
* There are more functionalities I use with devalution calculator. And I was too lazy to add it into main.py If u are interested u can check devaluation calculator and look it up to use it.
