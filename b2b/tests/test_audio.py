import numpy as np
from scipy.io import wavfile
from b2b.audio import rhythm, SR, prepare, decode, tonal
import pytest
from b2b.planner import edge, make_plan

def kicks(bpm=125,seconds=100,offset=.13):
    y=np.zeros(int(seconds*SR),dtype=np.float32)
    t=np.arange(int(.2*SR))/SR
    hit=.8*np.sin(2*np.pi*(65*t+8*(1-np.exp(-30*t))))*np.exp(-28*t)
    for at in np.arange(offset,seconds-.2,60/bpm):
        i=int(at*SR);y[i:i+len(hit)]+=hit
    return y

def test_constant_grid_with_leading_offset():
    bpm,phase,beats,confidence,_,_=rhythm(kicks())
    assert abs(bpm-125)<.03
    assert abs(phase-.13)<.035
    assert confidence>.95
    assert len(beats)>190

def test_stretch_preserves_grid_and_pitch(tmp_path):
    y=kicks(seconds=45)
    # Persistent tone measures pitch independently of beat timing.
    t=np.arange(len(y))/SR;y+=.08*np.sin(2*np.pi*440*t)
    source=tmp_path/'a.wav';out=tmp_path/'b.wav';wavfile.write(source,SR,y)
    prepare(source,out,128/125);result=decode(out)
    bpm,*_=rhythm(result)
    assert abs(bpm-128)<.08
    spec=np.abs(np.fft.rfft(result[SR:SR*10]));freq=np.fft.rfftfreq(SR*9,1/SR)
    region=(freq>400)&(freq<470)
    assert abs(freq[region][np.argmax(spec[region])]-440)<1
    assert abs(len(result)/SR-45/(128/125))<.08

def fixture(id,bpm=125,**overrides):
    return dict(id=id,ready=True,bpm=bpm,introBars=16,outroBars=16,entry=0,introEnd=16*240/bpm,
                exitEnd=320,energy=.7,key={'root':0,'confidence':'estimated'},**overrides)

def test_transition_duration_and_windows():
    a=fixture('a');b=fixture('b',128);e=edge(a,b,128,16)
    assert e['duration']==30
    assert e['bars']==16
    assert e['exit']+16*240/a['bpm']<=a['exitEnd']+.001
    assert abs(e['exit']/(16*240/a['bpm'])-round(e['exit']/(16*240/a['bpm'])))<.001
    assert abs((b['introEnd']-e['entry'])*b['bpm']/240-16)<.001

def test_reject_unsafe_pair():
    a=fixture('a');b=fixture('b');b['ready']=False
    assert edge(a,b,125,16) is None
    b['ready']=True;b['introBars']=4
    assert edge(a,b,125,16) is None

def test_order_no_repeat_and_only_valid_edges():
    ts=[fixture('a'),fixture('b',126),fixture('c',124)];p=make_plan(ts,125)
    assert len(p['order'])==3 and len(set(p['order']))==3
    assert len(p['transitions'])==2
    assert p['mode']=='Rules'

@pytest.mark.parametrize('frequencies,expected', [([261.63,329.63,392],'C'),([220,261.63,329.63],'Am')])
def test_known_tonal_chords(frequencies,expected):
    t=np.arange(SR*20)/SR
    y=sum(.15*np.sin(2*np.pi*f*t) for f in frequencies)
    assert tonal(y)['name']==expected

def test_auto_rejects_large_tempo_change():
    assert edge(fixture('a',133),fixture('b',125),124,16) is None
