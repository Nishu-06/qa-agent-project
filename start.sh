#!/bin/bash
# Start Streamlit frontend (backend.py is imported as a module, not run separately)
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
