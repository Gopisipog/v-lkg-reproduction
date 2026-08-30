"""Verify pipeline guard logic: fire-once, never auto-re-trigger after rerun."""
import unittest

class FakeSessionState(dict):
    """Mimics st.session_state: dict-like but with attribute access."""
    def __getattr__(self, k):
        if k.startswith('_'): raise AttributeError(k)
        try: return self[k]
        except KeyError: raise AttributeError(k)
    def __setattr__(self, k, v):
        self[k] = v

class FakeButton:
    def __init__(self, click_sequence):
        self._clicks = iter(click_sequence + [False]*100)
    def clicked(self):
        return next(self._clicks)

class GuardTest(unittest.TestCase):

    def setUp(self):
        self.ss = FakeSessionState()
        self.button = FakeButton([])  # never clicked

    def run_cycle(self, video_url=""):
        """Simulate one Streamlit re-run cycle with guard logic."""
        if "pipeline_armed" not in self.ss:
            self.ss.pipeline_armed = False
        if self.button.clicked():
            self.ss.pipeline_armed = True
        if self.ss.pipeline_armed and video_url:
            self.ss.pipeline_armed = False
            return "FIRED"
        return "IDLE"

    def test_no_url_no_click(self):
        self.assertEqual(self.run_cycle(""), "IDLE")

    def test_url_no_click(self):
        self.assertEqual(self.run_cycle("https://youtube.com/watch?v=test"), "IDLE")

    def test_no_url_with_click(self):
        self.button = FakeButton([True])
        self.assertEqual(self.run_cycle(""), "IDLE")

    def test_click_fires_exactly_once(self):
        """Button click + URL → fires. Next cycle → IDLE (no re-trigger)."""
        self.button = FakeButton([True])
        self.assertEqual(self.run_cycle("https://youtube.com/watch?v=test"), "FIRED")
        self.assertEqual(self.run_cycle("https://youtube.com/watch?v=test"), "IDLE")

    def test_rerun_preserves_url_no_retrigger(self):
        """After successful fire, subsequent cycles don't re-trigger."""
        self.button = FakeButton([True])
        self.assertEqual(self.run_cycle("https://youtube.com/watch?v=test"), "FIRED")
        for _ in range(10):
            self.assertEqual(self.run_cycle("https://youtube.com/watch?v=test"), "IDLE")

    def test_fresh_click_after_completion(self):
        """User clicks button again → should fire again."""
        self.button = FakeButton([True, False, False, True])
        # First click fires
        self.assertEqual(self.run_cycle("https://youtube.com/watch?v=test"), "FIRED")
        # Idle cycles
        self.assertEqual(self.run_cycle("https://youtube.com/watch?v=test"), "IDLE")
        self.assertEqual(self.run_cycle("https://youtube.com/watch?v=test"), "IDLE")
        # Second fresh click fires
        self.assertEqual(self.run_cycle("https://youtube.com/watch?v=test"), "FIRED")

    def test_changed_url_after_click(self):
        """After click fires, changing URL shouldn't auto-fire."""
        self.button = FakeButton([True])
        self.assertEqual(self.run_cycle("https://youtube.com/watch?v=a"), "FIRED")
        # URL changes but no new click
        self.assertEqual(self.run_cycle("https://youtube.com/watch?v=b"), "IDLE")

    def test_empty_url_after_click(self):
        """After click fires, clearing URL shouldn't cause issues."""
        self.button = FakeButton([True])
        self.assertEqual(self.run_cycle("https://youtube.com/watch?v=test"), "FIRED")
        self.assertEqual(self.run_cycle(""), "IDLE")

    def test_rapid_double_click_same_cycle(self):
        """Even if button reports clicked twice (shouldn't happen), only fires once per cycle."""
        self.button = FakeButton([True])
        self.assertEqual(self.run_cycle("url"), "FIRED")
        self.assertEqual(self.run_cycle("url"), "IDLE")

if __name__ == "__main__":
    unittest.main()
