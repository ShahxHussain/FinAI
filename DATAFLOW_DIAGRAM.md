# FinAI - Dataflow Diagram

## 🔄 Complete System Dataflow Architecture

```mermaid
graph TB
    %% External Inputs
    subgraph "📥 Input Sources"
        A1[Receipt Files<br/>PDF/Image/CSV/TXT]
        A2[Manual Income Entry]
        A3[Manual Transaction Entry]
        A4[Stock Symbols<br/>Investment Analysis]
        A5[Tax Questions<br/>Compliance Queries]
    end

    %% AI Processing Layer
    subgraph "🤖 AI Processing Layer"
        B1[Together.ai Client<br/>Document Processing]
        B2[Together.ai Client<br/>Text Generation]
        B3[Together.ai Client<br/>JSON Generation]
        B4[OCR Processing<br/>Pytesseract]
        B5[PDF Text Extraction<br/>PyPDF2]
    end

    %% Data Processing
    subgraph "⚙️ Data Processing"
        C1[Receipt Analysis<br/>Extract: Amount, Merchant,<br/>Date, Category, Line Items]
        C2[Income Data Validation<br/>Required Fields Check]
        C3[Transaction Data<br/>Confidence Scoring]
        C4[Financial Analysis<br/>Trends & Patterns]
        C5[Investment Analysis<br/>Market Intelligence]
    end

    %% Database Layer
    subgraph "🗄️ Snowflake Database"
        D1[transactions Table<br/>- id (Primary Key)<br/>- date, merchant, amount<br/>- confidence scores<br/>- category, description<br/>- is_reconciled]
        D2[income Table<br/>- id (Primary Key)<br/>- date, source, amount<br/>- category, payment_method<br/>- is_taxable, recurrence<br/>- tags (Array)]
        D3[enriched_transactions View<br/>Ordered by date DESC]
        D4[income_summary View<br/>Aggregated income data]
    end

    %% Business Logic Layer
    subgraph "🧠 Business Logic"
        E1[TransactionManager<br/>- log_receipt()<br/>- log_bulk_receipts()<br/>- get_recent_transactions()<br/>- update_category()<br/>- get_spending_analytics()]
        E2[IncomeManager<br/>- log_income()<br/>- get_income()<br/>- get_income_report()<br/>- get_monthly_income_average()]
        E3[Financial Analytics<br/>- get_combined_financial_report()<br/>- calculate_monthly_trend()<br/>- get_categorical_summary()]
        E4[Tax Optimization<br/>- TaxComplianceAssistant<br/>- TaxOptimizationDashboard]
        E5[Investment Planning<br/>- MarketIntelligence<br/>- InvestmentAdvisor]
    end

    %% Dashboard Components
    subgraph "📊 Dashboard Components"
        F1[Receipt Processing Tab<br/>- Single/Bulk Upload<br/>- AI Extraction<br/>- Data Validation<br/>- Save to DB]
        F2[Income Management Tab<br/>- Income Entry Form<br/>- Income History<br/>- Monthly Trends]
        F3[Financial Reports Tab<br/>- KPI Metrics<br/>- Interactive Charts<br/>- Time Period Analysis]
        F4[Tax & Compliance Tab<br/>- Tax Summary<br/>- Deductible Expenses<br/>- AI Q&A Chat]
        F5[Savings & Investing Tab<br/>- Goal Setting<br/>- AI Investment Advice<br/>- Savings Projections]
        F6[Investment Planning Tab<br/>- Stock Analysis<br/>- Market Intelligence<br/>- Risk Assessment]
    end

    %% Output Layer
    subgraph "📤 Output & Visualization"
        G1[Interactive Dashboards<br/>Streamlit Components]
        G2[Financial Reports<br/>PDF/Export]
        G3[AI Recommendations<br/>Investment Advice]
        G4[Tax Optimization<br/>Compliance Guidance]
        G5[Data Export<br/>CSV/JSON]
    end

    %% Data Flow Connections
    A1 --> B1
    A1 --> B4
    A1 --> B5
    A2 --> C2
    A3 --> C3
    A4 --> C5
    A5 --> B2

    B1 --> C1
    B2 --> C4
    B3 --> C1
    B4 --> C1
    B5 --> C1

    C1 --> E1
    C2 --> E2
    C3 --> E1
    C4 --> E3
    C5 --> E5

    E1 --> D1
    E2 --> D2
    E3 --> D3
    E3 --> D4

    D1 --> E1
    D2 --> E2
    D3 --> E3
    D4 --> E3

    E1 --> F1
    E2 --> F2
    E3 --> F3
    E4 --> F4
    E5 --> F5
    E5 --> F6

    F1 --> G1
    F2 --> G1
    F3 --> G1
    F3 --> G2
    F4 --> G1
    F4 --> G4
    F5 --> G1
    F5 --> G3
    F6 --> G1
    F6 --> G3

    %% Styling
    classDef inputClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef aiClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef processClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef dbClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef logicClass fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef dashboardClass fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    classDef outputClass fill:#e0f2f1,stroke:#004d40,stroke-width:2px

    class A1,A2,A3,A4,A5 inputClass
    class B1,B2,B3,B4,B5 aiClass
    class C1,C2,C3,C4,C5 processClass
    class D1,D2,D3,D4 dbClass
    class E1,E2,E3,E4,E5 logicClass
    class F1,F2,F3,F4,F5,F6 dashboardClass
    class G1,G2,G3,G4,G5 outputClass
```

