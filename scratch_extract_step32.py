import json
import os

log_file = "/Users/273974/.gemini/antigravity-ide/brain/d9283a32-1180-433c-8d28-f924b3cfbdff/.system_generated/logs/transcript_full.jsonl"

if os.path.exists(log_file):
    with open(log_file, "r") as f:
        for line in f:
            try:
                data = json.loads(line)
                # Look specifically for step_index 32 or VIEW_FILE targeting workout_data.csv
                if data.get("step_index") == 32:
                    print("--- STEP 32 CONTENT ---")
                    print(data.get("content"))
            except Exception as e:
                pass
else:
    print("Log file not found")
