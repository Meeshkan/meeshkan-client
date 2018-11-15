from typing import Any
from unittest import mock
import os

import pytest

from meeshkan.tracker import TrackerBase
import meeshkan

def test_tracker_history():
    tb = TrackerBase()
    tracked_value = 0
    tb.add_tracked("tracked_value", tracked_value)  # Test adding (integer) values
    tracked_value += 1e-7
    tb.add_tracked("tracked_value", tracked_value)  # Test adding scientic notation
    history = tb._history_by_scalar
    assert len(history) == 1  # Number of value_names tracked
    assert "tracked_value" in history  # Keeps correct naming
    history = history["tracked_value"]
    assert len(history) == 2  # Correct number of values tracked
    assert history[0] == 0
    assert history[1] == 1e-7

    tb.add_tracked("another value", -2.3)  # Checks multiple value names
    assert len(tb._history_by_scalar) == 2
    assert tb._history_by_scalar["another value"][0] == -2.3


def test_generate_image():
    tb = TrackerBase()
    tb.add_tracked("tracked_value", 0)
    tb.add_tracked("tracked_value", 2)
    history = tb._history_by_scalar
    fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
    tb.generate_image(history, output_path=fname)
    new_fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp" + TrackerBase.DEF_IMG_EXT)
    assert os.path.isfile(new_fname)
    os.remove(new_fname)


def test_get_updates_with_image():
    tb = TrackerBase()
    tb.add_tracked("tracked_value", 1)
    tb.add_tracked("tracked_value", 2)
    history, fname = tb.get_updates()

    assert "tracked_value" in history
    assert len(history) == 1
    history = history["tracked_value"]
    assert len(history) == 2
    assert history[0] == 1
    assert history[1] == 2
    assert os.path.isfile(fname)
    os.remove(fname)

def test_get_latest_updates():
    tb = TrackerBase()
    tb.add_tracked("tracked_value", 1)
    tb.add_tracked("tracked_value", 2.2)
    tb.add_tracked("tracked_value", -4.1)
    history, fname = tb.get_updates(plot=False)
    history = history["tracked_value"]
    assert fname is None
    assert len(history) == 3
    assert history == [1, 2.2, -4.1]

    tb.add_tracked("tracked_value", 0)
    history, _ = tb.get_updates(plot=False)
    history = history["tracked_value"]
    assert len(history) == 1

    history, _ = tb.get_updates(plot=False, latest=False)
    history = history["tracked_value"]
    assert len(history) == 4


def test_get_updates_with_name():
    tb = TrackerBase()
    tb.add_tracked("tracked_value", 1)
    tb.add_tracked("another value", 1)
    history, _ = tb.get_updates(name="tracked_value", plot=False, latest=True)
    assert len(history) == 1
    assert len(history["tracked_value"]) == 1


def test_base_clean():
    tb = TrackerBase()
    tb.add_tracked("my value", 2)
    tb.add_tracked("another value", 0.4)
    assert len(tb._history_by_scalar) == 2
    tb.clean()
    assert len(tb._history_by_scalar) == 0


def test_base_refresh():
    # Should just call clean...
    tb = TrackerBase()
    tb.add_tracked("my value", 2)
    tb.add_tracked("another value", 0.4)
    assert len(tb._history_by_scalar) == 2
    tb.refresh()
    assert len(tb._history_by_scalar) == 0
