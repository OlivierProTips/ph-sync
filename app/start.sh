#!/bin/sh

CRON_SCHEDULE="${CRON_SCHEDULE:-0 * * * *}"

echo "Configuration du cron avec la planification : $CRON_SCHEDULE"

CRON_FILE="/etc/cron.d/my-cron-file"

env | grep -E 'PIHOLE_MASTER|PIHOLE_SLAVES|CRON_SCHEDULE' > /etc/environment

PYTHON_BIN=$(which python3)
echo "$CRON_SCHEDULE root $PYTHON_BIN /app/ph-sync.py >> /proc/1/fd/1 2>&1" > "$CRON_FILE"
chmod 0644 "$CRON_FILE"

$PYTHON_BIN /app/ph-sync.py

cron -f -l 2