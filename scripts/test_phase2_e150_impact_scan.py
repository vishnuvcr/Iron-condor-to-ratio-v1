import pandas as pd

from phase2_e150_impact_scan import classify_close_impact, as_ist


def test_impact_classification_treats_changed_as_affected():
    old = pd.Timestamp("2025-10-30 15:30", tz="Asia/Kolkata")
    corrected = pd.Timestamp("2025-10-30 15:29", tz="Asia/Kolkata")
    assert classify_close_impact(old, corrected) == "changed"


def test_impact_classification_treats_old_only_as_affected():
    old = pd.Timestamp("2025-10-30 15:30", tz="Asia/Kolkata")
    assert classify_close_impact(old, pd.NaT) == "old_only"


def test_impact_classification_treats_corrected_only_as_affected():
    corrected = pd.Timestamp("2025-10-30 15:30", tz="Asia/Kolkata")
    assert classify_close_impact(pd.NaT, corrected) == "corrected_only"


def test_impact_classification_equivalent_naive_and_aware_closes_are_same():
    naive = pd.Timestamp("2025-10-30 15:30")
    aware = pd.Timestamp("2025-10-30 15:30", tz="Asia/Kolkata")
    assert as_ist(naive) == as_ist(aware)
    assert classify_close_impact(naive, aware) is None
