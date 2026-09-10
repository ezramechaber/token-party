"""Encode the browser's actual master bus as a bounded rolling HLS stream."""
import subprocess
import threading
import uuid


class Broadcast:
    def __init__(self, directory):
        self.directory=directory
        directory.mkdir(parents=True,exist_ok=True)
        self.lock=threading.RLock();self.process=None;self.session=None;self.log=None

    def stop(self, session=None):
        with self.lock:
            if session and session != self.session:return False
            if self.process:
                try:self.process.stdin.close();self.process.wait(timeout=5)
                except (OSError,subprocess.TimeoutExpired):self.process.kill();self.process.wait()
                self.process=None
            if self.log:self.log.close();self.log=None
            self.session=None
            return True

    def start(self):
        with self.lock:
            self.stop()
            for pattern in ('*.ts','*.m3u8','*.tmp'):
                for path in self.directory.glob(pattern):path.unlink(missing_ok=True)
            self.session=uuid.uuid4().hex
            self.log=(self.directory/'encoder.log').open('wb')
            self.process=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','warning','-y',
                '-i','pipe:0','-vn','-c:a','aac','-b:a','192k','-ar','48000',
                '-f','hls','-hls_time','2','-hls_list_size','8',
                '-hls_flags','delete_segments+temp_file+independent_segments',
                '-hls_segment_filename',str(self.directory/'segment-%06d.ts'),
                str(self.directory/'index.m3u8')],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=self.log)
            return self.session

    def write(self, session, chunk):
        with self.lock:
            if session != self.session or not self.process or self.process.poll() is not None:
                raise ValueError('Broadcast is no longer running. Start it again.')
            try:self.process.stdin.write(chunk);self.process.stdin.flush()
            except (BrokenPipeError,OSError) as error:raise ValueError('Audio encoder stopped. Start broadcasting again.') from error
