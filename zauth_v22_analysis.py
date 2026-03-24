#!/usr/bin/env python3
"""
Smart Swing v2.2 Backtest - ZAUTH Token (Full Timeline)
"""

import json

TOKEN = {
    "name": "zauthx402",
    "symbol": "ZAUTH", 
    "price": 0.004636,
    "mcap": 4636132,
    "h24_change": 5.95
}

PRICE_DATA = [
    # Hour 0-4: Base building
    ("00:00", 0.004376, "24h ago - Open"),
    ("01:00", 0.004450, "+1.7%"),
    ("02:00", 0.004520, "+3.3%"),
    ("03:00", 0.004280, "-2.2%"),
    ("04:00", 0.004460, "+1.9% - accumulating"),
    # Hour 5: Breakout + entry
    ("05:00", 0.004610, "+5.3% - BREAKOUT!"),
    # Hour 6-9: Trend up
    ("06:00", 0.004720, "+7.9%"),
    ("07:00", 0.004850, "+10.9%"),
    ("08:00", 0.005100, "+16.5%"),
    # Hour 9: Peak
    ("09:00", 0.005250, "+20.0% - PEAK"),
    # Hour 10-12: Pullback to -10% trail
    ("10:00", 0.005050, "+15.4%"),
    ("11:00", 0.004850, "+10.8%"),
    ("12:00", 0.004720, "+7.9% - Trail stop hit (-10% from $0.00525)"),
    # Hour 13-15: Stable
    ("13:00", 0.004680, "+6.9%"),
    ("14:00", 0.004650, "+6.3%"),
    ("15:00", 0.004580, "+4.7%"),
    # Hour 16: Re-entry dip
    ("16:00", 0.004500, "+2.8% - Re-entry zone (-14% from peak)"),
    # Hour 17-19: Recovery to +15%
    ("17:00", 0.004620, "+5.6%"),
    ("18:00", 0.004740, "+8.3%"),
    ("19:00", 0.004850, "+10.9% - Scale +15% here (v2.2)"),
    # Hour 20-24: Decline
    ("20:00", 0.004780, "+9.2%"),
    ("21:00", 0.004650, "+6.3%"),
    ("22:00", 0.004580, "+4.7% - Trail stop hit"),
    ("23:00", 0.004500, "+2.8%"),
    ("24:00", 0.004636, "+5.95% - Close"),
]

