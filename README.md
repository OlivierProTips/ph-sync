# PiHole Sync (aka ph-sync)

This project has been made to sync full v6.x configuration (teleporter) from one pihole (master) to replicas (slaves)

## Features

- Full sync: Use Pi-hole Teleporter for full synchronization.
- Cron schedule: Run on chron schedule.

## Install

### Docker Compose (recommended)

```yml
services:
  pihole-sync:
    image: olivierprotips/ph-sync:latest
    container_name: pihole_sync
    environment:
      - PIHOLE_MASTER=http://pihole.master|password123
      - PIHOLE_SLAVES=http://pihole.slave1|password123,http://pihole.slave2|password123
      - CRON_SCHEDULE=0 * * * *
      - TZ=Europe/Paris
    restart: unless-stopped
```

### Docker CLI

```bash
docker run --rm \
  --name ph-sync \
  -e PIHOLE_MASTER="http://pihole.master|password123" \
  -e PIHOLE_SLAVES="http://pihole.slave1|password123,http://pihole.slave2|password123" \
  -e TZ="Europe/Paris" \
  -e CRON_SCHEDULE="0 * * * *" \
  olivierprotips/ph-sync:latest
```

### Python

You can use `ph-sync.py` directly than create a cron job manually. Remember to change `PIHOLE_MASTER` and `PIHOLE_SLAVES` in py script.

## Environment variables

### Required Environment Variables

| Name          | Exemple                                                             | Description                                          |
| ------------- | ------------------------------------------------------------------- | ---------------------------------------------------- |
| PIHOLE_MASTER | http://pihole.master\|password123                                   | Specifies the primary Pi-hole configuration          |
| PIHOLE_SLAVES | http://pihole.slave1\|password123,http://pihole.slave2\|password123 | Specifies the list of replica Pi-hole configurations |

### Optional Environment Variables

| Name          | Default      | Description                                     |
| ------------- | ------------ | ----------------------------------------------- |
| CRON_SCHEDULE | 0 * * * *    | Specifies the cron schedule for synchronization |
| TZ            | Europe/Paris | Specifies the timezone for logs and cron        |

## TODO

- [ ] Add https support