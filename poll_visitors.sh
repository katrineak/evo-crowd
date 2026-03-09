#!/bin/bash
# Poll EVO Adamstuen + Teisen visitor counts every 5 minutes

ADAMSTUEN_ID="360e51d3-a434-4697-91c9-f956725108fc"
TEISEN_ID="eebcd9b8-93f1-4b2d-9ab9-7b064d66ba3c"
BASE_URL="https://visits.evofitness.no/api/v1/locations"
LOG_ADAMSTUEN="/Users/k/Claude/evo-crowd/visitor_log.csv"
LOG_TEISEN="/Users/k/Claude/evo-crowd/visitor_log_teisen.csv"

# Create headers if files don't exist
for LOG_FILE in "$LOG_ADAMSTUEN" "$LOG_TEISEN"; do
    if [ ! -f "$LOG_FILE" ]; then
        echo "timestamp,current,max_capacity,percentageUsed" > "$LOG_FILE"
    fi
done

poll_location() {
    local LOC_ID="$1"
    local LOG_FILE="$2"
    local NAME="$3"
    local RESPONSE=$(curl -s -H "Accept: application/json" "${BASE_URL}/${LOC_ID}/current")
    local CURRENT=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['current'])" 2>/dev/null)
    local MAX_CAP=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['max_capacity'])" 2>/dev/null)
    local PCT=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['percentageUsed'])" 2>/dev/null)
    local TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    if [ -n "$CURRENT" ]; then
        echo "${TIMESTAMP},${CURRENT},${MAX_CAP},${PCT}" >> "$LOG_FILE"
        echo "[${TIMESTAMP}] ${NAME}: ${CURRENT}/${MAX_CAP} (${PCT}%)"
    else
        echo "[${TIMESTAMP}] ${NAME}: Failed to fetch data"
    fi
}

while true; do
    poll_location "$ADAMSTUEN_ID" "$LOG_ADAMSTUEN" "Adamstuen"
    poll_location "$TEISEN_ID" "$LOG_TEISEN" "Teisen"
    python3 /Users/k/Claude/evo-crowd/generate_graf.py > /dev/null 2>&1 && echo "[$(date '+%Y-%m-%d %H:%M:%S')] graf.html oppdatert"
    sleep 300  # 5 minutes
done
