import csv      
import json     
import os       
import sys      
from datetime import date, datetime  # date — для типа поля birthday, datetime — для парсинга строк

import psycopg2              # основной драйвер для работы с PostgreSQL
import psycopg2.extras       # RealDictCursor — курсор, который возвращает строки как словари

from connect import get_connection  


def _conn():
    # Открываем новое соединение с базой данных.
    # Вызывается в каждой функции отдельно — это намеренно,
    # чтобы не держать одно долгое соединение на весь сеанс работы программы.
    return get_connection()


def _fmt_date(d):
    # Превращает объект date в строку вида "2000-12-31".
    # Если дата не задана (None) — возвращает пустую строку,
    # чтобы не получить ошибку при выводе.
    return d.isoformat() if d else ""


def _parse_date(s):
    # Пытается распознать дату из строки формата "YYYY-MM-DD".
    # Используется при импорте контактов, где дата приходит как текст.
    # Если строка пустая или формат неверный — возвращаем None и предупреждаем пользователя.
    s = (s or "").strip()  # на всякий случай убираем лишние пробелы по краям
    if not s:
        return None  # пустая строка — просто нет даты, это нормально

    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        # дата была, но формат неправильный — сообщаем об этом
        print(f"  Неверная дата '{s}' (нужно YYYY-MM-DD), пропускаю.")
        return None


def _print_contacts(rows):
    # выводит список контактов в терминал.
    # Каждый контакт занимает три строки:
    #   1) ID, имя и фамилия
    #   2) email, день рождения, группа
    #   3) телефоны с типами (домашний / рабочий / мобильный)

    if not rows:
        print("  (контакты не найдены)")
        return

    sep = "-" * 80  # горизонтальная черта для визуального разделения контактов
    print(sep)

    for r in rows:
        phones = r.get("phones", [])

        # Собираем все телефоны в одну строку вида: "+7... [mobile], +7... [work]"
        # Если телефонов нет — пишем явно, чтобы было понятно
        phone_str = ", ".join(
            f"{p['phone']} [{p['type']}]"
            for p in phones
        ) if phones else "(нет телефонов)"

        # Выводим контакт. Тире «—» ставим там, где поле не заполнено
        print(
            f"  [{r['id']:>4}]  {r['first_name']} {r.get('last_name') or ''}\n"
            f"          {r.get('email') or '—'} "
            f"   {_fmt_date(r.get('birthday')) or '—'} "
            f"   {r.get('group_name') or '—'}\n"
            f"          {phone_str}"
        )

    print(sep)


def _fetch_contacts_with_phones(conn, contact_ids):
    # Загружает из базы контакты по списку ID и прикрепляет к каждому его телефоны.
    # Делаем два отдельных запроса: сначала основные данные, потом телефоны —
    # так проще, чем пытаться склеить всё в одном JOIN с повторяющимися строками.

    if not contact_ids:
        return []  # нечего запрашивать — возвращаем пустой список сразу

    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

        # Первый запрос: основная информация о контактах + название группы через JOIN
        cur.execute(
            """
            SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
                   g.name AS group_name
            FROM contacts c
            LEFT JOIN groups g ON g.id = c.group_id
            WHERE c.id = ANY(%s)
            """,
            (list(contact_ids),),
        )
        # Складываем результат в словарь по id, чтобы потом быстро добавлять телефоны
        contacts = {r["id"]: dict(r) for r in cur.fetchall()}

        # Второй запрос: все телефоны для этих же контактов
        cur.execute(
            "SELECT contact_id, phone, type FROM phones WHERE contact_id = ANY(%s)",
            (list(contact_ids),),
        )

        # Добавляем каждый телефон к соответствующему контакту в словаре
        for row in cur.fetchall():
            contacts[row["contact_id"]].setdefault("phones", []).append(
                {"phone": row["phone"], "type": row["type"]}
            )

    # Убеждаемся, что поле "phones" есть у каждого контакта, даже если телефонов нет
    for c in contacts.values():
        c.setdefault("phones", [])

    # Возвращаем список в том же порядке, в котором пришли contact_ids
    return [contacts[cid] for cid in contact_ids if cid in contacts]




# Инициализация базы данных


def init_schema():
    # Читает SQL-файлы schema.sql и procedures.sql из той же папки, что и этот скрипт,
    # и выполняет их в базе данных. Нужно запускать один раз при первом развёртывании,
    # или повторно, если нужно обновить структуру БД.

    base = os.path.dirname(os.path.abspath(__file__))  # папка, где лежит этот файл

    with _conn() as conn:
        with conn.cursor() as cur:

            for fname in ("schema.sql", "procedures.sql"):
                fpath = os.path.join(base, fname)

                with open(fpath, encoding="utf-8") as f:
                    sql = f.read()

                cur.execute(sql)  # выполняем весь файл целиком как один SQL-блок

        conn.commit()  # фиксируем изменения — без этого ничего не сохранится

    print("База данных и процедуры успешно применены.")


