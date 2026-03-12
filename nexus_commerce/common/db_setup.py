"""
Nexus Commerce Suite — Database Setup Helper
===============================================
Provides SQL that users can copy-paste into Supabase SQL Editor.
"""
import logging
from ..common.supabase_client import get_supabase_client

logger = logging.getLogger("nexus_commerce.common.db_setup")


def check_tables_exist() -> dict:
    """
    Check which required tables exist in the database.
    Returns a dict with table names as keys and boolean existence as values.
    """
    supabase = get_supabase_client()
    required_tables = [
        'products', 'customers', 'sales', 'sale_items', 
        'payments', 'stock_adjustments', 'expenses', 
        'returns', 'categories', 'brands'
    ]
    results = {}

    for table in required_tables:
        try:
            response = supabase.table(table).select("*", count="exact").limit(0).execute()
            results[table] = True
        except Exception:
            results[table] = False

    return results


def get_setup_sql() -> str:
    """Return the complete SQL to create all tables."""
    return """
-- ═══════════════════════════════════════════════════════════════
-- NEXUS COMMERCE SUITE — Database Schema
-- ═══════════════════════════════════════════════════════════════
-- Run this in: Supabase Dashboard → SQL Editor → New Query
-- ═══════════════════════════════════════════════════════════════

-- 1. PRODUCTS
        -- 1. Categorization
        CREATE TABLE IF NOT EXISTS categories (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid(),
            created_at TIMESTAMPTZ DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS brands (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT UNIQUE NOT NULL,
            user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid(),
            created_at TIMESTAMPTZ DEFAULT now()
        );

        -- 2. Products
        CREATE TABLE IF NOT EXISTS products (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            cost_price NUMERIC(12, 2) NOT NULL DEFAULT 0,
            selling_price NUMERIC(12, 2) NOT NULL DEFAULT 0,
            tax_rate NUMERIC(5, 2) DEFAULT 0,
            quantity_on_hand INTEGER NOT NULL DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
            brand_id UUID REFERENCES brands(id) ON DELETE SET NULL,
            user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid(),
            last_sale_date TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT now(),
            updated_at TIMESTAMPTZ DEFAULT now()
        );
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);

-- 2. CUSTOMERS
CREATE TABLE IF NOT EXISTS customers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    email TEXT,
    user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid(),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);

-- 3. SALES
CREATE TABLE IF NOT EXISTS sales (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    total_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    total_tax NUMERIC(12, 2) NOT NULL DEFAULT 0,
    total_profit NUMERIC(12, 2) NOT NULL DEFAULT 0,
    user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid(),
    sale_date TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);

-- 4. SALE ITEMS
CREATE TABLE IF NOT EXISTS sale_items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sale_id UUID NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL DEFAULT 1,
    price_per_unit NUMERIC(12, 2) NOT NULL DEFAULT 0,
    tax_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid(),
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id);

-- 5. PAYMENTS
CREATE TABLE IF NOT EXISTS payments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sale_id UUID NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
    payment_method TEXT NOT NULL DEFAULT 'Cash',
    amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid(),
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_payments_sale ON payments(sale_id);

-- 6. STOCK ADJUSTMENTS
        CREATE TABLE IF NOT EXISTS stock_adjustments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            product_id UUID REFERENCES products(id) ON DELETE CASCADE,
            warehouse_id UUID, -- Optional for now
            change_amount INTEGER NOT NULL,
            reason TEXT,
            user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid(),
            created_at TIMESTAMPTZ DEFAULT now()
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            category TEXT NOT NULL,
            amount NUMERIC(12, 2) NOT NULL,
            expense_date DATE DEFAULT CURRENT_DATE,
            description TEXT,
            user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid(),
            created_at TIMESTAMPTZ DEFAULT now()
        );

        -- 8. Returns
        CREATE TABLE IF NOT EXISTS returns (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            sale_id UUID REFERENCES sales(id) ON DELETE CASCADE,
            product_id UUID REFERENCES products(id) ON DELETE CASCADE,
            quantity INTEGER NOT NULL,
            refund_amount NUMERIC(12, 2) NOT NULL,
            reason TEXT,
            user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid(),
            created_at TIMESTAMPTZ DEFAULT now()
        );
CREATE INDEX IF NOT EXISTS idx_adjustments_product ON stock_adjustments(product_id);

-- AUTO-UPDATE TIMESTAMPS TRIGGER
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_products_updated_at ON products;
CREATE TRIGGER set_products_updated_at
    BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS set_customers_updated_at ON customers;
CREATE TRIGGER set_customers_updated_at
    BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ROW LEVEL SECURITY
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;
ALTER TABLE sale_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_adjustments ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE returns ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE brands ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can only see their own products" ON products;
CREATE POLICY "Users can only see their own products" ON products FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can only see their own customers" ON customers;
CREATE POLICY "Users can only see their own customers" ON customers FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can only see their own sales" ON sales;
CREATE POLICY "Users can only see their own sales" ON sales FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can only see their own sale_items" ON sale_items;
CREATE POLICY "Users can only see their own sale_items" ON sale_items FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can only see their own payments" ON payments;
CREATE POLICY "Users can only see their own payments" ON payments FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can only see their own stock_adjustments" ON stock_adjustments;
CREATE POLICY "Users can only see their own stock_adjustments" ON stock_adjustments FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can only see their own expenses" ON expenses;
CREATE POLICY "Users can only see their own expenses" ON expenses FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can only see their own returns" ON returns;
CREATE POLICY "Users can only see their own returns" ON returns FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can only see their own categories" ON categories;
CREATE POLICY "Users can only see their own categories" ON categories FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can only see their own brands" ON brands;
CREATE POLICY "Users can only see their own brands" ON brands FOR ALL USING (auth.uid() = user_id);

-- ═══════════════════════════════════════════════════════════════
-- ✅ DONE! All tables created successfully.
-- ═══════════════════════════════════════════════════════════════
"""
