import streamlit as st
import pandas as pd
import json

def human_format(num, precision=2):
    """Convert a number to a human-readable string (e.g., 1.2M, 3.4B). For $ amounts < 1M, use commas."""
    if num is None or num == '-' or pd.isnull(num):
        return num
    try:
        num = float(num)
    except Exception:
        return num
    abs_num = abs(num)
    if abs_num >= 1_000_000_000:
        return f"{num/1_000_000_000:.{precision}f}B"
    elif abs_num >= 1_000_000:
        return f"{num/1_000_000:.{precision}f}M"
    elif abs_num >= 1_000:
        return f"{num/1_000:.{precision}f}K"
    else:
        return f"{int(round(num)):,}"

def run_valuation(user_inputs):
    # Unpack user inputs
    products = user_inputs['products']
    robotaxi_network = user_inputs['robotaxi_network']
    toggles = user_inputs['toggles']
    net_profit_margin = user_inputs['net_profit_margin']
    base_shares_outstanding = user_inputs['base_shares_outstanding']
    shares_growth_rate = user_inputs['shares_growth_rate']
    pe_ratios = user_inputs['pe_ratios']
    years = user_inputs['years']

    yearly_results = []
    for year in years:
        shares_outstanding = base_shares_outstanding * (1 + shares_growth_rate) ** (year - years[0])
        product_results = []
        total_product_revenue = 0
        revenue_breakdown = []
        for product, data in products.items():
            if product in ['Cars', 'Robotaxi', 'Optimus']:
                units_sold = data['units_sold'] * (1 + data['growth_rate']) ** (year - years[0])
                revenue = units_sold * data['sale_price']
            else:
                revenue = data['revenue'] * (1 + data['growth_rate']) ** (year - years[0]) * 1e6
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

        # Robotaxi Network
        network_vehicles = robotaxi_network['network_vehicles'] * (1 + robotaxi_network['vehicle_growth_rate']) ** (year - years[0])
        operating_cost_per_mile = robotaxi_network['operating_cost_per_mile'] * (1 - robotaxi_network['cost_reduction_rate']) ** (year - years[0])
        utilization_rate = min(0.70, robotaxi_network['utilization_rate'] * (1 + robotaxi_network['utilization_growth_rate']) ** (year - years[0]))
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

        revenue_breakdown.append({
            'Category': 'Robotaxi Network',
            'Revenue ($M)': tesla_earnings / 1e6
        })

        total_company_revenue = total_product_revenue + tesla_earnings
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

        yearly_results.append({
            'Year': year,
            'product_valuation': product_results,
            'robotaxi_network': robotaxi_results,
            'revenue_breakdown': revenue_breakdown,
            'total_revenue_million': total_company_revenue / 1e6,
            'market_cap': market_cap_results
        })
    return {'yearly_results': yearly_results}

# --- Streamlit UI ---
st.set_page_config(page_title="Tesla Stock Valuation Simulator", layout="wide")
st.title("Tesla Stock Valuation Simulator")

st.sidebar.header("Adjust Assumptions")

# Default values (from your script)
default_products = {
    'Cars': {
        'units_sold': 1800000,
        'sale_price': 45000,
        'gross_margin': 0.18,
        'op_expense_ratio': 0.80,
        'growth_rate': 0.05
    },
    'Robotaxi': {
        'units_sold': 10000,
        'sale_price': 30000,
        'gross_margin': 0.25,
        'op_expense_ratio': 0.70,
        'growth_rate': 0.50
    },
    'Optimus': {
        'units_sold': 1000,
        'sale_price': 20000,
        'gross_margin': 0.30,
        'op_expense_ratio': 0.70,
        'growth_rate': 1.00
    },
    'Energy': {
        'revenue': 15000,
        'gross_margin': 0.30,
        'op_expense_ratio': 0.20,
        'growth_rate': 0.20
    },
    'Services': {
        'revenue': 10000,
        'gross_margin': 0.15,
        'op_expense_ratio': 0.30,
        'growth_rate': 0.10
    }
}
default_robotaxi_network = {
    'network_vehicles': 8000,
    'miles_per_car': 50000,
    'rider_pays_per_mile': 1.00,
    'car_owner_cut_per_mile': 0.60,
    'tesla_cut_per_mile': 0.40,
    'operating_cost_per_mile': 0.42,
    'utilization_rate': 0.50,
    'vehicle_growth_rate': 1.00,
    'cost_reduction_rate': 0.05,
    'utilization_growth_rate': 0.0234
}
default_toggles = {
    'Cars': False,
    'Robotaxi': False,
    'Optimus': False,
    'Energy': False,
    'Services': False,
    'Robotaxi Network': True
}
default_pe_ratios = {
    'Conservative': 100,
    'Current': 191.60,
    'Optimistic': 250,
    'Bullish': 350
}

