"""Local measurements of recorded master output; not a substitute for musical listening."""
import json
import math
import re
import subprocess
from pathlib import Path
import numpy as np
from scipy import signal


def loudness(path):
    result=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-af','loudnorm=I=-16:TP=-1:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    values=json.loads(re.search(r'\{\s*"input_i".*?\}',result.stderr,re.S)[0])
    integrated=float(values['input_i']);peak=float(values['input_tp'])
    if not math.isfinite(integrated) or not math.isfinite(peak):raise ValueError('Cannot measure a silent track.')
    gain=min(6,max(-18,-16-integrated),-1-peak)
    return {'integratedLufs':integrated,'truePeakDb':peak,'gainDb':round(gain,2),'targetLufs':-16}


def inspect_capture(path,metadata):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    sr=22050;out=path.with_suffix('.wav')
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(path),'-ar',str(sr),'-ac','2',str(out)],check=True,capture_output=True)
    raw=subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','f32le','-'],check=True,capture_output=True).stdout
    stereo=np.frombuffer(raw,dtype='<f4').reshape(-1,2);y=stereo.mean(axis=1)
    if len(y)<sr:raise ValueError('Record at least one second of audio.')
    duration=len(y)/sr;starts=np.arange(0,max(1,len(y)-int(.4*sr)),int(.1*sr));times=starts/sr+.2
    def curve(samples):
        return np.array([20*np.log10(max(1e-8,np.sqrt(np.mean(samples[s:s+int(.4*sr)]**2)))) for s in starts])
    full=curve(stereo);low=signal.sosfiltfilt(signal.butter(3,[35,180],fs=sr,btype='band',output='sos'),y);bass=curve(low)
    start=float(metadata.get('blendStart',duration*.2));end=float(metadata.get('blendEnd',duration*.8))
    def mean_db(values,lo,hi):
        v=values[(times>=lo)&(times<hi)]
        return round(float(10*np.log10(np.mean(10**(v/10)))),2) if len(v) else None
    windows={'before':(max(.4,start-2),start),'middle':(start+(end-start)*.35,start+(end-start)*.65),'after':(end+.2,min(duration-.3,end+2.5))}
    levels={name:{'rmsDbfs':mean_db(full,*bounds),'bassDbfs':mean_db(bass,*bounds)} for name,bounds in windows.items()}
    f,t,sxx=signal.spectrogram(y,sr,nperseg=2048,noverlap=1536,scaling='spectrum')
    fig,axes=plt.subplots(2,1,figsize=(13,7),sharex=True,gridspec_kw={'height_ratios':[2,1]},layout='constrained')
    fig.patch.set_facecolor('#101218')
    for ax in axes:
        ax.set_facecolor('#151a22');ax.tick_params(colors='#d7dcec');ax.xaxis.label.set_color('#d7dcec');ax.yaxis.label.set_color('#d7dcec')
        for spine in ax.spines.values():spine.set_color('#475269')
        ax.axvline(start,color='#f1b6d8',lw=1);ax.axvline(end,color='#c1b9ff',lw=1)
    sel=(f>=30)&(f<=10000);axes[0].pcolormesh(t,f[sel],10*np.log10(np.maximum(sxx[sel],1e-12)),shading='auto',cmap='magma',vmin=-85,vmax=-15)
    axes[0].set_yscale('log');axes[0].set_ylim(30,10000);axes[0].set_ylabel('Frequency (Hz)');axes[0].set_title(str(metadata.get('label','Recorded mix'))+' · actual master output',color='#eef0f6',loc='left')
    axes[1].plot(times,full,color='#eab5d1',label='Full-band RMS');axes[1].plot(times,bass,color='#aaa5f1',label='35–180 Hz RMS')
    axes[1].legend(facecolor='#151a22',labelcolor='#d7dcec',edgecolor='#475269');axes[1].set_ylabel('Level (dBFS)');axes[1].set_xlabel('Seconds from recording start');axes[1].set_xlim(0,duration);axes[1].grid(alpha=.15)
    png=path.with_suffix('.png');fig.savefig(png,dpi=150,facecolor=fig.get_facecolor());plt.close(fig)
    result={'id':path.stem,'duration':round(duration,3),'peakDbfs':round(20*np.log10(max(float(np.max(np.abs(stereo))),1e-9)),2),'levels':levels,'metadata':metadata,'audio':out.name,'spectrogram':png.name}
    path.with_suffix('.json').write_text(json.dumps(result,indent=2));return result
