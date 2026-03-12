"""
Nexus Commerce Suite — Advanced Analytics Logic
=================================================
Data science-powered analytics: ABC analysis, forecasting,
correlation analysis, moving averages, and RFM segmentation.
"""
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from ..common.supabase_client import get_supabase_client

logger = logging.getLogger("nexus_commerce.analytics")


def get_abc_analysis() -> dict:
    """
    ABC Analysis (Pareto Principle):
    Classify products into A (top 80% revenue), B (next 15%), C (remaining 5%).
    A data science approach to inventory prioritization.
    """
    supabase = get_supabase_client()
    try:
        logger.info("Running ABC Analysis...")
        # Get all sale items with product info
        items_res = supabase.table("sale_items").select("quantity, price_per_unit, product_id, products(name, sku)") \
            .eq("user_id", st.session_state.get("user_id")) \
            .execute()

        if not items_res.data:
            return {"data": [], "summary": {}}

        df = pd.DataFrame(items_res.data)
        df['revenue'] = df['quantity'] * df['price_per_unit']
        df['product_name'] = df['products'].apply(lambda x: x.get('name', 'N/A') if x else 'N/A')
        df['product_sku'] = df['products'].apply(lambda x: x.get('sku', 'N/A') if x else 'N/A')

        # Aggregate by product
        product_revenue = df.groupby(['product_id', 'product_name', 'product_sku']).agg(
            total_revenue=('revenue', 'sum'),
            total_units=('quantity', 'sum')
        ).reset_index().sort_values('total_revenue', ascending=False)

        total_revenue = product_revenue['total_revenue'].sum()
        if total_revenue == 0:
            return {"data": [], "summary": {}}

        product_revenue['revenue_pct'] = (product_revenue['total_revenue'] / total_revenue * 100).round(2)
        product_revenue['cumulative_pct'] = product_revenue['revenue_pct'].cumsum().round(2)

        # Classify: A = top 80%, B = next 15%, C = rest
        def classify(cum_pct):
            if cum_pct <= 80:
                return 'A'
            elif cum_pct <= 95:
                return 'B'
            return 'C'

        product_revenue['category'] = product_revenue['cumulative_pct'].apply(classify)

        summary = {
            'A': int((product_revenue['category'] == 'A').sum()),
            'B': int((product_revenue['category'] == 'B').sum()),
            'C': int((product_revenue['category'] == 'C').sum()),
            'total_revenue': float(total_revenue)
        }

        result = product_revenue[['product_name', 'product_sku', 'total_revenue', 'total_units', 'revenue_pct', 'cumulative_pct', 'category']].to_dict('records')

        logger.info("ABC Analysis complete: A=%d, B=%d, C=%d", summary['A'], summary['B'], summary['C'])
        return {"data": result, "summary": summary}

    except Exception as e:
        logger.error("ABC Analysis failed: %s", e)
        return {"error": f"Could not run ABC analysis. Details: {e}"}


def get_sales_forecast(days_history: int = 30, days_forecast: int = 7) -> dict:
    """
    Sales Forecasting using Linear Regression (numpy polyfit).
    Uses historical daily sales to project future revenue with confidence intervals.
    """
    supabase = get_supabase_client()
    try:
        logger.info("Running sales forecast (history=%dd, forecast=%dd)", days_history, days_forecast)
        start_date = datetime.now() - timedelta(days=days_history)
        response = supabase.table("sales").select("sale_date, total_amount") \
            .eq("user_id", st.session_state.get("user_id")) \
            .gte("sale_date", start_date.isoformat()).execute()

        if not response.data or len(response.data) < 3:
            return {"error": "Need at least 3 days of sales data for forecasting."}

        df = pd.DataFrame(response.data)
        df['sale_date'] = pd.to_datetime(df['sale_date']).dt.date
        daily = df.groupby('sale_date')['total_amount'].sum().reset_index()
        daily.columns = ['date', 'revenue']
        daily = daily.sort_values('date')

        # Create numeric x-axis
        daily['day_num'] = np.arange(len(daily))

        if len(daily) < 2:
            return {"error": "Need at least 2 different days of sales data to generate a forecast trend."}

        # Linear regression
        try:
            coeffs = np.polyfit(daily['day_num'].values, daily['revenue'].values, 1)
            slope, intercept = coeffs
        except np.linalg.LinAlgError:
            return {"error": "Could not generate forecast: Math error (SVD did not converge). Try analyzing a longer historical period."}

        # Calculate residuals for confidence interval
        predicted = np.polyval(coeffs, daily['day_num'].values)
        residuals = daily['revenue'].values - predicted
        std_error = float(np.std(residuals))

        # Generate forecast
        last_day = int(daily['day_num'].max())
        last_date = daily['date'].max()
        forecast_days = np.arange(last_day + 1, last_day + 1 + days_forecast)
        forecast_values = np.polyval(coeffs, forecast_days)
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(days_forecast)]

        # Historical data
        historical = [{"date": str(row['date']), "revenue": round(float(row['revenue']), 2)}
                       for _, row in daily.iterrows()]

        # Forecast data with confidence intervals
        forecast = [{"date": str(d), "revenue": round(max(0, float(v)), 2),
                      "upper": round(max(0, float(v + 1.96 * std_error)), 2),
                      "lower": round(max(0, float(v - 1.96 * std_error)), 2)}
                     for d, v in zip(forecast_dates, forecast_values)]

        trend_direction = "upward" if slope > 0 else "downward" if slope < 0 else "flat"
        daily_growth = round(float(slope), 2)

        logger.info("Forecast complete: trend=%s, daily_growth=₹%.2f", trend_direction, daily_growth)
        return {
            "historical": historical,
            "forecast": forecast,
            "trend": trend_direction,
            "daily_growth": daily_growth,
            "r_squared": round(float(1 - np.sum(residuals**2) / np.sum((daily['revenue'].values - daily['revenue'].mean())**2)), 4) if np.sum((daily['revenue'].values - daily['revenue'].mean())**2) > 0 else 0,
            "std_error": round(std_error, 2)
        }

    except Exception as e:
        logger.error("Forecasting failed: %s", e)
        return {"error": f"Could not generate forecast. Details: {e}"}


