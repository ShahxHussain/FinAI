import streamlit as st
import requests
import os
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from typing import Dict, Any
from utils.together_client import TogetherClient

# --- Configuration ---
TOGETHER_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"

# --- API Clients ---
class TogetherClientWrapper:
    def __init__(self):
        self.client = TogetherClient()

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        return self.client.generate_text(prompt, temperature, max_tokens=4000)

    def generate_json(self, prompt: str, temperature: float = 0.1) -> Dict:
        return self.client.generate_json(prompt, temperature)

# --- Financial Services ---
class MarketIntelligence:
    def __init__(self):
        self.together = TogetherClientWrapper()
    
    def analyze_security(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """Comprehensive security analysis with Groq"""
        # Main analysis prompt
        analysis_prompt = f"""Perform professional analysis for {symbol} (last {days} days):
        
        1. Technical Analysis:
        - Trend analysis with moving averages
        - Key support/resistance levels
        - RSI and MACD indicators
        
        2. Fundamental Analysis:
        - Valuation metrics (P/E, P/B, EV/EBITDA)
        - Growth projections
        - Dividend analysis if applicable
        
        3. Risk Assessment:
        - Volatility metrics
        - Liquidity analysis
        - Sector-specific risks
        
        4. Recommendation:
        - Buy/Hold/Sell with price targets
        - Optimal entry/exit points
        
        Format as markdown with clear sections."""
        
        analysis = self.together.generate(analysis_prompt)
        
        # Generate visual data for charts - with improved JSON handling
        risk_prompt = f"""Provide a risk assessment for {symbol} in this EXACT JSON format:
        {{
            "volatility_score": 0-100,
            "liquidity_score": 0-100,
            "sector_risk": "Low/Medium/High",
            "overall_risk_rating": "Low/Medium/High",
            "risk_factors": ["list", "of", "key", "risks"]
        }}
        
        Only return the JSON object, nothing else."""
        
        try:
            risk_data = self.together.generate_json(risk_prompt, temperature=0.1)
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse risk assessment: {str(e)}")
            st.warning(f"Raw response: {risk_response}")
            risk_data = {
                "volatility_score": 50,
                "liquidity_score": 50,
                "sector_risk": "Medium",
                "overall_risk_rating": "Medium",
                "risk_factors": ["Data unavailable"],
                "error": True
            }
        except Exception as e:
            st.error(f"Risk assessment failed: {str(e)}")
            risk_data = {
                "volatility_score": 50,
                "liquidity_score": 50,
                "sector_risk": "Medium",
                "overall_risk_rating": "Medium",
                "risk_factors": ["Assessment failed"],
                "error": True
            }
        
        return {
            "analysis": analysis,
            "risk_data": risk_data
        }
# --- Streamlit UI ---
def detail_investmentplan():
    st.header("📈 Market Intelligence")
    symbol = st.text_input("Enter ticker symbol", "AAPL").upper()
    analysis_days = st.slider("Analysis period (days)", 7, 365, 30)
        
    if st.button("Analyze Security"):
        with st.spinner("Running comprehensive analysis..."):
            market = MarketIntelligence()
            result = market.analyze_security(symbol, analysis_days)
                
            # Display results
            st.subheader(f"{symbol} Analysis Report")
            st.markdown(result["analysis"])
                
            # Risk visualization
            st.subheader("Risk Assessment")
            risk_df = pd.DataFrame.from_dict(result["risk_data"], orient="index").reset_index()
            risk_df.columns = ["Metric", "Value"]
            fig = px.bar(risk_df, x="Metric", y="Value", 
                         title="Risk Profile", color="Metric")
            st.plotly_chart(fig, use_container_width=True)
    
    