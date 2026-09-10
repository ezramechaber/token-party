import { gallery } from './gallery';
import { getDb, secret } from '@/db';
export const finished = new Set(['completed','failed','cancelled','stale']);
export function json(data: unknown, status = 200) {
  return Response.json(data, { status, headers: {'Cache-Control':'no-store','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff'} });
}
export async function authorized(req: Request, kind: 'WORKER_KEY' | 'REVIEW_KEY') {
  const expected=secret(kind), actual=req.headers.get('Authorization')?.replace(/^Bearer /,'') || '';
  if(expected.length<32 || actual.length!==expected.length) return false;
  const a=new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(actual)));
  const b=new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(expected)));
  let diff=0; for(let i=0;i<a.length;i++)diff|=a[i]^b[i]; return diff===0;
}
export async function body(req: Request) {
  if(req.headers.get('Content-Type')?.split(';')[0]!=='application/json')throw new Error('JSON required.');
  const origin=req.headers.get('Origin');
  if(origin && origin!==new URL(req.url).origin)throw new Error('Request origin rejected.');
  const reader=req.body?.getReader(); if(!reader)throw new Error('Request body required.');
  let size=0, chunks:Uint8Array[]=[];
  while(true){const {value,done}=await reader.read();if(done)break;size+=value.length;if(size>12000){await reader.cancel();throw new Error('Request too large.');}chunks.push(value);}
  const bytes=new Uint8Array(size);let offset=0;for(const c of chunks){bytes.set(c,offset);offset+=c.length;}
  const result=JSON.parse(new TextDecoder().decode(bytes));if(!result||Array.isArray(result)||typeof result!=='object')throw new Error('Invalid request.');return result;
}
export async function snapshot() {
  const db=getDb();const studio=await db.prepare('SELECT * FROM studio WHERE id=1').first();
  const {results}=await db.prepare('SELECT * FROM requests ORDER BY created DESC LIMIT 12').all();
  const comments=await db.prepare('SELECT * FROM comments ORDER BY created DESC LIMIT 200').all();
  return {studio,requests:results,photos:await gallery(),comments:comments.results,now:Date.now()};
}