def get_correlation_analysis() -> dict:
    """
    Compute correlation matrix between product attributes and sales performance.
    Uses Pearson correlation coefficient.
    """
    supabase = get_supabase_client()
    try:
        logger.info("Running correlation analysis...")
        products_res = supabase.table("products").select("id, cost_price, selling_price, quantity_on_hand") \
            .eq("user_id", st.session_state.get("user_id")) \
            .execute()
        items_res = supabase.table("sale_items").select("product_id, quantity, price_per_unit") \
            .eq("user_id", st.session_state.get("user_id")) \
            .execute()

        if not products_res.data or not items_res.data:
            return {"error": "Need product and sales data for correlation analysis."}

        products_df = pd.DataFrame(products_res.data)
        items_df = pd.DataFrame(items_res.data)

        # Aggregate sales per product
        sales_agg = items_df.groupby('product_id').agg(
            total_units_sold=('quantity', 'sum'),
            total_revenue=('price_per_unit', lambda x: (x * items_df.loc[x.index, 'quantity']).sum())
        ).reset_index()
        sales_agg.columns = ['id', 'total_units_sold', 'total_revenue']

        merged = products_df.merge(sales_agg, on='id', how='left').fillna(0)
        merged['profit_margin'] = ((merged['selling_price'] - merged['cost_price']) / merged['selling_price'] * 100).round(2)

        analysis_cols = ['cost_price', 'selling_price', 'quantity_on_hand', 'profit_margin', 'total_units_sold', 'total_revenue']
        corr_matrix = merged[analysis_cols].corr().round(3)

        return {
            "matrix": corr_matrix.to_dict(),
            "columns": analysis_cols,
            "insights": _generate_correlation_insights(corr_matrix)
        }

    except Exception as e:
        logger.error("Correlation analysis failed: %s", e)
        return {"error": f"Could not run correlation analysis. Details: {e}"}


def _generate_correlation_insights(corr: pd.DataFrame) -> list:
    """Auto-generate insights from correlation matrix."""
    insights = []
    pairs = []
    for i, col1 in enumerate(corr.columns):
        for j, col2 in enumerate(corr.columns):
            if i < j:
                val = corr.loc[col1, col2]
                pairs.append((col1, col2, val))

    # Sort by absolute correlation
    pairs.sort(key=lambda x: abs(x[2]), reverse=True)
    for col1, col2, val in pairs[:5]:
        strength = "strong" if abs(val) > 0.7 else "moderate" if abs(val) > 0.4 else "weak"
        direction = "positive" if val > 0 else "negative"
        insights.append(f"{strength.capitalize()} {direction} correlation ({val:.3f}) between {col1.replace('_', ' ')} and {col2.replace('_', ' ')}")

    return insights


