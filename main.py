"""Currency rates converter with the Decorator pattern."""

from __future__ import annotations

import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable
from urllib.request import urlopen

import yaml


CurrencyData = dict[str, Any]
Fetcher = Callable[[str], bytes]


class CurrencyComponent(ABC):
    """Base interface for currency data components."""

    @abstractmethod
    def operation(self) -> str:
        """Return currency data as a string."""


class CbrCurrencyRates(CurrencyComponent):
    """Get currency rates from the Central Bank of Russia API."""

    API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"

    def __init__(self, fetcher: Fetcher | None = None) -> None:
        """Initialize the component with an optional fetcher."""
        self._fetcher = fetcher or self._default_fetcher

    def operation(self) -> str:
        """Return currency rates in JSON format."""
        return self._fetcher(self.API_URL).decode("utf-8")

    @staticmethod
    def _default_fetcher(url: str) -> bytes:
        """Load data from the API."""
        with urlopen(url, timeout=10) as response:
            return response.read()


class CurrencyDecorator(CurrencyComponent):
    """Base decorator for currency components."""

    def __init__(self, component: CurrencyComponent) -> None:
        """Store wrapped component."""
        self._component = component

    def operation(self) -> str:
        """Return data from wrapped component."""
        return self._component.operation()

    def _get_data(self) -> CurrencyData:
        """Return component data as a dictionary."""
        return json.loads(self._component.operation())


class JsonDecorator(CurrencyDecorator):
    """Decorator that returns and saves JSON data."""

    def operation(self) -> str:
        """Return formatted JSON data."""
        return json.dumps(self._get_data(), ensure_ascii=False, indent=2)

    def save_to_file(self, path: str | Path) -> None:
        """Save JSON data to a file."""
        Path(path).write_text(self.operation(), encoding="utf-8")


class YamlDecorator(CurrencyDecorator):
    """Decorator that returns and saves YAML data."""

    def operation(self) -> str:
        """Return YAML data."""
        return yaml.safe_dump(self._get_data(), allow_unicode=True, sort_keys=False)

    def save_to_file(self, path: str | Path) -> None:
        """Save YAML data to a file."""
        Path(path).write_text(self.operation(), encoding="utf-8")


class CsvDecorator(CurrencyDecorator):
    """Decorator that returns and saves CSV data."""

    def operation(self) -> str:
        """Return currency rates in CSV format."""
        data = self._get_data()
        rows = data.get("Valute", {}).values()
        output = ["CharCode,Name,Value"]

        for row in rows:
            output.append(f"{row['CharCode']},{row['Name']},{row['Value']}")

        return "\n".join(output)

    def save_to_file(self, path: str | Path) -> None:
        """Save CSV data to a file."""
        data = self._get_data()
        rows = data.get("Valute", {}).values()

        with Path(path).open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["CharCode", "Name", "Value"])

            for row in rows:
                writer.writerow([row["CharCode"], row["Name"], row["Value"]])


def main() -> None:
    """Show examples of all decorators."""
    component = CbrCurrencyRates()

    print(JsonDecorator(component).operation())
    print(YamlDecorator(component).operation())
    print(CsvDecorator(component).operation())


if __name__ == "__main__":
    main()
