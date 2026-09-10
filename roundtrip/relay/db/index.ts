import { env } from 'cloudflare:workers';
export function getDb(): D1Database { return env.DB; }
export function secret(name: 'WORKER_KEY' | 'REVIEW_KEY'): string { return env[name] || ''; }