## 📋 Detailed Data Flow Description

### **1. Input Sources (📥)**
- **Receipt Files**: PDF, images, CSV, text files uploaded by users
- **Manual Income Entry**: User-entered income data through forms
- **Manual Transaction Entry**: Direct transaction input
- **Stock Symbols**: For investment analysis
- **Tax Questions**: User queries for compliance advice

### **2. AI Processing Layer (🤖)**
- **Together.ai Client**: Unified AI service for all processing
- **Document Processing**: Receipt analysis and data extraction
- **Text Generation**: Financial advice and recommendations
- **JSON Generation**: Structured data output
- **OCR Processing**: Image text extraction
- **PDF Processing**: PDF text extraction

### **3. Data Processing (⚙️)**
- **Receipt Analysis**: Extracts amount, merchant, date, category, line items
- **Income Validation**: Validates required fields and data integrity
- **Transaction Processing**: Applies confidence scoring
- **Financial Analytics**: Calculates trends and patterns
- **Investment Analysis**: Market intelligence and stock analysis

### **4. Database Layer (🗄️)**
- **transactions Table**: Stores all expense transactions with confidence scores
- **income Table**: Stores income records with categorization
- **Views**: Optimized views for reporting and analytics
- **Data Relationships**: Links transactions and income for comprehensive reporting

### **5. Business Logic Layer (🧠)**
- **TransactionManager**: Handles all transaction operations
- **IncomeManager**: Manages income data and reporting
- **Financial Analytics**: Generates comprehensive financial reports
- **Tax Optimization**: Provides tax advice and compliance guidance
- **Investment Planning**: Offers investment recommendations

### **6. Dashboard Components (📊)**
- **Receipt Processing**: Upload and process receipts
- **Income Management**: Track and manage income
- **Financial Reports**: Interactive dashboards and analytics
- **Tax & Compliance**: Tax optimization and compliance tools
- **Savings & Investing**: Goal-based financial planning
- **Investment Planning**: Stock analysis and recommendations

### **7. Output & Visualization (📤)**
- **Interactive Dashboards**: Real-time financial insights
- **Financial Reports**: Comprehensive analytics and trends
- **AI Recommendations**: Personalized investment advice
- **Tax Optimization**: Compliance guidance and deductions
- **Data Export**: CSV/JSON exports for external use

## 🔄 Key Data Flow Patterns

### **Receipt Processing Flow:**
```
Receipt File → OCR/PDF Processing → AI Analysis → Data Validation → Database Storage → Dashboard Display
```

### **Income Management Flow:**
```
Manual Entry → Data Validation → Database Storage → Analytics Processing → Dashboard Reports
```

### **Financial Reporting Flow:**
```
Database Query → Data Aggregation → Analytics Processing → Visualization → Interactive Dashboard
```

### **Investment Analysis Flow:**
```
Stock Symbol → AI Market Analysis → Risk Assessment → Recommendations → Dashboard Display
```

### **Tax Optimization Flow:**
```
User Question → AI Analysis → Compliance Check → Tax Advice → Dashboard Display
```

## 🗄️ Database Schema Overview

### **transactions Table:**
```sql
CREATE TABLE transactions (
    id STRING PRIMARY KEY,
    date TIMESTAMP_NTZ,
    merchant STRING,
    merchant_confidence FLOAT,
    description STRING,
    amount FLOAT,
    amount_confidence FLOAT,
    category STRING,
    category_confidence FLOAT,
    date_confidence FLOAT,
    is_reconciled BOOLEAN DEFAULT FALSE
)
```

### **income Table:**
```sql
CREATE TABLE income (
    id STRING PRIMARY KEY,
    date TIMESTAMP_NTZ,
    source STRING,
    amount FLOAT,
    category STRING,
    payment_method STRING,
    description STRING,
    is_taxable BOOLEAN DEFAULT TRUE,
    recurrence STRING,
    tags ARRAY
)
```

## 🔐 Security & Data Protection

### **Data Encryption:**
- API keys stored in Streamlit secrets
- Database connections secured
- HTTPS for all external communications

### **Data Validation:**
- Input validation at multiple layers
- Confidence scoring for AI-extracted data
- Error handling and logging

### **Access Control:**
- Database user permissions
- API rate limiting
- Session management

## 📊 Performance Considerations

### **Database Optimization:**
- Indexed queries for fast retrieval
- Views for common operations
- Connection pooling

### **AI Processing:**
- Async processing for bulk operations
- Caching for repeated queries
- Error handling and retries

### **Dashboard Performance:**
- Lazy loading of data
- Pagination for large datasets
- Real-time updates where appropriate

This dataflow diagram provides a comprehensive view of how data moves through the FinAI system, from input sources through AI processing, database storage, business logic, and finally to user-facing dashboards and reports. 