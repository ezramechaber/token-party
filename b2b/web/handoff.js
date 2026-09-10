// A queued handoff owns the incoming cue; an earlier manual pause does not.
export function cueIncoming(deck, cue, now) {
 if(!Number.isFinite(cue)||cue<0||cue>=deck.buffer.duration)throw Error('The incoming cue is outside the prepared audio.');
 deck.stop(false);
 deck.offset=cue;
 for(const parameter of [deck.fade.gain,deck.low.gain])parameter.cancelScheduledValues(now);
 deck.fade.gain.setValueAtTime(0,now);
 deck.low.gain.setValueAtTime(-24,now);
 deck.status('CUED FOR MIX');
}
export function handoffTime(deck, cue, now) {
 const starts=deck.running?deck.start:now+.1;
 const at=starts+cue-deck.offset;
 if(at<now+.06)throw Error('The outgoing deck has passed its planned exit. The incoming deck is cued; use Preview transition to hear the handoff now, or seek the outgoing deck before its outro and try mixing again.');
 return at;
}
