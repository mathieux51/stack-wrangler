# Docker Compose Usage Guide

This guide explains how to use Docker Compose to run the Stack Wrangler monorepo.

## ✅ Everything Works! 

All services are confirmed working with the new fast package managers:
- **Frontend**: Next.js with **bun** 🚀 (lightning fast installs)
- **Backend**: Rust with cargo (already fast!)
- **AI Model**: Python with **uv** ⚡ (pip but 10x faster)

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Ports 3000, 8000, and 8001 available

### Start All Services
```bash
# Start all services with hot reloading
docker-compose up

# Or run in background
docker-compose up -d

# Or use the npm scripts
bun run docker:up
```

### Stop Services
```bash
docker-compose down

# Or use the script
bun run docker:down
```

### Build Services
```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build frontend
docker-compose build backend  
docker-compose build ai-model

# Or use the script
bun run docker:build
```

## Service Access

When running via Docker Compose:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **AI Model**: http://localhost:8001

## Docker Configuration Details

### Frontend (Next.js + Bun)
- Uses `oven/bun:1-alpine` image
- Installs dependencies with `bun install --frozen-lockfile`
- Runs with `bun run dev` for hot reloading
- Volume mounted for development

### Backend (Rust)
- Uses `rust:1.75` image  
- Pre-installs `cargo-watch` for hot reloading
- Runs with `cargo watch -x run`
- Volume mounted for development

### AI Model (Python + uv)
- Uses `ghcr.io/astral-sh/uv:python3.11-bookworm-slim` image
- Installs dependencies with `uv pip install --system`
- Much faster than pip for package installations
- Volume mounted for model persistence

## Development Features

### Hot Reloading
All services support hot reloading in development mode:
- **Frontend**: Bun's built-in hot reloading
- **Backend**: `cargo-watch` restarts on file changes
- **AI Model**: Uvicorn auto-reloads on file changes

### Volume Mounts
```yaml
# Frontend
volumes:
  - ./frontend:/app
  - /app/node_modules
  - /app/.next

# Backend  
volumes:
  - ./backend:/app
  - /app/target

# AI Model
volumes:
  - ./ai-model:/app
  - ./ai-model/models:/app/models
```

## Troubleshooting

### Port Already in Use
If you get port binding errors:
```bash
# Check what's using the ports
lsof -i :3000
lsof -i :8000  
lsof -i :8001

# Kill processes if needed
pkill -f "next\|bun"
pkill -f "backend\|cargo" 
pkill -f "python.*app.py"
```

### Docker Build Issues
```bash
# Clean build (removes cache)
docker-compose build --no-cache

# Remove all containers and rebuild
docker-compose down
docker system prune -f
docker-compose up --build
```

### Service Communication
Services communicate via Docker's internal network:
- Frontend can reach backend at `http://backend:8000`
- Frontend can reach AI model at `http://ai-model:8001`
- Backend can reach AI model at `http://ai-model:8001`

The Next.js proxy configuration handles routing from the browser.

## Performance Comparison

### Package Installation Speed
- **npm**: ~30-60s for typical installs
- **bun**: ~3-8s for same installs (6-10x faster) ⚡
- **pip**: ~45-90s for ML packages
- **uv**: ~5-15s for same packages (3-6x faster) 🚀

### Why These Are Better
- **Bun**: Written in Zig, uses system calls efficiently, better caching
- **uv**: Written in Rust, parallel downloads, better dependency resolution

## Production Considerations

For production, you'd want to:
1. Use multi-stage builds to reduce image size
2. Set `NODE_ENV=production` 
3. Build optimized frontend bundles
4. Use `--release` for Rust compilation
5. Pin specific versions in Dockerfiles

Example production Dockerfile for frontend:
```dockerfile
FROM oven/bun:1-alpine AS deps
WORKDIR /app
COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile --production

FROM oven/bun:1-alpine AS builder  
WORKDIR /app
COPY . .
COPY --from=deps /app/node_modules ./node_modules
RUN bun run build

FROM oven/bun:1-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package.json ./
EXPOSE 3000
CMD ["bun", "run", "start"]
```