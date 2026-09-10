"""Download the exact CC0 surface inputs recorded in the adjacent manifest."""
import hashlib,json,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parent/'assets/polyhaven'
for item in json.loads((root/'manifest.json').read_text()):
 p=root/item['file'];p.parent.mkdir(exist_ok=True)
 if p.exists() and hashlib.md5(p.read_bytes()).hexdigest()==item['md5']:continue
 request=urllib.request.Request(item['url'],headers={'User-Agent':'Back2Back-local-scene-build/1.0'})
 data=urllib.request.urlopen(request,timeout=45).read()
 if hashlib.md5(data).hexdigest()!=item['md5']:raise RuntimeError('Checksum mismatch: '+item['file'])
 p.write_bytes(data);print(item['file'],len(data))
