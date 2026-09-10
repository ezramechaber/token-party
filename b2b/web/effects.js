// Deck insert effects: before level/crossfader, so faded-out decks cannot leak tails.
export function createDeckEffects(ctx, {tempo=124}={}) {
 const input=ctx.createGain(),output=ctx.createGain(),dry=ctx.createGain();
 input.connect(dry);dry.connect(output);
 let state={kind:'off',amount:.25,beats:.5,tempo},branch=null,disposed=false;
 const smooth=(param,value)=>{param.cancelScheduledValues(ctx.currentTime);param.setTargetAtTime(value,ctx.currentTime,.015);};
 function removeBranch(){if(!branch)return;input.disconnect(branch.first);branch.osc?.stop();for(const node of branch.nodes)node.disconnect();branch=null;}
 function build(){
  removeBranch();if(state.kind==='off')return;
  const wet=ctx.createGain(),delay=ctx.createDelay(2),feedback=ctx.createGain();wet.gain.value=0;delay.connect(wet);wet.connect(output);
  if(state.kind==='delay'){
   const highpass=ctx.createBiquadFilter(),lowpass=ctx.createBiquadFilter();highpass.type='highpass';highpass.frequency.value=250;lowpass.type='lowpass';lowpass.frequency.value=5500;
   input.connect(highpass);highpass.connect(delay);delay.connect(lowpass);lowpass.connect(feedback);feedback.connect(delay);feedback.gain.value=.28;
   branch={first:highpass,wet,delay,nodes:[highpass,lowpass,wet,delay,feedback]};
  }else{
   const osc=ctx.createOscillator(),depth=ctx.createGain();delay.delayTime.value=.003;depth.gain.value=.002;feedback.gain.value=.2;
   input.connect(delay);delay.connect(feedback);feedback.connect(delay);osc.connect(depth);depth.connect(delay.delayTime);osc.start();
   branch={first:delay,wet,delay,osc,nodes:[wet,delay,feedback,osc,depth]};
  }
 }
 function apply(){
  const mix=state.kind==='off'?0:state.amount*.45;
  smooth(dry.gain,1-mix);
  if(branch){smooth(branch.wet.gain,mix);if(state.kind==='delay')smooth(branch.delay.delayTime,60/state.tempo*state.beats);else smooth(branch.osc.frequency,state.tempo/60/8);}
 }
 return {input,output,
  set(values={}){
   if(disposed)return;
   const next={...state,...values};if(!['off','delay','flanger'].includes(next.kind))next.kind='off';
   for(const key of ['amount','beats','tempo'])if(!Number.isFinite(next[key]))next[key]=state[key];
   next.amount=Math.max(0,Math.min(1,next.amount));next.beats=Math.max(.25,Math.min(1,next.beats));next.tempo=Math.max(108,Math.min(142,next.tempo));
   const changed=next.kind!==state.kind;state=next;if(changed)build();apply();return {...state};
  },
  clear(){if(disposed)return;build();apply();},
  dispose(){if(disposed)return;removeBranch();input.disconnect();dry.disconnect();output.disconnect();disposed=true;}
 };
}
