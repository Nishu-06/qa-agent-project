# Autonomous QA Agent - Test Case and Script Generation

An intelligent, autonomous QA agent that constructs a "testing brain" from project documentation. The system ingests support documents (product specifications, UI/UX guidelines) alongside the HTML structure of a target web project to generate comprehensive, documentation-grounded test cases and executable Python Selenium scripts.

## Capabilities

The QA Agent operates in three phases:

1. **Knowledge Base Ingestion** - Processes and stores support documents and HTML content in a vector database for intelligent retrieval
2. **Test Case Generation** - Uses RAG (Retrieval-Augmented Generation) to create structured test cases grounded in the provided documentation
3. **Selenium Script Generation** - Converts generated test cases into production-ready, executable Python Selenium automation scripts

## Setup Instructions

### Python Version

This project requires **Python 3.10 or higher**. Verify your Python version:

```bash
python --version
```

### Dependencies

All required dependencies are listed in `requirements.txt`:

- `streamlit>=1.28.0` - Web UI framework
- `langchain>=0.1.0` - LangChain core library
- `langchain-core>=0.1.0` - LangChain core components
- `langchain-community>=0.0.20` - LangChain community integrations
- `langchain-openai>=0.1.0` - OpenAI integration for LangChain
- `openai>=1.0.0` - OpenAI Python SDK
- `unstructured>=0.10.30` - Document parsing
- `pymupdf>=1.23.0` - PDF parsing
- `chromadb>=0.4.15` - Vector database
- `python-dotenv>=1.0.0` - Environment variable management

### Virtual Environment Setup

It is recommended to use a virtual environment to isolate project dependencies:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Installing Dependencies

Once your virtual environment is activated, install all required packages:

```bash
pip install -r requirements.txt
```

### Additional Requirements

**OpenAI API Key Setup:**
- Get your OpenAI API key from https://platform.openai.com/api-keys
- Create a `.env` file in the project root directory
- Add your API key to the `.env` file:
  ```
  OPENAI_API_KEY=your_api_key_here
  ```
- Optional: You can also set custom models:
  ```
  OPENAI_LLM_MODEL=gpt-4o-mini
  OPENAI_EMBED_MODEL=text-embedding-3-small
  ```

## How to Run

### Local Development

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will launch in your default web browser at `http://localhost:8501`.

### Deployment (Render)

The application is fully deployable on Render or similar cloud platforms:

1. **Connect your GitHub repository** to Render
2. **Create a new Web Service** with the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
3. **Set Environment Variables** in Render dashboard:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - Optional: `OPENAI_LLM_MODEL` and `OPENAI_EMBED_MODEL`
4. **Deploy**: Render will automatically build and deploy your application

The app will be accessible at your Render-provided URL.

## Usage Examples (Workflow)

The QA Agent follows a three-phase workflow. Follow these steps to generate test cases and Selenium scripts:

### Phase 1: Knowledge Base Ingestion

**Objective:** Build a comprehensive knowledge base from your documentation and HTML content.

**Steps:**

1. **Upload Support Documents:**
   - In the "Support Documents" section, click "Select support documents"
   - Upload one or more support documents (e.g., `test_assets/product_specs.md`)
   - Supported formats: MD, TXT, JSON, PDF, DOCX, HTML

2. **Provide HTML Content:**
   - Choose either "Paste HTML" or "Upload HTML file"
   - If pasting: Copy and paste the HTML content into the text area
   - If uploading: Select `test_assets/checkout.html` or your HTML file
   - The HTML content provides the structure for Selenium selector identification

3. **Build Knowledge Base:**
   - Click the "🔨 Build Knowledge Base" button
   - Wait for the processing to complete (this may take a moment)
   - You will see a success message: "✅ Knowledge Base Built Successfully"
   - The system displays statistics: number of documents processed and HTML content size

**What Happens:**
- Documents are parsed and chunked into manageable pieces
- Text embeddings are generated using OpenAI's embedding models
- Content is stored in ChromaDB vector database with metadata
- HTML content is stored for Phase 3 script generation

