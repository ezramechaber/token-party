"""House pulse grids anchored to attacks, with separate rendered-audio timing evidence.

This estimates beats, not musical downbeats or drum identities. Low-band periodicity
finds the pulse; broadband attacks remove the timbre-dependent low-envelope delay.
"""
import numpy as np
from scipy import optimize, signal


def _weighted_median(values, weights):
    order = np.argsort(values)
    return float(values[order][np.searchsorted(np.cumsum(weights[order]), np.sum(weights) / 2)])


def _attacks(y, sr):
    # Zero-phase filtering avoids adding a frequency-dependent filter delay.
    hop = max(1, round(sr * .0025))
    filtered = signal.sosfiltfilt(signal.butter(2, [300, min(8000, sr * .45)],
                                               fs=sr, btype='band', output='sos'), y)
    n = len(filtered) // hop
    envelope = np.sqrt(np.mean(filtered[:n * hop].reshape(n, hop) ** 2, axis=1))
    flux = np.maximum(0, envelope - np.roll(envelope, 2))
    flux[:2] = 0
    peaks, _ = signal.find_peaks(flux, distance=max(1, int(.10 * sr / hop)),
                                 prominence=max(float(np.percentile(flux, 75)) * .6, 1e-8))
    # Return onset rise, rather than maximum energy or a universal lag constant.
    starts = []
    for peak in peaks:
        start = peak
        while start > max(0, peak - 4) and flux[start - 1] > flux[peak] * .2:
            start -= 1
        starts.append((start + .5) * hop / sr)
    return np.asarray(starts), flux[peaks]


def local_attack_offset(y, sr, bpm, offset, start=0., end=None):
    """Signed seconds to ADD to a grid cue to align with local audible attacks.

    Insufficient/ambiguous percussion returns reliable=False and zero correction.
    The caller should preserve the nominal map in such regions and expose uncertainty.
    """
    end = len(y) / sr if end is None else min(end, len(y) / sr)
    start = max(0., start)
    lo = max(0, int((start - .2) * sr))
    hi = min(len(y), int((end + .2) * sr))
    if hi - lo < sr:
        return {'offset': 0., 'spread': None, 'count': 0, 'reliable': False}
    times, weights = _attacks(y[lo:hi], sr)
    times += lo / sr
    period = 60 / bpm
    residual = (times - offset + period / 2) % period - period / 2
    mask = (times >= start) & (times < end) & (np.abs(residual) < .085)
    values = residual[mask]
    weights = weights[mask]
    if len(values) < 8:
        return {'offset': 0., 'spread': None, 'count': len(values), 'reliable': False}
    weights = np.minimum(weights, np.percentile(weights, 70))
    correction = _weighted_median(values, weights)
    spread = _weighted_median(np.abs(values - correction), weights)
    enough = len(values) >= max(8, (end - start) / period * .4)
    reliable = bool(enough and spread < .018)
    return {'offset': correction if reliable else 0., 'spread': float(spread),
            'count': len(values), 'reliable': reliable}


def rhythm(y, sr=22050):
    """Drop-in six-value replacement for audio.rhythm; final envelope uses 10ms frames."""
    hop = round(sr * .01)
    low = signal.sosfilt(signal.butter(3, [35, 180], fs=sr, btype='band', output='sos'), y)
    n = len(low) // hop
    envelope = np.sqrt(np.mean(low[:n * hop].reshape(n, hop) ** 2, axis=1))
    novelty = np.maximum(0, envelope - np.roll(envelope, 2)); novelty[:2] = 0
    peaks, _ = signal.find_peaks(novelty, distance=int(.27 * sr / hop),
                                 prominence=max(float(np.percentile(novelty, 75)) * .6, 1e-5))
    times = peaks * hop / sr
    weights = novelty[peaks]
    if len(times) < 16:
        raise ValueError('Not enough stable percussion to build a house beat grid.')
    # Cap accents so one loud breakdown cannot outweigh the rest of the record.
    weights = np.minimum(weights, np.percentile(weights, 80))
    candidates = np.arange(108, 142, .025)
    scores = [abs(np.sum(weights * np.exp(2j * np.pi * times * b / 60))) for b in candidates]
    initial = float(candidates[np.argmax(scores)])
    fit = optimize.minimize_scalar(lambda b: -abs(np.sum(weights * np.exp(2j * np.pi * times * b / 60))),
                                   bounds=(initial - .04, initial + .04), method='bounded')
    bpm = float(fit.x); period = 60 / bpm
    vector = np.sum(weights * np.exp(2j * np.pi * times / period))
    phase = float((np.angle(vector) % (2 * np.pi)) * period / (2 * np.pi))
    residual = np.abs((times - phase + period / 2) % period - period / 2)
    good = residual < .055
    confidence = float(np.sum(weights[good]) / max(np.sum(weights), 1e-8))
    # Use multiple drum-rich regions, not the opening (which may have no kicks).
    corrections = []
    for start in np.arange(0, len(y) / sr - 12, 24):
        evidence = local_attack_offset(y, sr, bpm, phase, start, start + 24)
        if evidence['reliable']:
            corrections.append(evidence['offset'])
    if corrections:
        phase = (phase + float(np.median(corrections))) % period
    else:
        # No reliable broadband attack evidence: retain the measured low-band pulse.
        confidence = min(confidence, .6)
    beats = np.arange(phase, len(y) / sr, period)
    return bpm, phase, beats, confidence, times[good], envelope


def prepared_anchors(y, sr, source_bpm, target_bpm, source_offset, source_duration):
    """Local WSOLA timing corrections for an already prepared file.

    A cue maps to sourceTime / ratio + offset. Sparse anchors are evidence, not
    a new tempo curve; use the nearest reliable anchor to preserve beat spacing.
    """
    ratio = target_bpm / source_bpm
    period = 60 / source_bpm
    anchors = []
    for source_time in np.arange(source_offset, source_duration, 16 * period):
        center = source_time / ratio
        evidence = local_attack_offset(y, sr, target_bpm, source_offset / ratio,
                                       center - 16 * 60 / target_bpm,
                                       center + 16 * 60 / target_bpm)
        anchors.append({'sourceTime': round(float(source_time), 6),
                        'preparedTime': round(float(center + evidence['offset']), 6),
                        **evidence})
    return anchors