# Sidebar inputs for each product
products = {}
for product, vals in default_products.items():
    st.sidebar.subheader(product)
    if product in ['Cars', 'Robotaxi', 'Optimus']:
        units_sold = st.sidebar.number_input(f"{product} Units Sold (2025)", min_value=0, value=vals['units_sold'], step=1000)
        sale_price = st.sidebar.number_input(f"{product} Sale Price ($)", min_value=0, value=vals['sale_price'], step=1000)
        gross_margin = st.sidebar.slider(f"{product} Gross Margin (%)", min_value=0.0, max_value=1.0, value=vals['gross_margin'])
        op_expense_ratio = st.sidebar.slider(f"{product} Op Expense Ratio", min_value=0.0, max_value=1.0, value=vals['op_expense_ratio'])
        growth_rate = st.sidebar.slider(f"{product} Unit Growth Rate", min_value=0.0, max_value=2.0, value=vals['growth_rate'])
        products[product] = {
            'units_sold': units_sold,
            'sale_price': sale_price,
            'gross_margin': gross_margin,
            'op_expense_ratio': op_expense_ratio,
            'growth_rate': growth_rate
        }
    else:
        revenue = st.sidebar.number_input(f"{product} Revenue (2025, $M)", min_value=0, value=vals['revenue'], step=1000)
        gross_margin = st.sidebar.slider(f"{product} Gross Margin (%)", min_value=0.0, max_value=1.0, value=vals['gross_margin'])
        op_expense_ratio = st.sidebar.slider(f"{product} Op Expense Ratio", min_value=0.0, max_value=1.0, value=vals['op_expense_ratio'])
        growth_rate = st.sidebar.slider(f"{product} Revenue Growth Rate", min_value=0.0, max_value=2.0, value=vals['growth_rate'])
        products[product] = {
            'revenue': revenue,
            'gross_margin': gross_margin,
            'op_expense_ratio': op_expense_ratio,
            'growth_rate': growth_rate
        }

# Robotaxi Network inputs
st.sidebar.subheader("Robotaxi Network")
network_vehicles = st.sidebar.number_input("Network Vehicles (2025)", min_value=0, value=default_robotaxi_network['network_vehicles'], step=1000)
miles_per_car = st.sidebar.number_input("Miles per Car (2025)", min_value=0, value=default_robotaxi_network['miles_per_car'], step=1000)
rider_pays_per_mile = st.sidebar.number_input("Rider Pays per Mile ($)", min_value=0.0, value=default_robotaxi_network['rider_pays_per_mile'], step=0.01)
car_owner_cut_per_mile = st.sidebar.number_input("Car Owner Cut per Mile ($)", min_value=0.0, value=default_robotaxi_network['car_owner_cut_per_mile'], step=0.01)
tesla_cut_per_mile = st.sidebar.number_input("Tesla Cut per Mile ($)", min_value=0.0, value=default_robotaxi_network['tesla_cut_per_mile'], step=0.01)
operating_cost_per_mile = st.sidebar.number_input("Operating Cost per Mile ($)", min_value=0.0, value=default_robotaxi_network['operating_cost_per_mile'], step=0.01)
utilization_rate = st.sidebar.slider("Utilization Rate (2025)", min_value=0.0, max_value=1.0, value=default_robotaxi_network['utilization_rate'])
vehicle_growth_rate = st.sidebar.slider("Vehicle Growth Rate", min_value=0.0, max_value=2.0, value=default_robotaxi_network['vehicle_growth_rate'])
cost_reduction_rate = st.sidebar.slider("Cost Reduction Rate", min_value=0.0, max_value=0.2, value=default_robotaxi_network['cost_reduction_rate'])
utilization_growth_rate = st.sidebar.slider("Utilization Growth Rate", min_value=0.0, max_value=0.1, value=default_robotaxi_network['utilization_growth_rate'])

