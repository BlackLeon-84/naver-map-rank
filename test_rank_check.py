import unittest

import rank_check


class AlertScheduleTests(unittest.TestCase):
    def test_regular_hour_alerts_even_without_rank_change(self):
        should_alert = getattr(rank_check, "should_alert", lambda *args: False)

        self.assertTrue(should_alert(3, 3, 9, [9, 19]))

    def test_thirteen_hundred_stays_silent_without_rank_change(self):
        should_alert = getattr(rank_check, "should_alert", lambda *args: False)

        self.assertFalse(should_alert(3, 3, 13, [9, 19]))

    def test_thirteen_hundred_alerts_when_rank_changes(self):
        should_alert = getattr(rank_check, "should_alert", lambda *args: False)

        self.assertTrue(should_alert(2, 3, 13, [9, 19]))

    def test_gangnam_has_one_fixed_alert_at_seventeen_hundred(self):
        should_alert = getattr(rank_check, "should_alert", lambda *args: False)

        self.assertFalse(should_alert(4, 4, 16, [17]))
        self.assertTrue(should_alert(4, 4, 17, [17]))
        self.assertFalse(should_alert(4, 4, 18, [17]))


if __name__ == "__main__":
    unittest.main()
