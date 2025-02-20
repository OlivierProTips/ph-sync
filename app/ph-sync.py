import os, sys
import requests
import pendulum
from croniter import croniter

# Remove https warnings (osef)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

DEFAULT_PIHOLE_MASTER = "http://pihole.master|password123"
DEFAULT_PIHOLE_SLAVES = "http://pihole.slave1|password123,http://pihole.slave2|password123"
DEFAULT_CRON_SCHEDULE = "0 * * * *"

# Retrieve environment variables
PIHOLE_MASTER = os.getenv("PIHOLE_MASTER", DEFAULT_PIHOLE_MASTER)
PIHOLE_SLAVES = os.getenv("PIHOLE_SLAVES", DEFAULT_PIHOLE_SLAVES).split(",")
CRON_SCHEDULE = os.getenv("CRON_SCHEDULE", DEFAULT_CRON_SCHEDULE)
EXPORT_FILE = "/tmp/teleporter.zip"

def get_next_execution(cron_schedule):
    """Calculate the next execution time based on the cron schedule"""
    now = pendulum.now()
    cron = croniter(cron_schedule, now)
    next_execution = cron.get_next(pendulum.DateTime)
    return next_execution

def log(message):
    """Better log with a timestamp"""
    timestamp = pendulum.now().to_datetime_string()
    print(f"[{timestamp}] {message}")

def get_sid(pihole_url, password):
    """Get SID after authentication"""
    response = requests.post(
        f"{pihole_url}/api/auth",
        headers={"accept": "application/json", "content-type": "application/json"},
        json={"password": password},
        verify=False
    )
    response.raise_for_status()
    return response.json().get('session').get("sid")

def get_current_session_id(pihole_url, sid):
    """Retrieve the currently active session ID"""
    response = requests.get(
        f"{pihole_url}/api/auth/sessions",
        headers={"accept": "application/json", "sid": sid},
        verify=False
    )
    response.raise_for_status()
    sessions = response.json().get("sessions", [])

    for session in sessions:
        if session.get("current_session") is True:
            return session.get("id")
    
    return None  # No ID found (which should not normally happen)

def export_teleporter(sid, pihole_url):
    """Download the Teleporter file"""
    response = requests.get(
        f"{pihole_url}/api/teleporter",
        headers={"accept": "application/zip", "sid": sid},
        verify=False,
        stream=True
    )
    response.raise_for_status()
    with open(EXPORT_FILE, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def import_teleporter(sid, pihole_url):
    """Upload the Teleporter file"""
    with open(EXPORT_FILE, "rb") as f:
        response = requests.post(
            f"{pihole_url}/api/teleporter",
            headers={"accept": "application/json", "sid": sid},
            files={"file": f},
            verify=False
        )
    response.raise_for_status()

def delete_session(pihole_url, sid):
    """Delete the active session"""
    session_id = get_current_session_id(pihole_url, sid)
    if session_id is None:
        log(f"No active session found for {pihole_url}, nothing to delete.")
        return
    
    response = requests.delete(
        f"{pihole_url}/api/auth/session/{session_id}",
        headers={"accept": "application/json", "sid": sid},
        verify=False
    )
    if response.status_code != 204:
        log(f"Error deleting session {session_id} on {pihole_url}: {response.text}")

def main():
    log("Sync start...")
    master_url, master_password = PIHOLE_MASTER.split("|")
    log(f"{master_url}: Authenticating...")
    master_sid = get_sid(master_url, master_password)
    
    log(f"{master_url}: Exporting configuration...")
    export_teleporter(master_sid, master_url)

    for slave in PIHOLE_SLAVES:
        slave_url, slave_password = slave.split("|")
        log(f"{slave_url}: Syncing...")
        log(f"{slave_url}: Authenticating...")
        slave_sid = get_sid(slave_url, slave_password)

        log(f"{slave_url}: Importing configuration...")
        import_teleporter(slave_sid, slave_url)

        log(f"{slave_url}: Deleting session...")
        delete_session(slave_url, slave_sid)

    log(f"{master_url}: Deleting master session...")
    delete_session(master_url, master_sid)
    
    log("Sync done!")

    next_execution = get_next_execution(CRON_SCHEDULE)
    log(f"Next execution: {next_execution}")

if __name__ == "__main__":
    main()
