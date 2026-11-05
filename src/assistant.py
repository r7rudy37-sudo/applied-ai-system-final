"""Reliable recommendation workflow extending the Project 3 simulator."""
import math
from .recommender import MODES, load_songs, normalize_preferences, recommend_songs, score_song


class RecommendationAssistant:
    """Validate, rank, audit, and either return supported results or refuse."""

    def __init__(self, catalog_path, minimum_support=0.7):
        if not isinstance(minimum_support, (int, float)) or not math.isfinite(minimum_support) or not 0 <= minimum_support <= 1:
            raise ValueError('minimum_support must be between 0 and 1')
        self.songs = load_songs(catalog_path)
        if not self.songs:
            raise ValueError('Catalog contains no songs')
        self.minimum_support = minimum_support
        self.by_id = {song['id']: song for song in self.songs}

    def answer(self, request):
        """Run the full workflow, exposing decisions rather than hidden guesses."""
        trace = []

        def refuse(reason):
            trace.append({'step': 'refuse', 'result': reason})
            return {'status': 'refused', 'message': reason, 'recommendations': [], 'trace': trace}

        if not isinstance(request, dict):
            return refuse('Request must be a JSON object.')
        allowed = {'genre', 'mood', 'energy', 'likes_acoustic', 'k', 'mode', 'diversity_penalty'}
        unknown = set(request) - allowed
        if unknown:
            return refuse('Unsupported request fields: ' + ', '.join(sorted(unknown)))
        if not {'genre', 'mood', 'energy'}.issubset(request):
            return refuse('Please provide genre, mood, and energy explicitly.')
        try:
            prefs = normalize_preferences(request)
            k = request.get('k', 3)
            mode = request.get('mode', 'genre-first')
            penalty = request.get('diversity_penalty', 0.8)
            if not isinstance(mode, str) or mode not in MODES:
                return refuse('Unknown ranking mode.')
            if isinstance(k, bool) or not isinstance(k, int) or not 1 <= k <= 10:
                return refuse('k must be an integer between 1 and 10.')
            if (isinstance(penalty, bool) or not isinstance(penalty, (float, int))
                    or not math.isfinite(penalty) or not 0 <= penalty <= 4):
                return refuse('diversity_penalty must be between 0 and 4.')
        except ValueError as exc:
            return refuse(str(exc))
        trace.append({'step': 'validate', 'result': 'valid explicit preferences'})
        for field in ('genre', 'mood'):
            labels = {song[field].casefold() for song in self.songs}
            if prefs[field] not in labels:
                return refuse(f'No catalog evidence for {field}: {prefs[field]}')
        trace.append({'step': 'plan', 'result': f'score {len(self.songs)} catalog records using {mode}'})
        candidates = recommend_songs(prefs, self.songs, len(self.songs), mode, penalty)
        trace.append({'step': 'rank', 'result': f'{len(candidates)} scored candidates; artist penalty {penalty}'})
        audited = self.audit(prefs, candidates, mode, penalty)
        if audited is None:
            return refuse('Output audit failed; no unaudited recommendations were released.')
        trace.append({'step': 'audit', 'result': 'IDs, records, scores, penalties, and explanations verified'})
        supported = [record for record in audited if record['support'] >= self.minimum_support][:k]
        if not supported:
            return refuse('The catalog does not contain a sufficiently supported match. Try different preferences.')
        trace.append({'step': 'filter', 'result': f'{len(supported)} results meet support threshold {self.minimum_support}'})
        return {
            'status': 'ok',
            'message': 'Rule-based recommendations from the synthetic catalog; support is not a probability of enjoyment.',
            'recommendations': supported,
            'trace': trace,
        }

    def audit(self, prefs, candidates, mode, penalty):
        """Fail closed on changed catalog records or inconsistent score reasons."""
        maximum = sum(MODES[mode].values()) + (0.25 if 'likes_acoustic' in prefs else 0)
        seen, artists, records = set(), {}, []
        for song, adjusted, explanation in candidates:
            identifier = song.get('id')
            if identifier not in self.by_id or identifier in seen or song != self.by_id[identifier]:
                return None
            base, reasons = score_song(prefs, song, mode)
            artist = song['artist'].casefold()
            deduction = penalty * artists.get(artist, 0)
            if deduction:
                reasons.append(f'repeated artist (-{deduction:.2f})')
            if not math.isfinite(adjusted) or not math.isclose(adjusted, base - deduction, abs_tol=1e-9):
                return None
            if explanation != '; '.join(reasons):
                return None
            records.append({
                'id': identifier, 'title': song['title'], 'artist': song['artist'],
                'genre': song['genre'], 'mood': song['mood'],
                'score': round(adjusted, 4), 'base_score': round(base, 4),
                'support': base / maximum, 'explanation': explanation,
            })
            artists[artist] = artists.get(artist, 0) + 1
            seen.add(identifier)
        return records
