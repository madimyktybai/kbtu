import re
import json

# читаем файл
with open("raw.txt", "r", encoding="utf-8") as file:
    text = file.read()

# ---------------- ЦЕНЫ ----------------
# заменил \s на обычный пробел
prices = re.findall(r"\d[\d ]*,\d{2}", text)
clean_prices = [float(p.replace(" ", "").replace(",", ".")) for p in prices]

# ---------------- ТОВАРЫ ----------------
products = re.findall(r"\d+\.\n(.+)", text)

# ---------------- ИТОГО ----------------
total_match = re.search(r"ИТОГО:\n([\d\s]+,\d{2})", text)
total = total_match.group(1) if total_match else None

# ---------------- ДАТА ----------------
date_match = re.search(r"\d{2}\.\d{2}\.\d{4}", text)
date = date_match.group() if date_match else None

# ---------------- ВРЕМЯ ----------------
time_match = re.search(r"\d{2}:\d{2}:\d{2}", text)
time = time_match.group() if time_match else None

# ---------------- ОПЛАТА ----------------
payment_match = re.search(r"(Наличные|Банковская карта)", text)
payment = payment_match.group() if payment_match else None

# ---------------- РЕЗУЛЬТАТ ----------------
result = {
    "products": products,
    "prices": clean_prices,
    "total": total,
    "date": date,
    "time": time,
    "payment_method": payment
}

print(json.dumps(result, indent=4, ensure_ascii=False))