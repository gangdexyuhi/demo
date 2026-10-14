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
# dnf проверяем первым: на MOS/ROSA команда apt — заглушка «используйте dnf»
if command -v dnf >/dev/null 2>&1; then
    $SUDO dnf install -y python3 python3-pip git || fail "dnf install завершился с ошибкой"
elif command -v apt-get >/dev/null 2>&1; then
    $SUDO apt-get update
    $SUDO apt-get install -y python3 python3-venv python3-pip git postgresql postgresql-contrib \
        libxcb-cursor0 libegl1 || fail "apt install завершился с ошибкой"
else
    fail "Не найден dnf/apt — поставьте Python 3, Git и PostgreSQL вручную"
fi

step "2. Запуск PostgreSQL, пароль и база chudo_obuv"
# sudo -u postgres из домашней папки ругается «Отказано в доступе» — работаем из /tmp
run_psql() { (cd /tmp && $SUDO -u postgres psql -v ON_ERROR_STOP=1 "$@"); }
if [ -z "$SUDO" ]; then run_psql() { (cd /tmp && su postgres -c "psql $(printf '%q ' "$@")"); }; fi

server_is_up() { (cd /tmp && $SUDO -u postgres psql -tAc "SELECT 1" >/dev/null 2>&1) || \
                 { [ -z "$SUDO" ] && (cd /tmp && su postgres -c "psql -tAc 'SELECT 1'" >/dev/null 2>&1); }; }

# Служба может называться postgresql, postgresql12, postgresql17 ...
# Берём ту, что совпадает с версией psql (иначе pg_dump откажется работать), иначе самую новую.
PSQL_MAJOR=$(psql --version 2>/dev/null | grep -oE '[0-9]+' | head -1)
UNITS=$(systemctl list-unit-files --no-legend 2>/dev/null | awk '{print $1}' \
        | grep -E '^postgresql(-?[0-9]+)?\.service$' | sort -V -r)
UNIT=$(echo "$UNITS" | grep -E "^postgresql-?${PSQL_MAJOR}\.service$" | head -1)
[ -z "$UNIT" ] && UNIT=$(echo "$UNITS" | head -1)
echo "  служба PostgreSQL: ${UNIT:-не найдена}, версия psql: ${PSQL_MAJOR:-?}"

init_cluster() {
    # 1) штатный способ RedHat/ROSA
    if command -v postgresql-setup >/dev/null 2>&1; then
        $SUDO postgresql-setup --initdb --unit "${UNIT%.service}" 2>/dev/null && return 0
        $SUDO postgresql-setup initdb "${UNIT%.service}" 2>/dev/null && return 0
    fi
    for setup_tool in /usr/bin/postgresql*-setup /usr/pgsql-*/bin/postgresql*-setup; do
        [ -x "$setup_tool" ] && $SUDO "$setup_tool" initdb 2>/dev/null && return 0
    done
    # 2) вручную: каталог данных и initdb той же версии, что и служба
    PGDATA_DIR=$(systemctl show -p Environment "$UNIT" | grep -oE 'PGDATA=[^ ]+' | cut -d= -f2)
    SERVER_BIN=$(systemctl show -p ExecStart "$UNIT" | grep -oE 'path=[^ ;]+' | cut -d= -f2)
    INITDB=$(dirname "$SERVER_BIN")/initdb
    [ -x "$INITDB" ] || INITDB=$(command -v initdb)
    [ -n "$PGDATA_DIR" ] || PGDATA_DIR=/var/lib/pgsql/data
    echo "  initdb: $INITDB -D $PGDATA_DIR"
    $SUDO mkdir -p "$PGDATA_DIR" && $SUDO chown postgres:postgres "$PGDATA_DIR" && $SUDO chmod 700 "$PGDATA_DIR"
    (cd /tmp && $SUDO -u postgres "$INITDB" -D "$PGDATA_DIR" -E UTF8 --no-locale \
        --auth-local=trust --auth-host=md5)
}

wait_server() { for _ in 1 2 3 4 5 6 7 8 9 10; do server_is_up && return 0; sleep 1; done; return 1; }

if ! server_is_up; then
    if [ -n "$UNIT" ]; then
        $SUDO systemctl enable --now "$UNIT" 2>/dev/null || $SUDO service "${UNIT%.service}" start
        if ! wait_server; then
            echo "  служба не стартовала — инициализирую каталог данных"
            init_cluster
            $SUDO systemctl enable --now "$UNIT" 2>/dev/null || $SUDO service "${UNIT%.service}" start
            wait_server
        fi
    else
        $SUDO service postgresql start
        wait_server
    fi
fi
server_is_up && ok "сервер PostgreSQL работает" || fail "сервер PostgreSQL не запустился: systemctl status $UNIT"

run_psql -c "ALTER USER postgres PASSWORD '$DB_PASSWORD';" && ok "пароль postgres = $DB_PASSWORD"
run_psql -tAc "SELECT 1 FROM pg_database WHERE datname='chudo_obuv'" | grep -q 1 \
    || run_psql -c "CREATE DATABASE chudo_obuv;"
ok "база chudo_obuv есть"

# Если вход по паролю через localhost запрещён (ident/peer) — разрешаем md5
if ! PGPASSWORD=$DB_PASSWORD psql -h localhost -U postgres -d chudo_obuv -c "SELECT 1" >/dev/null 2>&1; then
    HBA=$(run_psql -tAc "SHOW hba_file" | tr -d ' ')
    echo "  вход по паролю не работает, правлю $HBA"
    $SUDO sed -i -E '/^host/ s/(ident|peer)$/md5/' "$HBA"
    $SUDO systemctl restart "${UNIT:-postgresql}" 2>/dev/null || $SUDO service postgresql restart
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
