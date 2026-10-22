-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on customer_id
CREATE INDEX IF NOT EXISTS idx_customers_customer_id ON customers(customer_id);

-- Insert customer Jeevith with ID 1022
INSERT INTO customers (customer_id, name, email, status)
VALUES ('1022', 'Jeevith', 'jeevith@example.com', 'active')
ON CONFLICT (customer_id) DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    updated_at = NOW();

-- Verify the insert
SELECT * FROM customers WHERE customer_id = '1022';
