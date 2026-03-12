-- ═══════════════════════════════════════════════════════════════
-- NEXUS COMMERCE SUITE — Multi-Tenant Migration
-- ═══════════════════════════════════════════════════════════════
-- 1. Add user_id column to all relevant tables
-- 2. Link them to the auth.users table
-- 3. Update existing records (if any) to current user (optional)
-- 4. Re-configure RLS policies for strict isolation
-- ═══════════════════════════════════════════════════════════════

-- ── 1. ADD USER_ID COLUMNS ──

DO $$ 
BEGIN
    -- List of tables to migrate
    -- categories, brands, products, customers, sales, sale_items, payments, stock_adjustments, expenses, returns
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'categories' AND column_name = 'user_id') THEN
        ALTER TABLE categories ADD COLUMN user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'brands' AND column_name = 'user_id') THEN
        ALTER TABLE brands ADD COLUMN user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'products' AND column_name = 'user_id') THEN
        ALTER TABLE products ADD COLUMN user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'products' AND column_name = 'description') THEN
        ALTER TABLE products ADD COLUMN description TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'customers' AND column_name = 'user_id') THEN
        ALTER TABLE customers ADD COLUMN user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sales' AND column_name = 'user_id') THEN
        ALTER TABLE sales ADD COLUMN user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'sale_items' AND column_name = 'user_id') THEN
        ALTER TABLE sale_items ADD COLUMN user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'payments' AND column_name = 'user_id') THEN
        ALTER TABLE payments ADD COLUMN user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'stock_adjustments' AND column_name = 'user_id') THEN
        ALTER TABLE stock_adjustments ADD COLUMN user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'expenses' AND column_name = 'user_id') THEN
        ALTER TABLE expenses ADD COLUMN user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'returns' AND column_name = 'user_id') THEN
        ALTER TABLE returns ADD COLUMN user_id UUID REFERENCES auth.users(id) DEFAULT auth.uid();
    END IF;

END $$;

-- ── 2. DESTROY OLD "ALLOW ALL" POLICIES ──

DROP POLICY IF EXISTS "Allow all on products" ON products;
DROP POLICY IF EXISTS "Allow all on customers" ON customers;
DROP POLICY IF EXISTS "Allow all on sales" ON sales;
DROP POLICY IF EXISTS "Allow all on sale_items" ON sale_items;
DROP POLICY IF EXISTS "Allow all on payments" ON payments;
DROP POLICY IF EXISTS "Allow all on stock_adjustments" ON stock_adjustments;
DROP POLICY IF EXISTS "Allow all on expenses" ON expenses;
DROP POLICY IF EXISTS "Allow all on returns" ON returns;
DROP POLICY IF EXISTS "Allow all on categories" ON categories;
DROP POLICY IF EXISTS "Allow all on brands" ON brands;

-- ── 3. CREATE NEW ISOLATION POLICIES ──

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

-- ── 4. RETENTION PLAN (Optional) ──
-- If you have legacy data that has no user_id, you might want to assign it to your own user:
-- UPDATE products SET user_id = 'YOUR_UUID_HERE' WHERE user_id IS NULL;
