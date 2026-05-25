# Лабораторная работа 2. Декоратор

Небольшой пример паттерна «Декоратор».

Программа получает курсы валют в JSON через API ЦБ РФ, а декораторы
преобразуют результат в YAML и CSV.

## Запуск

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

## Тесты

```bash
python3 -m pytest -q
```