def get_rfm_analysis() -> dict:
    """
    RFM (Recency, Frequency, Monetary) Customer Segmentation.
    Segments customers into Gold, Silver, Bronze based on purchase behavior.
    """
    supabase = get_supabase_client()
    try:
        logger.info("Running RFM Analysis...")
        sales_res = supabase.table("sales").select("customer_id, total_amount, sale_date") \
            .not_.is_("customer_id", "null") \
            .eq("user_id", st.session_state.get("user_id")) \
            .execute()

        if not sales_res.data or len(sales_res.data) < 3:
            return {"error": "Need at least 3 customer-linked sales for RFM analysis."}

        df = pd.DataFrame(sales_res.data)
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        now = pd.Timestamp.now(tz='UTC')

        rfm = df.groupby('customer_id').agg(
            recency=('sale_date', lambda x: (now - x.max()).days),
            frequency=('customer_id', 'count'),
            monetary=('total_amount', 'sum')
        ).reset_index()

        # Score each dimension 1-3 using quantiles
        for col in ['recency', 'frequency', 'monetary']:
            try:
                if col == 'recency':
                    rfm[f'{col}_score'] = pd.qcut(rfm[col], q=3, labels=[3, 2, 1], duplicates='drop').astype(int)
                else:
                    rfm[f'{col}_score'] = pd.qcut(rfm[col], q=3, labels=[1, 2, 3], duplicates='drop').astype(int)
            except (ValueError, TypeError):
                rfm[f'{col}_score'] = 2  # Default to middle if not enough unique values

        rfm['rfm_score'] = rfm['recency_score'] + rfm['frequency_score'] + rfm['monetary_score']

        # Segment
        def segment(score):
            if score >= 7:
                return 'Gold'
            elif score >= 5:
                return 'Silver'
            return 'Bronze'

        rfm['segment'] = rfm['rfm_score'].apply(segment)

        # Get customer names
        customer_ids = rfm['customer_id'].tolist()
        customers_res = supabase.table("customers").select("id, name, phone") \
            .in_("id", customer_ids) \
            .eq("user_id", st.session_state.get("user_id")) \
            .execute()
        customers_map = {c['id']: c for c in customers_res.data}

        rfm['customer_name'] = rfm['customer_id'].map(lambda x: customers_map.get(x, {}).get('name', 'Unknown'))
        rfm['customer_phone'] = rfm['customer_id'].map(lambda x: customers_map.get(x, {}).get('phone', 'N/A'))

        summary = {
            'Gold': int((rfm['segment'] == 'Gold').sum()),
            'Silver': int((rfm['segment'] == 'Silver').sum()),
            'Bronze': int((rfm['segment'] == 'Bronze').sum()),
        }

        result = rfm[['customer_name', 'customer_phone', 'recency', 'frequency', 'monetary', 'rfm_score', 'segment']].round(2).to_dict('records')

        logger.info("RFM Analysis: Gold=%d, Silver=%d, Bronze=%d", summary['Gold'], summary['Silver'], summary['Bronze'])
        return {"data": result, "summary": summary}

    except Exception as e:
        logger.error("RFM Analysis failed: %s", e)
        return {"error": f"Could not run RFM analysis. Details: {e}"}


def get_moving_averages(days: int = 90) -> dict:
    """
    Calculate 7-day and 30-day moving averages for sales trend smoothing.
    """
    supabase = get_supabase_client()
    try:
        logger.info("Calculating moving averages over %d days", days)
        start_date = datetime.now() - timedelta(days=days)
        response = supabase.table("sales").select("sale_date, total_amount") \
            .eq("user_id", st.session_state.get("user_id")) \
            .gte("sale_date", start_date.isoformat()).execute()

        if not response.data:
            return {"error": "No sales data available."}

        df = pd.DataFrame(response.data)
        df['sale_date'] = pd.to_datetime(df['sale_date']).dt.date
        daily = df.groupby('sale_date')['total_amount'].sum().reset_index()
        daily.columns = ['date', 'revenue']
        daily = daily.sort_values('date')

        # Ensure continuous date range
        date_range = pd.date_range(start=daily['date'].min(), end=daily['date'].max())
        daily = daily.set_index('date').reindex(date_range, fill_value=0).reset_index()
        daily.columns = ['date', 'revenue']

        daily['ma_7'] = daily['revenue'].rolling(window=7, min_periods=1).mean().round(2)
        daily['ma_30'] = daily['revenue'].rolling(window=30, min_periods=1).mean().round(2)

        result = daily.to_dict('records')
        for r in result:
            r['date'] = str(r['date'].date()) if hasattr(r['date'], 'date') else str(r['date'])
            r['revenue'] = float(r['revenue'])
            r['ma_7'] = float(r['ma_7'])
            r['ma_30'] = float(r['ma_30'])

        return {"data": result}

    except Exception as e:
        logger.error("Moving averages calculation failed: %s", e)
        return {"error": f"Could not calculate moving averages. Details: {e}"}
