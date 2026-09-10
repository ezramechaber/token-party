import * as THREE from './vendor/three.module.min.js';
import { GLTFLoader } from './vendor/GLTFLoader.js';
import { RoomEnvironment } from './vendor/RoomEnvironment.js';

// This is a spatial illustration of real mixer state, never an audio clock or controller.
export function createBoothScene(canvas) {
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false }); }
  catch { canvas.setAttribute('aria-label', '3D view unavailable. Audio controls remain available.'); return { update() {}, onTrackLoaded() {}, dispose() {} }; }
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.6));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#cbc1b1');
  const environment = new THREE.PMREMGenerator(renderer);
  const room = new RoomEnvironment(); const env = environment.fromScene(room, .04);
  scene.environment = env.texture; room.dispose(); environment.dispose();
  const camera = new THREE.PerspectiveCamera(34, 1, .1, 60);
  camera.position.set(4.6, 3.6, 7.4); camera.lookAt(-.3, 1.95, -.5);
  scene.add(new THREE.HemisphereLight(0xffedcc, 0x807761, 2.2));
  const key = new THREE.DirectionalLight(0xffdfab, 3.5); key.position.set(-4,4,1); scene.add(key);
  const rim = new THREE.DirectionalLight(0xfff0dd, 1.4); rim.position.set(3,5,4); scene.add(rim);
  const floor = new THREE.Mesh(new THREE.CircleGeometry(5, 64), new THREE.MeshStandardMaterial({ color: 0xc9c5bd, roughness: .65 }));
  floor.rotation.x=-Math.PI/2; floor.position.y=.05; floor.visible=false; scene.add(floor);
  const nodes = {}, deckArt=[], crateArt=[], textures = new Map();
  let width=0,height=0,time=0,lastRender=0,disposed=false,crateKey='', state={decks:[]}, ready=false;
  const queue=[]; let action=null;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const vector = p => new THREE.Vector3(...p), Y=vector([0,1,0]);
  const positions={crate:vector([-2.05,2.10,.5]),decks:[vector([-.94,1.91,.44]),vector([.94,1.91,.44])]};
  function cover(track) {
    const key=track?.artworkUrl || track?.id || track?.title || 'b2b';
    if(textures.has(key))return textures.get(key);
    const c=document.createElement('canvas'); c.width=c.height=256; const g=c.getContext('2d');
    let seed=0; for(const char of key)seed=(seed*31+char.charCodeAt(0))>>>0;
    g.fillStyle=`hsl(${seed%360} 30% 55%)`;g.fillRect(0,0,256,256);
    g.fillStyle='#25252a';g.beginPath();g.arc(130,118,81,0,Math.PI*2);g.fill();
    g.strokeStyle='#f4ede0';g.lineWidth=3;for(let r=25;r<76;r+=12){g.beginPath();g.arc(130,118,r,0,Math.PI*2);g.stroke();}
    g.fillStyle='#f4ede0';g.font='bold 18px sans-serif';g.fillText((track?.title || 'b2b').slice(0,21),12,236);
    const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;textures.set(key,t);
    if(track?.artworkUrl){new THREE.TextureLoader().load(track.artworkUrl,loaded=>{if(disposed){loaded.dispose();return;}loaded.colorSpace=THREE.SRGBColorSpace;textures.set(key,loaded); for(const mesh of [...crateArt,...deckArt,carry])if(mesh?.userData.coverKey===key){mesh.material.map=loaded;mesh.material.needsUpdate=true;}},undefined,()=>{});}
    return t;
  }
  function assignCover(mesh,track){mesh.userData.coverKey=track?.artworkUrl || track?.id || track?.title || 'b2b';mesh.material.map=cover(track);mesh.material.needsUpdate=true;}
  function card(size){return new THREE.Mesh(new THREE.PlaneGeometry(size,size),new THREE.MeshStandardMaterial({side:THREE.DoubleSide,roughness:.7}));}
  const carry=card(.45);carry.visible=false;scene.add(carry);
  new GLTFLoader().load('/scene/b2b-booth.glb',gltf=>{
    if(disposed)return;
    scene.add(gltf.scene);gltf.scene.traverse(o=>{if(o.name)nodes[o.name]=o;});
    for(let i=0;i<2;i++){const art=card(.42);art.position.set(i? .94:-.94,1.818,.55);art.rotation.x=-Math.PI/2;deckArt.push(art);scene.add(art);assignCover(art,state.decks?.[i]);}
    for(let i=0;i<8;i++){const art=card(.45);art.position.set(-2.05,1.89,.114+i*.075);crateArt.push(art);scene.add(art);}
    for(const side of ['L','R'])for(const part of ['upperArm','forearm']){const n=nodes[part+side];if(n)n.userData.baseLength=part==='upperArm'?.73:.67;}
    ready=true;crateKey=''; canvas.dataset.sceneStatus='ready';
  },undefined,()=>{canvas.dataset.sceneStatus='error';canvas.setAttribute('aria-label','Could not load 3D booth. Audio controls remain available.');});
  function poseArm(side,shoulder,hand) {
    // Two-bone elbow construction follows named anchors, with a small reach lean.
    const mid=shoulder.clone().lerp(hand,.48);mid.z-=.22;mid.x+=side==='L'?-.19:.19;
    const elbow=nodes['elbow'+side];if(elbow)elbow.position.copy(mid);
    const joint=nodes['shoulder'+side];if(joint)joint.position.copy(shoulder);
    for(const [name,a,b] of [['upperArm',shoulder,mid],['forearm',mid,hand]]){
      const obj=nodes[name+side];if(!obj)continue;const delta=b.clone().sub(a);
      obj.position.copy(a).add(b).multiplyScalar(.5);obj.quaternion.setFromUnitVectors(Y,delta.clone().normalize());obj.scale.set(1,delta.length()/obj.userData.baseLength,1);
    }
    nodes['hand'+side]?.position.copy(hand);
  }
  const smooth = t=>{t=THREE.MathUtils.clamp(t,0,1);return t*t*(3-2*t);};
  function onTrackLoaded(index,track) {if(index!==0&&index!==1)return;queue.push({index,track});if(queue.length>4)queue.shift();}
  function update(next,dt=1/60) {
    if(disposed)return;state=next||state;const now=performance.now();
    if(now-lastRender<32)return;const elapsed=Math.min(.1,(now-lastRender)/1000||dt);lastRender=now;time+=elapsed;
    const w=canvas.clientWidth,h=canvas.clientHeight;if(!w||!h)return;
    if(width!==w||height!==h){width=w;height=h;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}
    if(ready){
      const newKey=(state.crate||[]).map(t=>t.id+':'+(t.artworkUrl||'')).join('|');
      if(newKey!==crateKey){crateKey=newKey;crateArt.forEach((m,i)=>{const t=state.crate?.[i];m.visible=!!t;if(t)assignCover(m,t);});}
      if(!action&&queue.length){action={...queue.shift(),start:time};assignCover(carry,action.track);}
      let lean=0; const hands=[vector([-.15,1.94,.48]),vector([.15,1.94,.48])];
      if(action){
        const p=(time-action.start)/(reduced.matches ? .15 : 3.4),target=positions.decks[action.index];
        if(p<.25){hands[0].lerp(positions.crate,smooth(p/.25));carry.visible=false;lean=-.32*smooth(p/.25);}
        else if(p<.72){const u=smooth((p-.25)/.47);hands[0].copy(positions.crate).lerp(target,u);hands[0].y+=Math.sin(Math.PI*u)*.42;carry.visible=true;carry.position.copy(hands[0]);carry.position.y-=.08;carry.rotation.x=-Math.PI*.5*u;lean=-.32*(1-u);}
        else{carry.visible=false;assignCover(deckArt[action.index],action.track);hands[0].copy(target).lerp(vector([-.15,1.94,.48]),smooth((p-.72)/.28));}
        if(p>=1)action=null;
      } else if(state.transition) {const p=THREE.MathUtils.clamp(state.transition.progress||0,0,1);hands[1].set(-.18+.36*p,1.925,.93);}
      for(let i=0;i<2;i++){
        const d=state.decks?.[i]||{},side=i?'B':'A';
        if(nodes['platter'+side]&&d.playing&&!reduced.matches)nodes['platter'+side].rotation.y+=elapsed*1.1;
        const fader=nodes['channelFader'+side];if(fader)fader.position.z=.81-.22*THREE.MathUtils.clamp(d.level??1,0,1);
        const eq=nodes['eq'+side];if(eq)eq.rotation.y=(THREE.MathUtils.clamp(d.low??0,-24,0)/24)*2.5;
        const label=nodes['recordLabel'+side];if(label)label.material.emissiveIntensity=d.playing?1.5:.2;
        if(!action&&d.id&&deckArt[i].userData.trackId!==d.id){deckArt[i].userData.trackId=d.id;assignCover(deckArt[i],d);}
      }
      const x=(state.decks?.[1]?.fade??0)-(state.decks?.[0]?.fade??1);
      if(nodes.crossfader)nodes.crossfader.position.x=THREE.MathUtils.clamp(x,-1,1)*.18;
      for(const name of ['torso','waist','neck','head','visor','visorSignal'])if(nodes[name])nodes[name].position.x=lean;
      const playing=state.decks?.some(d=>d.playing);
      const bob=playing&&!reduced.matches?Math.sin(time*3.2)*.023:0;
      if(nodes.head)nodes.head.position.y=3.29+bob;
      poseArm('L',vector([-.47+lean,2.75,-.46]),hands[0]);poseArm('R',vector([.47+lean,2.75,-.46]),hands[1]);
    }
    renderer.render(scene,camera);
  }
  return {update,onTrackLoaded,dispose(){disposed=true;scene.traverse(o=>{o.geometry?.dispose();if(o.material){const materials=Array.isArray(o.material)?o.material:[o.material];materials.forEach(m=>m.dispose());}});for(const t of textures.values())t.dispose();env.dispose();renderer.dispose();}};
}
