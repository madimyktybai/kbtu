-- Процедура добавления телефона к контакту
-- Мы передаём имя контакта, номер телефона и тип номера (по умолчанию mobile)
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR DEFAULT 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER; -- сюда будем сохранять найденный ID контакта
BEGIN
    -- Ищем контакт в базе по имени
    -- Поддерживается два варианта:
    -- 1) полное имя (имя + фамилия)
    -- 2) только имя
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE LOWER(first_name || COALESCE(' ' || last_name, '')) = LOWER(TRIM(p_contact_name))
       OR LOWER(first_name) = LOWER(TRIM(p_contact_name))
    LIMIT 1;

    -- если контакт не найден — останавливаем выполнение с ошибкой
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- проверяем корректность типа телефона
    -- разрешены только: home, work, mobile
    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type "%". Must be home, work, or mobile.', p_type;
    END IF;

    -- добавляем телефон в таблицу phones и привязываем к контакту
    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);

    -- выводим сообщение в консоль, что всё успешно добавилось
    RAISE NOTICE 'Phone % (%) added to contact "%".', p_phone, p_type, p_contact_name;
END;
$$;


-- Процедура перемещения контакта в группу
-- Если группы нет — она создаётся автоматически
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INTEGER; -- ID контакта
    v_group_id   INTEGER; -- ID группы
BEGIN
    -- ищем контакт по имени (так же как в предыдущей процедуре)
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE LOWER(first_name || COALESCE(' ' || last_name, '')) = LOWER(TRIM(p_contact_name))
       OR LOWER(first_name) = LOWER(TRIM(p_contact_name))
    LIMIT 1;

    -- если контакт не найден — ошибка
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found.', p_contact_name;
    END IF;

    -- создаём группу, если её ещё нет
    INSERT INTO groups (name)
    VALUES (p_group_name)
    ON CONFLICT (name) DO NOTHING;

    -- получаем id группы (она точно существует после insert)
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

    -- обновляем контакт, привязывая его к новой группе
    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;

    -- сообщение об успешном выполнении
    RAISE NOTICE 'Contact "%" moved to group "%".', p_contact_name, p_group_name;
END;
$$;


-- Функция поиска контактов по любому тексту
-- Ищет по имени, фамилии, email и телефону
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_name VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    -- делаем шаблон поиска в стиле LIKE '%text%'
    v_pattern TEXT := '%' || LOWER(TRIM(p_query)) || '%';
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        c.id,
        c.first_name,
        c.last_name,
        c.email,
        c.birthday,
        g.name AS group_name
    FROM contacts c
    LEFT JOIN groups g  ON g.id  = c.group_id
    LEFT JOIN phones ph ON ph.contact_id = c.id
    WHERE
        -- ищем совпадения по разным полям
        LOWER(c.first_name)                  LIKE v_pattern
        OR LOWER(COALESCE(c.last_name, ''))  LIKE v_pattern
        OR LOWER(COALESCE(c.email, ''))      LIKE v_pattern
        OR LOWER(COALESCE(ph.phone, ''))     LIKE v_pattern
    ORDER BY c.first_name, c.last_name;
END;
$$;


-- Функция постраничного вывода контактов
-- используется когда нужно показывать список частями (например в UI или API)
CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INTEGER, p_offset INTEGER)
RETURNS TABLE (
    id         INTEGER,
    first_name VARCHAR,
    last_name  VARCHAR,
    email      VARCHAR,
    birthday   DATE,
    group_id   INTEGER,
    created_at TIMESTAMP
) 
LANGUAGE plpgsql AS $$
BEGIN
    -- просто берём контакты с сортировкой и ограничением
    -- LIMIT = сколько записей вернуть
    -- OFFSET = с какой позиции начать
    RETURN QUERY
    SELECT *
    FROM contacts
    ORDER BY first_name, last_name
    LIMIT p_limit
    OFFSET p_offset;
END;
$$;