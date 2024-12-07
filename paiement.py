import streamlit as st
import stripe
import re
import uuid
from datetime import datetime

# Azure Imports
from azure.identity import DefaultAzureCredential
from azure.data.tables import TableServiceClient, TableClient

#stripe config
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "default_key_if_not_set")
stripe.api_key = STRIPE_SECRET_KEY

# Azure Configuration
STORAGE_ACCOUNT_NAME = "your_storage_account_name"
TABLE_NAME = "CNCOrientationTransactions"

# Get storage account from environment
storage_account_name = os.environ.get('AZURE_STORAGE_ACCOUNT')

# Use DefaultAzureCredential (works with managed identity)
credential = DefaultAzureCredential()

# Create Table Service Client
table_service_client = TableServiceClient(
    account_url=f"https://{storage_account_name}.table.core.windows.net",
    credential=credential
)

class AzureTableManager:
    def __init__(self):
        # Use DefaultAzureCredential for flexible authentication
        try:
            # This will try multiple authentication methods
            self.credential = DefaultAzureCredential()
            
            # Create table service client
            self.table_service_client = TableServiceClient(
                account_url=f"https://{STORAGE_ACCOUNT_NAME}.table.core.windows.net",
                credential=self.credential
            )
            
            # Get or create table client
            self.table_client = self.table_service_client.get_table_client(table_name=TABLE_NAME)
        except Exception as e:
            st.error(f"Azure Authentication Error: {e}")
            raise

    def create_transaction(self, transaction_data):
        """
        Create a new transaction record in Azure Table Storage
        """
        try:
            # Generate a unique partition and row key
            partition_key = transaction_data['Formation']
            row_key = str(uuid.uuid4())
            
            # Prepare entity
            entity = {
                'PartitionKey': partition_key,
                'RowKey': row_key,
                **transaction_data
            }
            
            # Insert entity
            self.table_client.create_entity(entity)
            return row_key
        except Exception as e:
            st.error(f"Error creating transaction: {e}")
            return None

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def create_payment_intent(amount):
    try:
        amount_in_cents = int(amount * 100)
        payment_intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency="mad",
            payment_method_types=["card"],
        )
        return payment_intent.client_secret
    except Exception as e:
        st.error(f"Payment Error: {e}")
        return None

def main():
    st.set_page_config(page_title="CNC Orientation Service")

    # Initialize Azure Table Manager
    try:
        azure_table_manager = AzureTableManager()
    except Exception as e:
        st.error("Failed to initialize Azure Table Storage. Check your configuration.")
        return

    # Rest of your existing Streamlit app logic...
    st.sidebar.header("Student Profile")
    nom = st.sidebar.text_input("Full Name")
    email = st.sidebar.text_input("Email")
    phone = st.sidebar.text_input("Phone Number")

    # Your formations and other logic remain the same...

    # During payment, use Azure Table Manager to log transaction
    if st.button("Proceed to Payment"):
        transaction_data = {
            'Name': nom,
            'Email': email,
            'PhoneNumber': phone,
            'Formation': selected_formation['Nom'],
            'Amount': selected_formation['Frais'],
            'Timestamp': datetime.now().isoformat()
        }
        
        transaction_id = azure_table_manager.create_transaction(transaction_data)
        if transaction_id:
            st.success(f"Transaction logged with ID: {transaction_id}")

if __name__ == "__main__":
    main()
