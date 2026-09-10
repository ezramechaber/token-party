import * as THREE from './vendor/three.module.min.js';

// Exact-length two-bone reach on a connected skinned character. Audio remains
// the source of events; this module has no access to the transport or mixer.
export function createHumanRig(nodes) {
  const rig=nodes.djRig;
  if(!rig)return null;
  rig.updateMatrixWorld(true);
  const Y=new THREE.Vector3(0,1,0), cache={};
  for(const side of ['L','R']) {
    const upper=nodes['upperArm'+side], lower=nodes['forearm'+side], hand=nodes['hand'+side];
    if(!upper||!lower||!hand)throw new Error('The DJ skeleton is missing an arm joint.');
    // Resolve landmarks through the hand hierarchy: the source skeleton's L/R
    // suffixes are anatomical and differ from our screen-side aliases.
    const tips=[];hand.traverse(n=>{if(/^finger[23]-3\./.test(n.name))tips.push(n);});
    const gripLocal=new THREE.Vector3();
    for(const tip of tips)gripLocal.add(hand.worldToLocal(tip.getWorldPosition(new THREE.Vector3())));
    if(tips.length)gripLocal.multiplyScalar(1/tips.length);else gripLocal.set(0,.30,0);
    cache[side]={upper,lower,hand,gripLocal,
      upperQ:upper.getWorldQuaternion(new THREE.Quaternion()),
      lowerQ:lower.getWorldQuaternion(new THREE.Quaternion()),
      handQ:hand.getWorldQuaternion(new THREE.Quaternion()),
      lengths:[upper.getWorldPosition(new THREE.Vector3()).distanceTo(lower.getWorldPosition(new THREE.Vector3())),lower.getWorldPosition(new THREE.Vector3()).distanceTo(hand.getWorldPosition(new THREE.Vector3()))]};
  }
  const origin=rig.position.clone();
  const idleBones=['torso','head'].map(name=>nodes[name]).filter(Boolean).map(bone=>({bone,rotation:bone.getWorldQuaternion(new THREE.Quaternion())}));
  const X=new THREE.Vector3(1,0,0),Z=new THREE.Vector3(0,0,1);
  const turn=(axis,angle)=>new THREE.Quaternion().setFromAxisAngle(axis,angle);
  let maxReachError=0;
  const expected=rig.userData.posePositions||{};
  let initialPoseError=0;
  for(const [name,xyz] of Object.entries(expected)){
    const n=nodes[name];if(n)initialPoseError=Math.max(initialPoseError,n.getWorldPosition(new THREE.Vector3()).distanceTo(new THREE.Vector3(...xyz)));
  }
  function worldRotation(obj,quaternion){
    const parentQ=obj.parent.getWorldQuaternion(new THREE.Quaternion());
    obj.quaternion.copy(parentQ.invert().multiply(quaternion));obj.updateMatrixWorld(true);
  }
  function pointBone(obj,baseQ,direction){
    const initial=Y.clone().applyQuaternion(baseQ);
    const swing=new THREE.Quaternion().setFromUnitVectors(initial,direction.clone().normalize());
    worldRotation(obj,swing.multiply(baseQ));
  }
  function wristForGrip(side,grip){
    const {gripLocal,handQ}=cache[side];
    return grip.clone().sub(gripLocal.clone().applyQuaternion(handQ));
  }
  function update({hands,shift=0,advance=0,idle=0,time=0,tempo=124,playing=false}){
    // Slow, overlapping rhythms avoid a conspicuous repeating sway. Arm IK
    // keeps the hands planted while the chest and weight move underneath.
    const breath=Math.sin(time*Math.PI*2/4.8);
    rig.position.copy(origin);
    rig.position.x+=shift+idle*(.024*Math.sin(time*.57)+.009*Math.sin(time*.23));
    rig.position.y+=idle*.007*breath;
    rig.position.z+=advance+idle*.006*Math.sin(time*.67);
    rig.updateMatrixWorld(true);
    for(const {bone,rotation} of idleBones){
      const q=rotation.clone();
      if(bone.name==='torso')q.premultiply(turn(Z,idle*.008*Math.sin(time*.57))).premultiply(turn(X,idle*.006*breath));
      else {
        const nod=playing ? .022*Math.sin(time*Math.PI*2*tempo/60):.018*Math.sin(time*1.13);
        q.premultiply(turn(Y,idle*(.065*Math.sin(time*.43)+.035*Math.sin(time*.19))))
          .premultiply(turn(X,idle*(nod+.012*breath)))
          .premultiply(turn(Z,idle*.013*Math.sin(time*.71)));
      }
      worldRotation(bone,q);
    }
    maxReachError=0;
    const actual=[],grips={};let maxContactError=0;
    for(const [index,side] of ['L','R'].entries()){
      const {upper,lower,hand,upperQ,lowerQ,handQ,lengths:[a,b]}=cache[side];
      const shoulder=upper.getWorldPosition(new THREE.Vector3());
      const requested=hands[index].clone();const delta=requested.clone().sub(shoulder);
      const distance=delta.length(),clamped=THREE.MathUtils.clamp(distance,Math.abs(a-b)+.001,a+b-.002);
      const direction=delta.normalize();const target=shoulder.clone().addScaledVector(direction,clamped);
      maxReachError=Math.max(maxReachError,target.distanceTo(requested));
      const along=(a*a-b*b+clamped*clamped)/(2*clamped);
      const height=Math.sqrt(Math.max(0,a*a-along*along));
      const pole=new THREE.Vector3((side==='L'?-1.1:1.1)+shift,2.22,-.5).sub(shoulder);
      pole.addScaledVector(direction,-pole.dot(direction)).normalize();
      const elbow=shoulder.clone().addScaledVector(direction,along).addScaledVector(pole,height);
      pointBone(upper,upperQ,elbow.clone().sub(shoulder));
      pointBone(lower,lowerQ,target.clone().sub(elbow));
      worldRotation(hand,handQ);
      grips[side]=hand.localToWorld(cache[side].gripLocal.clone());
      actual.push(hand.getWorldPosition(new THREE.Vector3()));
      maxContactError=Math.max(maxContactError,actual.at(-1).distanceTo(target));
    }
    return {hands:actual,grips,maxReachError,maxContactError,initialPoseError};
  }
  return {update,wristForGrip,initialPoseError};
}
