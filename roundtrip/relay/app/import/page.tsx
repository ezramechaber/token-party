'use client';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function Import() {
  const [key,setKey]=useState(''), [photo,setPhoto]=useState('gallery-one');
  const [files,setFiles]=useState<File[]>([]), [status,setStatus]=useState(''), [busy,setBusy]=useState(false);
  async function upload(e: React.FormEvent) {
    e.preventDefault(); setBusy(true);
    try {
      if(photo!=='portrait'&&files.length!==1) throw Error('Choose one JPEG for this photo.');
      for(const file of files) {
        const nativeStudy=photo==='portrait';
        const stem=file.name.replace(/\.jpg$/i,'');
        const order=stem==='original'?0:stem==='v1'?1:stem==='v2'?2:3;
        const labels=['Original','V1','V2','V3'];
        const summaries=['Original RAW rendering','First edit inspired by the Fuji reference','Cooler skin tones and a darker background','Face brightened with a feathered mask at +0.35 EV'];
        const form=new FormData();
        form.set('file',file); form.set('photo_id',photo);
        form.set('id',nativeStudy?stem:photo+'-original');
        form.set('label',nativeStudy?labels[order]:'Current edit');
        form.set('summary',nativeStudy?summaries[order]:'The photographer’s existing Lightroom edit.');
        form.set('created',nativeStudy?String(order+1):String(Date.now()));
        setStatus('Uploading '+file.name+'…');
        const response=await fetch('/api/gallery/upload',{method:'POST',headers:{Authorization:'Bearer '+key},body:form});
        const result=await response.json() as {error?:string};
        if(!response.ok) throw Error(result.error||'Upload failed');
      }
      setStatus('Upload complete. The photo is available in the review gallery.');
    } catch(e) { setStatus(e instanceof Error?e.message:'Upload failed.'); }
    finally { setBusy(false); }
  }
  return <main><h1>Add Lightroom exports</h1><p>Upload JPEG exports to the private review gallery. Existing revisions are preserved.</p>
    <section><form onSubmit={upload}>
      <label htmlFor="credential">Photographer key</label><Input id="credential" type="password" disabled={busy} value={key} onChange={e=>setKey(e.target.value)} autoComplete="off" required/>
      <label htmlFor="photo">Photo</label><select id="photo" disabled={busy} value={photo} onChange={e=>{setPhoto(e.target.value);setStatus('');}}>
        <option value="gallery-one">Seated portrait</option><option value="gallery-two">Portrait by the plants</option><option value="gallery-three">Studio portrait</option><option value="portrait">Lightroom portrait study (Original–V3)</option>
      </select>
      <label htmlFor="exports">JPEG exports</label><Input id="exports" type="file" disabled={busy} accept="image/jpeg" multiple={photo==='portrait'} onChange={e=>setFiles(Array.from(e.target.files||[]))}/>
      <Button type="submit" disabled={busy||!files.length} style={{marginTop:24}}>Upload exports</Button><p role="status">{status}</p>
    </form></section>
  </main>;
}
