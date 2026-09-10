const $=s=>document.querySelector(s);
const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const time=s=>`${String(Math.floor(Math.max(0,s)/60)).padStart(2,'0')}:${String(Math.floor(Math.max(0,s)%60)).padStart(2,'0')}`;
let tracks=[],order=[],plan=null,ctx,master,analyser,active=false,transition=null,generation=0,editId=null,loading=false;
let masterTempo=124, manualOrder=false;
async function api(path,body,method='POST'){
 const res=await fetch('/api/'+path,body===undefined?{}:{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
 if(!res.ok){let message;try{message=(await res.json()).detail}catch{message=res.statusText}throw Error(typeof message==='string'?message:JSON.stringify(message))}return res.json();
}
function toast(s){$('#toast').textContent=s;$('#toast').hidden=false;clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('#toast').hidden=true,6500)}
function audioContext(){if(!ctx){ctx=new AudioContext();master=ctx.createGain();master.gain.value=+.65;analyser=ctx.createAnalyser();analyser.fftSize=256;master.connect(analyser);analyser.connect(ctx.destination)}return ctx}
async function unlock(){audioContext();await ctx.resume()}
function track(id){return tracks.find(t=>t.id===id)}
class Deck{
 constructor(letter){this.letter=letter;this.el=$('#deck'+letter);this.track=null;this.buffer=null;this.source=null;this.offset=0;this.start=0;this.running=false;this.token=0;
 this.el.querySelector('.play').onclick=()=>safe(async()=>{await unlock();takeover(false);this.running?this.pause():this.play()});
 this.el.querySelector('.cue').onclick=()=>safe(async()=>{await unlock();takeover(false);this.seek(this.track.entry/this.ratio);this.play()});
 this.el.querySelector('.outcue').onclick=()=>safe(async()=>{await unlock();takeover(false);this.seek(Math.max(0,this.track.outroStart/this.ratio));this.play()});
 this.el.querySelector('.review').onclick=()=>this.track&&edit(this.track.id);
 this.el.querySelector('.gain').oninput=e=>{takeover(false);this.level?.gain.setValueAtTime(+e.target.value,ctx.currentTime)};
 this.el.querySelector('.low').oninput=e=>{takeover(false);this.low?.gain.setValueAtTime(+e.target.value,ctx.currentTime)};
 this.el.querySelector('.wave').onclick=e=>{if(!this.buffer)return;takeover(false);const r=e.target.getBoundingClientRect();this.seek(Math.max(0,Math.min(this.buffer.duration-.01,(e.clientX-r.left)/r.width*this.buffer.duration)))};
 }
 async load(t,tempo){if(!t)throw Error('Choose a track first.');const token=++this.token;this.stop();this.track=t;this.buffer=null;this.ratio=tempo/t.bpm;this.status('PREPARING AUDIO');this.render();audioContext();
 const res=await fetch(`/api/audio/${t.id}?tempo=${tempo}`);if(!res.ok){const j=await res.json();throw Error(j.detail)}const buffer=await ctx.decodeAudioData(await res.arrayBuffer());if(token!==this.token)return;
 this.buffer=buffer;this.offset=t.entry/this.ratio;this.low?.disconnect();this.level?.disconnect();this.fade?.disconnect();
 this.low=ctx.createBiquadFilter();this.low.type='lowshelf';this.low.frequency.value=200;
 this.level=ctx.createGain();this.fade=ctx.createGain();this.fade.gain.value=this.letter==='A'?1-+$('#crossfader').value:+$('#crossfader').value;this.low.connect(this.level);this.level.connect(this.fade);this.fade.connect(master);
 this.status('READY · KEY LOCK');this.render();if(+$('#inspectDeck').value===(this.letter==='A'?0:1))inspectAt(+$('#inspectDeck').value,t.entry);
 }
 status(s){this.el.querySelector('.deck-state').textContent=s}
 position(){return this.running?Math.min(this.buffer.duration,this.offset+Math.max(0,ctx.currentTime-this.start)):this.offset}
 play(at=ctx.currentTime+.04,offset=this.offset){if(!this.buffer)throw Error('Wait for the deck to finish loading.');this.stop(false);this.offset=Math.max(0,Math.min(offset,this.buffer.duration-.01));this.start=at;this.running=true;
 const s=ctx.createBufferSource();s.buffer=this.buffer;s.connect(this.low);this.source=s;const token=this.token;s.onended=()=>{if(this.source===s&&token===this.token){this.running=false;this.source=null;this.offset=0;this.status('FINISHED')}};s.start(at,this.offset);this.status(at>ctx.currentTime+.1?'ARMED':'PLAYING');}
 stop(reset=true){if(this.source){this.source.onended=null;try{this.source.stop()}catch{}this.source.disconnect();this.source=null}this.running=false;if(reset)this.offset=0}
 pause(){const p=this.position();this.stop(false);this.offset=p;this.status('PAUSED')}
 seek(p){const was=this.running;this.stop(false);this.offset=p;if(was)this.play();}
 render(){if(!this.track)return;const t=this.track;this.el.querySelector('h2').textContent=t.title;this.el.querySelector('.track-heading p').textContent=t.artist;
 this.el.querySelector('.deck-bpm').innerHTML=`${masterTempo.toFixed(1)}<small>BPM</small>`;this.el.querySelector('.deck-key').textContent=t.key.name+' · '+t.key.camelot;
 this.el.querySelector('.intro').textContent=t.introBars+' BARS';this.el.querySelector('.outro').textContent=t.outroBars+' BARS';this.el.querySelector('.key-status').textContent=t.reviewed?'CUES CONFIRMED':'CUES ESTIMATED';}
 draw(){const canvas=this.el.querySelector('.wave'),w=canvas.clientWidth,h=canvas.clientHeight,dpr=devicePixelRatio||1;if(canvas.width!==w*dpr||canvas.height!==h*dpr){canvas.width=w*dpr;canvas.height=h*dpr}
 const c=canvas.getContext('2d');c.setTransform(dpr,0,0,dpr,0,0);c.clearRect(0,0,w,h);c.strokeStyle='#2b3529';c.lineWidth=1;c.beginPath();c.moveTo(0,h/2);c.lineTo(w,h/2);c.stroke();
 if(!this.track)return;const t=this.track,color=this.letter==='A'?'#d8f982':'#8db6ef',duration=t.duration,p=this.position()*this.ratio;
 const sx=seconds=>seconds/duration*w;
 c.fillStyle=this.letter==='A'?'#d8f98216':'#8db6ef16';c.fillRect(sx(t.entry),0,sx(t.introEnd-t.entry),h);c.fillRect(sx(t.outroStart),0,sx(t.exitEnd-t.outroStart),h);
 for(let x=0;x<w;x+=2){const i=Math.floor(x/w*t.waveform.length),amp=t.waveform[i]||0;const barIndex=Math.floor((x/w*duration-t.gridOffset)/(240/t.bpm));const band=t.bands[Math.max(0,barIndex)];c.fillStyle=x<sx(p)?color:(band&&band[0]>band[2]?'#648452':'#4d6761');const a=Math.max(1,amp*h*.43);c.fillRect(x,h/2-a,1.4,a*2)}
 c.strokeStyle='#dce7d06a';c.setLineDash([3,4]);for(const v of [t.entry,t.introEnd,t.outroStart,t.exitEnd]){c.beginPath();c.moveTo(sx(v),0);c.lineTo(sx(v),h);c.stroke()}c.setLineDash([]);c.strokeStyle=color;c.beginPath();c.moveTo(sx(p),0);c.lineTo(sx(p),h);c.stroke();
 this.el.querySelector('.deck-time').textContent=time(this.position());this.el.querySelector('.deck-bar').textContent='BAR '+Math.max(1,Math.floor((p-t.gridOffset)/(240/t.bpm))+1);this.el.querySelector('.play').textContent=this.running?'Ⅱ':'▶';
 if(this.running&&ctx.currentTime>=this.start)this.status('PLAYING');
 if(this.low){const value=this.low.gain.value,level=this.level.gain.value;this.el.querySelector('.low').value=value;this.el.querySelector('.low').nextElementSibling.value=Math.round(value)+' dB';this.el.querySelector('.gain').value=level;this.el.querySelector('.gain').nextElementSibling.value=Math.round(level*100)+'%'}
 }
}
const decks=[new Deck('A'),new Deck('B')];
async function safe(fn){try{await fn()}catch(e){toast(e.message);console.error(e)}}
function hold(param){if(!param)return;if(param.cancelAndHoldAtTime)param.cancelAndHoldAtTime(ctx.currentTime);else{const v=param.value;param.cancelScheduledValues(ctx.currentTime);param.setValueAtTime(v,ctx.currentTime)}}
function takeover(notify=true){generation++;active=false;
 if(transition){clearTimeout(transition.timer);for(const d of decks){if(d.start>ctx.currentTime)d.stop();hold(d.fade?.gain);hold(d.low?.gain)}transition=null}
 $('#autoTitle').textContent='Manual control';$('#autoDetail').textContent='Manual control. Future handoffs are cancelled.';$('#takeover').hidden=true;$('#auto').hidden=false;$('#tempo').disabled=false;
 if(notify)toast('You have the decks. Current levels are held.');}
function stopAll(){takeover(false);decks.forEach(d=>{d.stop();if(d.track)d.status(d.buffer?'READY · KEY LOCK':'RELOAD AUDIO')});if(ctx){decks.forEach(d=>{d.fade?.gain.setValueAtTime(d.letter==='A'?1:0,ctx.currentTime);d.low?.gain.setValueAtTime(0,ctx.currentTime)})}$('#crossfader').value=0}
function setFade(v){if(!ctx)return;decks[0].fade?.gain.setValueAtTime(1-v,ctx.currentTime);decks[1].fade?.gain.setValueAtTime(v,ctx.currentTime)}
$('#crossfader').oninput=e=>{takeover(false);setFade(+e.target.value)};
$('#master').oninput=e=>{if(master)master.gain.setTargetAtTime(+e.target.value,ctx.currentTime,.015)};
$('#stop').onclick=stopAll;$('#takeover').onclick=()=>takeover();
$('#tempo').onchange=()=>{if(decks.some(d=>d.running)){toast('Stop playback before changing the set tempo.');$('#tempo').value=masterTempo;return}masterTempo=+$('#tempo').value;plan=null;decks.forEach(d=>{d.buffer=null;d.status('RELOAD AT NEW TEMPO')});toast('Tempo changed. Load the decks again or start Auto.');};
$('#bars').onchange=()=>{if(active)takeover();plan=null};
async function refresh(){const data=await api('crate');tracks=data.tracks;for(const t of tracks)if(!order.includes(t.id))order.push(t.id);
 $('#connection').textContent='● LOCAL AUDIO';$('#count').textContent=tracks.length;$('#astra').disabled=!data.astra;$('#direction').disabled=!data.astra;$('#direction').placeholder=data.astra?'Set direction, e.g. start mellow and build':'Astra set direction · not connected';$('#astraHint').textContent=data.astra?'':' · add API key later';
 $('#jobs').innerHTML=Object.values(data.jobs).filter(j=>j.status!=='done').map(j=>`<div>${j.status==='error'?'⚠':'◌'} ${escape(j.title)}${j.error?' — '+escape(j.error):' · analyzing'}</div>`).join('');renderCrate();}
function renderCrate(){const list=order.map(track).filter(Boolean);$('#empty').hidden=list.length>0;
 $('#tracks').innerHTML=list.map((t,i)=>`<tr data-id="${t.id}"><td>${String(i+1).padStart(2,'0')}</td><td><div class="song-title">${escape(t.title)}</div><div class="artist">${escape(t.artist)} · ${time(t.duration)}</div></td><td>${t.bpm.toFixed(1)}</td><td><span class="key-pill" title="${escape(t.key.confidence)}">${escape(t.key.name)} ${t.key.confidence==='uncertain'?'?':''}</span></td><td>${t.introBars} bars</td><td>${t.outroBars} bars</td><td class="${t.ready?'ready':'review-needed'}">${t.reviewed?'Confirmed':t.ready?'Estimated':'Review'}</td><td><div class="load-buttons"><button data-load="0">A</button><button data-load="1">B</button><button data-edit aria-label="Edit cues for ${escape(t.title)}">⋯</button><button data-up aria-label="Move ${escape(t.title)} earlier">↑</button></div></td></tr>`).join('');
}
$('#tracks').onclick=e=>{const row=e.target.closest('tr');if(!row)return;const t=track(row.dataset.id);if(e.target.hasAttribute('data-load'))safe(async()=>{takeover(false);await unlock();await decks[+e.target.dataset.load].load(t,masterTempo)});if(e.target.hasAttribute('data-edit'))edit(t.id);if(e.target.hasAttribute('data-up')){if(active)takeover();const i=order.indexOf(t.id);if(i>0)[order[i-1],order[i]]=[order[i],order[i-1]];plan=null;manualOrder=true;renderCrate();$('#planNote').textContent='Manual order · Auto will check phrase compatibility.'}};
async function suggest(fixed=false){const p=await api('plan',{ids:order,tempo:masterTempo,bars:+$('#bars').value,direction:$('#direction').value,astra:$('#astra').checked,fixed});plan=p;manualOrder=fixed;if(!fixed)order=[...p.order,...order.filter(id=>!p.order.includes(id))];renderCrate();$('#planNote').textContent=p.mode+' · '+p.reason+(p.excluded.length?` · ${p.excluded.length} need review`:'');return p}
$('#suggest').onclick=()=>safe(async()=>{if(active)throw Error('Take over before changing the armed order.');$('#suggest').disabled=true;try{await suggest()}finally{$('#suggest').disabled=false}});
async function startAuto(preview=false){await unlock();if(loading)throw Error('Audio is preparing.');loading=true;$('#auto').disabled=true;$('#preview').disabled=true;
 try{stopAll();await suggest(manualOrder);if(plan.order.length<2)throw Error('Auto needs two compatible tracks. Confirm their cue markers or adjust the set tempo.');const my=++generation;active=true;$('#tempo').disabled=true;$('#auto').hidden=true;$('#takeover').hidden=false;
 await decks[0].load(track(plan.order[0]),masterTempo);if(my!==generation)return;await decks[1].load(track(plan.order[1]),masterTempo);if(my!==generation)return;
 decks[0].fade.gain.value=1;decks[1].fade.gain.value=0;decks[0].low.gain.value=0;decks[1].low.gain.value=-24;
 const first=plan.transitions[0];const position=preview?Math.max(track(first.from).entry,first.exit-8*60/track(first.from).bpm)/decks[0].ratio:track(first.from).entry/decks[0].ratio;
 decks[0].play(ctx.currentTime+.1,position);await arm(0,0,my,preview);
 }catch(e){takeover(false);throw e}finally{loading=false;$('#auto').disabled=false;$('#preview').disabled=false}}
async function arm(index,currentIndex,my,preview){if(!active||my!==generation)return;const a=decks[currentIndex],b=decks[1-currentIndex],e=plan.transitions[index];if(!e){$('#autoTitle').textContent='Last record';$('#autoDetail').textContent='Enjoy the rest of the track.';active=false;$('#takeover').hidden=true;$('#auto').hidden=false;$('#tempo').disabled=false;return}
 if(index>0){await b.load(track(e.to),masterTempo);if(my!==generation)return}
 const at=a.start+(e.exit/a.ratio-a.offset),end=at+e.duration;
 if(at<ctx.currentTime+.06){takeover(false);throw Error('The mixing window has passed. Audition the next transition or cue the track again.')}
 b.fade.gain.cancelScheduledValues(ctx.currentTime);b.fade.gain.setValueAtTime(0,ctx.currentTime);b.low.gain.setValueAtTime(-24,ctx.currentTime);b.play(at,e.entry/b.ratio);
 a.fade.gain.setValueAtTime(1,at);a.fade.gain.linearRampToValueAtTime(0,end);b.fade.gain.setValueAtTime(0,at);b.fade.gain.linearRampToValueAtTime(1,end);
 a.low.gain.setValueAtTime(0,at);a.low.gain.linearRampToValueAtTime(-24,end);b.low.gain.setValueAtTime(-24,at);b.low.gain.linearRampToValueAtTime(0,end);
 // Both sources and all ramps are armed on the audio clock. The UI timer only manages the next preload.
 const tr={at,end,a,b,e,index,currentIndex,my,preview,completed:false};transition=tr;
 $('#autoTitle').textContent=preview?'Auditioning the handoff':'Auto has the decks';$('#autoDetail').textContent=`${e.bars} bars → ${b.track.title} · ${e.reason}`;
 a.source.onended=null;
}
async function finishTransition(tr){if(tr!==transition||tr.completed)return;tr.completed=true;tr.a.stop();tr.a.status('HANDED OVER');tr.b.status('PLAYING');transition=null;
 if(tr.preview){active=false;$('#tempo').disabled=false;$('#autoTitle').textContent='Transition complete';$('#autoDetail').textContent='Incoming track continues. Take over or stop.';$('#auto').hidden=false;$('#takeover').hidden=false;return}
 await arm(tr.index+1,1-tr.currentIndex,tr.my,false);
}
$('#auto').onclick=()=>safe(()=>startAuto(false));$('#preview').onclick=()=>safe(auditionLoaded);
async function auditionLoaded(){
 if(loading)throw Error('Wait for audio preparation to finish.');
 if(!decks.every(d=>d.buffer))throw Error('Load your outgoing track into A and your incoming track into B first.');
 const next=await api('plan',{ids:decks.map(d=>d.track.id),tempo:masterTempo,bars:+$('#bars').value,fixed:true});
 if(next.order.length!==2||next.transitions.length!==1)throw Error('This pair needs grid / cue review or a closer set tempo before a matched transition.');
 await unlock();stopAll();plan=next;const my=++generation;active=true;
 $('#tempo').disabled=true;$('#auto').hidden=true;$('#takeover').hidden=false;
 const a=decks[0],b=decks[1],e=next.transitions[0];a.fade.gain.value=1;b.fade.gain.value=0;a.low.gain.value=0;b.low.gain.value=-24;
 a.play(ctx.currentTime+.1,Math.max(a.track.entry,e.exit-8*60/a.track.bpm)/a.ratio);
 $('#inspectBars').value=e.bars;inspectAt(0,e.exit);
 try{await arm(0,0,my,true)}catch(e){takeover(false);throw e}
}
$('#mixNow').onclick=()=>safe(async()=>{
 if(active)throw Error('A phrase-aligned handoff is already armed.');
 if(!decks.every(d=>d.buffer))throw Error('Load both decks first.');
 if(decks.every(d=>d.running))throw Error('Pause the incoming deck before arming a handoff.');
 const index=decks[0].running?0:decks[1].running?1:0,a=decks[index],b=decks[1-index];
 const next=await api('plan',{ids:[a.track.id,b.track.id],tempo:masterTempo,bars:+$('#bars').value,fixed:true});
 if(next.order.length!==2)throw Error('Both tracks need compatible grids, phrases and tempos.');
 await unlock();plan=next;const my=++generation;active=true;$('#tempo').disabled=true;$('#auto').hidden=true;$('#takeover').hidden=false;
 if(!a.running)a.play();try{await arm(0,index,my,false)}catch(e){takeover(false);throw e}
});
function edit(id){if(active)takeover();editId=id;const t=track(id);$('#editTitle').textContent=t.title+' · '+t.artist;for(const k of ['bpm','gridOffset','entry','introBars','exitEnd','outroBars'])$('#editForm').elements[k].value=t[k];$('#editWarning').textContent=t.warnings.join(' · ');$('#editor').showModal()}
$('#closeEditor').onclick=()=>$('#editor').close();$('#editForm').onsubmit=e=>{e.preventDefault();safe(async()=>{if(decks.some(d=>d.running))throw Error('Stop playback before changing the grid.');const values=Object.fromEntries(new FormData(e.target));for(const k in values)values[k]=+values[k];await api('track/'+editId,{...values,reviewed:true},'PUT');plan=null;decks.filter(d=>d.track?.id===editId).forEach(d=>{d.buffer=null;d.status('RELOAD WITH NEW GRID')});$('#editor').close();await refresh()})};
async function upload(files){for(const file of files){const form=new FormData();form.append('file',file);const res=await fetch('/api/upload',{method:'POST',body:form});if(!res.ok)throw Error((await res.json()).detail)}toast('Tracks added. Analysis is running locally.');await refresh()}
$('#upload').onchange=e=>safe(()=>upload(e.target.files));$('#scan').onclick=()=>safe(async()=>{const r=await api('scan',{});toast(r.jobs.length?`Analyzing ${r.jobs.length} tracks.`:'Your local imports are already in the crate.');await refresh()});
document.addEventListener('dragover',e=>{e.preventDefault();document.body.classList.add('dragging')});document.addEventListener('dragleave',()=>document.body.classList.remove('dragging'));document.addEventListener('drop',e=>{e.preventDefault();document.body.classList.remove('dragging');safe(()=>upload(e.dataTransfer.files))});
document.addEventListener('keydown',e=>{if(e.code==='Escape'&&!$('#editor').open)takeover();if(e.code==='Space'&&!['INPUT','SELECT','TEXTAREA','BUTTON'].includes(document.activeElement.tagName)){e.preventDefault();safe(async()=>{await unlock();takeover(false);const d=decks.find(d=>d.running)||decks[0];d.running?d.pause():d.play()})}});
let inspectStart=0,inspectCache=null;
function inspection(){const d=decks[+$('#inspectDeck').value];if(!d.track)return null;const t=d.track,span=+$('#inspectBars').value*240/t.bpm;inspectStart=Math.max(0,Math.min(inspectStart,Math.max(0,t.duration-span)));return {d,t,span};}
function inspectAt(index,seconds){$('#inspectDeck').value=index;inspectStart=Math.max(0,seconds);inspectCache=null;}
$('#inspectDeck').onchange=()=>inspectAt(+$('#inspectDeck').value,decks[+$('#inspectDeck').value].track?.entry||0);
$('#inspectBars').onchange=()=>{inspectCache=null};
$('#inspectIntro').onclick=()=>{const v=inspection();if(v)inspectAt(+$('#inspectDeck').value,v.t.entry)};
$('#inspectOutro').onclick=()=>{const v=inspection();if(v)inspectAt(+$('#inspectDeck').value,v.t.outroStart)};
$('#inspectHere').onclick=()=>{const v=inspection();if(v)inspectAt(+$('#inspectDeck').value,v.d.position()*v.d.ratio)};
for(const [id,sign] of [['inspectPrev',-1],['inspectNext',1]])$('#'+id).onclick=()=>{const v=inspection();if(v)inspectStart+=sign*v.span};
$('#inspectPosition').oninput=e=>{const v=inspection();if(v)inspectStart=+e.target.value*Math.max(0,v.t.duration-v.span)};
$('#detailWave').onclick=e=>{const v=inspection();if(!v?.d.buffer)return;takeover(false);const r=e.target.getBoundingClientRect();v.d.seek((inspectStart+(e.clientX-r.left)/r.width*v.span)/v.d.ratio)};
$('#inspectListen').onclick=()=>safe(async()=>{const v=inspection();if(!v?.d.buffer)throw Error('Load audio into the selected deck first.');await unlock();stopAll();$('#crossfader').value=v.d.letter==='A'?0:1;setFade(+$('#crossfader').value);v.d.play(ctx.currentTime+.04,inspectStart/v.d.ratio);toast('Soloing deck '+v.d.letter+' from the left edge of this view.');});
function drawInspection(){
 const canvas=$('#detailWave'),w=canvas.clientWidth,h=canvas.clientHeight,dpr=devicePixelRatio||1;
 if(canvas.width!==w*dpr||canvas.height!==h*dpr){canvas.width=w*dpr;canvas.height=h*dpr;inspectCache=null}
 const c=canvas.getContext('2d');c.setTransform(dpr,0,0,dpr,0,0);c.clearRect(0,0,w,h);const v=inspection();if(!v)return;const {d,t,span}=v;
 const sx=s=>(s-inspectStart)/span*w,color=d.letter==='A'?'#d8f982':'#8db6ef';
 const key=[d.letter,d.token,!!d.buffer,inspectStart,span,w].join(':');
 if(inspectCache?.key!==key){const peaks=[];if(d.buffer){const channels=Array.from({length:d.buffer.numberOfChannels},(_,i)=>d.buffer.getChannelData(i));const rate=d.buffer.sampleRate/d.ratio;for(let x=0;x<w;x++){const start=Math.max(0,Math.floor((inspectStart+x/w*span)*rate)),end=Math.min(channels[0].length,Math.ceil((inspectStart+(x+1)/w*span)*rate));let peak=0;for(let i=start;i<end;i++)for(const ch of channels)peak=Math.max(peak,Math.abs(ch[i]));peaks.push(peak)}}inspectCache={key,peaks};}
 c.fillStyle=color+'18';for(const [a,b] of [[t.entry,t.introEnd],[t.outroStart,t.exitEnd]])c.fillRect(sx(a),25,sx(b)-sx(a),h-45);
 c.fillStyle=color+'99';inspectCache.peaks.forEach((p,x)=>c.fillRect(x,h/2-p*(h-65)/2,1,Math.max(1,p*(h-65))));
 const beat=60/t.bpm,first=Math.max(0,Math.ceil((inspectStart-t.gridOffset)/beat));
 for(let i=first;t.gridOffset+i*beat<=inspectStart+span;i++){const x=sx(t.gridOffset+i*beat),bar=i%4===0;c.strokeStyle=bar?'#eef2dd99':'#eef2dd30';c.beginPath();c.moveTo(x,bar?22:40);c.lineTo(x,h-22);c.stroke();c.fillStyle=bar?'#eef2dd':'#91a095';c.font=(bar?'bold ':'')+'10px monospace';c.fillText(bar?'BAR '+(Math.floor(i/4)+1):String(i%4+1),x+3,bar?15:34);}
 c.fillStyle='#e8af6d';for(const k of t.kickTimes||[])if(k>=inspectStart&&k<=inspectStart+span){c.beginPath();c.arc(sx(k),h-12,2,0,Math.PI*2);c.fill()}
 for(const [s,label] of [[t.entry,'INTRO IN'],[t.introEnd,'INTRO END'],[t.outroStart,'OUTRO IN'],[t.exitEnd,'OUTRO END']])if(s>=inspectStart&&s<=inspectStart+span){c.fillStyle=color;c.fillRect(sx(s),22,2,h-44);c.font='bold 10px monospace';c.fillText(label,Math.max(2,Math.min(w-75,sx(s)+4)),h-27)}
 const p=d.position()*d.ratio;if(p>=inspectStart&&p<=inspectStart+span){c.fillStyle='#fff';c.fillRect(sx(p),22,2,h-44)}
 $('#inspectPosition').value=inspectStart/Math.max(.001,t.duration-span);
 $('#inspectTitle').textContent=`Deck ${d.letter} · ${t.title} · original ${t.bpm.toFixed(2)} BPM · 4/4 assumed`;
 $('#inspectReadout').textContent=`Original file ${time(inspectStart)}–${time(inspectStart+span)} · ${$('#inspectBars').value} bars · tall lines = bars, short lines = beats, orange dots = kick candidates · ${t.reviewed?'cues confirmed':'grid and phrases estimated'}${d.buffer?'':' · preparing detailed audio'}`;
}
function frame(){drawInspection();decks.forEach(d=>d.draw());if(analyser){const samples=new Uint8Array(analyser.frequencyBinCount);analyser.getByteTimeDomainData(samples);const peak=Math.max(...samples.map(v=>Math.abs(v-128)))/128;const percentage=Math.max(0,Math.min(100,100+(20*Math.log10(Math.max(peak,.001)))*2));$('#meterL').style.clipPath=`inset(${100-percentage}% 0 0)`;$('#meterR').style.clipPath=`inset(${100-percentage}% 0 0)`}
 if(transition&&ctx.state==='running'){const tr=transition,p=Math.max(0,Math.min(1,(ctx.currentTime-tr.at)/(tr.end-tr.at)));$('#crossfader').value=tr.currentIndex===0?p:1-p;if(ctx.currentTime<tr.at)$('#autoDetail').textContent=`${tr.e.bars}-bar handoff in ${time(tr.at-ctx.currentTime)} → ${tr.b.track.title}`;else $('#autoDetail').textContent=`Blending · bar ${Math.min(tr.e.bars,Math.floor(p*tr.e.bars)+1)} / ${tr.e.bars} · swapping low EQ`;if(ctx.currentTime>=tr.end)safe(()=>finishTransition(tr))}requestAnimationFrame(frame)}
safe(async()=>{await refresh();await api('scan',{});await refresh()});setInterval(()=>safe(refresh),4000);requestAnimationFrame(frame);
