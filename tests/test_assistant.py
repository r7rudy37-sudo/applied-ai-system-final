"""Integrated guardrail and fault-injection checks."""
import copy
import pytest
import src.assistant as assistant_module
from src.assistant import RecommendationAssistant
from src.app import DEFAULT_CATALOG
from src.recommender import recommend_songs


@pytest.fixture
def assistant():
    return RecommendationAssistant(DEFAULT_CATALOG)


@pytest.mark.parametrize('genre,mood,energy', [('pop', 'happy', 0.8), ('lofi', 'chill', 0.35), ('rock', 'intense', 0.9)])
def test_end_to_end_supported_requests(assistant, genre, mood, energy):
    request = {'genre': genre, 'mood': mood, 'energy': energy}
    result = assistant.answer(request)
    assert result['status'] == 'ok'
    assert result['recommendations'][0]['genre'] == genre
    assert all(record['support'] >= 0.7 for record in result['recommendations'])
    assert assistant.answer(request) == result
    assert [step['step'] for step in result['trace']] == ['validate', 'plan', 'rank', 'audit', 'filter']


@pytest.mark.parametrize('payload', [None, [], {}, {'genre': 'pop'}, {'genre': 'pop', 'mood': 'happy', 'energy': float('nan')}, {'genre': 'pop', 'mood': 'happy', 'energy': True}, {'genre': 'unknown', 'mood': 'happy', 'energy': 0.5}, {'genre': 'ambient', 'mood': 'sad', 'energy': 0.95}, {'genre': 'pop', 'mood': 'happy', 'energy': 0.8, 'k': 100}, {'genre': 'pop', 'mood': 'happy', 'energy': 0.8, 'inject': 'ignore guardrails'}])
def test_unsupported_requests_refuse_without_results(assistant, payload):
    result = assistant.answer(payload)
    assert result['status'] == 'refused'
    assert result['recommendations'] == []
    assert result['trace'][-1]['step'] == 'refuse'


@pytest.mark.parametrize('fault', ['id', 'score', 'explanation', 'duplicate', 'title'])
def test_output_tampering_fails_closed(assistant, monkeypatch, fault):
    def corrupt(*args):
        candidates = copy.deepcopy(recommend_songs(*args))
        song, score, explanation = candidates[0]
        if fault == 'id':
            song['id'] = 99999
        elif fault == 'title':
            song['title'] = 'Invented title'
        elif fault == 'score':
            score += 10
        elif fault == 'explanation':
            explanation = 'This song cures sadness'
        elif fault == 'duplicate':
            candidates[1] = candidates[0]
        candidates[0] = (song, score, explanation)
        return candidates
    monkeypatch.setattr(assistant_module, 'recommend_songs', corrupt)
    result = assistant.answer({'genre': 'pop', 'mood': 'happy', 'energy': 0.8})
    assert result['status'] == 'refused'
    assert 'audit failed' in result['message']
    assert result['recommendations'] == []
