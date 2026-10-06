"""Small desktop interface for UnitConvert; Python standard library only."""

import tkinter as tk
from tkinter import ttk

import core

CONVERSIONS = {
    "Температура: °C → °F": (core.celsius_to_fahrenheit, "°F"),
    "Температура: °F → °C": (core.fahrenheit_to_celsius, "°C"),
    "Длина: км → мили": (core.km_to_miles, "мили"),
    "Длина: мили → км": (core.miles_to_km, "км"),
    "Масса: кг → фунты": (core.kg_to_pounds, "фунты"),
    "Масса: фунты → кг": (core.pounds_to_kg, "кг"),
}


def main():
    window = tk.Tk()
    window.title("UnitConvert — конвертер единиц")
    window.geometry("580x360")
    window.resizable(False, False)
    panel = ttk.Frame(window, padding=24)
    panel.pack(fill="both", expand=True)
    ttk.Label(panel, text="UnitConvert", font=("Segoe UI", 22, "bold")).pack(anchor="w")
    ttk.Label(panel, text="Шесть простых преобразований единиц").pack(anchor="w", pady=(0, 20))
    mode = tk.StringVar(value=next(iter(CONVERSIONS)))
    ttk.Combobox(panel, textvariable=mode, values=list(CONVERSIONS), state="readonly", width=52).pack(fill="x")
    ttk.Label(panel, text="Исходное значение:").pack(anchor="w", pady=(14, 4))
    entry = ttk.Entry(panel, font=("Segoe UI", 13))
    entry.pack(fill="x")
    result = tk.StringVar(value="Введите число и нажмите «Перевести».")

    def calculate(event=None):
        try:
            value = float(entry.get().strip().replace(",", "."))
            function, unit = CONVERSIONS[mode.get()]
            converted = function(value)
            result.set(f"Результат: {converted:.8g} {unit}")
        except (ValueError, TypeError) as exc:
            if "could not convert" in str(exc):
                result.set("Ошибка: введите корректное число.")
            else:
                result.set(f"Ошибка: {exc}")

    ttk.Button(panel, text="Перевести", command=calculate).pack(anchor="w", pady=16)
    ttk.Label(panel, textvariable=result, wraplength=525, font=("Segoe UI", 11)).pack(anchor="w")
    ttk.Label(panel, text=f"Версия {core.__version__} · Команда «Крутые перцы»").pack(anchor="w", pady=(18, 0))
    entry.bind("<Return>", calculate)
    entry.focus_set()
    window.mainloop()


if __name__ == "__main__":
    main()
