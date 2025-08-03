import os
import streamlit as st
import json
from datetime import datetime
from utils.snowflake_helpers import TransactionManager
from utils.income_manager import IncomeManager
from utils.together_client import TogetherClient
import dotenv

dotenv.load_dotenv()

class TaxComplianceAssistant:
    """Handles all tax compliance queries using Together.ai"""
    
    def __init__(self):
        self.together_client = TogetherClient()
    
    def ask_compliance_question(self, question: str) -> str:
        """Call Together.ai for tax optimization and compliance advice"""
        # Enhanced prompt for FinAI tax optimization context
        prompt = f"""You are a tax optimization expert specializing in personal and business finance, 
    particularly for freelancers, contractors, and small business owners using AI-powered financial tools.

    Provide practical, actionable tax advice for the following question. Focus on:
    - Maximizing legitimate tax deductions
    - Proper expense categorization
    - Tax-efficient business practices
    - Compliance with current tax laws
    - Best practices for financial record-keeping

    Question: {question}

    Answer in clear, actionable terms suitable for FinAI users managing their finances. 
    Include specific examples and actionable steps when possible."""

        return self.together_client.generate_text(prompt, temperature=0.2, max_tokens=1000)

class TaxOptimizationDashboard:
    """Handles the tax optimization calculations and visualizations"""
    
    @staticmethod
    def display_annual_tax_summary(report: dict):
        """Display key tax metrics"""
        with st.expander("📊 Annual Tax Summary"):
            if report:
                st.metric("Total Income", f"${report['income']['total']:,.2f}")
                st.metric("Total Expenses", f"${report['expenses']['total']:,.2f}")
                st.metric("Taxable Income", f"${report['income']['total'] - report['expenses']['total']:,.2f}")
                
                # Simple tax estimate (example rates)
                taxable_income = report['income']['total'] - report['expenses']['total']
                tax_estimate = taxable_income * 0.25  # Example 25% rate
                st.metric("Estimated Tax Liability", f"${tax_estimate:,.2f}")
                
                # Important notice
                st.warning("""
                **Important Notice**: 
                - These are estimates only
                - Actual tax liability may vary based on jurisdiction
                - Consult a qualified tax professional for official advice
                """)
            else:
                st.warning("No financial data available for tax analysis")
    
    @staticmethod
    def display_tax_deductible_expenses(report: dict):
        """Show expense categories with tax benefits"""
        with st.expander("💡 Tax-Deductible Expenses"):
            if report and report['expenses']['category_breakdown']:
                deductible_categories = {
                    'Office': "100% deductible for home office",
                    'Software': "100% deductible if used for business",
                    'Travel': "50-100% deductible depending on purpose",
                    'Meals': "50% deductible for business meals"
                }
                
                for category, amount in report['expenses']['category_breakdown'].items():
                    if category in deductible_categories:
                        st.write(f"**{category}**: ${amount:,.2f} - {deductible_categories[category]}")
                
                # Important notice
                st.info("""
                **Note**: 
                - Deductibility rules vary by country
                - Some expenses may require special documentation
                - Maintain proper receipts for all deductions
                """)
            else:
                st.info("No tax-deductible expenses identified")

class ComplianceChatInterface:
    """Manages the compliance Q&A interface"""
    
    def __init__(self):
        if 'tax_chat_history' not in st.session_state:
            st.session_state.tax_chat_history = []
    
    def display_common_questions(self):
        """Show pre-defined compliance questions"""
        common_questions = [
            "How can I maximize tax deductions for my business expenses?",
            "What expenses are deductible for freelancers and contractors?",
            "How should I categorize software and technology expenses for tax purposes?",
            "What tax benefits can I claim for home office and remote work?",
            "How do I properly track and report income from multiple sources?",
            "What are the tax implications of different business structures?",
            "How can I optimize my tax strategy for investment income?",
            "What records should I keep for tax audits and compliance?"
        ]
        
        selected_question = st.selectbox(
            "Common compliance questions:",
            ["Select a question..."] + common_questions
        )
        return selected_question
    
    def process_user_question(self, question: str):
        """Handle user questions and display responses"""
        if st.button("💡 Get Tax Optimization Advice") and question:
            with st.spinner("🧠 Analyzing tax optimization strategies..."):
                try:
                    assistant = TaxComplianceAssistant()
                    response = assistant.ask_compliance_question(question)
                    
                    # Add to chat history
                    st.session_state.tax_chat_history.append({
                        "question": question,
                        "response": response,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                except Exception as e:
                    st.error(f"Failed to get tax optimization advice: {str(e)}")
    
    def display_chat_history(self):
        """Show previous Q&A"""
        if st.session_state.tax_chat_history:
            st.subheader("Previous Q&A")
            for i, chat in enumerate(reversed(st.session_state.tax_chat_history)):
                with st.expander(f"Q: {chat['question']} ({chat['timestamp']})"):
                    st.write(chat['response'])
                    
                    # Disclaimer for all responses
                    if i == 0:  # Only show once
                        st.caption("""
                        **Disclaimer**: These responses are AI-generated tax optimization suggestions only. 
                        For legally binding tax advice, please consult a qualified tax professional.
                        """)

def tax_optimization_tab():
    """
    Main entry point for the Tax Optimizer dashboard tab.
    
    This function:
    - Displays important legal disclaimers
    - Shows tax insights and recommendations
    - Provides a compliance Q&A assistant
    - Manages all layout and component coordination
    
    Layout:
    - Left column: Tax calculations and visualizations
    - Right column: Compliance question answering interface
    
    Returns:
        None (renders Streamlit components directly)
        
    Side Effects:
        - Modifies Streamlit session state for chat history
        - Makes API calls to Together.ai for compliance advice
    """
    st.header("🧾 Tax Optimizer")
    
    # Important global notice
    st.warning("""
    **Important Legal Disclaimer**:
    - This tool provides general information only, not professional tax advice
    - Tax laws vary by jurisdiction and change frequently
    - Always verify information with official sources or qualified professionals
    - The developers assume no liability for decisions made based on this tool's outputs
    """)
    
    # Rest of your existing implementation...
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 Tax Optimization Insights")
        
        # Get financial data for the year
        report = TransactionManager.get_combined_financial_report('year')
        
        # Display tax optimization components
        TaxOptimizationDashboard.display_annual_tax_summary(report)
        TaxOptimizationDashboard.display_tax_deductible_expenses(report)
    
    with col2:
        st.subheader("🎯 Tax Optimization Assistant")
        
        # Initialize and display chat interface
        chat_interface = ComplianceChatInterface()
        
        # User can select common questions or ask their own
        selected_question = chat_interface.display_common_questions()
        user_question = st.text_input("Or ask your own question:")
        
        question_to_ask = user_question if user_question else (
            selected_question if selected_question != "Select a question..." else None
        )
        
        # Process and display questions
        chat_interface.process_user_question(question_to_ask)
        chat_interface.display_chat_history()