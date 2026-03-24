#!/usr/bin/env python3
"""
Budget Calculator - Weekly income vs expenses
"""

def get_float_input(prompt):
    """Get float input from user with basic validation."""
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
    print("        BUDGET CALCULATOR")
    print("=" * 50)
    print()
    
    # Income
    print("📥 INCOME (Weekly)")
    print("-" * 30)
    weekly_income = get_float_input("Weekly income: $")
    print()
    
    # Expenses
    print("📤 EXPENSES")
    print("-" * 30)
    print("(Enter 0 or press Enter to skip)")
    print()
    
    rent = get_float_input("  Rent:              $")
    car = get_float_input("  Car payments:      $")
    registration = get_float_input("  Car registration:  $")
    flights = get_float_input("  Flights:           $")
    groceries = get_float_input("  Groceries:         $")
    accommodation = get_float_input("  Accommodation:     $")
    other = get_float_input("  Other expenses:    $")
    
    # Calculate totals
    total_expenses = rent + car + registration + flights + groceries + accommodation + other
    remaining = weekly_income - total_expenses
    
    # Monthly projections
    monthly_income = weekly_income * 4.33  # Average weeks per month
    monthly_expenses = total_expenses * 4.33
    monthly_remaining = monthly_income - monthly_expenses
    
    # Display results
    print()
    print("=" * 50)
    print("        BUDGET BREAKDOWN")
    print("=" * 50)
    print()
    print("WEEKLY:")
    print(f"  Income:     {format_currency(weekly_income):>12}")
    print(f"  Expenses:   {format_currency(total_expenses):>12}")
    print(f"  Remaining:  {format_currency(remaining):>12}")
    print()
    
    print("MONTHLY (approx):")
    print(f"  Income:     {format_currency(monthly_income):>12}")
    print(f"  Expenses:   {format_currency(monthly_expenses):>12}")
    print(f"  Remaining:  {format_currency(monthly_remaining):>12}")
    print()
    
    # Expense breakdown
    print("EXPENSE BREAKDOWN:")
    expenses_list = [
        ("Rent", rent),
        ("Car", car),
        ("Registration", registration),
        ("Flights", flights),
        ("Groceries", groceries),
        ("Accommodation", accommodation),
        ("Other", other),
    ]
    
    for name, amount in expenses_list:
        if amount > 0:
            pct = (amount / weekly_income * 100) if weekly_income > 0 else 0
            print(f"  {name:<15} {format_currency(amount):>12} ({pct:5.1f}%)")
    
    print()
    print("=" * 50)
    
    # Status
    if remaining > 0:
        print(f"✅ SURPLUS: {format_currency(remaining)} per week")
    elif remaining < 0:
        print(f"❌ DEFICIT: {format_currency(abs(remaining))} per week")
    else:
        print("⚖️  BREAK EVEN")
    
    print("=" * 50)
    print()
    
    # Savings potential
    if remaining > 0:
        yearly_savings = remaining * 52
        print(f"💰 If you save your surplus: {format_currency(yearly_savings)} per year")
        print()

if __name__ == "__main__":
    main()
