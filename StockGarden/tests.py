from django.test import TestCase
from .models import *

# 1. Creating Purchase Voucher with Items
def create_purchase_with_items():
    """Example of creating a purchase voucher with items"""
    from django.db import transaction
    
    try:
        with transaction.atomic():
            # Create voucher
            voucher = PurchaseVoucher.objects.create(
                vendor_id=1,  # Assuming vendor exists
                discount=Decimal('100.00'),
                payment_method=PaymentMethodChoices.CASH
            )
            
            # Create items
            item1 = PurchaseItem.objects.create(
                voucher=voucher,
                product_name="iPhone 14",
                quantity=2,
                price=Decimal('50000.00'),
                condition='new'
            )
            
            item2 = PurchaseItem.objects.create(
                voucher=voucher,
                product_name="Samsung Galaxy S23",
                quantity=1,
                price=Decimal('45000.00'),
                condition='new'
            )
            
            # Voucher totals will be automatically calculated via signals
            voucher.refresh_from_db()
            print(f"Total Amount: {voucher.total_amount}")
            print(f"Cost after discount: {voucher.cost}")
            
    except Exception as e:
        print(f"Error creating purchase: {e}")


# 2. Managing Stock with StockLedger
def handle_stock_movement():
    """Example of proper stock management"""
    try:
        # Get or create product
        product = Product.objects.get(name="iPhone 14")
        
        # Record purchase (incoming stock)
        StockLedger.create_entry(
            product=product,
            transaction_type='purchase',
            reference_id=1,  # Purchase voucher ID
            reference_model='PurchaseVoucher',
            quantity=10,  # Positive for incoming
            unit_cost=Decimal('48000.00'),
            created_by_id=1,
            notes="Initial stock purchase"
        )
        
        # Record sale (outgoing stock)
        StockLedger.create_entry(
            product=product,
            transaction_type='sale',
            reference_id=1,  # Sales voucher ID
            reference_model='SalesVoucher',
            quantity=-2,  # Negative for outgoing
            unit_cost=Decimal('48000.00'),
            created_by_id=1,
            notes="Sale to customer"
        )
        
        # Check current stock
        product.refresh_from_db()
        print(f"Current stock: {product.stock}")
        
    except ValidationError as e:
        print(f"Stock validation error: {e}")
    except Exception as e:
        print(f"Error managing stock: {e}")


# 3. Creating Sales Invoice
def create_sales_invoice():
    """Example of creating a sales invoice"""
    try:
        invoice = SalesInvoice.objects.create(
            product_name="iPhone 14",
            quantity=1,
            unit_price=Decimal('55000.00'),
            warranty=12,
            customer_name="John Doe",
            customer_number="9801234567",
            customer_address="Kathmandu, Nepal",
            discount_amount=Decimal('2000.00'),
            paid_amount=Decimal('50000.00'),
            payment_method=PaymentMethodChoices.CASH,
        )
        
        print(f"Invoice created: {invoice.invoice_number}")
        print(f"Total: {invoice.total_amount}")
        print(f"Remaining: {invoice.remaining_amount}")
        print(f"Status: {invoice.payment_status}")
        
    except ValidationError as e:
        print(f"Validation error: {e}")


# 4. Recording Cash Transactions
def record_cash_transaction():
    """Example of recording cash transactions"""
    try:
        # Record cash receipt
        cash_entry = Cashbook.create_entry(
            entry_type='receipt',
            source_type='sale',
            reference_id='SV000001',
            reference_model='SalesVoucher',
            description='Cash received from sale',
            amount=Decimal('50000.00'),
            payment_method=PaymentMethodChoices.CASH,
            transaction_date=timezone.now().date(),
            is_bank=False,
            recorded_by_id=1
        )
        
        print(f"Cash balance: {cash_entry.cash_balance}")
        
        # Record bank payment
        bank_entry = Cashbook.create_entry(
            entry_type='payment',
            source_type='purchase',
            reference_id='PV000001',
            reference_model='PurchaseVoucher',
            description='Payment to supplier',
            amount=Decimal('100000.00'),
            payment_method=PaymentMethodChoices.BANK_TRANSFER,
            transaction_date=timezone.now().date(),
            is_bank=True,
            bank_name='Nepal Bank',
            recorded_by_id=1
        )
        
        print(f"Bank balance: {bank_entry.bank_balance}")
        
    except ValidationError as e:
        print(f"Cash transaction error: {e}")


# 5. Generating Reports
def generate_business_report():
    """Example of generating business reports"""
    try:
        # Generate current report
        report = Report.generate_report()
        
        print("=== Business Report ===")
        print(f"Total Sales: {report.total_sales}")
        print(f"Total Purchases: {report.total_purchases}")
        print(f"Total Stock: {report.total_stock}")
        print(f"Low Stock Items: {report.low_stock_count}")
        print(f"Empty Stock Items: {report.empty_stock_count}")
        print(f"Total Stock Value: {report.total_stock_value}")
        
    except Exception as e:
        print(f"Report generation error: {e}")


# 6. Utility Functions
def get_product_stock_history(product_id):
    """Get complete stock history for a product"""
    try:
        entries = StockLedger.objects.filter(
            product_id=product_id
        ).order_by('transaction_date')
        return entries
    except Exception as e:
        print(f"Error fetching stock history: {e}")
        return StockLedger.objects.none()