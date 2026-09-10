"""Focused regressions for calendar parsing and contribution streaks."""
import datetime as dt
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from update_metrics import parse_calendar, compute_streaks, render

def days(*values):
    return [{'date':date,'count':count,'level':int(count>0)} for date,count in values]

class MetricsTests(unittest.TestCase):
    def test_current_day_may_be_unfinished(self):
        result=compute_streaks(days(('2026-09-07',1),('2026-09-08',3),('2026-09-09',0)),dt.date(2026,9,9))
        self.assertEqual(result,{'current':2,'longest':2})

    def test_cross_year_streak(self):
        result=compute_streaks(days(('2025-12-30',1),('2025-12-31',2),('2026-01-01',1)),dt.date(2026,1,1))
        self.assertEqual(result,{'current':3,'longest':3})

    def test_yesterday_zero_breaks_current_streak(self):
        result=compute_streaks(days(('2026-09-07',2),('2026-09-08',0),('2026-09-09',0)),dt.date(2026,9,9))
        self.assertEqual(result,{'current':0,'longest':1})

    def test_missing_day_is_not_bridged(self):
        result=compute_streaks(days(('2026-09-07',2),('2026-09-09',3)),dt.date(2026,9,9))
        self.assertEqual(result,{'current':1,'longest':1})

    def test_parses_tooltips_and_zero_days(self):
        markup='<td id="a" data-date="2026-09-08" data-level="4"></td><tool-tip for="a">1,234 contributions on September 8th.</tool-tip><td id="b" data-date="2026-09-09" data-level="0"></td><tool-tip for="b">No contributions on September 9th.</tool-tip>'
        self.assertEqual([d['count'] for d in parse_calendar(markup)],[1234,0])

    def test_handles_singular_and_legacy_data_count(self):
        markup='<td id="a" data-date="2026-09-08" data-level="1"></td><tool-tip for="a">1 contribution on September 8th.</tool-tip><rect data-date="2026-09-09" data-level="2" data-count="5"/>'
        self.assertEqual([d['count'] for d in parse_calendar(markup)],[1,5])

    def test_rejects_missing_counts_instead_of_inventing_zero(self):
        with self.assertRaises(ValueError):parse_calendar('<td id="a" data-date="2026-09-08" data-level="1"></td>')

    def test_rejects_error_pages(self):
        with self.assertRaises(ValueError):parse_calendar('<html>Rate limited</html>')

    def test_duplicate_cell_does_not_double_count(self):
        parsed=parse_calendar('<td id="a" data-date="2026-09-09" data-level="1" data-count="2"/><td id="b" data-date="2026-09-09" data-level="1" data-count="2"/>')
        self.assertEqual(len(parsed),1)

    def test_saved_real_data_renders_valid_svgs(self):
        import json
        path=Path(__file__).resolve().parents[1]/'data'/'metrics.json'
        if not path.exists():self.skipTest('Initial real-data snapshot not available')
        data=json.loads(path.read_text())
        for body in render(data).values():ET.fromstring(body)

if __name__=='__main__':unittest.main()
