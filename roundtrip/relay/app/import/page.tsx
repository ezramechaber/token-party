'use client';
import {useState} from 'react';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
export default function Import(){
 const [key,setKey]=useState(''),[files,setFiles]=useState<File[]>([]),[status,setStatus]=useState(''),[busy,setBusy]=useState(false);
 async function upload(e:React.FormEvent){e.preventDefault();setBusy(true);try{for(const file of files){
 const id=file.name.replace(/\.jpg$/i,'');const order=id==='original'?0:id==='v1'?1:id==='v2'?2:3;
 const labels=['Original','V1','V2','V3'];const summaries=['Original RAW rendering','First edit inspired by the Fuji reference','Cooler skin tones and a darker background','Face brightened with a feathered mask at +0.35 EV'];
 const form=new FormData();form.set('file',file);form.set('id',id);form.set('label',labels[order]);form.set('summary',summaries[order]);form.set('created',String(order+1));
 setStatus('Uploading '+labels[order]+'…');const r=await fetch('/api/gallery/upload',{method:'POST',headers:{Authorization:'Bearer '+key},body:form});const d=await r.json() as {error?:string};if(!r.ok)throw Error(d.error||'Upload failed');
 }setKey('');setStatus('All selected Lightroom exports are in the gallery.');}catch(e){setStatus(e instanceof Error?e.message:'Upload failed.');}finally{setBusy(false);}}
 return <main><h1>Import the Lightroom study</h1><p>Add the existing original, V1, V2, and V3 JPEG exports. These stay behind the gallery’s review link.</p><section><form onSubmit={upload}><label htmlFor="credential">Photographer key</label><Input id="credential" type="password" value={key} onChange={e=>setKey(e.target.value)} autoComplete="off" required/><label htmlFor="exports">JPEG exports</label><Input id="exports" type="file" accept="image/jpeg" multiple onChange={e=>setFiles(Array.from(e.target.files||[]))}/><Button type="submit" disabled={busy||!files.length} style={{marginTop:24}}>Upload exports</Button><p role="status">{status}</p></form></section></main>;
}
