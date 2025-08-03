import streamlit as st
from dashboard.detail_financialinvestment import detail_investmentplan
from dashboard.financial_report import generate_financial_dashboard
from dashboard.savingandinvest import savings_and_investing_tab
from dashboard.taxandcomp import tax_optimization_tab
from utils.income_manager import IncomeManager
from utils.snowflake_conn import init_db
from utils.snowflake_helpers import TransactionManager
from utils.together_client import TogetherClient
import os
from datetime import datetime
import pandas as pd
import numpy as np

def map_category_to_predefined(category, predefined_categories):
    """
    Maps any category to the most relevant predefined category.
    Uses keyword matching to find the best fit.
    """
    if not category:
        return "Other"
    
    category_lower = category.lower()
    
    # Define mapping rules for common categories
    category_mappings = {
        # Meals & Food
        "food": "Meals", "restaurant": "Meals", "dining": "Meals", "cafe": "Meals", 
        "coffee": "Meals", "lunch": "Meals", "dinner": "Meals", "breakfast": "Meals",
        "groceries": "Meals", "meal": "Meals", "catering": "Meals",
        
        # Travel
        "travel": "Travel", "transport": "Travel", "uber": "Travel", "lyft": "Travel",
        "taxi": "Travel", "flight": "Travel", "hotel": "Travel", "airbnb": "Travel",
        "gas": "Travel", "fuel": "Travel", "parking": "Travel", "rental": "Travel",
        "car": "Travel", "bus": "Travel", "train": "Travel", "subway": "Travel",
        
        # Office & Business
        "office": "Office", "business": "Office", "work": "Office", "professional": "Office",
        "meeting": "Office", "conference": "Office", "workspace": "Office", "coworking": "Office",
        "equipment": "Office", "supplies": "Office", "stationery": "Office",
        
        # Software & Technology
        "software": "Software", "cloud": "Software", "saas": "Software", "subscription": "Software",
        "app": "Software", "platform": "Software", "service": "Software", "digital": "Software",
        "online": "Software", "web": "Software", "internet": "Software", "hosting": "Software",
        "domain": "Software", "website": "Software", "api": "Software", "tool": "Software",
        "development": "Software", "programming": "Software", "tech": "Software",
        
        # Rent & Real Estate
        "rent": "Rent", "lease": "Rent", "property": "Rent", "real estate": "Rent",
        "apartment": "Rent", "house": "Rent", "accommodation": "Rent", "lodging": "Rent",
        
        # Utilities
        "utility": "Utilities", "electricity": "Utilities", "water": "Utilities", 
        "gas": "Utilities", "internet": "Utilities", "phone": "Utilities", 
        "telephone": "Utilities", "mobile": "Utilities", "cable": "Utilities",
        "tv": "Utilities", "television": "Utilities", "wifi": "Utilities",
        "broadband": "Utilities", "energy": "Utilities", "power": "Utilities"
    }
    
    # Check for exact matches first
    for keyword, mapped_category in category_mappings.items():
        if keyword in category_lower:
            return mapped_category
    
    # Check if the category is already in predefined list
    if category in predefined_categories:
        return category
    
    # If no match found, return "Other"
    return "Other"



st.set_page_config(layout="wide", page_title="FinAI", page_icon="🧾")

