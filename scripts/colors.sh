#!/usr/bin/env bash
# ONETOO — tiny ANSI color helper (Git Bash friendly)
set -euo pipefail

if [ -t 1 ]; then
  C_RESET="\033[0m"
  C_DIM="\033[2m"
  C_BOLD="\033[1m"
  C_RED="\033[31m"
  C_GREEN="\033[32m"
  C_YELLOW="\033[33m"
  C_BLUE="\033[34m"
  C_MAGENTA="\033[35m"
  C_CYAN="\033[36m"
else
  C_RESET=""; C_DIM=""; C_BOLD=""
  C_RED=""; C_GREEN=""; C_YELLOW=""; C_BLUE=""; C_MAGENTA=""; C_CYAN=""
fi

log(){ echo -e "${C_CYAN}[*]${C_RESET} $*"; }
ok(){  echo -e "${C_GREEN}[OK]${C_RESET} $*"; }
warn(){echo -e "${C_YELLOW}[!!]${C_RESET} $*"; }
bad(){ echo -e "${C_RED}[XX]${C_RESET} $*"; }
