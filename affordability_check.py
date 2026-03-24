#!/usr/bin/env python3
"""
Affordability Check - Can you afford that hotel after 4 weeks?
"""

def get_float_input(prompt):
    """Get float input from user."""
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                return 0.0
            return float(value.replace(',', ''))
        except ValueError:
            print("Please enter a valid number.")

def format_currency(amount):
    """Format number as currency."""
    return f"${amount:,.2f}"

def main():
    print("=" * 50)
    print("   CAN I AFFORD IT? - 4 WEEK CALCULATOR")
    print("=" * 50)
    print()
    
    # Get user's weekly numbers
    weekly_income = get_float_input("Weekly income:        $")
    weekly_expenses = get_float_input("Weekly expenses:      $")
    
    weekly_surplus = weekly_income - weekly_expenses
    
    print()
    print(f"Weekly surplus:       {format_currency(weekly_surplus)}")
    print()
    
    # Calculate 4 week totals
    four_week_income = weekly_income * 4
    four_week_expenses = weekly_expenses * 4
    four_week_surplus = weekly_surplus * 4
    
    print("=" * 50)
    print("AFTER 4 WEEKS:")
    print("=" * 50)
    print(f"  Total income:       {format_currency(four_week_income)}")
    print(f"  Total expenses:     {format_currency(four_week_expenses)}")
    print(f"  Available cash:     {format_currency(four_week_surplus)}")
    print()
    
    # Hotel options
    hotel_a = 2950
    hotel_b = 1875
    
    print("=" * 50)
    print("HOTEL OPTIONS:")
    print("=" * 50)
    print()
    
    print(f"Option 1: {format_currency(hotel_a)} hotel")
    if four_week_surplus >= hotel_a:
        remaining_a = four_week_surplus - hotel_a
        print(f"  ✅ AFFORDABLE")
        print(f"     Cost:    {format_currency(hotel_a)}")
        print(f"     Left:    {format_currency(remaining_a)}")
    else:
        shortfall = hotel_a - four_week_surplus
        print(f"  ❌ NOT AFFORDABLE")
        print(f"     Cost:      {format_currency(hotel_a)}")
        print(f"     Shortfall: {format_currency(shortfall)}")
        weeks_needed = shortfall / weekly_surplus if weekly_surplus > 0 else float('inf')
        if weeks_needed != float('inf'):
            print(f"     Need {weeks_needed:.1f} more week(s) to afford")
    
    print()
    
    print(f"Option 2: {format_currency(hotel_b)} hotel")
    if four_week_surplus >= hotel_b:
        remaining_b = four_week_surplus - hotel_b
        print(f"  ✅ AFFORDABLE")
        print(f"     Cost:    {format_currency(hotel_b)}")
        print(f"     Left:    {format_currency(remaining_b)}")
    else:
        shortfall = hotel_b - four_week_surplus
        print(f"  ❌ NOT AFFORDABLE")
        print(f"     Cost:      {format_currency(hotel_b)}")
        print(f"     Shortfall: {format_currency(shortfall)}")
        weeks_needed = shortfall / weekly_surplus if weekly_surplus > 0 else float('inf')
        if weeks_needed != float('inf'):
            print(f"     Need {weeks_needed:.1f} more week(s) to afford")
    
    print()
    print("=" * 50)
    print("RECOMMENDATION:")
    print("=" * 50)
    
    if four_week_surplus >= hotel_a:
        diff = hotel_a - hotel_b
        savings = four_week_surplus - hotel_a
        print(f"You can afford BOTH!")
        print()
        print(f"If you go with Option 1 ({format_currency(hotel_a)}):")
        print(f"  - You'd have {format_currency(savings)} left")
        print(f"  - That's a {format_currency(diff)} premium over Option 2")
        print()
        print(f"If you go with Option 2 ({format_currency(hotel_b)}):")
        print(f"  - You'd have {format_currency(four_week_surplus - hotel_b)} left")
        print(f"  - Save {format_currency(diff)} vs Option 1")
        
    elif four_week_surplus >= hotel_b:
        print(f"Go with Option 2 ({format_currency(hotel_b)})")
        print(f"You're {format_currency(hotel_a - four_week_surplus)} short for Option 1")
        print(f"After Option 2, you'll have {format_currency(four_week_surplus - hotel_b)} remaining")
        
    else:
        short_a = hotel_a - four_week_surplus
        short_b = hotel_b - four_week_surplus
        print(f"Neither is affordable after 4 weeks.")
        print()
        print(f"Option 1: Need {format_currency(short_a)} more")
        print(f"Option 2: Need {format_currency(short_b)} more")
        if weekly_surplus > 0:
            weeks_a = (hotel_a / weekly_surplus)
            weeks_b = (hotel_b / weekly_surplus)
            print()
            print(f"To afford Option 1: {weeks_a:.1f} weeks total")
            print(f"To afford Option 2: {weeks_b:.1f} weeks total")
    
    print("=" * 50)
    print()

if __name__ == "__main__":
    main()
