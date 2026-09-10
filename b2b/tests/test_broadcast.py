"""Exercise FFmpeg streaming ingestion and rolling HLS output with synthetic audio."""
import subprocess
import pytest
from b2b.broadcast import Broadcast


def test_streaming_master_to_hls(tmp_path):
    source=tmp_path/'tone.webm'
    subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','sine=frequency=110:duration=6','-c:a','libopus',str(source)],check=True)
    live=tmp_path/'live';broadcast=Broadcast(live)
    session=broadcast.start()
    data=source.read_bytes()
    for index in range(0,len(data),4096):broadcast.write(session,data[index:index+4096])
    assert not broadcast.stop('stale-session')
    assert broadcast.stop(session)
    manifest=(live/'index.m3u8').read_text()
    assert '#EXTM3U' in manifest
    assert list(live.glob('*.ts'))
    with pytest.raises(ValueError):broadcast.write(session,b'stale')
