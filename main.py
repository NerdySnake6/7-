"""Example of the Decorator pattern for currency rates."""

from __future__ import annotations

import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from urllib.request import urlopen

import yaml


class Component(ABC):
    """Common interface for all components."""

    @abstractmethod
    def operation(self) -> str:
        """Return data in a selected format."""


class CurrencyRates(Component):
    """Component that gets currency rates from the Central Bank API."""

    url = "https://www.cbr-xml-daily.ru/daily_json.js"

    def __init__(self, data: dict | None = None) -> None:
        """Create component with optional prepared data for tests."""
        self.data = data

    def operation(self) -> str:
        """Return currency rates in JSON format."""
        if self.data is not None:
            return json.dumps(self.data, ensure_ascii=False)

        with urlopen(self.url, timeout=10) as response:
            return response.read().decode("utf-8")


class Decorator(Component):
    """Base class for decorators."""

    def __init__(self, component: Component) -> None:
        """Save wrapped component."""
        self.component = component

    def operation(self) -> str:
        """Return result from wrapped component."""
        return self.component.operation()

    def get_json_data(self) -> dict:
        """Convert wrapped component result to a dictionary."""
        return json.loads(self.component.operation())


class YamlDecorator(Decorator):
    """Decorator for YAML format."""

    def operation(self) -> str:
        """Return data in YAML format."""
        return yaml.dump(self.get_json_data(), allow_unicode=True, sort_keys=False)

    def save_to_file(self, filename: str) -> None:
        """Save YAML data to a file."""
        Path(filename).write_text(self.operation(), encoding="utf-8")


class CsvDecorator(Decorator):
    """Decorator for CSV format."""

    def operation(self) -> str:
        """Return data in CSV format."""
        data = self.get_json_data()
        result = ["CharCode,Name,Value"]

        for currency in data["Valute"].values():
            result.append(
                f"{currency['CharCode']},{currency['Name']},{currency['Value']}"
            )

        return "\n".join(result)

    def save_to_file(self, filename: str) -> None:
        """Save CSV data to a file."""
        data = self.get_json_data()

        with Path(filename).open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["CharCode", "Name", "Value"])

            for currency in data["Valute"].values():
                writer.writerow(
                    [currency["CharCode"], currency["Name"], currency["Value"]]
                )


if __name__ == "__main__":
    rates = CurrencyRates()

    print(rates.operation())
    print(YamlDecorator(rates).operation())
    print(CsvDecorator(rates).operation())
