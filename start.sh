#!/bin/bash
# Start FastAPI backend
python backend.py &
# Start Streamlit frontend
streamlit run app.py --server.port $PORT --server.address 0.0.0.0

