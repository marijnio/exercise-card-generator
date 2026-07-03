import json
import os

log_file = "/Users/273974/.gemini/antigravity-ide/brain/d9283a32-1180-433c-8d28-f924b3cfbdff/.system_generated/logs/transcript_full.jsonl"

queries = ["Glute Bridge March", "Suitcase Deadlift", "Kettlebell Swing"]

if os.path.exists(log_file):
    with open(log_file, "r") as f:
        for line_num, line in enumerate(f):
            for q in queries:
                if q in line:
                    print(f"--- MATCH FOUND in line {line_num} for query: {q} ---")
                    try:
                        data = json.loads(line)
                        content = data.get("content", "")
                        print(content[:1500])  # print first 1500 chars of the content
                        print("...")
                    except Exception as e:
                        print("JSON decode error, printing raw line snippet:")
                        print(line[:500])
                    break
else:
    print("Log file not found")