### Phase 2: Test Case Generation

**Objective:** Generate structured test cases based on the knowledge base using RAG.

**Steps:**

1. **Navigate to Phase 2 Section:**
   - Ensure Phase 1 is completed (knowledge base is built)
   - Scroll to the "🧪 Phase 2: Test Case Generation" section

2. **Enter Test Case Generation Prompt:**
   - Option 1: Use the default AI-optimized prompt (checkbox enabled)
   - Option 2: Enter a custom prompt describing what test cases you want
   
   **Example Prompts:**
   ```
   Generate comprehensive test cases for the E-Shop Checkout system covering:
   1. Discount code functionality (SAVE15 code)
   2. Shipping options (Standard and Express)
   3. Form validation for all user detail fields
   4. Cart summary calculations
   5. Order completion workflow
   ```

3. **Generate Test Cases:**
   - Click "🚀 Generate Test Cases"
   - Wait for the RAG pipeline to process (may take 30-60 seconds)
   - The system retrieves relevant documentation chunks
   - LLM generates structured test cases grounded in the documentation

4. **Review Generated Test Cases:**
   - Test cases are displayed with:
     - **Test_ID**: Unique identifier (e.g., TC-001)
     - **Feature**: Feature being tested
     - **Test_Scenario**: Detailed test steps
     - **Expected_Result**: Expected outcome
     - **Grounded_In**: Source document reference
   - Expand any test case to view full details
   - Download test cases as JSON if needed

**What Happens:**
- User prompt is embedded and used to retrieve relevant document chunks
- Retrieved context + prompt is sent to LLM
- LLM generates structured JSON test cases
- All test cases reference source documents (no hallucinations)

### Phase 3: Selenium Script Generation

**Objective:** Convert a selected test case into an executable Python Selenium script.

**Steps:**

1. **Navigate to Phase 3 Section:**
   - Ensure Phase 2 is completed (test cases are generated)
   - Scroll to the "⚙️ Phase 3: Selenium Script Generation" section

2. **Select a Test Case:**
   - Use the dropdown to select a test case (e.g., "TC-001: Discount Code Application")
   - View test case details in the expandable section if needed

3. **Generate Selenium Script:**
   - Click "🚀 Generate Selenium Script"
   - Wait for script generation (may take 30-60 seconds)
   - The system:
     - Retrieves full HTML content
     - Retrieves relevant documentation snippets
     - Uses LLM to generate Python Selenium code

4. **Review and Download Script:**
   - The generated script is displayed in a code block with syntax highlighting
   - Review the script for accuracy
   - Click "📥 Download Selenium Script" to save the file

5. **Run the Script:**
   - Install Selenium dependencies: `pip install selenium webdriver-manager`
   - Update the HTML file path in the script (if needed)
   - Run: `python <script_name>.py`

**What Happens:**
- Full HTML content is retrieved for accurate selector identification
- Relevant documentation is retrieved for expected behavior
- LLM acts as a Selenium expert to generate production-ready code
- Script includes proper selectors, waits, and assertions

## Explanation of Included Support Documents

The project includes two key assets that work together to enable test generation:

### 1. `checkout.html` - Target Web Project

**Purpose:** This is the single-page E-Shop Checkout application that serves as the target for testing.

**Contribution to Testing:**
- **HTML Structure**: Provides the actual DOM structure for Selenium selector identification
- **Element IDs and Classes**: Contains the exact selectors (IDs, names, CSS classes) needed for automation
- **Form Fields**: Defines all input fields, buttons, and interactive elements
- **Validation Logic**: Contains client-side validation that test cases can verify
- **UI Elements**: Includes cart summary, discount code input, shipping options, etc.

**How it's Used:**
- Phase 1: Stored for reference during script generation
- Phase 3: Analyzed by LLM to identify stable selectors (IDs, names, CSS selectors)
- Phase 3: Used to generate accurate Selenium code that matches the actual HTML structure

### 2. `product_specs.md` - Product Specifications Document

**Purpose:** Contains feature specifications, business rules, and validation requirements for the checkout system.