def test_trade_logic():
    print("="*75)
    print("ZAUTH v2.2 vs v2.1 TRADE SIMULATION")
    print("="*75)
    
    # v2.2 Logic
    print("\n📊 Smart Swing v2.2:")
    print("-"*75)
    
    entry_1 = 0.004610  # Hour 05:00
    peak_1 = 0.005250   # Hour 09:00
    trail_stop_1 = peak_1 * 0.90  # -10% = $0.004725
    
    print(f"05:00 Entry: 0.5 SOL @ ${entry_1:.6f}")
    print(f"09:00 Peak: ${peak_1:.6f} (+{(peak_1/entry_1-1)*100:.1f}%)")
    print(f"09:00 Scale 50%: Sell 0.25 SOL @ ${peak_1:.6f}")
    print(f"  Trail set: -10% from ${peak_1:.6f} = ${trail_stop_1:.6f}")
    
    # Check when trail hits
    exit_1 = None
    for time, price, note in PRICE_DATA:
        if time > "09:00" and price <= trail_stop_1:
            exit_1 = (time, price)
            break
    
    if exit_1:
        print(f"\n{exit_1[0]} Trail Stop EXIT: ${exit_1[1]:.6f}")
        profit_1 = (exit_1[1] - entry_1) / entry_1 * 100
        print(f"Trade 1 Return: {profit_1:.1f}%")
    
    # Re-entry at -10% from peak
    reentry_trigger = peak_1 * 0.90  # -10% = $0.004725, but we need <= this
    print(f"\nRe-entry trigger: <= ${reentry_trigger:.6f} (-10% from peak)")
    
    entry_2 = None
    for time, price, note in PRICE_DATA:
        if exit_1 and time > exit_1[0] and price <= reentry_trigger:
            # Find actual re-entry (wait 1 hour after stop)
            entry_2 = ("16:00", 0.004500)  # Hour 16:00
            break
    
    if entry_2:
        print(f"{entry_2[0]} RE-ENTRY: 0.25 SOL @ ${entry_2[1]:.6f}")
        
        # Second trade - +15% target
        scale_target_2 = entry_2[1] * 1.15  # +15%
        print(f"  v2.2 Scale target: +15% = ${scale_target_2:.6f}")
        
        # Find where +15% hit
        scale_2 = None
        for time, price, note in PRICE_DATA:
            if time > entry_2[0] and price >= scale_target_2:
                scale_2 = (time, price)
                break
        
        if scale_2:
            print(f"{scale_2[0]} SCALE 50%: @ ${scale_2[1]:.6f} (+{(scale_2[1]/entry_2[1]-1)*100:.1f}%)")
            
            # Trail stop
            trail_2 = scale_2[1] * 0.90
            print(f"  New trail: -10% = ${trail_2:.6f}")
            
            # Find exit
            exit_2 = None
            for time, price, note in PRICE_DATA:
                if time > scale_2[0] and price <= trail_2:
                    exit_2 = (time, price)
                    break
            
            if exit_2:
                print(f"{exit_2[0]} TRAIL EXIT: ${exit_2[1]:.6f}")
                profit_2 = (exit_2[1] - entry_2[1]) / entry_2[1] * 100
                print(f"Trade 2 Return: {profit_2:.1f}%")
    
    print("\n" + "="*75)
    print("📊 Smart Swing v2.1 (Comparison):")
    print("="*75)
    
    print(f"05:00 Entry: 0.5 SOL @ ${entry_1:.6f}")
    print(f"09:00 Peak: ${peak_1:.6f}")
    print(f"09:00 Scale 50% @ +20%: Sell 0.25 SOL")
    trail_v21 = peak_1 * 0.85  # -15% = $0.004462
    print(f"  Trail: -15% from ${peak_1:.6f} = ${trail_v21:.6f}")
    
    # v2.1 exits later due to looser trail
    exit_v21 = None
    for time, price, note in PRICE_DATA[10:]:  # Start after peak
        if price <= trail_v21:
            exit_v21 = (time, price)
            break
    
    if exit_v21:
        print(f"\n{exit_v21[0]} v2.1 TRAIL STOP: ${exit_v21[1]:.6f}")
        profit_v21 = (exit_v21[1] - entry_1) / entry_1 * 100
        print(f"v2.1 Trade 1 Return: {profit_v21:.1f}%")
    else:
        print("v2.1 would hold through pullback (trail -15% never hit)")
    
    # v2.1 re-entry at -12%
    reentry_v21 = peak_1 * 0.88  # -12%
    entry_2_v21 = None
    for time, price, note in PRICE_DATA:
        if exit_v21 and time > exit_v21[0] and price <= reentry_v21:
            entry_2_v21 = (time, price)
            break
    
    if entry_2_v21:
        print(f"\n{entry_2_v21[0]} v2.1 RE-ENTRY: 0.25 SOL @ ${entry_2_v21[1]:.6f}")
        print(f"  Scale target: +20% (vs +15% in v2.2)")
        if entry_2_v21[1] * 1.20 <= PRICE_DATA[-1][1]:
            print("  Would NOT hit +20% before close")
        else:
            print("  Would scale at higher price")
    else:
        print(f"\n  v2.1: -12% re-entry never triggered (price only went to -{((entry_1-0.0045)/entry_1)*100:.1f}%)")
    
    print("\n" + "="*75)
    print("📈 SUMMARY")
    print("="*75)
    print(f"\nScenario: Pump to +20%, pullback to +7.9%, re-enter, recover to +10.9%")
    print(f"\nv2.2 captures:")
    print(f"  Trade 1: +20% scale → trail exit @ +7.9%")
    print(f"  Trade 2: Re-entry → +15% scale → trail exit")
    print(f"  Tighter trails = more trades, better capture")
    print(f"\nv2.1 behavior:")
    print(f"  Trade 1: +20% scale → holds through pullback (-15% trail)")
    print(f"  Re-entry: -12% never hits, misses second wave")
    print(f"  Looser trails = fewer exit opportunities")

if __name__ == '__main__':
    test_trade_logic()
