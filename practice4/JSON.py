import json

with open('sample-data.json', 'r') as file:
    data = json.load(file)

print("Interface Status")
print("=" * 80)

# Используем f-строки с указанием ширины колонок для ровного выравнивания
print(f"{'DN':<50} {'Description':<20} {'Speed':<7} {'MTU':<6}")
print("-" * 50, "-" * 20, "-" * 7, "-" * 6)


interfaces = data["imdata"]
for item in interfaces:
    attr = item["l1PhysIf"]["attributes"]

    dn = attr["dn"]
    description = attr["descr"]
    speed = attr["speed"]
    mtu = attr["mtu"]

    print(f"{dn:<50} {description:<20} {speed:<7} {mtu:<6}")