robotaxi_network = {
    'network_vehicles': network_vehicles,
    'miles_per_car': miles_per_car,
    'rider_pays_per_mile': rider_pays_per_mile,
    'car_owner_cut_per_mile': car_owner_cut_per_mile,
    'tesla_cut_per_mile': tesla_cut_per_mile,
    'operating_cost_per_mile': operating_cost_per_mile,
    'utilization_rate': utilization_rate,
    'vehicle_growth_rate': vehicle_growth_rate,
    'cost_reduction_rate': cost_reduction_rate,
    'utilization_growth_rate': utilization_growth_rate
}

# Toggles
st.sidebar.subheader("Advanced Calculation Toggles")
toggles = {}
for key in default_toggles:
    toggles[key] = st.sidebar.checkbox(f"Advanced for {key}", value=default_toggles[key])

# Other assumptions
st.sidebar.subheader("Other Assumptions")
net_profit_margin = st.sidebar.slider("Net Profit Margin", min_value=0.0, max_value=0.5, value=0.08)
base_shares_outstanding = st.sidebar.number_input("Shares Outstanding (2025, millions)", min_value=0, value=3220, step=10)
shares_growth_rate = st.sidebar.slider("Shares Growth Rate", min_value=0.0, max_value=0.05, value=0.01)

# P/E Ratios
st.sidebar.subheader("P/E Ratios")
pe_ratios = {}
for scenario, val in default_pe_ratios.items():
    pe_ratios[scenario] = st.sidebar.number_input(f"{scenario} P/E", min_value=1, value=int(val), step=1)

# Years
st.sidebar.subheader("Projection Period")
projection_period = st.sidebar.radio("Projection Period", ["5 Years", "10 Years"], index=1)
if projection_period == "5 Years":
    years = list(range(2025, 2030))
else:
    years = list(range(2025, 2036))

# 5-year override flags and values
st.sidebar.subheader("5-Year Override (Year 2029)")
override_flags = {}
override_values = {}
for product in default_products:
    override_flags[product] = st.sidebar.checkbox(f"Override 5-Year for {product}", value=False)
    if override_flags[product]:
        if product in ['Cars', 'Robotaxi', 'Optimus']:
            override_values[product] = st.sidebar.number_input(f"{product} Units Sold (2029 Override)", min_value=0, value=default_products[product]['units_sold'], step=1000)
        else:
            override_values[product] = st.sidebar.number_input(f"{product} Revenue (2029 Override, $M)", min_value=0, value=default_products[product]['revenue'], step=1000)

user_inputs = {
    'products': products,
    'robotaxi_network': robotaxi_network,
    'toggles': toggles,
    'net_profit_margin': net_profit_margin,
    'base_shares_outstanding': base_shares_outstanding,
    'shares_growth_rate': shares_growth_rate,
    'pe_ratios': pe_ratios,
    'years': years,
    'override_flags': override_flags,
    'override_values': override_values
}

# Run valuation
def run_valuation_with_override(user_inputs):
    # Unpack user inputs
    products = user_inputs['products']
    robotaxi_network = user_inputs['robotaxi_network']
    toggles = user_inputs['toggles']
    net_profit_margin = user_inputs['net_profit_margin']
    base_shares_outstanding = user_inputs['base_shares_outstanding']
    shares_growth_rate = user_inputs['shares_growth_rate']
    pe_ratios = user_inputs['pe_ratios']
    years = user_inputs['years']
    override_flags = user_inputs.get('override_flags', {})
    override_values = user_inputs.get('override_values', {})

    yearly_results = []
    for year in years:
        shares_outstanding = base_shares_outstanding * (1 + shares_growth_rate) ** (year - years[0])
        product_results = []
        total_product_revenue = 0
        revenue_breakdown = []
        for product, data in products.items():
            # Apply override for 5th year if flag is set
            if year == years[4] and override_flags.get(product, False):
                if product in ['Cars', 'Robotaxi', 'Optimus']:
                    units_sold = override_values[product]
                    revenue = units_sold * data['sale_price']
                else:
                    revenue = override_values[product] * 1e6
            else:
                if product in ['Cars', 'Robotaxi', 'Optimus']:
                    units_sold = data['units_sold'] * (1 + data['growth_rate']) ** (year - years[0])
                    revenue = units_sold * data['sale_price']
                else:
                    revenue = data['revenue'] * (1 + data['growth_rate']) ** (year - years[0]) * 1e6
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

        # Robotaxi Network (no override for network)
        network_vehicles = robotaxi_network['network_vehicles'] * (1 + robotaxi_network['vehicle_growth_rate']) ** (year - years[0])
        operating_cost_per_mile = robotaxi_network['operating_cost_per_mile'] * (1 - robotaxi_network['cost_reduction_rate']) ** (year - years[0])
        utilization_rate = min(0.70, robotaxi_network['utilization_rate'] * (1 + robotaxi_network['utilization_growth_rate']) ** (year - years[0]))
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

        revenue_breakdown.append({
            'Category': 'Robotaxi Network',
            'Revenue ($M)': tesla_earnings / 1e6
        })

        total_company_revenue = total_product_revenue + tesla_earnings
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

        yearly_results.append({
            'Year': year,
            'product_valuation': product_results,
            'robotaxi_network': robotaxi_results,
            'revenue_breakdown': revenue_breakdown,
            'total_revenue_million': total_company_revenue / 1e6,
            'market_cap': market_cap_results
        })
    return {'yearly_results': yearly_results}

