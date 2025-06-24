import pandas as pd
import json

# Toggle flags for advanced calculations per product
toggles = {
    'Cars': False,
    'Robotaxi': False,
    'Optimus': False,
    'Energy': False,
    'Services': False,
    'Robotaxi Network': True
}

# Assumptions for Product Categories (2025 Base)
products = {
    'Cars': {
        'units_sold': 1800000,  # 1.8M vehicles for 2025
        'sale_price': 45000,    # Average selling price ($45,000)
        'gross_margin': 0.18,   # 18% gross margin
        'op_expense_ratio': 0.80,  # 80% of revenue (advanced only)
        'growth_rate': 0.05    # 5% annual unit growth
    },
    'Robotaxi': {
        'units_sold': 10000,    # 10K for 2025 (pre-production)
        'sale_price': 30000,    # Sale price per Robotaxi ($30,000)
        'gross_margin': 0.25,   # 25% gross margin
        'op_expense_ratio': 0.70,  # 70% of revenue (advanced only)
        'growth_rate': 0.50    # 50% annual unit growth
    },
    'Optimus': {
        'units_sold': 1000,     # 1K (pilot production)
        'sale_price': 20000,    # Sale price per Optimus ($20,000)
        'gross_margin': 0.30,   # 30% gross margin
        'op_expense_ratio': 0.70,  # 70% of revenue (advanced only)
        'growth_rate': 1.00    # 100% annual unit growth
    },
    'Energy': {
        'revenue': 15000,       # $15B for 2025
        'gross_margin': 0.30,   # 30% gross margin
        'op_expense_ratio': 0.20,  # 20% of revenue (advanced only)
        'growth_rate': 0.20    # 20% annual revenue growth
    },
    'Services': {
        'revenue': 10000,       # $10B for 2025
        'gross_margin': 0.15,   # 15% gross margin
        'op_expense_ratio': 0.30,  # 30% of revenue (advanced only)
        'growth_rate': 0.10    # 10% annual revenue growth
    }
}

# Assumptions for Robotaxi Network (2025 Base)
robotaxi_network = {
    'network_vehicles': 8000,        # 8K (early network)
    'miles_per_car': 50000,         # Miles at 100% utilization
    'rider_pays_per_mile': 1.00,    # Rider pays $1.00/mile
    'car_owner_cut_per_mile': 0.60, # Car owner gets $0.60/mile
    'tesla_cut_per_mile': 0.40,    # Tesla gets $0.40/mile
    'operating_cost_per_mile': 0.42, # Operating cost ($/mile, advanced only)
    'utilization_rate': 0.50,      # 50% utilization (advanced only)
    'vehicle_growth_rate': 1.00,   # 100% annual vehicle growth
    'cost_reduction_rate': 0.05,   # 5% annual cost reduction
    'utilization_growth_rate': 0.0234  # Reach 70% by 2035
}

# Assumptions for Market Cap Calculation
net_profit_margin = 0.08  # 8% net margin (based on 2024's 8.2%)
base_shares_outstanding = 3220  # 3.22B shares (June 2025)
shares_growth_rate = 0.01  # 1% annual dilution
pe_ratios = {
    'Conservative': 100,
    'Current': 191.60,  # TTM P/E as of June 23, 2025
    'Optimistic': 250,
    'Bullish': 350
}
years = list(range(2025, 2036))  # 2025 to 2035

# Initialize yearly results
yearly_results = []