# Поиск и фильтрация контактов


def filter_by_group():
    # Показывает список доступных групп и выводит все контакты выбранной группы.
    # Группу можно выбрать как по числовому ID, так и по названию — удобно в обоих случаях.

    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, name FROM groups ORDER BY name")
            groups = cur.fetchall()

    if not groups:
        print("Группы не найдены.")
        return

    print("\nСписок групп:")
    for g in groups:
        print(f"  {g['id']}. {g['name']}")

    choice = input("Введите ID или название группы: ").strip()

    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

            # Если пользователь ввёл цифру — ищем по ID, иначе — по названию без учёта регистра
            if choice.isdigit():
                cur.execute(
                    """
                    SELECT c.id FROM contacts c
                    JOIN groups g ON g.id = c.group_id
                    WHERE g.id = %s
                    """,
                    (int(choice),),
                )
            else:
                cur.execute(
                    """
                    SELECT c.id FROM contacts c
                    JOIN groups g ON g.id = c.group_id
                    WHERE LOWER(g.name) = LOWER(%s)
                    """,
                    (choice,),
                )

            ids = [r["id"] for r in cur.fetchall()]

        results = _fetch_contacts_with_phones(conn, ids)

    _print_contacts(results)


def search_by_email():
    # Ищет контакты по части email (регистр не важен).
    # Например, "gmail" найдёт всех, у кого есть gmail в адресе.

    query = input("Введите часть email: ").strip()

    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id FROM contacts WHERE LOWER(email) LIKE %s",
                (f"%{query.lower()}%",),  # оборачиваем в % с обеих сторон — ищем вхождение
            )
            ids = [r["id"] for r in cur.fetchall()]

        results = _fetch_contacts_with_phones(conn, ids)

    _print_contacts(results)


def sort_and_list():
    # Выводит все контакты, отсортированные по выбранному полю.

    print("\nСортировка:  1) Имя  2) День рождения  3) Дата добавления")
    choice = input("Выбор [1]: ").strip() or "1"

    # Сопоставляем выбор пользователя с реальными полями в SQL
    order_map = {
        "1": "c.first_name, c.last_name",
        "2": "c.birthday NULLS LAST",  # контакты без дня рождения идут в конец
        "3": "c.created_at"
    }

    order = order_map.get(choice, "c.first_name, c.last_name")  # неверный ввод — по умолчанию по имени

    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT id FROM contacts c ORDER BY {order}")
            ids = [r["id"] for r in cur.fetchall()]

        results = _fetch_contacts_with_phones(conn, ids)

    _print_contacts(results)


def paginated_browse():
    # Постраничный просмотр контактов — по 5 штук на странице.
    # Позволяет листать вперёд (N), назад (P) или выйти (Q).
    # Используем хранимую функцию get_contacts_paginated из базы.

    page_size = 5  # количество контактов на одной странице
    page = 0       # начинаем с первой страницы (нумерация с 0 внутри кода)

    # Узнаём общее количество контактов, чтобы рассчитать число страниц
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM contacts")
            total = cur.fetchone()[0]

    total_pages = max(1, (total + page_size - 1) // page_size)  # округление вверх, минимум 1 страница

    print(f"\nВсего контактов: {total} | страниц: {total_pages}")

    while True:
        offset = page * page_size  # смещение для SQL — сколько записей пропустить

        with _conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM get_contacts_paginated(%s, %s)",
                    (page_size, offset),
                )
                rows = cur.fetchall()

        print(f"\n--- Страница {page + 1} из {total_pages} ---")  # показываем нумерацию с 1 для пользователя

        if rows:
            ids = [r["id"] for r in rows]
            results = _fetch_contacts_with_phones(conn, ids)
            _print_contacts(results)
        else:
            print("Пустая страница")

        cmd = input("[N] дальше [P] назад [Q] выход: ").strip().lower()

        if cmd == "n":
            if page + 1 < total_pages:
                page += 1
            else:
                print("Уже последняя страница")
        elif cmd == "p":
            if page > 0:
                page -= 1
            else:
                print("Уже первая страница")
        elif cmd == "q":
            break  # выходим из цикла просмотра


# Экспорт и импорт данных


