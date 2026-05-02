-- Таблица групп контактов (например: семья, работа и т.д.)
-- Используется для удобной классификации людей в телефонной книге
CREATE TABLE IF NOT EXISTS groups (
    id   SERIAL PRIMARY KEY,         -- уникальный ID группы (создаётся автоматически)
    name VARCHAR(50) UNIQUE NOT NULL -- название группы (должно быть уникальным)
);

-- Добавляем базовые группы, чтобы система не была пустой при первом запуске
-- ON CONFLICT означает: если такая группа уже есть — ничего не делаем, чтобы не было ошибок
INSERT INTO groups (name) VALUES
    ('Family'), ('Work'), ('Friend'), ('Other')
ON CONFLICT (name) DO NOTHING;

-- Основная таблица контактов (люди, которых мы сохраняем)
CREATE TABLE IF NOT EXISTS contacts (
    id         SERIAL PRIMARY KEY,        -- уникальный ID контакта
    first_name VARCHAR(50)  NOT NULL,     -- имя (обязательное поле)
    last_name  VARCHAR(50),               -- фамилия (необязательное поле)
    email      VARCHAR(100),              -- email адрес
    birthday   DATE,                      -- дата рождения
    group_id   INTEGER REFERENCES groups(id), -- связь с таблицей групп (кому принадлежит контакт)
    created_at TIMESTAMP DEFAULT NOW()    -- когда контакт был добавлен в систему
);

-- Этот блок нужен для безопасного обновления базы данных
-- Он проверяет, есть ли уже нужные колонки, и добавляет их только если их нет
-- Это важно, чтобы не потерять старые данные при обновлении программы
DO $$
BEGIN
    -- проверяем наличие колонки email
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'contacts' AND column_name = 'email'
    ) THEN
        -- если нет email, добавляем его
        ALTER TABLE contacts ADD COLUMN email VARCHAR(100);
    END IF;

    -- проверяем наличие даты рождения
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'contacts' AND column_name = 'birthday'
    ) THEN
        -- добавляем колонку birthday, если её нет
        ALTER TABLE contacts ADD COLUMN birthday DATE;
    END IF;

    -- проверяем наличие связи с группами
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'contacts' AND column_name = 'group_id'
    ) THEN
        -- добавляем group_id и связываем с таблицей groups
        ALTER TABLE contacts ADD COLUMN group_id INTEGER REFERENCES groups(id);
    END IF;
END
$$;

-- Таблица телефонов (один контакт может иметь несколько номеров)
CREATE TABLE IF NOT EXISTS phones (
    id         SERIAL PRIMARY KEY,              -- уникальный ID телефона
    contact_id INTEGER NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    -- связь с контактом; если контакт удаляется, все его номера тоже удаляются

    phone      VARCHAR(20) NOT NULL,            -- сам номер телефона
    type       VARCHAR(10) CHECK (type IN ('home', 'work', 'mobile'))
    -- тип номера: домашний, рабочий или мобильный (другие значения запрещены)
);