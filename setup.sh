#!/bin/bash
# Полная подготовка машины к экзамену (Linux). Запуск из папки проекта:  bash setup.sh
# Ставит программы, PostgreSQL, создаёт базу, venv с библиотеками, загружает данные.

cd "$(dirname "$0")" || exit 1
DB_PASSWORD="postgres"
if [ "$(id -u)" = "0" ]; then SUDO=""; else SUDO="sudo"; fi

step() { echo; echo "========== $1 =========="; }
ok()   { echo "  [OK] $1"; }
fail() { echo "  [!!] $1"; }

step "1. Системные пакеты"
if command -v apt >/dev/null 2>&1; then
    $SUDO apt update
    $SUDO apt install -y python3 python3-venv python3-pip git postgresql postgresql-contrib \
        libxcb-cursor0 libegl1 libxkbcommon-x11-0 || fail "apt install завершился с ошибкой"
elif command -v dnf >/dev/null 2>&1; then
    $SUDO dnf install -y python3 python3-pip git postgresql-server postgresql-contrib xcb-util-cursor \
        || fail "dnf install завершился с ошибкой"
    $SUDO postgresql-setup --initdb 2>/dev/null || true
elif command -v urpmi >/dev/null 2>&1; then
    $SUDO urpmi --auto python3 python3-pip git postgresql-server || fail "urpmi завершился с ошибкой"
else
    fail "Не найден apt/dnf/urpmi — поставьте Python 3, Git и PostgreSQL вручную"
fi

step "2. Запуск PostgreSQL, пароль и база chudo_obuv"
$SUDO systemctl enable --now postgresql 2>/dev/null || $SUDO service postgresql start
sleep 2
run_psql() { $SUDO -u postgres psql -v ON_ERROR_STOP=1 "$@"; }
if [ -z "$SUDO" ]; then run_psql() { su postgres -c "psql $(printf '%q ' "$@")"; }; fi
run_psql -c "ALTER USER postgres PASSWORD '$DB_PASSWORD';" && ok "пароль postgres = $DB_PASSWORD"
run_psql -tAc "SELECT 1 FROM pg_database WHERE datname='chudo_obuv'" | grep -q 1 \
    || run_psql -c "CREATE DATABASE chudo_obuv;"
ok "база chudo_obuv есть"

# Если вход по паролю через localhost запрещён (ident/peer) — разрешаем md5
if ! PGPASSWORD=$DB_PASSWORD psql -h localhost -U postgres -d chudo_obuv -c "SELECT 1" >/dev/null 2>&1; then
    HBA=$(run_psql -tAc "SHOW hba_file" | tr -d ' ')
    echo "  вход по паролю не работает, правлю $HBA"
    $SUDO sed -i -E '/^host/ s/(ident|peer)$/md5/' "$HBA"
    $SUDO systemctl restart postgresql 2>/dev/null || $SUDO service postgresql restart
    sleep 2
fi
PGPASSWORD=$DB_PASSWORD psql -h localhost -U postgres -d chudo_obuv -c "SELECT 1" >/dev/null 2>&1 \
    && ok "подключение к базе по паролю работает" || fail "не удаётся подключиться к базе — покажите вывод эксперту"

step "3. Виртуальное окружение и библиотеки"
[ -d venv ] || python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt pandas || fail "pip install завершился с ошибкой"
python -c "import PyQt6.QtWidgets" 2>/dev/null || { fail "PyQt6 не работает, ставлю PyQt5"; pip install PyQt5; }
echo "  сохраняю копии библиотек в папку wheels (на случай без интернета)"
pip download -q -r requirements.txt pandas -d wheels || fail "pip download не удался (не критично)"

step "4. Загрузка данных в базу"
python database/import_data.py || fail "импорт не удался"

step "5. Итоговая проверка"
python -c "import psycopg2, openpyxl, pandas, PyInstaller; from app.qt import QT_API; print('  библиотеки OK, интерфейс:', QT_API)"
echo
echo "Готово! Запуск приложения:  bash run.sh"