def export_to_json(filepath="contacts_export.json"):
    # Выгружает все контакты с телефонами в JSON-файл.
    # Дата рождения сохраняется как строка "YYYY-MM-DD", а не объект Python —
    # иначе json.dump не сможет её сериализовать.

    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id FROM contacts ORDER BY first_name, last_name")
            ids = [r["id"] for r in cur.fetchall()]

        contacts = _fetch_contacts_with_phones(conn, ids)

    # Конвертируем объекты date в строки перед сохранением
    for c in contacts:
        if isinstance(c.get("birthday"), date):
            c["birthday"] = c["birthday"].isoformat()

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)  # ensure_ascii=False — чтобы кириллица не превращалась в \uXXXX

    print(f"Экспортировано {len(contacts)} контактов в {filepath}")


def _upsert_contact_from_dict(conn, data, on_duplicate="ask"):
    # Добавляет контакт в базу или обновляет его, если такой уже есть.
    # Дубликат определяется по совпадению first_name + last_name.
    # Поведение при дубликате задаётся параметром on_duplicate:
    #   "ask"       — спросить пользователя интерактивно
    #   "skip"      — молча пропустить
    #   "overwrite" — удалить старый контакт и записать новый

    first = (data.get("first_name") or "").strip()
    last = (data.get("last_name") or "").strip() or None  # None вместо пустой строки — важно для сравнения в SQL

    if not first:
        print("Пропущена запись без имени")
        return  # контакт без имени бессмысленен — пропускаем

    # Проверяем, есть ли уже контакт с таким именем
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            "SELECT id FROM contacts WHERE first_name = %s AND "
            "(last_name = %s OR (last_name IS NULL AND %s IS NULL))",
            (first, last, last),  # last передаётся дважды из-за особенности сравнения NULL в PostgreSQL
        )
        existing = cur.fetchone()

    if existing:
        action = on_duplicate

        if action == "ask":
            # Спрашиваем прямо в терминале — всё, что не "o", считаем пропуском
            print(f"  Дубликат: {first} {last or ''}. [S] пропустить / [O] заменить: ", end="")
            action = "skip" if input().strip().lower() != "o" else "overwrite"

        if action == "skip":
            print("     -> пропущено")
            return

        # При перезаписи просто удаляем старый контакт — каскадное удаление уберёт и телефоны
        with conn.cursor() as cur:
            cur.execute("DELETE FROM contacts WHERE id = %s", (existing["id"],))

    # Если у контакта указана группа — находим или создаём её
    group_id = None
    group_name = (data.get("group_name") or data.get("group") or "").strip()  # поддерживаем оба варианта ключа

    if group_name:
        with conn.cursor() as cur:
            # ON CONFLICT DO NOTHING — не падаем если группа уже есть
            cur.execute(
                "INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                (group_name,),
            )
            cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
            row = cur.fetchone()
            if row:
                group_id = row[0]

    birthday = _parse_date(data.get("birthday"))
    email = (data.get("email") or "").strip() or None  # пустую строку превращаем в NULL

    # Вставляем основную запись контакта
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
            """,
            (first, last, email, birthday, group_id),
        )
        contact_id = cur.fetchone()[0]  # получаем id только что вставленной записи

    # Телефоны могут прийти двумя способами: список "phones" или одно поле "phone"
    phones = data.get("phones", [])

    if not phones and data.get("phone"):
        # Поддерживаем простой CSV-формат, где телефон — одно поле, а не список
        phones = [{"phone": data["phone"], "type": data.get("phone_type", "mobile")}]

    with conn.cursor() as cur:
        for p in phones:
            ph_type = (p.get("type") or "mobile").lower()
            if ph_type not in ("home", "work", "mobile"):
                ph_type = "mobile"  # неизвестный тип заменяем на "mobile" как самый универсальный

            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                (contact_id, p["phone"], ph_type),
            )

    conn.commit()  # фиксируем контакт и все его телефоны одной транзакцией
    print(f"  Сохранено: {first} {last or ''}")


def import_from_json(filepath=None):
    # Загружает контакты из JSON-файла (обычно созданного через export_to_json).
    # Если путь не передан — спрашивает у пользователя. Умеет обрабатывать дубликаты.

    if filepath is None:
        filepath = input("Файл JSON [contacts_export.json]: ").strip() or "contacts_export.json"

    if not os.path.exists(filepath):
        print("Файл не найден")
        return

    with open(filepath, encoding="utf-8") as f:
        records = json.load(f)

    print(f"Найдено {len(records)} записей")

    mode = input("Дубликаты: [A] спрашивать [S] пропуск [O] заменить: ").strip().lower()
    on_dup = {"s": "skip", "o": "overwrite"}.get(mode, "ask")  # всё остальное — "ask"

    with _conn() as conn:
        for rec in records:
            _upsert_contact_from_dict(conn, rec, on_duplicate=on_dup)

    print("Импорт завершён")


def import_from_csv(filepath=None):
    # Загружает контакты из CSV-файла. Ожидает заголовки колонок в первой строке.
    # Поддерживаемые колонки: first_name, last_name, email, birthday, phone, phone_type, group.

    if filepath is None:
        filepath = input("Файл CSV [contacts.csv]: ").strip() or "contacts.csv"

    if not os.path.exists(filepath):
        print("Файл не найден")
        return

    mode = input("Дубликаты: [A] [S] [O]: ").strip().lower()
    on_dup = {"s": "skip", "o": "overwrite"}.get(mode, "ask")

    imported = 0

    with _conn() as conn, open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)  # читаем CSV как словари, используя первую строку как ключи

        for row in reader:
            _upsert_contact_from_dict(conn, row, on_duplicate=on_dup)
            imported += 1

    print(f"CSV обработан: {imported} строк")


# Вызовы хранимых процедур из базы данных


def call_add_phone():
    # Добавляет телефон к существующему контакту через хранимую процедуру add_phone.
    # Процедура сама находит контакт по имени — не нужно знать его ID.

    name = input("Имя контакта: ")
    phone = input("Телефон: ")
    ptype = input("Тип (home/work/mobile) [mobile]: ").strip() or "mobile"

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()

    print("Телефон добавлен")


def call_move_to_group():
    # Перемещает контакт в другую группу через хранимую процедуру move_to_group.
    # Если группы не существует — процедура должна её создать (логика внутри SQL).

    name = input("Имя контакта: ")
    group = input("Новая группа: ")

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()

    print("Контакт перемещён")


def call_search_contacts():
    # Полнотекстовый поиск по всем полям контакта через функцию search_contacts.
    # Удобно, когда не знаешь точно — имя это, email или номер телефона.

    query = input("Поиск: ")

    with _conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            rows = cur.fetchall()

        ids = [r["id"] for r in rows]
        results = _fetch_contacts_with_phones(conn, ids)

    _print_contacts(results)


# Главное меню и точка входа


# Текст меню — рисуется перед каждым шагом, чтобы пользователь не забыл варианты
MENU = """
╔════════════════════════════════════════════╗
║               PHONEBOOK APP                ║
╠════════════════════════════════════════════╣
║  0  Применить структуру БД                 ║
╠════════════════════════════════════════════╣
║  1  Фильтр по группе                       ║
║  2  Поиск по email                         ║
║  3  Список контактов                       ║
║  4  Просмотр страниц                       ║
╠════════════════════════════════════════════╣
║  5  Экспорт JSON                           ║
║  6  Импорт JSON                            ║
║  7  Импорт CSV                             ║
╠════════════════════════════════════════════╣
║  8  Добавить телефон                       ║
║  9  Переместить в группу                   ║
║  10 Поиск по всем полям                    ║
╠════════════════════════════════════════════╣
║  Q  Выход                                  ║
╚════════════════════════════════════════════╝
"""

# Словарь: пункт меню -> функция. Позволяет добавлять новые пункты без изменения main()
HANDLERS = {
    "0": init_schema,
    "1": filter_by_group,
    "2": search_by_email,
    "3": sort_and_list,
    "4": paginated_browse,
    "5": export_to_json,
    "6": import_from_json,
    "7": import_from_csv,
    "8": call_add_phone,
    "9": call_move_to_group,
    "10": call_search_contacts,
}


def main():
    # Основной цикл программы: показываем меню, читаем ввод, вызываем нужную функцию.
    # Ошибки базы данных перехватываем здесь, чтобы не вылетать из программы при проблемах.
    # Ctrl+C тоже обрабатываем — показываем сообщение вместо некрасивого стектрейса.

    while True:
        print(MENU)
        choice = input("Выберите пункт: ").strip().lower()

        if choice == "q":
            print("Выход из программы")
            break

        handler = HANDLERS.get(choice)

        if handler:
            try:
                handler()
            except psycopg2.Error as e:
                # Что-то пошло не так на стороне базы — показываем понятное сообщение
                print(f"Ошибка базы данных: {e.pgerror or e}")
            except KeyboardInterrupt:
                # Пользователь нажал Ctrl+C — выходим из текущей операции, но не из программы
                print("\nПрервано пользователем")
        else:
            print("Неверный выбор")


if __name__ == "__main__":
    main()