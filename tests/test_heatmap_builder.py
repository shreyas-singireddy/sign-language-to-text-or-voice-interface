import pytest
from analytics.heatmap_builder import heatmap_builder

def test_build_alphabet_heatmap():
    freq = {"A": 5, "B": 10, "Z": 2}
    res = heatmap_builder.build_alphabet_heatmap(freq)
    
    assert "z" in res
    assert "x" in res
    assert "y" in res
    assert "text" in res
    
    # Grid should be 6 rows by 6 columns
    assert len(res["z"]) == 6
    assert len(res["z"][0]) == 6
    
    # Verify exact counts mapped
    # "A" is at row 0, col 0
    assert res["z"][0][0] == 5
    assert res["text"][0][0] == "A: 5"

def test_build_word_heatmap():
    freq = {"HELLO": 8, "EMERGENCY": 15, "WATER": 3, "RANDOM_UNKNOWN": 20}
    res = heatmap_builder.build_word_heatmap(freq, top_n=3)
    
    assert len(res["gestures"]) == 3
    assert len(res["counts"]) == 3
    
    # "RANDOM_UNKNOWN" has highest count, should be first
    assert res["gestures"][0] == "RANDOM_UNKNOWN"
    assert res["counts"][0] == 20
    
    # "EMERGENCY" should be second
    assert res["gestures"][1] == "EMERGENCY"
    assert res["counts"][1] == 15

def test_build_emotion_pie_data():
    dist = {"Neutral": 10, "Urgent": 2, "Friendly": 5}
    res = heatmap_builder.build_emotion_pie_data(dist)
    
    assert res["labels"] == ["Neutral", "Urgent", "Friendly"]
    assert res["values"] == [10, 2, 5]
    # Check that colors were mapped
    assert len(res["colors"]) == 3
    # Neutral should map to "#888888" (case-insensitive)
    assert res["colors"][0] == "#888888"

def test_build_confidence_trend():
    hist = {"80-90%": 12, "90-100%": 25}
    res = heatmap_builder.build_confidence_trend(hist)
    
    assert res["buckets"] == ["80-90%", "90-100%"]
    assert res["counts"] == [12, 25]
