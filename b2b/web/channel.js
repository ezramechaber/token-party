import {createDeckEffects} from './effects.js';
// Three real EQ bands. Auto schedules only the low band; mid/high remain manual.
export function createChannel(ctx, destination, {trimDb=0, fade=1, tempo=124}={}) {
 const low=ctx.createBiquadFilter();low.type='lowshelf';low.frequency.value=200;
 const mid=ctx.createBiquadFilter();mid.type='peaking';mid.frequency.value=1000;mid.Q.value=.7;
 const high=ctx.createBiquadFilter();high.type='highshelf';high.frequency.value=4000;
 const trim=ctx.createGain();trim.gain.value=10**(trimDb/20);
 const level=ctx.createGain(),fader=ctx.createGain();fader.gain.value=fade;
 const effects=createDeckEffects(ctx,{tempo});
 low.connect(mid);mid.connect(high);high.connect(trim);trim.connect(effects.input);effects.output.connect(level);level.connect(fader);fader.connect(destination);
 return {low,mid,high,trim,level,fade:fader,effects};
}
export function crossfadeGains(position, balanced=true) {
 const p=Math.min(1,Math.max(0,position));
 return balanced?[p===1?0:Math.cos(p*Math.PI/2),p===0?0:Math.sin(p*Math.PI/2)]:[1-p,p];
}
export function waveformOverview(buffer, bins=1200) {
 const channels=Array.from({length:buffer.numberOfChannels},(_,i)=>buffer.getChannelData(i));
 const peaks=new Float32Array(bins),rms=new Float32Array(bins);
 for(let bin=0;bin<bins;bin++){
  const start=Math.floor(bin*buffer.length/bins),end=Math.floor((bin+1)*buffer.length/bins);let power=0,count=0;
  for(const channel of channels)for(let i=start;i<end;i++){const value=channel[i];peaks[bin]=Math.max(peaks[bin],Math.abs(value));power+=value*value;count++;}
  rms[bin]=count?Math.sqrt(power/count):0;
 }
 return {peaks,rms};
}