for year in years:
    # Calculate shares outstanding
    shares_outstanding = base_shares_outstanding * (1 + shares_growth_rate) ** (year - 2025)

    # Calculate product revenues
    product_results = []
    total_product_revenue = 0
    revenue_breakdown = []
    for product, data in products.items():
        if product in ['Cars', 'Robotaxi', 'Optimus']:
            units_sold = data['units_sold'] * (1 + data['growth_rate']) ** (year - 2025)
            revenue = units_sold * data['sale_price']
        else:
            revenue = data['revenue'] * (1 + data['growth_rate']) ** (year - 2025) * 1e6  # Convert $B to $M
        if toggles[product]:
            op_expenses = revenue * data['op_expense_ratio']
            net_revenue = revenue - op_expenses
            gross_profit = net_revenue * data['gross_margin']
        else:
            net_revenue = revenue
            gross_profit = revenue * data['gross_margin']
        total_product_revenue += net_revenue
        product_results.append({
            'Product': product,
            'Units Sold': units_sold if product in ['Cars', 'Robotaxi', 'Optimus'] else '-',
            'Sale Price ($)': data['sale_price'] if product in ['Cars', 'Robotaxi', 'Optimus'] else '-',
            'Gross Margin (%)': data['gross_margin'] * 100,
            'Revenue ($M)': net_revenue / 1e6,
            'Gross Profit ($M)': gross_profit / 1e6,
            'Operating Expenses ($M)' if toggles[product] else None: op_expenses / 1e6 if toggles[product] else None
        })
        revenue_breakdown.append({
            'Category': product,
            'Revenue ($M)': net_revenue / 1e6
        })

    # Calculate Robotaxi Network Earnings
    network_vehicles = robotaxi_network['network_vehicles'] * (1 + robotaxi_network['vehicle_growth_rate']) ** (year - 2025)
    operating_cost_per_mile = robotaxi_network['operating_cost_per_mile'] * (1 - robotaxi_network['cost_reduction_rate']) ** (year - 2025)
    utilization_rate = min(0.70, robotaxi_network['utilization_rate'] * (1 + robotaxi_network['utilization_growth_rate']) ** (year - 2025))
    if toggles['Robotaxi Network']:
        utilized_miles_per_car = robotaxi_network['miles_per_car'] * utilization_rate
        total_miles = network_vehicles * utilized_miles_per_car
        gross_revenue = total_miles * robotaxi_network['rider_pays_per_mile']
        car_owner_earnings = total_miles * robotaxi_network['car_owner_cut_per_mile']
        tesla_gross_earnings = total_miles * robotaxi_network['tesla_cut_per_mile']
        operating_costs = total_miles * operating_cost_per_mile
        tesla_net_earnings = tesla_gross_earnings - operating_costs
        robotaxi_results = {
            'Network Vehicles': network_vehicles,
            'Miles per Car (Utilized)': utilized_miles_per_car,
            'Utilization Rate (%)': utilization_rate * 100,
            'Rider Pays per Mile ($)': robotaxi_network['rider_pays_per_mile'],
            'Car Owner Cut per Mile ($)': robotaxi_network['car_owner_cut_per_mile'],
            'Tesla Cut per Mile ($)': robotaxi_network['tesla_cut_per_mile'],
            'Operating Cost per Mile ($)': operating_cost_per_mile,
            'Gross Revenue ($M)': gross_revenue / 1e6,
            'Car Owner Earnings ($M)': car_owner_earnings / 1e6,
            'Tesla Gross Earnings ($M)': tesla_gross_earnings / 1e6,
            'Operating Costs ($M)': operating_costs / 1e6,
            'Tesla Net Earnings ($M)': tesla_net_earnings / 1e6
        }
        tesla_earnings = tesla_net_earnings
    else:
        total_miles = network_vehicles * robotaxi_network['miles_per_car']
        tesla_earnings = total_miles * robotaxi_network['tesla_cut_per_mile']
        robotaxi_results = {
            'Network Vehicles': network_vehicles,
            'Miles per Car': robotaxi_network['miles_per_car'],
            'Rider Pays per Mile ($)': robotaxi_network['rider_pays_per_mile'],
            'Car Owner Cut per Mile ($)': robotaxi_network['car_owner_cut_per_mile'],
            'Tesla Cut per Mile ($)': robotaxi_network['tesla_cut_per_mile'],
            'Tesla Earnings per Year ($M)': tesla_earnings / 1e6
        }

    # Add Robotaxi Network to revenue breakdown
    revenue_breakdown.append({
        'Category': 'Robotaxi Network',
        'Revenue ($M)': tesla_earnings / 1e6
    })

    # Calculate Total Company Revenue
    total_company_revenue = total_product_revenue + tesla_earnings

    # Calculate Market Capitalization
    net_income = total_company_revenue * net_profit_margin
    market_cap_results = []
    for scenario, pe_ratio in pe_ratios.items():
        market_cap = net_income * pe_ratio
        market_cap_results.append({
            'Scenario': scenario,
            'P/E Ratio': pe_ratio,
            'Net Income ($M)': net_income / 1e6,
            'Market Cap ($B)': market_cap / 1e9,
            'Stock Price ($)': market_cap / (shares_outstanding * 1e6)
        })

    # Store yearly results
    yearly_results.append({
        'Year': year,
        'product_valuation': product_results,
        'robotaxi_network': robotaxi_results,
        'revenue_breakdown': revenue_breakdown,
        'total_revenue_million': total_company_revenue / 1e6,
        'market_cap': market_cap_results
    })

# Prepare JSON output for website
output = {'yearly_results': yearly_results}

# Output Results (2025 and 2035 for brevity)
for result in yearly_results:
    if result['Year'] in [2025, 2035]:
        print(f"\n=== Year {result['Year']} ===")
        print("Product Valuation Results:")
        df_products = pd.DataFrame(result['product_valuation'])
        print(df_products.to_string(index=False))
        print("\nRobotaxi Network Earnings:")
        df_robotaxi = pd.DataFrame([result['robotaxi_network']])
        print(df_robotaxi.to_string(index=False))
        print("\nTotal Company Revenue Breakdown:")
        df_breakdown = pd.DataFrame(result['revenue_breakdown'])
        print(df_breakdown.to_string(index=False))
        print(f"\nTotal Company Revenue: ${result['total_revenue_million']:.2f} million")
        print("\nMarket Capitalization Results:")
        df_market_cap = pd.DataFrame(result['market_cap'])
        print(df_market_cap.to_string(index=False))

print("\nJSON Output for Website (first and last years for brevity):")
print(json.dumps([output['yearly_results'][0], output['yearly_results'][-1]], indent=4))