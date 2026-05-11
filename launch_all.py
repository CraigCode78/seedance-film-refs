#!/usr/bin/env python3
"""Launch all remaining shots for 'The Map Beneath' and save task IDs."""
import json, urllib.request

BASE_URL = 'https://ark.ap-southeast.bytepluses.com/api/v3'
ENDPOINT = '/contents/generations/tasks'
H = {
    'Authorization': 'Bearer ark-e9a4c0c0-4c69-4c0c-98f7-db8e268f5d01-96f2f',
    'Content-Type': 'application/json',
}

shots = {
    '02': "Medium shot: a man at a minimalist office desk. Abstract translucent screens and data fragments begin to appear and float in the air around him, glowing faintly blue. He looks at them with curiosity. Bright soft daylight. Cinematic, photorealistic, muted grey and blue-grey tones.",
    '03': "Medium close-up: a man types rapidly across multiple holographic screens and interfaces surrounding his desk. Flow and productivity. Bright office lighting. Cinematic, photorealistic, muted tones. Subtle lateral camera movement.",
    '04': "Wide shot: holographic data screens and fragments multiply and completely surround a man at his desk, creating visual pressure. The man looks stressed. Slow orbit camera. Cinematic, muted grey and cool blue tones.",
    '09': "Wide shot: an old grey organisational chart dissolves and transforms into five luminous horizontal operational layers, glowing with golden light. Warm illumination. Slow subtle push. Clarity. Cinematic, photorealistic.",
    '10': "Wide shot: abstract luminous agent nodes move through layered grid structures, executing work. Golden orbs travelling along glowing connection lines. Gentle parallax camera movement. Warm and alive lighting. Cinematic.",
    '11': "Medium wide shot: a man in a grey sweater stands tall, looking confidently over a vast luminous map of interconnected golden layers glowing beneath his office floor. Very slow push in. Warm bright lighting. Cinematic.",
    '12': "Final wide hero shot: a man stands with his back to camera looking out over a massive luminous living map beneath him, golden cityscape visible through office windows. Warm golden natural light. Slow push in. Confidence and hope.",
}

ids = {}

for name, prompt in shots.items():
    payload = {
        "model": "dreamina-seedance-2-0-fast-260128",
        "content": [{"type": "text", "text": prompt}],
        "ratio": "16:9",
        "duration": 5,
        "watermark": False,
    }
    req = urllib.request.Request(
        BASE_URL + ENDPOINT,
        data=json.dumps(payload).encode(),
        headers=H,
    )
    try:
        d = json.load(urllib.request.urlopen(req))
        tid = d.get("id", "")
        ids[name] = tid
        print(f"Shot {name}: launched → {tid}")
    except Exception as e:
        print(f"Shot {name}: FAILED → {e}")

# Save IDs
with open('/tmp/seedance-film/task_ids.json', 'w') as f:
    json.dump(ids, f, indent=2)

# Also merge with already-downloaded shots
existing = {'01': True, '05': True, '06': True, '07': True, '08': True}
ids.update({k: v for k, v in existing.items()})
with open('/tmp/seedance-film/all_tasks.json', 'w') as f:
    json.dump(ids, f, indent=2)

print(f"\nLaunched {len(ids)-len(existing)} new shots")
print(f"Total tracked: {len(ids)} shots")
