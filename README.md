# Stack Wrangler Monorepo

A monorepo containing three interconnected services that communicate via HTTP for local development.

## Architecture

- **Frontend**: Next.js with TypeScript (Port 3000)
- **Backend**: Rust with Actix-web (Port 8000)
- **AI Model**: Python with FastAPI & PyTorch (Port 8001)

## Prerequisites

- **Bun** 1.2+ (Node.js runtime & package manager - much faster than npm!)
- **Rust** 1.75+ with cargo
- **uv** (Python package manager - 10x faster than pip!)
- **Python** 3.11+
- **Docker & Docker Compose** (optional)

## Quick Start

### Option 1: Run with Docker Compose

```bash
docker-compose up
```

This will start all three services with hot reloading enabled.

### Option 2: Run Services Individually

#### 1. Install Dependencies

```bash
# Root level (for orchestration scripts)
bun install

# Frontend (lightning fast with bun!)
cd frontend
bun install

# Backend
cd ../backend
cargo build

# AI Model (super fast with uv!)
cd ../ai-model
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -r requirements.txt
```

#### 2. Start Services

In separate terminal windows:

```bash
# Terminal 1 - Frontend
cd frontend
bun run dev

# Terminal 2 - Backend
cd backend
cargo run
# Or with auto-reload: cargo watch -x run

# Terminal 3 - AI Model
cd ai-model
source .venv/bin/activate
python app.py
```

#### 3. Run All Services Concurrently

From the root directory:

```bash
bun run dev
```

Note: This requires all dependencies to be installed first.

## Service Endpoints

### Frontend (http://localhost:3000)
- Main dashboard with service status checker
- Data processing interface
- Model training interface

### Backend (http://localhost:8000)
- `GET /api/health` - Health check
- `POST /api/process` - Process data (calculates mean)
- `POST /api/predict` - Forward prediction to AI service

### AI Model (http://localhost:8001)
- `GET /api/health` - Health check
- `POST /api/predict` - Make prediction
- `POST /api/train` - Train the model
- `GET /api/model/info` - Get model information

## API Communication

The services communicate as follows:

1. Frontend → Backend: Direct API calls via proxy (`/api/backend/*`)
2. Frontend → AI Model: Direct API calls via proxy (`/api/ai/*`)
3. Backend → AI Model: Direct HTTP calls for predictions

## Development Features

- **Hot Reloading**: All services support hot reloading during development
- **CORS**: Configured for local development
- **Error Handling**: Basic error handling and service availability checks
- **Extensible AI Model**: The PyTorch model can be easily extended or replaced

## Testing the Services

1. Open http://localhost:3000 in your browser
2. Click "Check Services" to verify all services are running
3. Try processing data through the backend (calculates mean)
4. Try making predictions through the AI service
5. Train the model with custom data

## Extending the AI Model

The AI model is designed to be easily extensible. To modify it:

1. Edit `ai-model/app.py`
2. Modify the `SimpleNN` class to change the architecture
3. Add new endpoints for different model operations
4. The model automatically saves/loads from `ai-model/models/`

## Project Structure

```
stack-wrangler/
├── frontend/           # Next.js TypeScript frontend
│   ├── app/           # App router pages
│   ├── public/        # Static assets
│   └── package.json   # Frontend dependencies
├── backend/           # Rust backend service
│   ├── src/          # Rust source code
│   └── Cargo.toml    # Rust dependencies
├── ai-model/         # Python AI model service
│   ├── app.py        # FastAPI application
│   ├── models/       # Saved model files
│   └── requirements.txt
├── docker-compose.yml # Docker orchestration
└── package.json      # Root package for scripts
```

## Troubleshooting

### Port Already in Use
If any port is already in use, you can modify the port numbers in:
- Frontend: `next.config.ts` and `package.json`
- Backend: `src/main.rs`
- AI Model: `app.py`

### Service Communication Issues
- Ensure all services are running
- Check the browser console for CORS errors
- Verify the proxy configuration in `next.config.ts`

### Python Dependencies
If you encounter issues with PyTorch installation:
```bash
uv pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Package Manager Installation
If you don't have the fast package managers installed:

**Install Bun:**
```bash
curl -fsSL https://bun.sh/install | bash
# or with npm: npm install -g bun
```

**Install uv:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# or with pip: pip install uv
```

## License

MIT