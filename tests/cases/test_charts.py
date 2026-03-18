"""
Test chart types: pie, bar, group bar.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kaxe
from runner import judge, sanity, smoke


@smoke()
@sanity()
@judge(
    elements=["pie slices", "labels or legend"],
    focus="pie chart legibility",
    strict_elements=False,
)
def test_pie_chart():
    """Pie chart with title."""
    chart = kaxe.chart.Pie()
    chart.add(19, "n1")
    chart.add(6, "n2")
    chart.add(8, "n3")
    chart.add(58, "n4")
    chart.add(25, "n4")
    chart.title("$x^2$ er nu en lang lang laaaang titel")
    return chart


@smoke()
@sanity()
@judge(
    elements=["bars", "axis labels", "legend", "title"],
    focus="bar chart legibility and bar visibility",
)
def test_bar_chart():
    """Bar chart with legends."""
    chart = kaxe.chart.Bar()
    chart.add(2013, 2.8)
    chart.add(2014, 3.1)
    chart.add(2015, 3.3)
    chart.add(2016, 3.6)
    chart.add(2017, [4, 1])
    chart.add(2018, 4.3)
    chart.add(2019, 4.6)
    chart.add(2020, 5)
    chart.add(2021, [5.5, 2, 1])
    chart.add(2022, [5.9, 1])
    chart.add(2023, [6.4, 0, 1])
    chart.legends("Profit", "Marked", "Andre buzzwords")
    chart.title("$x^2$ er nu en lang lang laaaang titel", "$x^2$ er nu en lang lang laaaang titel", "$x^2$ er nu en lang lang laaaang titel")
    chart.style(rotateLabel=45)
    return chart


@smoke()
@sanity()
@judge(
    elements=["grouped bars", "bars visible"],
    focus="group bar chart legibility",
    min_score=5,
)
def test_group_bar_chart():
    """Group bar chart."""
    chart = kaxe.chart.GroupBar()
    chart.add(2013, 2.8)
    chart.add(2014, 3.1)
    chart.add(2015, 3.3)
    chart.add(2016, 3.6)
    chart.add(2017, [4, 1])
    chart.add(2018, 4.3)
    chart.add(2019, 4.6)
    chart.add(2020, 5)
    chart.add(2021, [5.5, 2, 1])
    chart.add(2022, [5.9, 1])
    chart.add(2023, [6.4, None, 1])
    chart.legends("Profit", "Marked", "Andre buzzwords")
    chart.title("$x^2$ er nu en lang lang laaaang titel", "$x^2$ er nu en lang lang laaaang titel", "$x^2$ er nu en lang lang laaaang titel")
    chart.style(rotateLabel=0)
    return chart
