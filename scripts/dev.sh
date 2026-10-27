#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
BACKEND_LOG="${ROOT_DIR}/.backend.log"
FRONTEND_LOG="${ROOT_DIR}/.frontend.log"

cd "$ROOT_DIR"

port_pid() {
  lsof -tiTCP:"$1" -sTCP:LISTEN 2>/dev/null || true
}

stop_port() {
  local port="$1"
  local pid child_pid
  while read -r pid; do
    [[ -z "$pid" ]] && continue
    echo "Stopping process $pid on port $port"
    while read -r child_pid; do
      [[ -n "$child_pid" ]] && kill "$child_pid" 2>/dev/null || true
    done < <(pgrep -P "$pid" 2>/dev/null || true)
    kill "$pid" 2>/dev/null || true
  done < <(port_pid "$port")
}

kill_services() {
  stop_port "$BACKEND_PORT"
  stop_port "$FRONTEND_PORT"
}

start_backend() {
  if [[ ! -x "$ROOT_DIR/.venv/bin/python" ]]; then
    echo "Missing .venv. Create it with: python3 -m venv .venv"
    exit 1
  fi
  echo "Starting FastAPI on http://127.0.0.1:${BACKEND_PORT}"
  nohup "$ROOT_DIR/.venv/bin/python" -m uvicorn app.main:app \
    --reload --host 127.0.0.1 --port "$BACKEND_PORT" \
    >"$BACKEND_LOG" 2>&1 &
}

start_frontend() {
  if [[ ! -d "$ROOT_DIR/frontend/node_modules" ]]; then
    echo "Installing frontend dependencies"
    npm --prefix "$ROOT_DIR/frontend" install
  fi
  echo "Starting Next.js on http://localhost:${FRONTEND_PORT}"
  nohup npm --prefix "$ROOT_DIR/frontend" run dev -- \
    --hostname 127.0.0.1 --port "$FRONTEND_PORT" \
    >"$FRONTEND_LOG" 2>&1 &
}

case "${1:-restart}" in
  start)
    start_backend
    start_frontend
    ;;
  stop)
    kill_services
    ;;
  kill)
    kill_services
    ;;
  restart)
    kill_services
    start_backend
    start_frontend
    ;;
  status)
      backend_pid="$(port_pid "$BACKEND_PORT" | tr '\n' ' ')"
      frontend_pid="$(port_pid "$FRONTEND_PORT" | tr '\n' ' ')"
    [[ -n "$backend_pid" ]] && echo "Backend: running (PID $backend_pid)" || echo "Backend: stopped"
    [[ -n "$frontend_pid" ]] && echo "Frontend: running (PID $frontend_pid)" || echo "Frontend: stopped"
    ;;
  logs)
    tail -n 40 "$BACKEND_LOG" "$FRONTEND_LOG"
    ;;
  *)
    echo "Usage: ./scripts/dev.sh [start|stop|kill|restart|status|logs]"
    exit 2
    ;;
esac