output = run_valuation_with_override(user_inputs)

# Display results for 2025 and 2035
for result in output['yearly_results']:
    if result['Year'] in [2025, 2035]:
        st.header(f"Year {result['Year']}")
        st.subheader("Product Valuation Results")
        df_product = pd.DataFrame(result['product_valuation'])
        for col in ['Revenue ($M)', 'Gross Profit ($M)', 'Operating Expenses ($M)']:
            if col in df_product.columns:
                df_product[col] = df_product[col].apply(lambda x: human_format(x * 1e6) if x != '-' and pd.notnull(x) else x)
        # Format Units Sold as integer with commas
        if 'Units Sold' in df_product.columns:
            df_product['Units Sold'] = df_product['Units Sold'].apply(lambda x: f"{int(round(x)):,}" if x != '-' and pd.notnull(x) else x)
        # Ensure columns with possible '-' are all strings for Streamlit compatibility
        for col in ['Sale Price ($)', 'Units Sold', 'Gross Margin (%)', 'Revenue ($M)', 'Gross Profit ($M)', 'Operating Expenses ($M)']:
            if col in df_product.columns:
                df_product[col] = df_product[col].astype(str)
        st.dataframe(df_product)
        st.subheader("Robotaxi Network Earnings")
        df_robotaxi = pd.DataFrame([result['robotaxi_network']])
        for col in df_robotaxi.columns:
            if any(unit in col for unit in ['($M)', 'per Year', 'Earnings', 'Revenue', 'Costs']):
                df_robotaxi[col] = df_robotaxi[col].apply(lambda x: human_format(x * 1e6) if pd.notnull(x) and isinstance(x, (int, float)) else x)
        # Convert all columns to string for compatibility
        df_robotaxi = df_robotaxi.astype(str)
        st.dataframe(df_robotaxi)
        st.subheader("Total Company Revenue Breakdown")
        df_revenue = pd.DataFrame(result['revenue_breakdown'])
        if 'Revenue ($M)' in df_revenue.columns:
            df_revenue['Revenue ($M)'] = df_revenue['Revenue ($M)'].apply(lambda x: human_format(x * 1e6) if pd.notnull(x) else x)
        # Convert all columns to string for compatibility
        df_revenue = df_revenue.astype(str)
        st.dataframe(df_revenue)
        st.markdown(f"**Total Company Revenue:** ${human_format(result['total_revenue_million'] * 1e6)}")
        st.subheader("Market Capitalization Results")
        df_market = pd.DataFrame(result['market_cap'])
        for col in ['Net Income ($M)', 'Market Cap ($B)', 'Stock Price ($)']:
            if col in df_market.columns:
                if col == 'Market Cap ($B)':
                    df_market[col] = df_market[col].apply(lambda x: human_format(x * 1e9) if pd.notnull(x) else x)
                elif col == 'Net Income ($M)':
                    df_market[col] = df_market[col].apply(lambda x: human_format(x * 1e6) if pd.notnull(x) else x)
                else:
                    df_market[col] = df_market[col].apply(lambda x: human_format(x) if pd.notnull(x) else x)
        # Convert all columns to string for compatibility
        df_market = df_market.astype(str)
        st.dataframe(df_market)

st.header("JSON Output for Website (first and last years for brevity):")
st.code(json.dumps([output['yearly_results'][0], output['yearly_results'][-1]], indent=4), language='json') 