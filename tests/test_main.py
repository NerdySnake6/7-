"""Tests for currency decorators."""

import json
from pathlib import Path

import yaml

from main import CbrCurrencyRates, CsvDecorator, JsonDecorator, YamlDecorator


TEST_DATA = {
    "Date": "2024-01-01T11:30:00+03:00",
    "Valute": {
        "USD": {
            "CharCode": "USD",
            "Name": "Доллар США",
            "Value": 90.5,
        },
        "EUR": {
            "CharCode": "EUR",
            "Name": "Евро",
            "Value": 99.1,
        },
    },
}


def make_component() -> CbrCurrencyRates:
    """Create test component without real API requests."""

    def fetcher(_: str) -> bytes:
        """Return prepared JSON data."""
        return json.dumps(TEST_DATA).encode("utf-8")

    return CbrCurrencyRates(fetcher=fetcher)


def test_base_component_returns_json() -> None:
    """Check that base component returns JSON string."""
    result = make_component().operation()

    assert json.loads(result)["Valute"]["USD"]["CharCode"] == "USD"


def test_base_component_uses_fetcher() -> None:
    """Check that component uses passed fetcher."""
    component = CbrCurrencyRates(fetcher=lambda _: b'{"ok": true}')

    assert json.loads(component.operation()) == {"ok": True}


def test_json_decorator_returns_json() -> None:
    """Check JSON decorator result."""
    result = JsonDecorator(make_component()).operation()

    assert json.loads(result)["Valute"]["EUR"]["Value"] == 99.1


def test_json_decorator_saves_file(tmp_path: Path) -> None:
    """Check JSON decorator file saving."""
    file_path = tmp_path / "rates.json"

    JsonDecorator(make_component()).save_to_file(file_path)

    assert json.loads(file_path.read_text(encoding="utf-8"))["Date"]


def test_yaml_decorator_returns_yaml() -> None:
    """Check YAML decorator result."""
    result = YamlDecorator(make_component()).operation()

    assert yaml.safe_load(result)["Valute"]["USD"]["Name"] == "Доллар США"


def test_yaml_decorator_saves_file(tmp_path: Path) -> None:
    """Check YAML decorator file saving."""
    file_path = tmp_path / "rates.yaml"

    YamlDecorator(make_component()).save_to_file(file_path)

    assert yaml.safe_load(file_path.read_text(encoding="utf-8"))["Valute"]["EUR"]


def test_csv_decorator_returns_csv() -> None:
    """Check CSV decorator result."""
    result = CsvDecorator(make_component()).operation()

    assert "CharCode,Name,Value" in result
    assert "USD,Доллар США,90.5" in result


def test_csv_decorator_saves_file(tmp_path: Path) -> None:
    """Check CSV decorator file saving."""
    file_path = tmp_path / "rates.csv"

    CsvDecorator(make_component()).save_to_file(file_path)

    assert "EUR,Евро,99.1" in file_path.read_text(encoding="utf-8")
