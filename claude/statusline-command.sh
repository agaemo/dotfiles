#!/bin/sh
input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd')
model=$(echo "$input" | jq -r '.model.display_name // empty')
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
total_in=$(echo "$input" | jq -r '.context_window.total_input_tokens // empty')
total_out=$(echo "$input" | jq -r '.context_window.total_output_tokens // empty')
five_hour=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
seven_day=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
seven_day_resets_at=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')

# ANSI colors
RESET='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'

C_BLUE='\033[38;5;39m'
C_CYAN='\033[38;5;51m'
C_GREEN='\033[38;5;82m'
C_YELLOW='\033[38;5;220m'
C_ORANGE='\033[38;5;208m'
C_RED='\033[38;5;196m'
C_PURPLE='\033[38;5;135m'
C_GRAY='\033[38;5;240m'
C_WHITE='\033[38;5;255m'

SEP="${C_GRAY}│${RESET}"

# Shorten home directory to ~
home="$HOME"
short_cwd=$(echo "$cwd" | sed "s|^$home|~|")
dirname=$(basename "$short_cwd")

# Git branch
branch=""
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  branch=$(git -C "$cwd" -c core.hooksPath=/dev/null symbolic-ref --short HEAD 2>/dev/null || git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
fi

# Mini bar chart (5 chars wide) for a percentage
bar() {
  pct=$1
  filled=$(awk "BEGIN { printf \"%d\", ($pct * 5) / 100 }")
  empty=$(( 5 - filled ))
  bar_str=""
  i=0
  while [ $i -lt $filled ]; do
    bar_str="${bar_str}█"
    i=$(( i + 1 ))
  done
  i=0
  while [ $i -lt $empty ]; do
    bar_str="${bar_str}░"
    i=$(( i + 1 ))
  done
  printf '%s' "$bar_str"
}

# Color based on percentage
pct_color() {
  pct=$1
  if [ "$pct" -ge 80 ]; then
    printf '%s' "$C_RED"
  elif [ "$pct" -ge 50 ]; then
    printf '%s' "$C_ORANGE"
  else
    printf '%s' "$C_GREEN"
  fi
}

out=""

# ── Directory
out="${out}${C_BLUE}󰉋 ${BOLD}${C_WHITE}${dirname}${RESET}"

# ── Git branch
if [ -n "$branch" ]; then
  out="${out} ${SEP} ${C_PURPLE} ${branch}${RESET}"
fi

# ── Model
if [ -n "$model" ]; then
  short_model=$(echo "$model" | sed 's/Claude //')
  out="${out} ${SEP} ${C_CYAN}󰚩 ${short_model}${RESET}"
fi

# ── Context window bar
if [ -n "$used" ]; then
  used_int=$(printf '%.0f' "$used")
  color=$(pct_color "$used_int")
  b=$(bar "$used_int")
  out="${out} ${SEP} ${color}${b} ctx ${used_int}%%${RESET}"
fi


# ── Rate limits
if [ -n "$five_hour" ]; then
  five_int=$(printf '%.0f' "$five_hour")
  color=$(pct_color "$five_int")
  b=$(bar "$five_int")
  out="${out} ${SEP} ${color}${b} 5h ${five_int}%%${RESET}"
fi
if [ -n "$seven_day" ]; then
  seven_int=$(printf '%.0f' "$seven_day")
  color=$(pct_color "$seven_int")
  b=$(bar "$seven_int")
  days_left_str=""
  if [ -n "$seven_day_resets_at" ]; then
    now=$(date +%s)
    secs_left=$(( seven_day_resets_at - now ))
    if [ "$secs_left" -gt 0 ]; then
      days_left=$(awk "BEGIN { printf \"%d\", ($secs_left / 86400) }")
      days_left_str=" (${days_left}d left)"
    fi
  fi
  out="${out} ${SEP} ${color}${b} 7d${days_left_str} ${seven_int}%%${RESET}"
fi

printf "${out}\n"
