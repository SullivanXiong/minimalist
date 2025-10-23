#!/bin/bash

# Blocks browser navigation to any URL except http://localhost:5173
#
# Note: This only prevents direct navigation. It cannot prevent:
# - Clicking buttons/links that navigate to other domains
# - JavaScript redirects triggered by user interactions

# Read the JSON input from stdin
input=$(cat)

# Parse the JSON to extract tool_name and tool_input
tool_name=$(echo "$input" | jq -r '.tool_name // empty')
tool_input=$(echo "$input" | jq -r '.tool_input // empty')

echo "[Hook] beforeMCPExecution called: tool_name=$tool_name" >&2

# Handle MCP tool calls (browser_navigate)
if [ "$tool_name" = "browser_navigate" ] && [ -n "$tool_input" ]; then
    # Parse the tool_input JSON to get the URL
    url=$(echo "$tool_input" | jq -r '.url // empty')

    if [ -n "$url" ]; then
        # Check if URL is actually a localhost URL (not just containing "localhost")
        # Match: http://localhost, https://localhost, http://127.0.0.1, relative paths starting with /
        if [[ "$url" =~ ^https?://(localhost|127\.0\.0\.1|\[::1\])(:[0-9]+)?(/.*)?$ ]] || [[ "$url" =~ ^/ ]]; then
            echo "[Hook] ALLOWED browser navigation to: $url" >&2
            echo '{"permission": "allow"}'
        else
            echo "[Hook] BLOCKED browser navigation to: $url" >&2
            echo '{"permission": "deny", "userMessage": "Browser navigation blocked: only localhost URLs are allowed"}'
        fi
    else
        echo "[Hook] No URL found in tool_input" >&2
        echo '{"permission": "allow"}'
    fi
else
    # Allow all other tool calls
    echo '{"permission": "allow"}'
fi

