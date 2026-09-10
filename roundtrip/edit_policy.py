"""The same fail-closed Lightroom request grammar used by the hosted form."""
import json
import re
from pathlib import Path
POLICY=json.loads((Path(__file__).parent/'relay/lib/edit-policy.json').read_text())
def supported_edit(feedback):
    clauses=[s.strip() for s in re.split(r"[.!;]+|,?\s+but\s+|,\s*(?=keep\b)",re.sub(r'^please\s+','',feedback.lower().strip())) if s.strip()]
    if not clauses or len(clauses)>6:return False
    edits=0
    for clause in clauses:
        if any(re.fullmatch(p,clause) for p in POLICY['actions']):edits+=1
        elif not any(re.fullmatch(p,clause) for p in POLICY['preservation']):return False
    return 0<edits<=3