# Custom CSS for improved UI
st.markdown("""
<style>
    /* Custom styling for better UI */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1rem;
        border-radius: 10px;
        color: #333333;
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    
    .upload-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
    }
    
    .success-message {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, #17a2b8 0%, #6f42c1 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .save-form {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #dee2e6;
        margin: 1rem 0;
    }
    
    .review-section {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)
# Initialize clients
together_client = TogetherClient()
transaction_manager = TransactionManager()

# Initialize database (run once)
@st.cache_resource
def initialize_database():
    try:
        init_db()
        return True
    except Exception as e:
        st.error(f"Failed to initialize database: {e}")
        return False

if not initialize_database():
    st.stop()
    


# Initialize session state variables
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'bulk_processing' not in st.session_state:
    st.session_state.bulk_processing = False
if 'receipt_data' not in st.session_state:
    st.session_state.receipt_data = None
st.markdown('<div class="main-header"><h1>🚀 FinAI - Your AI-Powered Financial Companion</h1></div>', unsafe_allow_html=True)

# Tab interface with updated names and styling
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📄 Smart Document Scanner", 
    "💰 Revenue Tracker",
    "📊 Transaction History", 
    "📈 Financial Analytics", 
    "🧾 Tax Optimizer", 
    "🎯 Wealth Builder", 
    "📈 Market Intelligence"
])

with tab1:
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("🔍 Intelligent Document Scanner")
        
        # Unified file uploader for single file
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "📄 Upload Financial Document (PDF, CSV, or Text)",
            type=["pdf","csv", "txt"],
            help="Upload any financial document for AI analysis",
            key="single_upload"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Text fallback
        receipt_text = st.text_area(
            "📝 Or paste document text directly",
            height=200,
            placeholder="Paste financial document text here...",
            key="single_text"
        )
        
        if st.button("🔍 Analyze Document", type="primary", key="process_single"):
            if uploaded_file or receipt_text:
                with st.spinner("🧠 Analyzing document content..."):
                    try:
                        file_bytes = None
                        file_type = None
                        extracted_text = receipt_text
                        
                        if uploaded_file:
                            file_bytes = uploaded_file.read()
                            file_ext = os.path.splitext(uploaded_file.name)[1].lower()[1:]
                            
                            if file_ext == 'pdf':
                                file_type = 'pdf'
                                extracted_text = together_client._extract_text_from_pdf(file_bytes)
                            elif file_ext in ['jpg', 'jpeg', 'png']:
                                file_type = file_ext
                                extracted_text = together_client._extract_text_from_image(file_bytes)
                            elif file_ext == 'txt':
                                extracted_text = file_bytes.decode('utf-8')
                        
                        # Process with Together.ai
                        result = together_client.process_receipt(
                            file_bytes=file_bytes,
                            text=extracted_text,
                            file_type=file_type
                        )
                        
                        # Store in session state
                        st.session_state.receipt_data = result
                        st.session_state.analysis_time = datetime.now()
                        st.session_state.bulk_processing = False
                        st.session_state.form_submitted = False  # Reset form submission flag
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error processing receipt: {str(e)}")
            else:
                st.warning("Please upload a file or paste receipt text")

    with col2:
        st.header("⚡ Batch Document Processor")
        
        # Multi-file uploader
        bulk_files = st.file_uploader(
            "Upload Multiple Documents",
            type=["pdf", "jpg", "jpeg", "png", "txt"],
            accept_multiple_files=True,
            help="Upload multiple financial documents at once",
            key="bulk_upload"
        )
        
        if st.button("Process Batch Documents", type="primary", key="process_bulk"):
            if bulk_files:
                with st.spinner(f"🧠 Analyzing {len(bulk_files)} documents..."):
                    try:
                        # Process files in bulk
                        files_to_process = []
                        for uploaded_file in bulk_files:
                            file_bytes = uploaded_file.read()
                            file_ext = os.path.splitext(uploaded_file.name)[1].lower()[1:]
                            files_to_process.append((file_bytes, file_ext))
                            
                        results = together_client.process_bulk_receipts(files=files_to_process)
                        
                        # Store in session state
                        st.session_state.bulk_results = results
                        st.session_state.bulk_processing = True
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Bulk processing failed: {str(e)}")
            else:
                st.warning("Please upload at least one file")

    # Display results based on processing mode
    if st.session_state.get('bulk_processing', False) and 'bulk_results' in st.session_state:
        st.subheader("📊 Batch Processing Results")
        
        # Create summary table
        summary_data = []
        for i, result in enumerate(st.session_state.bulk_results):
            summary_data.append({
                "#": i+1,
                "Merchant": result['merchant']['value'],
                "Amount": f"${result['amount']['value']:.2f}",
                "Confidence": f"{result['amount']['confidence']*100:.1f}%",
                "Category": result['category']['value'],
                "Date": result['date']['value'] or "N/A"
            })
        
        st.dataframe(
            pd.DataFrame(summary_data),
            column_config={
                "#": st.column_config.NumberColumn(width="small"),
                "Amount": st.column_config.TextColumn(width="small")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Batch save options
        with st.expander("💾 Save All Transactions"):
            if st.button("Save All to Database", key="save_all_bulk"):
                with st.spinner(f"Saving {len(st.session_state.bulk_results)} transactions..."):
                    try:
                        transaction_ids = transaction_manager.log_bulk_receipts(st.session_state.bulk_results)

                        st.success(f"✅ Successfully saved {len(transaction_ids)} transactions!")
                        del st.session_state.bulk_results
                        del st.session_state.bulk_processing
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to save transactions: {str(e)}")
            
            # Option to edit individual transactions before saving
            if st.checkbox("Review individual transactions before saving"):
                for i, result in enumerate(st.session_state.bulk_results):
                    with st.container(border=True):
                        cols = st.columns([1, 3])
                        with cols[0]:
                            st.markdown(f"**Document #{i+1}**")
                            st.metric("Amount", f"${result['amount']['value']:.2f}")
                        with cols[1]:
                            with st.form(f"edit_receipt_{i}"):
                                merchant = st.text_input(
                                    "Merchant",
                                    value=result['merchant']['value'],
                                    key=f"merchant_{i}"
                                )
                                # Map category to predefined list to avoid ValueError
                                predefined_categories = ["Meals", "Travel", "Office", "Software", "Rent", "Utilities", "Other"]
                                original_category = result['category']['value']
                                mapped_category = map_category_to_predefined(original_category, predefined_categories)
                                
                                # Show info if category was mapped
                                if original_category != mapped_category:
                                    st.info(f"📝 Category '{original_category}' was automatically mapped to '{mapped_category}' for better organization.")
                                
                                category = st.selectbox(
                                    "Category",
                                    options=predefined_categories,
                                    index=predefined_categories.index(mapped_category),
                                    key=f"category_{i}"
                                )
                                # Handle different date formats safely for bulk processing
                                date_value = result['date']['value']
                                try:
                                    if date_value:
                                        # Try multiple date formats
                                        for fmt in ['%Y-%m-%d', '%d-%b-%Y', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']:
                                            try:
                                                parsed_date = datetime.strptime(date_value, fmt).date()
                                                break
                                            except ValueError:
                                                continue
                                        else:
                                            # If no format matches, use current date
                                            parsed_date = datetime.now().date()
                                    else:
                                        parsed_date = datetime.now().date()
                                except:
                                    parsed_date = datetime.now().date()
                                
                                date = st.date_input(
                                    "Date",
                                    value=parsed_date,
                                    key=f"date_{i}"
                                )
                                
                                if st.form_submit_button(f"Update Document #{i+1}"):
                                    st.session_state.bulk_results[i]['merchant']['value'] = merchant
                                    st.session_state.bulk_results[i]['category']['value'] = category
                                    st.session_state.bulk_results[i]['date']['value'] = date.strftime('%Y-%m-%d')
                                    st.success(f"Document #{i+1} updated!")
                                    st.rerun()

    elif 'receipt_data' in st.session_state and not st.session_state.get('bulk_processing', True):
        # Single document processing results (existing code)
        st.subheader("✅ Document Analysis Results")
        
        # Safe data extraction with fallbacks
        receipt_data = st.session_state.receipt_data
        
        # Helper function to safely get nested values
        def safe_get(data, key, subkey=None, default=None):
            try:
                if subkey:
                    return data.get(key, {}).get(subkey, default)
                return data.get(key, default)
            except:
                return default
        
        # Extract values safely
        amount_value = safe_get(receipt_data, 'amount', 'value', 0.0)
        amount_confidence = safe_get(receipt_data, 'amount', 'confidence', 0.0)
        merchant_value = safe_get(receipt_data, 'merchant', 'value', 'Unknown')
        merchant_confidence = safe_get(receipt_data, 'merchant', 'confidence', 0.0)
        category_value = safe_get(receipt_data, 'category', 'value', 'Other')
        category_confidence = safe_get(receipt_data, 'category', 'confidence', 0.0)
        date_value = safe_get(receipt_data, 'date', 'value', 'Not detected')
        date_confidence = safe_get(receipt_data, 'date', 'confidence', 0.0)
        
        with st.container():
            cols = st.columns(2)
            
            with cols[0]:
                st.metric(
                    "Total Amount", 
                    f"${float(amount_value):.2f}" if amount_value else "$0.00", 
                    f"Confidence: {float(amount_confidence)*100:.1f}%" if amount_confidence else "Confidence: 0.0%"
                )
                st.metric(
                    "Merchant",
                    str(merchant_value),
                    f"Confidence: {float(merchant_confidence)*100:.1f}%" if merchant_confidence else "Confidence: 0.0%"
                )
            
            with cols[1]:
                st.metric(
                    "Category",
                    str(category_value),
                    f"Confidence: {float(category_confidence)*100:.1f}%" if category_confidence else "Confidence: 0.0%"
                )
                st.metric(
                    "Date",
                    str(date_value) if date_value else 'Not detected',
                    f"Confidence: {float(date_confidence)*100:.1f}%" if date_confidence else "Confidence: 0.0%"
                )
        
        line_items = safe_get(receipt_data, 'line_items', default=[])
        if line_items and isinstance(line_items, list) and len(line_items) > 0:
            st.subheader("📝 Line Items")
            try:
                line_items_df = pd.DataFrame(line_items)
                st.dataframe(
                    line_items_df,
                    column_config={
                        "amount": st.column_config.NumberColumn(
                            "Amount",
                            format="$%.2f"
                        )
                    },
                    hide_index=True,
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"⚠️ Could not display line items: {str(e)}")
                st.json(line_items)

        # Debug information (can be removed later)
        with st.expander("🔧 Debug Information"):
            st.write(f"Form submitted: {st.session_state.get('form_submitted', False)}")
            st.write(f"Receipt data exists: {'receipt_data' in st.session_state}")
            st.write(f"Bulk processing: {st.session_state.get('bulk_processing', False)}")
            st.write("Extracted values:")
            st.write(f"- Amount: {amount_value} (type: {type(amount_value)})")
            st.write(f"- Merchant: {merchant_value} (type: {type(merchant_value)})")
            st.write(f"- Category: {category_value} (type: {type(category_value)})")
            st.write(f"- Date: {date_value} (type: {type(date_value)})")
            st.write("Raw receipt data:")
            st.json(receipt_data)
        
        # Save to database section (existing code)
        if not st.session_state.form_submitted:
            st.markdown("---")
            st.markdown("## 💾 Review & Save Transaction")
            st.info("📝 Review the extracted information below and save to your database.")
            
            st.markdown('<div class="save-form">', unsafe_allow_html=True)
            with st.form("save_transaction"):
                st.subheader("🔍 Transaction Details")

                amount = st.number_input(
                    "Amount",
                    value=float(amount_value) if amount_value else 0.0,
                    min_value=0.0,
                    step=0.01,
                    format="%.2f"
                )

                merchant = st.text_input(
                    "Merchant",
                    value=str(merchant_value) if merchant_value else ""
                )

                # Map category to predefined list to avoid ValueError
                predefined_categories = ["Meals", "Travel", "Office", "Software", "Rent", "Utilities", "Other"]
                original_category = str(category_value) if category_value else "Other"
                mapped_category = map_category_to_predefined(original_category, predefined_categories)
                
                # Show info if category was mapped
                if original_category != mapped_category:
                    st.info(f"📝 Category '{original_category}' was automatically mapped to '{mapped_category}' for better organization.")
                
                category = st.selectbox(
                    "Category",
                    options=predefined_categories,
                    index=predefined_categories.index(mapped_category)
                )

                # Handle different date formats safely
                date_value = str(date_value) if date_value else None
                try:
                    if date_value:
                        # Try multiple date formats
                        for fmt in ['%Y-%m-%d', '%d-%b-%Y', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']:
                            try:
                                parsed_date = datetime.strptime(date_value, fmt).date()
                                break
                            except ValueError:
                                continue
                        else:
                            # If no format matches, use current date
                            parsed_date = datetime.now().date()
                    else:
                        parsed_date = datetime.now().date()
                except:
                    parsed_date = datetime.now().date()
                
                date = st.date_input(
                    "Date",
                    value=parsed_date
                )

                st.markdown("---")
                submitted = st.form_submit_button("💾 Save Transaction to Database", type="primary", use_container_width=True)

                if submitted:
                    try:
                        # Create a clean receipt data structure
                        clean_receipt_data = {
                            'amount': {'value': amount, 'confidence': amount_confidence},
                            'merchant': {'value': merchant, 'confidence': merchant_confidence},
                            'category': {'value': category, 'confidence': category_confidence},
                            'date': {'value': date.strftime('%Y-%m-%d'), 'confidence': date_confidence},
                            'line_items': line_items if line_items else []
                        }

                        transaction_id = transaction_manager.log_receipt(clean_receipt_data)

                        st.session_state.form_submitted = True
                        st.session_state.last_transaction_id = transaction_id
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error saving transaction: {str(e)}")
                        st.error("Please check your database connection and try again.")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success(f"✅ Transaction {st.session_state.last_transaction_id} saved successfully!")
            if st.button("➕ New Transaction"):
                del st.session_state.receipt_data
                st.session_state.form_submitted = False
                del st.session_state.last_transaction_id
                st.rerun()
with tab2:
    st.header("💰 Revenue Tracker")
    
    # Income entry form
    with st.form("income_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input("Amount", min_value=0.01, step=0.01, format="%.2f")
            source = st.text_input("Income Source", placeholder="Employer, Client, etc.")
            payment_method = st.selectbox(
                "Payment Method",
                options=["Direct Deposit", "Check", "Cash", "Bank Transfer", "Other"]
            )
        
        with col2:
            date = st.date_input("Date Received", value=datetime.now())
            category = st.selectbox(
                "Income Category",
                options=["Salary", "Freelance", "Investment", "Gift", "Other"]
            )
            tags = st.multiselect(
                "Tags",
                options=["Recurring", "Bonus", "Taxable", "Non-Taxable"]
            )
        
        description = st.text_area("Description/Notes")
        
        submitted = st.form_submit_button("Record Income", type="primary")
        if submitted:
            try:
                income_data = {
                    "amount": amount,
                    "source": source,
                    "date": date,
                    "payment_method": payment_method,
                    "category": category,
                    "tags": tags,
                    "description": description
                }
                transaction_id = IncomeManager.log_income(income_data)
                st.success(f"Income recorded successfully! Transaction ID: {transaction_id}")
            except Exception as e:
                st.error(f"Error recording income: {str(e)}")
    
    # Revenue history and reports
    st.subheader("Revenue History")
    
    income_report = IncomeManager.get_income_report()
    if income_report:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Revenue", f"${income_report['total_income']:,.2f}")
            st.metric("Average Revenue", f"${income_report['average_income']:,.2f}")
        
        with col2:
            st.write("**Top Revenue Sources**")
            for source, amount in income_report['top_sources'].items():
                st.write(f"- {source}: ${amount:,.2f}")
        
        st.subheader("Monthly Revenue Trend")
        monthly_df = pd.DataFrame.from_dict(
            income_report['income_by_month'],
            orient='index',
            columns=['Amount']
        )
        st.line_chart(monthly_df)
    else:
        st.info("No income records found")
        
with tab3:
    st.header("📊 Transaction History")
    
    view_type = st.radio(
        "Transaction Type:",
        options=["All Transactions", "Expenses Only", "Revenue Only"],
        horizontal=True,
        key="transaction_view_type"
    )
    
    try:
        # Initialize empty DataFrames
        expenses_df = pd.DataFrame()
        income_df = pd.DataFrame()
        combined_df = pd.DataFrame()

        # Get expenses data with duplicate column handling
        try:
            expenses_data = transaction_manager.get_recent_transactions(200)
            if isinstance(expenses_data, pd.DataFrame) and not expenses_data.empty:
                expenses_df = pd.DataFrame(expenses_data)
                # Clean column names
                expenses_df.columns = [str(col).lower() for col in expenses_df.columns]
                expenses_df = expenses_df.loc[:, ~expenses_df.columns.duplicated()]
                
                # Prepare expense-specific columns
                if not expenses_df.empty:
                    expenses_df['type'] = 'expense'
                    if 'amount' in expenses_df.columns:
                        expenses_df['amount_display'] = np.abs(expenses_df['amount'])
                    if 'date' in expenses_df.columns:
                        expenses_df['date'] = pd.to_datetime(expenses_df['date'])
        except Exception as e:
            st.error(f"Error loading expenses: {str(e)}")

        # Get income data with duplicate column handling
        try:
            income_df = IncomeManager.get_income_for_transactions_view(200)
        except Exception as e:
            st.error(f"Error loading income: {str(e)}")
            income_df = pd.DataFrame()

        # Combine data based on view type
        dfs_to_combine = []
        if view_type in ["All Transactions", "Expenses Only"] and not expenses_df.empty:
            dfs_to_combine.append(expenses_df)
        if view_type in ["All Transactions", "Revenue Only"] and not income_df.empty:
            dfs_to_combine.append(income_df)

        if dfs_to_combine:
            try:
                combined_df = pd.concat(dfs_to_combine, ignore_index=True)
                if not combined_df.empty and 'date' in combined_df.columns:
                    combined_df = combined_df.sort_values('date', ascending=False)
            except Exception as e:
                st.error(f"Error combining data: {str(e)}")

        if not combined_df.empty:
            # Display the transactions table
            display_columns = ['date', 'merchant', 'amount_display', 'type', 'category']
            display_columns = [col for col in display_columns if col in combined_df.columns]
            
            st.dataframe(
                combined_df[display_columns].style.applymap(
                    lambda x: 'color: green' if x == 'income' else 'color: red', 
                    subset=['type']
                ),
                column_config={
                    "date": st.column_config.DateColumn("Transaction Date"),
                    "merchant": "Merchant/Revenue Source",
                    "amount_display": st.column_config.NumberColumn(
                        "Amount",
                        format="$%.2f"
                    ),
                    "type": "Transaction Type",
                    "category": "Category"
                },
                hide_index=True,
                use_container_width=True,
                height=600
            )

            # [Rest of your transaction details and summary view...]
            # Keep your existing code for transaction details and summary statistics

        else:
            st.info("No transactions found for the selected view")
            
    except Exception as e:
        st.error(f"Failed to load transactions: {str(e)}")
with tab4:
    st.header("📈 Financial Analytics")   
        # Time period selector
    time_period = st.selectbox(
            "Analytics Time Period",
            ["Week", "Month", "Quarter", "Year"],
            index=1
        )
    generate_financial_dashboard(time_period)
with tab5:
    tax_optimization_tab()

with tab6:
    savings_and_investing_tab()
with tab7:
    detail_investmentplan()