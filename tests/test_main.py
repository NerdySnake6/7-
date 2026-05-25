"""Tests for the currency decorators."""

import json
from pathlib import Path

import yaml

from main import CsvDecorator, CurrencyRates, YamlDecorator


DATA = {
    "Valute": {
        "USD": {
            "CharCode": "USD",
            "Name": "Доллар США",
            "Value": 90.1,
        },
        "EUR": {
            "CharCode": "EUR",
            "Name": "Евро",
            "Value": 98.2,
        },
    }
}


def test_base_component_returns_json() -> None:
    """Test JSON result from the base component."""
    rates = CurrencyRates(DATA)

    assert json.loads(rates.operation())["Valute"]["USD"]["Value"] == 90.1


def test_base_component_contains_currency_code() -> None:
    """Test that JSON contains currency code."""
    rates = CurrencyRates(DATA)

    assert "USD" in rates.operation()


def test_yaml_decorator_returns_yaml() -> None:
    """Test YAML decorator result."""
    result = YamlDecorator(CurrencyRates(DATA)).operation()

    assert yaml.safe_load(result)["Valute"]["EUR"]["Name"] == "Евро"


def test_yaml_decorator_saves_file(tmp_path: Path) -> None:
    """Test saving YAML to a file."""
    filename = tmp_path / "rates.yaml"

    YamlDecorator(CurrencyRates(DATA)).save_to_file(str(filename))

    assert "Доллар США" in filename.read_text(encoding="utf-8")


def test_csv_decorator_returns_csv() -> None:
    """Test CSV decorator result."""
    result = CsvDecorator(CurrencyRates(DATA)).operation()

    assert "CharCode,Name,Value" in result
    assert "USD,Доллар США,90.1" in result


def test_csv_decorator_saves_file(tmp_path: Path) -> None:
    """Test saving CSV to a file."""
    filename = tmp_path / "rates.csv"

    CsvDecorator(CurrencyRates(DATA)).save_to_file(str(filename))

    assert "EUR,Евро,98.2" in filename.read_text(encoding="utf-8")
