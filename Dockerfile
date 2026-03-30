# =============================================================================
# Vajra Exocortex -- Multi-stage Docker build
# Stage 1: Build the React frontend
# Stage 2: Run the FastAPI backend and serve the built frontend
# =============================================================================

# -- Stage 1: Frontend build ------------------------------------------------
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --frozen-lockfile 2>/dev/null || npm install
COPY frontend/ ./
RUN npm run build

# -- Stage 2: Python backend + static serve ---------------------------------
FROM python:3.11-slim
WORKDIR /code

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy backend source
COPY backend/ ./backend/
COPY main.py ./

# Copy built frontend into /code/frontend/dist so FastAPI can serve it
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