**Contribution to Testing:**
- **Business Rules**: Defines discount code logic (e.g., "SAVE15 applies 15% discount")
- **Feature Specifications**: Describes shipping options, form validation rules, cart calculations
- **Expected Behaviors**: Provides the "ground truth" for what test cases should verify
- **Validation Requirements**: Specifies field validation rules (email format, phone length, etc.)

**How it's Used:**
- Phase 1: Parsed, chunked, and stored in vector database
- Phase 2: Retrieved via RAG to ground test case generation in actual specifications
- Phase 2: Ensures test cases reference real features, not hallucinated ones
- Phase 3: Retrieved to understand expected behavior for script assertions

**Example Content:**
- Discount code rules: "SAVE15 applies 15% off subtotal"
- Shipping costs: "Standard shipping is free, Express costs $10"
- Form validation: "Email must be valid format, phone must be 10-15 digits"
- Cart calculations: "Total = Subtotal - Discount + Shipping"

**Together, these documents ensure:**
- Test cases are based on real specifications (not assumptions)
- Selenium scripts use correct selectors from actual HTML
- Assertions verify documented expected behaviors
- No hallucinations or fabricated features

## Agent Components

The QA Agent leverages several key technologies:

- **LangChain**: Framework for building LLM applications, providing RAG pipeline components, document loaders, and chain orchestration
- **RAG (Retrieval-Augmented Generation)**: Technique that retrieves relevant document chunks before generating responses, ensuring test cases are grounded in documentation
- **ChromaDB**: Vector database that stores document embeddings, enabling semantic search and retrieval of relevant context
- **OpenAI API**: Cloud-based LLM and embedding services providing text generation (GPT models) and embeddings (text-embedding-3-small)
- **Streamlit**: Web framework for building the interactive user interface
- **Unstructured & PyMuPDF**: Document parsing libraries for extracting text from various file formats (PDF, DOCX, etc.)

## Project Structure

```
qa_agent_project/
├── app.py                 # Streamlit UI and Orchestration
├── backend.py             # Core QA Agent Backend Logic
├── requirements.txt       # Python dependencies
├── test_assets/          # Test files and support documents
│   ├── checkout.html     # E-Shop Checkout page (target web project)
│   └── product_specs.md  # Product specifications document
├── chroma_db/            # Vector database storage (auto-generated)
└── temp_uploads/          # Temporary file storage (auto-generated)
```

## Notes

- **OpenAI API Key**: Required for both LLM inference and embeddings. Get your key from https://platform.openai.com/api-keys
- **Default Models**: 
  - LLM: `gpt-4o-mini` (fast and cost-effective)
  - Embeddings: `text-embedding-3-small` (768 dimensions)
- **Vector Database**: Stored in `./chroma_db/` directory (automatically created)
- **Temporary Files**: Uploaded files are temporarily stored in `./temp_uploads/` and cleaned up after processing
- **Knowledge Grounding**: All test cases include a "Grounded_In" field referencing source documents to ensure no hallucinations
- **Deployment**: Fully deployable on Render or similar cloud platforms. Set `OPENAI_API_KEY` as an environment variable in your deployment settings

## Troubleshooting

**Issue**: "OPENAI_API_KEY environment variable is required"  
**Solution**: Create a `.env` file in the project root and add `OPENAI_API_KEY=your_key_here`, or set it as an environment variable

**Issue**: "Knowledge base not found"  
**Solution**: Complete Phase 1 first by building the knowledge base

**Issue**: "Error building knowledge base: Collection expecting embedding with dimension..."  
**Solution**: Delete the `./chroma_db/` directory and rebuild the knowledge base. This happens when switching embedding models

**Issue**: Selenium script doesn't run  
**Solution**: Install dependencies (`pip install selenium webdriver-manager`) and update the HTML file path in the script

**Issue**: API quota exceeded  
**Solution**: Check your OpenAI account usage and billing. Consider upgrading your plan or using rate limiting

---

**For questions or issues, please refer to the project documentation or check the Streamlit UI for system feedback messages.**
