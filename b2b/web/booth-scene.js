import * as THREE from './vendor/three.module.min.js';
import { GLTFLoader } from './vendor/GLTFLoader.js';
import { RoomEnvironment } from './vendor/RoomEnvironment.js';
import { mergeGeometries } from './vendor/BufferGeometryUtils.js';
import { createHumanRig } from './human-rig.js?v=idle-1';

// This is a spatial illustration of real mixer state, never an audio clock or controller.
export function createBoothScene(canvas) {
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false }); }
  catch { canvas.setAttribute('aria-label', '3D view unavailable. Audio controls remain available.'); return { update() {}, onTrackLoaded() {}, dispose() {} }; }
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 1.6));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = .95;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene(); scene.background = new THREE.Color('#cbc1b1');
  const environment = new THREE.PMREMGenerator(renderer);
  const room = new RoomEnvironment(); const env = environment.fromScene(room, .04);
  scene.environment = env.texture; scene.environmentIntensity=.45; room.dispose(); environment.dispose();
  const camera = new THREE.PerspectiveCamera(34, 1, .1, 60);
  camera.position.set(4.6, 3.6, 7.4); camera.lookAt(-.3, 1.95, -.5);
  const viewPosition=camera.position.clone(), viewTarget=new THREE.Vector3(-.3,1.95,-.5), cameraTarget=viewTarget.clone();
  let motionRate=1;
  scene.add(new THREE.HemisphereLight(0xffedcc, 0x807761, .6));
  const key = new THREE.DirectionalLight(0xffdfab, 2.4); key.position.set(-4,4,1); scene.add(key);
  key.castShadow=true; key.shadow.mapSize.set(2048,2048);
  Object.assign(key.shadow.camera,{left:-5,right:5,top:5,bottom:-4,near:.1,far:16});
  key.shadow.normalBias=.04; key.shadow.bias=-.001;
  const rim = new THREE.DirectionalLight(0xfff0dd, .55); rim.position.set(3,5,4); scene.add(rim);
  const floor = new THREE.Mesh(new THREE.CircleGeometry(5, 64), new THREE.MeshStandardMaterial({ color: 0xc9c5bd, roughness: .65 }));
  floor.rotation.x=-Math.PI/2; floor.position.y=.05; floor.visible=false; scene.add(floor);
  const nodes = {}, deckArt=[], crateArt=[], textures = new Map();
  let width=0,height=0,time=0,lastRender=0,disposed=false,crateKey='', state={decks:[]}, ready=false;
  const queue=[]; let action=null; let humanRig=null;let transitionBlend=0;let idleBlend=0;let peakReach=0,peakContact=0,frameCount=0,frameStart=performance.now();
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const vector = p => new THREE.Vector3(...p), Y=vector([0,1,0]);
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
  const carry=card(.45);carry.visible=false;carry.castShadow=true;scene.add(carry);
  // Grasp the top edge at the distal index/middle joints, never the wrist.
  const gripOffset=side=>vector([side==='L'?-.10:.10,.225,.004]);
  const sleeveGrip=(side,center,rotation)=>gripOffset(side).applyQuaternion(rotation).add(center);
  new GLTFLoader().load('/scene/b2b-booth.glb?v=678ba95-grasp-1',gltf=>{
    if(disposed)return;
    scene.add(gltf.scene);gltf.scene.traverse(o=>{if(o.name)nodes[o.name]=o;if(o.isMesh){
      o.castShadow=!o.name.startsWith('djGlasses');o.receiveShadow=!o.name.startsWith('djGlasses');
      for(const m of (Array.isArray(o.material)?o.material:[o.material])){
        if(m.name.startsWith('American walnut veneer'))m.color.setRGB(.58,.28,.115);
        // Thin spectacles need stable transparency on animated glTF meshes.
        if(m.name.startsWith('Translucent olive acetate')){m.transmission=0;m.transparent=true;m.opacity=.30;m.depthWrite=false;}
        if(m.name.startsWith('Clear spectacle lenses')){m.transmission=0;m.transparent=true;m.opacity=.07;m.depthWrite=false;}
      }
    }});
    for(let i=0;i<2;i++){const art=new THREE.Mesh(new THREE.CircleGeometry(.095,48),new THREE.MeshStandardMaterial({roughness:.85}));art.position.set(i? .94:-.94,1.818,.55);art.rotation.x=-Math.PI/2;deckArt.push(art);scene.add(art);assignCover(art,state.decks?.[i]);}
    for(let i=0;i<8;i++){const art=card(.45);art.position.set(-2.05,1.89,.114+i*.075);crateArt.push(art);scene.add(art);}
    for(const side of ['L','R'])for(const part of ['upperArm','forearm']){const n=nodes[part+side];if(n?.isMesh){n.geometry.computeBoundingBox();n.userData.baseLength=n.geometry.boundingBox.max.y-n.geometry.boundingBox.min.y;}}
    // Batch only static geometry. Preserve the independently animated controls and skin.
    gltf.scene.updateMatrixWorld(true);
    const batches=new Map();
    gltf.scene.traverse(o=>{
      if(!o.isMesh||o.isSkinnedMesh||o.children.length||Array.isArray(o.material)||/^(platter|recordLabel|channelFader|eq|crossfader)/.test(o.name))return;
      for(let p=o.parent;p;p=p.parent)if(/^(platter|recordLabel|channelFader|eq|crossfader)/.test(p.name))return;
      const signature=Object.entries(o.geometry.attributes).map(([name,a])=>`${name}:${a.itemSize}:${a.normalized}:${a.array.constructor.name}`).sort().join('|');
      const key=o.material.uuid+'|'+!!o.geometry.index+'|'+signature;
      const group=batches.get(key)||{material:o.material,objects:[]};group.objects.push(o);batches.set(key,group);
    });
    for(const {material,objects} of batches.values()){
      if(objects.length<2)continue;
      const copies=objects.map(o=>{const g=o.geometry.clone();g.applyMatrix4(o.matrixWorld);return g;});
      const geometry=mergeGeometries(copies);copies.forEach(g=>g.dispose());
      if(!geometry)continue;
      const merged=new THREE.Mesh(geometry,material);merged.name='Static '+material.name;merged.castShadow=true;merged.receiveShadow=true;scene.add(merged);
      objects.forEach(o=>{o.removeFromParent();o.geometry.dispose();});
    }
    humanRig=createHumanRig(nodes);
    if(humanRig)canvas.dataset.poseError=humanRig.initialPoseError.toFixed(5);
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
    if(now-lastRender<32)return;const elapsed=Math.min(.1,(now-lastRender)/1000||dt);lastRender=now;time+=elapsed*motionRate;
    const cameraBlend=reduced.matches?1:1-Math.exp(-elapsed*7);
    camera.position.lerp(viewPosition,cameraBlend);cameraTarget.lerp(viewTarget,cameraBlend);camera.lookAt(cameraTarget);
    const w=canvas.clientWidth,h=canvas.clientHeight;if(!w||!h)return;
    if(width!==w||height!==h){width=w;height=h;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();}
    if(ready){
      const newKey=(state.crate||[]).map(t=>t.id+':'+(t.artworkUrl||'')).join('|');
      if(newKey!==crateKey){crateKey=newKey;crateArt.forEach((m,i)=>{const t=state.crate?.[i];m.visible=!!t;if(t)assignCover(m,t);});}
      if(!action&&queue.length){action={...queue.shift(),start:time};peakReach=0;peakContact=0;assignCover(carry,action.track);}
      transitionBlend+=(Number(!!state.transition&&!action)-transitionBlend)*Math.min(1,elapsed*4);
      let lean=0,shift=0,advance=0,carrySide=null;
      const restHands=[vector([-.20,1.93,.28]),vector([.20,1.93,.28])];
      const hands=restHands.map(v=>v.clone());
      if(action){
        const p=(time-action.start)/(reduced.matches ? .15 : 5.2);
        const start=vector([-2.05,1.96,.40]), middle=vector([0,2.08,.53]);
        const end=vector([action.index ? .94 : -.94,1.825,.55]);
        const rotation=new THREE.Quaternion(), center=start.clone();
        const reach=(side,point)=>humanRig ? humanRig.wristForGrip(side,point) : point.clone();
        const leftPick=reach('L',sleeveGrip('L',start,rotation));
        if(p<.22){
          const u=smooth(p/.22);shift=-1.12*u;advance=.18*u;
          hands[0].lerp(leftPick,u);hands[1].x+=shift;hands[1].z+=advance;carry.visible=false;
        }else if(p<.54){
          const u=smooth((p-.22)/.32);shift=-1.12*(1-u);advance=.18*(1-u);
          center.lerp(middle,u);center.y+=Math.sin(Math.PI*u)*.12;
          carry.visible=true;carrySide='L';
          hands[0].copy(reach('L',sleeveGrip('L',center,rotation)));
          hands[1].x+=shift;hands[1].z+=advance;
          if(action.index===1)hands[1].lerp(reach('R',sleeveGrip('R',center,rotation)),smooth((p-.40)/.14));
        }else if(p<.85){
          // Briefly share the top edge before the right hand takes deck B.
          const u=smooth((p-.60)/.25),index=action.index;
          shift=(index?1:-1)*.3*u;advance=.28*u;
          center.copy(middle).lerp(end,u);center.y+=Math.sin(Math.PI*u)*.08;
          rotation.setFromAxisAngle(vector([1,0,0]),-Math.PI/2*u);
          carry.visible=true;carrySide=index?'R':'L';
          hands[index].copy(reach(carrySide,sleeveGrip(carrySide,center,rotation)));
          hands[1-index].x+=shift;hands[1-index].z+=advance;
          if(index===1){
            const release=reach('L',sleeveGrip('L',middle,new THREE.Quaternion()));
            const withdrawn=release.clone().add(vector([-.22,.10,-.18]));
            hands[0].copy(p<.70 ? release.lerp(withdrawn,smooth((p-.60)/.10)) : withdrawn.lerp(restHands[0],smooth((p-.70)/.15)));
          }
        }else{
          carry.visible=false;
          const u=smooth((p-.85)/.15),index=action.index;
          shift=(index?1:-1)*.3*(1-u);advance=.28*(1-u);
          hands[1-index].x+=shift;hands[1-index].z+=advance;assignCover(deckArt[index],action.track);
          rotation.setFromAxisAngle(vector([1,0,0]),-Math.PI/2);
          hands[index].copy(reach(index?'R':'L',sleeveGrip(index?'R':'L',end,rotation))).lerp(restHands[index],u);
        }
        if(carry.visible){carry.position.copy(center);carry.quaternion.copy(rotation);}
        if(p>=1)action=null;
      }else if(transitionBlend>.001){
        const cross=(state.decks?.[1]?.fade??0)-(state.decks?.[0]?.fade??1);
        advance=.44*transitionBlend;
        hands[1].lerp(vector([THREE.MathUtils.clamp(cross,-1,1)*.18,1.96,.60]),transitionBlend);
      }
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
      if(humanRig){
        const idleTarget=!action&&transitionBlend<.01?1:0;
        idleBlend=reduced.matches?0:idleBlend+(idleTarget-idleBlend)*(1-Math.exp(-elapsed*5));
        const pose=humanRig.update({hands,shift,advance,idle:idleBlend,time,tempo:state.tempo||124,playing:state.decks?.some(d=>d.playing)});
        canvas.dataset.idleMotion=idleBlend.toFixed(3);
        canvas.dataset.reachError=pose.maxReachError.toFixed(4);
        canvas.dataset.contactError=pose.maxContactError.toFixed(4);
        if(action){if(pose.maxReachError>peakReach)canvas.dataset.peakReachPhase=((time-action.start)/5.2).toFixed(3);peakReach=Math.max(peakReach,pose.maxReachError);peakContact=Math.max(peakContact,pose.maxContactError);}
        canvas.dataset.motionPhase=action?((time-action.start)/(reduced.matches ? .15 : 5.2)).toFixed(3):'idle';
        canvas.dataset.peakReachError=peakReach.toFixed(4);canvas.dataset.peakContactError=peakContact.toFixed(4);
        if(carry.visible&&carrySide){
          const edgeOffset=gripOffset(carrySide).applyQuaternion(carry.quaternion);
          carry.position.copy(pose.grips[carrySide]).sub(edgeOffset);
          canvas.dataset.gripError=sleeveGrip(carrySide,carry.position,carry.quaternion).distanceTo(pose.grips[carrySide]).toFixed(5);
        }
      }else{
        for(const name of ['torso','waist','neck','head'])if(nodes[name])nodes[name].position.x=lean;
        poseArm('L',vector([-.47+lean,2.75,-.46]),hands[0]);poseArm('R',vector([.47+lean,2.75,-.46]),hands[1]);
      }

    }
    renderer.render(scene,camera);
    frameCount++;if(now-frameStart>3000){canvas.dataset.fps=(frameCount*1000/(now-frameStart)).toFixed(1);frameStart=now;frameCount=0;}
    canvas.dataset.drawCalls=renderer.info.render.calls;canvas.dataset.triangles=renderer.info.render.triangles;
  }
  function setView(name){
    const views={room:[[4.6,3.6,7.4],[-.3,1.95,-.5]],face:[[.65,3.13,2.25],[0,3.25,.06]],hands:[[1.7,2.65,2.7],[0,1.9,.4]]};
    const [p,t]=views[name]||views.room;viewPosition.set(...p);viewTarget.set(...t);
  }
  return {update,onTrackLoaded,setView,setMotionRate(rate){motionRate=THREE.MathUtils.clamp(Number(rate)||1,.1,1);},dispose(){disposed=true;scene.traverse(o=>{o.geometry?.dispose();if(o.material){const materials=Array.isArray(o.material)?o.material:[o.material];materials.forEach(m=>m.dispose());}});for(const t of textures.values())t.dispose();env.dispose();renderer.dispose();}};
}
