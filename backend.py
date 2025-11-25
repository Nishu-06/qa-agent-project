"""
Backend module for Autonomous QA Agent - Knowledge Base Ingestion Logic
"""
import os
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
import fitz  # PyMuPDF
from unstructured.partition.auto import partition
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


class TestCase(BaseModel):
    """Pydantic schema for a single test case."""
    Test_ID: str = Field(description="Unique identifier, e.g., TC-001.")
    Feature: str = Field(description="The feature being tested, e.g., Discount Code.")
    Test_Scenario: str = Field(description="The specific steps and inputs for the test.")
    Expected_Result: str = Field(description="The outcome expected based on documentation.")
    Triggering_Rule: str = Field(description="Specific rule, requirement, or trigger condition covered by this test.")
    Grounded_In: str = Field(description="The source document(s) used for reasoning, e.g., product_specs.md, checkout.html.")


class TestCaseList(BaseModel):
    """Wrapper for a list of test cases."""
    test_cases: List[TestCase] = Field(description="List of generated test cases")


class QAAgentBackend:
    """Backend class for handling knowledge base ingestion and document processing."""
    
    def __init__(self):
        """Initialize the backend with vector store and embeddings."""
        self.vector_store = None
        self.html_content = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Configure OpenAI API
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required for OpenAI integration."
            )

        embed_model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
        llm_model = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
        self.persist_directory = "./chroma_db"

        # Initialize OpenAI embeddings
        try:
            self.embeddings = OpenAIEmbeddings(
                model=embed_model,
                openai_api_key=openai_api_key,
            )
            print(f"Using OpenAI embeddings ({embed_model})")
        except Exception as exc:
            raise RuntimeError("Failed to initialize OpenAI embeddings.") from exc
        
        # Initialize OpenAI LLM
        try:
            self.llm = ChatOpenAI(
                model=llm_model,
                temperature=0.1,
                openai_api_key=openai_api_key,
            )
            print(f"Using OpenAI LLM ({llm_model})")
        except Exception as exc:
            raise RuntimeError("Failed to initialize OpenAI LLM. Check your API key and model name.") from exc
        
    def _run_llm(self, prompt: str) -> str:
        """Invoke OpenAI model and return plain text."""
        try:
            response = self.llm.invoke(prompt)
            if isinstance(response, str):
                return response
            # Extract content from LangChain message object
            if hasattr(response, 'content'):
                return response.content
            elif hasattr(response, 'text'):
                return response.text
            else:
                return str(response)
        except Exception as exc:
            raise RuntimeError(f"OpenAI generation failed: {exc}") from exc
    
    def _parse_document(self, file_path: str) -> str:
        """
        Parse a document based on its file extension.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text content from the document
        """
        file_ext = Path(file_path).suffix.lower()
        text_content = ""
        
        try:
            if file_ext == '.pdf':
                # Use PyMuPDF for PDF parsing
                doc = fitz.open(file_path)
                for page in doc:
                    text_content += page.get_text()
                doc.close()
            elif file_ext in ['.md', '.txt']:
                # Read text files directly
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            elif file_ext == '.json':
                # Read JSON files
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            else:
                # Use unstructured for other file types
                elements = partition(filename=file_path)
                text_content = "\n\n".join([str(el) for el in elements])
        except Exception as e:
            print(f"Error parsing {file_path}: {str(e)}")
            # Fallback: try reading as text
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text_content = f.read()
            except:
                text_content = ""
        
        return text_content
    
    def ingest_documents(self, support_docs_paths: List[str], html_content: str) -> Dict[str, Any]:
        """
        Ingest support documents and HTML content into the knowledge base.
        
        Args:
            support_docs_paths: List of paths to support documents
            html_content: HTML content string
            
        Returns:
            Dictionary with status and message
        """
        try:
            # Store HTML content separately (strip whitespace but keep content)
            self.html_content = html_content.strip() if html_content else ""
            
            # Parse all support documents
            all_texts = []
            for doc_path in support_docs_paths:
                if os.path.exists(doc_path):
                    text = self._parse_document(doc_path)
                    if text:
                        all_texts.append(text)
                else:
                    print(f"Warning: File not found: {doc_path}")
            
            if not all_texts:
                return {
                    "status": "error",
                    "message": "No valid documents were parsed. Please check file paths."
                }
            
            # Combine all texts
            combined_text = "\n\n---\n\n".join(all_texts)
            
            # Split into chunks
            chunks = self.text_splitter.split_text(combined_text)
            
            # Create documents with metadata
            documents = [
                Document(
                    page_content=chunk,
                    metadata={"source": "support_docs", "chunk_index": i}
                )
                for i, chunk in enumerate(chunks)
            ]
            
            # Ensure previous ChromaDB data is removed to prevent dimension mismatches
            if os.path.exists(self.persist_directory):
                import shutil
                shutil.rmtree(self.persist_directory, ignore_errors=True)
            
            # Create new vector store with current embeddings
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
            )
            
            return {
                "status": "success",
                "message": "Knowledge Base Built Successfully."
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error building knowledge base: {str(e)}"
            }
    
    def _clean_json_response(self, text: str) -> str:
        """
        Clean and extract JSON from LLM response.
        Handles common issues like trailing commas, comments, etc.
        """
        # Remove markdown code blocks if present
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Find JSON object boundaries
        json_start = text.find('{')
        json_end = text.rfind('}')
        
        if json_start == -1 or json_end == -1 or json_end <= json_start:
            return text
        
        json_str = text[json_start:json_end + 1]
        
        # Try to fix common JSON issues
        # Remove trailing commas before closing braces/brackets
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        # Remove comments (not standard JSON but sometimes LLMs add them)
        json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        return json_str
    
    def _parse_json_with_fallback(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON with multiple fallback strategies.
        """
        # Strategy 1: Try cleaning and parsing
        try:
            cleaned = self._clean_json_response(response)
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Try to extract just the test_cases array
        try:
            # Look for test_cases array pattern
            match = re.search(r'"test_cases"\s*:\s*\[(.*?)\]', response, re.DOTALL)
            if match:
                # Try to parse individual test case objects
                test_cases_text = match.group(1)
                # Split by test case boundaries (rough heuristic)
                test_cases = []
                current_case = {}
                in_string = False
                escape_next = False
                key = None
                value = None
                
                # This is complex, let's try a simpler approach
                # Extract each test case object
                case_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                cases = re.findall(case_pattern, test_cases_text)
                for case_str in cases:
                    try:
                        case_obj = json.loads(case_str)
                        test_cases.append(case_obj)
                    except:
                        continue
                
                if test_cases:
                    return {"test_cases": test_cases}
        except Exception:
            pass
        
        # Strategy 3: Try to find and parse individual test case objects
        try:
            # Find all objects that look like test cases
            test_case_pattern = r'\{\s*"Test_ID"[^}]*\}'
            matches = re.findall(test_case_pattern, response, re.DOTALL)
            test_cases = []
            for match in matches:
                try:
                    # Clean the match
                    cleaned_match = self._clean_json_response(match)
                    case_obj = json.loads(cleaned_match)
                    test_cases.append(case_obj)
                except:
                    continue
            
            if test_cases:
                return {"test_cases": test_cases}
        except Exception:
            pass
        
        # If all strategies fail, raise the original error
        raise json.JSONDecodeError("Could not parse JSON with any strategy", response, 0)
    
    def generate_test_cases(self, prompt: str) -> Dict[str, Any]:
        """
        Generate test cases using RAG pipeline based on the knowledge base.
        
        Args:
            prompt: User prompt describing what test cases to generate
            
        Returns:
            Dictionary with status, message, and generated test cases
        """
        try:
            # Check if knowledge base exists
            if self.vector_store is None:
                # Try to load existing vector store
                if os.path.exists(self.persist_directory):
                    try:
                        self.vector_store = Chroma(
                            persist_directory=self.persist_directory,
                            embedding_function=self.embeddings,
                        )
                    except Exception as load_err:
                        error_msg = str(load_err).lower()
                        if "dimension" in error_msg or "embedding" in error_msg:
                            import shutil
                            shutil.rmtree(self.persist_directory, ignore_errors=True)
                            return {
                                "status": "error",
                                "message": "Knowledge base embeddings are outdated. Please rebuild the knowledge base (Phase 1).",
                                "test_cases": []
                            }
                        raise
                else:
                    return {
                        "status": "error",
                        "message": "Knowledge base not found. Please build the knowledge base first.",
                        "test_cases": []
                    }
            
            # Create retriever from vector store
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}  # Retrieve top 5 relevant chunks
            )
            
            # Create QA Engineer prompt template
            qa_prompt_template = """You are an expert QA Engineer tasked with generating comprehensive test cases based on the provided documentation and HTML content.

**Your Role:**
- Analyze the retrieved context from support documents and HTML content
- Generate test cases that validate features, business rules, and functionality
- Ensure each test case is grounded in the provided documentation
- Create test cases that cover positive, negative, and edge cases

**Context from Knowledge Base:**
{context}

**User Request:**
{user_prompt}

**HTML Content (if available):**
{html_content}

**Instructions:**
1. Review the retrieved context carefully
2. Identify all features, business rules, validation requirements, and functionality
3. Generate comprehensive test cases covering:
   - Feature functionality (e.g., discount codes, shipping options)
   - Form validation rules (e.g., email, phone, address validation)
   - Business logic (e.g., price calculations, discount applications)
   - UI/UX requirements (e.g., error messages, real-time updates)
   - Edge cases and boundary conditions

4. For each test case, provide:
   - A unique Test_ID (format: TC-XXX)
   - The Feature being tested
   - Detailed Test_Scenario with specific steps and inputs
   - Expected_Result based on the documentation
   - Triggering_Rule: The exact business rule, validation, or requirement enforced by this test
   - Grounded_In: List the source document(s) used (e.g., product_specs.md, checkout.html)

5. Output ONLY valid JSON in the following format. CRITICAL: The output must be valid JSON that can be parsed directly:
{{
  "test_cases": [
    {{
      "Test_ID": "TC-001",
      "Feature": "Discount Code Application",
      "Test_Scenario": "Step 1: Navigate to checkout page. Step 2: Enter discount code SAVE15 in the discount code field. Step 3: Click Apply button.",
      "Expected_Result": "Discount of 15% should be applied to the subtotal. Discount amount should be displayed in the cart summary. Total should be updated to reflect the discount.",
      "Triggering_Rule": "SAVE15 requires case-sensitive exact match and applies 15% off subtotal",
      "Grounded_In": "product_specs.md - SAVE15 Discount Code section"
    }}
  ]
}}

**CRITICAL JSON FORMATTING RULES:**
- Output ONLY the JSON object, no markdown code blocks, no explanations before or after
- Use double quotes for all strings and keys
- Escape any double quotes inside string values using backslash: \\"
- Do NOT include trailing commas after the last item in arrays or objects
- Ensure all strings are properly closed with quotes
- Test_Scenario and Expected_Result can contain multiple sentences - keep them as single strings
- If a string contains newlines, represent them as \\n or keep as a single line

**Important:**
- Base your test cases STRICTLY on the retrieved context
- Do not make assumptions beyond what is documented
- Ensure test scenarios are specific and actionable
- Include both positive and negative test cases
- Reference the specific document sections in Grounded_In field

**OUTPUT FORMAT:** Start your response with {{ and end with }}. Output ONLY the JSON, nothing else.

Generate the test cases now:"""
            
            # Create the prompt template
            prompt_template = PromptTemplate(
                template=qa_prompt_template,
                input_variables=["context", "user_prompt", "html_content"]
            )
            
            # Create RAG chain
            def format_docs(docs):
                return "\n\n".join([f"Document {i+1}:\n{doc.page_content}\nSource: {doc.metadata.get('source', 'unknown')}" 
                                   for i, doc in enumerate(docs)])
            
            # Get HTML content for context (if available)
            html_context = self.html_content if self.html_content else "No HTML content available."
            
            # Create the RAG chain
            def format_docs_wrapper(docs):
                return format_docs(docs)
            
            # Retrieve relevant documents
            retrieved_docs = retriever.invoke(prompt)
            context = format_docs(retrieved_docs)
            
            # Format the prompt with all variables
            formatted_prompt = prompt_template.format(
                context=context,
                user_prompt=prompt,
                html_content=html_context
            )
            
            # Invoke Gemini
            response = self._run_llm(formatted_prompt)
            
            # Parse JSON from response with multiple fallback strategies
            try:
                parsed_response = self._parse_json_with_fallback(response)
            except json.JSONDecodeError as e:
                # If JSON parsing fails, try to extract test cases manually
                # Look for test case patterns in the response
                test_cases = []
                
                # Try to find test cases using regex patterns
                # Pattern for Test_ID
                test_id_pattern = r'Test_ID["\']?\s*[:=]\s*["\']?([^"\',}\n]+)'
                feature_pattern = r'Feature["\']?\s*[:=]\s*["\']?([^"\',}\n]+)'
                scenario_pattern = r'Test_Scenario["\']?\s*[:=]\s*["\']?([^"\',}\n]+)'
                expected_pattern = r'Expected_Result["\']?\s*[:=]\s*["\']?([^"\',}\n]+)'
                grounded_pattern = r'Grounded_In["\']?\s*[:=]\s*["\']?([^"\',}\n]+)'
                trigger_pattern = r'Triggering_Rule["\']?\s*[:=]\s*["\']?([^"\',}\n]+)'
                
                # Split response into potential test case sections
                sections = re.split(r'Test_ID|TC-\d+', response, flags=re.IGNORECASE)
                
                for section in sections[1:]:  # Skip first empty section
                    try:
                        test_id_match = re.search(test_id_pattern, section, re.IGNORECASE)
                        feature_match = re.search(feature_pattern, section, re.IGNORECASE)
                        scenario_match = re.search(scenario_pattern, section, re.IGNORECASE | re.DOTALL)
                        expected_match = re.search(expected_pattern, section, re.IGNORECASE | re.DOTALL)
                        grounded_match = re.search(grounded_pattern, section, re.IGNORECASE)
                        trigger_match = re.search(trigger_pattern, section, re.IGNORECASE)
                        
                        if test_id_match or feature_match:
                            tc = {
                                "Test_ID": test_id_match.group(1).strip() if test_id_match else f"TC-{len(test_cases)+1:03d}",
                                "Feature": feature_match.group(1).strip() if feature_match else "Unknown Feature",
                                "Test_Scenario": scenario_match.group(1).strip() if scenario_match else "See raw response",
                                "Expected_Result": expected_match.group(1).strip() if expected_match else "See raw response",
                                "Triggering_Rule": trigger_match.group(1).strip() if trigger_match else "Not specified",
                                "Grounded_In": grounded_match.group(1).strip() if grounded_match else "Unknown"
                            }
                            test_cases.append(tc)
                    except Exception:
                        continue
                
                if test_cases:
                    # If we extracted some test cases, use them
                    parsed_response = {"test_cases": test_cases}
                else:
                    # If all parsing strategies fail, return error with raw response
                    return {
                        "status": "error",
                        "message": f"Failed to parse JSON response from LLM: {str(e)}. Attempted multiple parsing strategies.",
                        "raw_response": response[:2000],  # Limit response length
                        "test_cases": []
                    }
            
            # Extract test cases
            test_cases = parsed_response.get("test_cases", [])
            
            # Validate test cases structure
            validated_test_cases = []
            for tc in test_cases:
                try:
                    # Validate using Pydantic
                    validated_tc = TestCase(**tc)
                    validated_test_cases.append(validated_tc.dict())
                except Exception as e:
                    print(f"Warning: Skipping invalid test case: {str(e)}")
                    continue
            
            return {
                "status": "success",
                "message": f"Generated {len(validated_test_cases)} test cases successfully.",
                "test_cases": validated_test_cases
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error generating test cases: {str(e)}",
                "test_cases": []
            }
    
    def generate_selenium_script(self, test_case: dict) -> Dict[str, Any]:
        """
        Generate a runnable Python Selenium script for a given test case.
        
        Args:
            test_case: Dictionary containing test case information (Test_ID, Feature, Test_Scenario, Expected_Result, Grounded_In)
            
        Returns:
            Dictionary with status, message, and generated script
        """
        try:
            # Check if knowledge base exists
            if self.vector_store is None:
                # Try to load existing vector store
                if os.path.exists(self.persist_directory):
                    try:
                        self.vector_store = Chroma(
                            persist_directory=self.persist_directory,
                            embedding_function=self.embeddings,
                        )
                    except Exception as load_err:
                        error_msg = str(load_err).lower()
                        if "dimension" in error_msg or "embedding" in error_msg:
                            import shutil
                            shutil.rmtree(self.persist_directory, ignore_errors=True)
                            return {
                                "status": "error",
                                "message": "Knowledge base embeddings are outdated. Please rebuild the knowledge base (Phase 1).",
                                "script": ""
                            }
                        raise
                else:
                    return {
                        "status": "error",
                        "message": "Knowledge base not found. Please build the knowledge base first.",
                        "script": ""
                    }
            
            # Check if HTML content is available
            if not self.html_content or len(self.html_content.strip()) == 0:
                return {
                    "status": "error",
                    "message": "HTML content not found. Please upload HTML content in Phase 1 and rebuild the knowledge base.",
                    "script": ""
                }
            
            # Retrieve relevant documentation chunks based on test case
            # Use Test_Scenario and Feature to create a search query
            search_query = f"{test_case.get('Feature', '')} {test_case.get('Test_Scenario', '')}"
            
            # Create retriever from vector store
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}  # Retrieve top 5 relevant chunks
            )
            
            # Retrieve relevant documentation
            retrieved_docs = retriever.invoke(search_query)
            
            # Format retrieved documentation
            def format_docs(docs):
                return "\n\n".join([
                    f"Document {i+1}:\n{doc.page_content}\nSource: {doc.metadata.get('source', 'unknown')}" 
                    for i, doc in enumerate(docs)
                ])
            
            documentation_context = format_docs(retrieved_docs)
            
            # Format test case as JSON for the prompt
            test_case_json = json.dumps(test_case, indent=2)
            
            # Create Selenium Expert prompt template
            selenium_prompt_template = """You are a highly experienced Python Selenium Expert with deep knowledge of web automation, element location strategies, and best practices for writing maintainable test scripts.

**Your Task:**
Generate a complete, runnable Python Selenium script that automates the test case provided below. The script must be production-ready, well-structured, and follow Selenium best practices.

**Test Case to Automate:**
{test_case_json}

**Full HTML Content (checkout.html):**
{html_content}

**Relevant Documentation Context:**
{documentation_context}

**Requirements for the Generated Script:**

1. **Script Structure:**
   - Import all necessary modules (selenium, time, etc.)
   - Use WebDriver Manager or provide clear instructions for driver setup
   - Include proper error handling
   - Add comments explaining key steps
   - Follow PEP 8 style guidelines

2. **Element Location:**
   - Analyze the HTML content carefully to find the most stable selectors
   - Prefer IDs > Names > CSS Selectors > XPath (in that order of preference)
   - Use explicit waits (WebDriverWait) instead of implicit waits or time.sleep()
   - Ensure selectors are robust and won't break with minor HTML changes
   - For form fields, use the exact IDs/names from the HTML (e.g., id="full-name", id="email", etc.)
   - For buttons, use appropriate selectors (e.g., id="discount-code", onclick attributes, etc.)

3. **Test Execution:**
   - Initialize WebDriver (Chrome recommended, with options for headless mode)
   - Navigate to a local HTML file or provide instructions for serving the HTML
   - Execute all steps from the Test_Scenario
   - Perform actions in the correct sequence as specified

4. **Assertions:**
   - Add assertions based on the Expected_Result
   - Verify element states, text content, calculations, etc.
   - Use explicit assertions (assert statements or unittest assertions)
   - Verify discount calculations if applicable
   - Verify form validation messages if applicable
   - Verify shipping cost updates if applicable

5. **Specific Implementation Details:**
   - For discount code: Enter the code and click Apply, then verify discount amount
   - For form fields: Fill all required fields with valid test data
   - For shipping options: Select the shipping method and verify cost update
   - For validation: Test both valid and invalid inputs as per the test scenario
   - Use WebDriverWait with expected_conditions for element visibility, clickability, etc.

6. **Output Format:**
   - Output ONLY the Python script code
   - Do not include markdown code blocks (no ```python or ```)
   - Start directly with import statements
   - Include a main block or clear execution instructions
   - Add a comment at the top with the Test_ID

**Example Script Structure:**
```python
# Test Case: TC-001 - Discount Code Application
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Setup WebDriver
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Uncomment for headless mode
driver = webdriver.Chrome(options=chrome_options)

try:
    # Navigate to the HTML file
    driver.get("file:///path/to/checkout.html")
    
    # Wait for page to load
    wait = WebDriverWait(driver, 10)
    
    # Your test steps here based on Test_Scenario
    # ...
    
    # Your assertions here based on Expected_Result
    # ...
    
    print("Test passed!")
    
finally:
    driver.quit()
```

**Important Notes:**
- Use the exact element IDs, names, or selectors from the provided HTML
- Ensure all actions match the Test_Scenario steps
- All assertions must verify the Expected_Result
- The script should be immediately runnable (provide file path instructions if needed)
- Handle dynamic content with proper waits
- Use try-finally to ensure driver cleanup

Generate the complete Selenium script now:"""
            
            # Create the prompt template
            prompt_template = PromptTemplate(
                template=selenium_prompt_template,
                input_variables=["test_case_json", "html_content", "documentation_context"]
            )
            
            # Format the prompt
            formatted_prompt = prompt_template.format(
                test_case_json=test_case_json,
                html_content=self.html_content,
                documentation_context=documentation_context
            )
            
            # Invoke Gemini to generate the script
            script = self._run_llm(formatted_prompt)
            
            # Convert literal \n to actual newlines
            script = script.replace('\\n', '\n')
            
            # Clean up the script (remove markdown code blocks if present)
            script = re.sub(r'```python\s*', '', script)
            script = re.sub(r'```\s*', '', script)
            script = script.strip()
            
            # Remove any leading text before the actual script starts
            # Look for common patterns like "Here's the complete script:" etc.
            lines = script.split('\n')
            script_start_idx = 0
            for i, line in enumerate(lines):
                # Skip lines that are clearly not code (explanatory text)
                if any(phrase in line.lower() for phrase in ['here\'s', 'here is', 'complete script', 'selenium script']):
                    continue
                # If we find a line that looks like code (import, from, #, def, class, etc.)
                if any(line.strip().startswith(keyword) for keyword in ['import', 'from', '#', 'def ', 'class ', 'try:', 'if ']):
                    script_start_idx = i
                    break
            
            script = '\n'.join(lines[script_start_idx:]).strip()
            
            # Extract script if it's wrapped in markdown
            if script.startswith('```'):
                # Find the actual code block
                lines = script.split('\n')
                script_lines = []
                in_code_block = False
                for line in lines:
                    if line.strip().startswith('```'):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block or (not script_lines and not line.strip().startswith('```')):
                        script_lines.append(line)
                script = '\n'.join(script_lines).strip()
            
            return {
                "status": "success",
                "message": f"Selenium script generated successfully for {test_case.get('Test_ID', 'test case')}.",
                "script": script,
                "test_case": test_case
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error generating Selenium script: {str(e)}",
                "script": "",
                "test_case": test_case
            }
