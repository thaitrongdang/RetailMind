"""Hand-countable tests for the main and eligible-label metrics."""

from math import isclose, log2

import pytest

from retailmind.evaluation.metrics import aggregate_metrics, user_metrics


def test_perfect_ranking_and_unknown_future_label() -> None:
    candidates = {"A", "B", "C"}
    perfect = user_metrics(["A", "B", "C"], {"A", "B"}, candidates, k=3)
    assert perfect["recall_at_10"] == 1
    assert perfect["ndcg_at_10"] == 1
    assert perfect["hit_rate_at_10"] == 1
    unknown = user_metrics(["A", "B"], {"A", "X"}, candidates, k=2)
    assert unknown["recall_at_10"] == 0.5
    assert unknown["eligible_recall_at_10"] == 1
    assert unknown["label_availability"] == 0.5


def test_order_matters_and_all_wrong() -> None:
    candidates = {"A", "B", "C"}
    shifted = user_metrics(["C", "A", "B"], {"A", "B"}, candidates, k=3)
    expected = (1 / log2(3) + 1 / log2(4)) / (1 + 1 / log2(3))
    assert isclose(shifted["ndcg_at_10"], expected)
    assert shifted["recall_at_10"] == 1
    wrong = user_metrics(["C"], {"A"}, candidates, k=1)
    assert wrong["recall_at_10"] == 0
    assert wrong["ndcg_at_10"] == 0
    assert wrong["hit_rate_at_10"] == 0


def test_empty_labels_and_invalid_lists_are_rejected() -> None:
    with pytest.raises(ValueError, match="Empty-label"):
        user_metrics(["A"], set(), {"A"})
    with pytest.raises(ValueError, match="duplicate"):
        user_metrics(["A", "A"], {"A"}, {"A"})
    with pytest.raises(ValueError, match="ineligible"):
        user_metrics(["X"], {"A"}, {"A"})


def test_macro_average_and_coverage() -> None:
    candidates = {"A", "B", "C"}
    first = user_metrics(["A"], {"A"}, candidates)
    second = user_metrics(["B"], {"A"}, candidates)
    aggregate = aggregate_metrics([first, second], [["A"], ["B"]], candidates)
    assert aggregate["recall_at_10"] == 0.5
    assert aggregate["catalog_coverage"] == 2 / 3
    assert aggregate["evaluated_customers"] == 2
