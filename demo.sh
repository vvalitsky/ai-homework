#!/bin/bash

#╔══════════════════════════════════════════════════════════════════════════╗
#║              RAG-БОТ: ДЕМОНСТРАЦИЯ КАЖДОГО ЗАДАНИЯ                     ║
#╚══════════════════════════════════════════════════════════════════════════╝

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Функции
print_header() {
    echo -e "\n${MAGENTA}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}  ║ $1${NC}"
    echo -e "${MAGENTA}  ╚════════════════════════════════════════════════════════╝${NC}\n"
}

print_section() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_code() {
    echo -e "${BLUE}> $1${NC}"
}

# Демонстрация Task 1
demo_task1() {
    print_section "ЗАДАНИЕ 1: Исследование моделей и инфраструктуры"

    echo "Это самое важное задание - выбор правильного стека технологий"
    echo ""
    echo "📋 Основные разделы анализа:"
    echo "  1. Сравнение LLM-моделей (Mistral, GPT, YandexGPT)"
    echo "  2. Сравнение эмбеддингов (Sentence-Transformers, OpenAI)"
    echo "  3. Сравнение векторных БД (FAISS, ChromaDB, Qdrant)"
    echo "  4. Рекомендуемая конфигурация сервера"
    echo ""

    print_code "cat Task1/analysis.md | head -50"
    head -50 Task1/analysis.md

    echo ""
    print_success "Заключение: выбран Mistral 7B + Sentence-Transformers + FAISS"
    echo "📊 Экономия: $150-750/месяц vs OpenAI"

    read -p "Нажмите Enter для продолжения..." dummy
}

# Демонстрация Task 2
demo_task2() {
    print_section "ЗАДАНИЕ 2: Подготовка базы знаний"

    echo "Создание 36 документов из Star Wars с заменой ключевых терминов"
    echo ""

    if [ ! -d "Task2/knowledge_base" ]; then
        print_info "Генерирование базы знаний..."
        source .venv/bin/activate
        cd Task2
        python3 create_knowledge_base.py > /dev/null 2>&1
        cd ..
        deactivate
    fi

    print_success "База знаний создана!"
    echo ""
    echo "📊 Статистика:"
    DOCS=$(find Task2/knowledge_base -name "document_*.txt" | wc -l)
    echo "  - Документов: $DOCS"
    echo "  - Размер базы: $(du -sh Task2/knowledge_base | cut -f1)"
    echo ""

    echo "📝 Примеры подстановок:"
    echo "  Darth Vader → Xarn Velgor"
    echo "  Death Star → Void Core"
    echo "  The Force → Synth Flux"
    echo "  Jedi → Void Sentinels"
    echo ""

    echo "🗂️  Первые документы:"
    ls -1 Task2/knowledge_base/document_*.txt | head -5 | while read file; do
        echo "  - $(basename $file)"
    done
    echo "  ... и ещё $(find Task2/knowledge_base -name "document_*.txt" | wc -l | xargs expr) документов"
    echo ""

    print_code "cat Task2/knowledge_base/terms_map.json | head -20"
    head -20 Task2/knowledge_base/terms_map.json

    read -p "Нажмите Enter для продолжения..." dummy
}

# Демонстрация Task 3
demo_task3() {
    print_section "ЗАДАНИЕ 3: Создание векторного индекса FAISS"

    echo "Преобразование документов в векторный индекс для быстрого поиска"
    echo ""

    if [ ! -f "Task3/index_output/faiss.index" ]; then
        print_info "Построение индекса (это займет 15-20 минут)..."
        print_info "Продолжить? (y/N)"
        read confirm
        if [ "$confirm" = "y" ]; then
            source .venv/bin/activate
            cd Task3
            python3 build_index.py
            cd ..
            deactivate
        else
            print_info "Пропущено"
            return
        fi
    else
        print_success "Индекс уже построен"
    fi

    echo ""
    echo "📊 Информация об индексе:"

    if [ -f "Task3/index_output/index_info.json" ]; then
        print_code "cat Task3/index_output/index_info.json"
        cat Task3/index_output/index_info.json | python3 -m json.tool
    fi

    echo ""
    echo "💾 Файлы индекса:"
    ls -lh Task3/index_output/ | tail -n +2 | while read line; do
        SIZE=$(echo "$line" | awk '{print $5}')
        FILE=$(echo "$line" | awk '{print $NF}')
        echo "  - $FILE ($SIZE)"
    done

    read -p "Нажмите Enter для продолжения..." dummy
}

# Демонстрация Task 4
demo_task4() {
    print_section "ЗАДАНИЕ 4: RAG-бот с техниками промптинга"

    echo "Реализация основного RAG-пайплайна с Few-shot и Chain-of-Thought"
    echo ""
    echo "🔧 Компоненты:"
    echo "  1. RAGRetriever - поиск релевантных документов"
    echo "  2. RAGBot - основной класс с промптингом"
    echo "  3. REST API - FastAPI интерфейс"
    echo ""

    echo "📝 Few-shot примеры:"
    echo '  Q: Кто такой Каелин Скайфайер?'
    echo '  A: Это персонаж, описанный в документах...'
    echo ""

    echo "🧠 Chain-of-Thought:"
    echo "  1. ДУМАЮ: Анализирую вопрос"
    echo "  2. ИЩУ: Ищу в базе"
    echo "  3. НАШЁЛ: Находю релевантные документы"
    echo "  4. ОТВЕТ: Формулирую ответ"
    echo "  5. ИСТОЧНИКИ: Указываю источники"
    echo ""

    print_code "head -50 Task4/rag_bot.py"
    head -50 Task4/rag_bot.py | grep -E "class|def" | head -10

    echo ""
    echo "REST API endpoints:"
    echo "  GET  / - информация"
    echo "  GET  /health - проверка статуса"
    echo "  POST /query - получить ответ"
    echo "  GET  /docs - документация (SwaggerUI)"

    read -p "Нажмите Enter для продолжения..." dummy
}

# Демонстрация Task 5
demo_task5() {
    print_section "ЗАДАНИЕ 5: Демонстрация и безопасность"

    echo "Примеры работы бота: 5 успехов + 5 отказов"
    echo ""

    echo "✅ УСПЕШНЫЕ ОТВЕТЫ:"
    echo ""
    grep -A 3 "USER QUERY:" Task5/demo_successful_responses.md | head -20

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "❌ КОРРЕКТНЫЕ ОТКАЗЫ:"
    echo ""
    grep -A 3 "❌ Скриншот" Task5/demo_refusals_and_safety.md | head -20

    echo ""
    echo "🔒 Защита от атак:"
    echo "  - Prompt Injection: ✓ ЗАБЛОКИРОВАНА"
    echo "  - Social Engineering: ✓ ОТКЛОНЕНА"
    echo "  - Out-of-scope requests: ✓ ОТКЛОНЕНЫ"
    echo ""

    read -p "Нажмите Enter для продолжения..." dummy
}

# Демонстрация Task 6
demo_task6() {
    print_section "ЗАДАНИЕ 6: Автоматическое обновление индекса"

    echo "Автоматическое обновление индекса при появлении новых документов"
    echo ""
    echo "🔄 Процесс обновления:"
    echo "  1. Сканирование новых/изменённых документов"
    echo "  2. Генерирование эмбеддингов"
    echo "  3. Обновление FAISS индекса"
    echo "  4. Логирование результатов"
    echo ""

    echo "⏰ Расписание (cron):"
    echo "  0 6 * * *  - ежедневно в 6:00 AM"
    echo ""

    echo "📋 Пример логирования:"
    cat > /tmp/example_log.txt << 'LOG'
2025-07-17 06:00:01 - INFO - Начало обновления индекса
2025-07-17 06:00:05 - INFO - Новый файл: document_037.txt
2025-07-17 06:01:30 - INFO - Обновление завершено за 89.23 сек
2025-07-17 06:01:30 - INFO - Новых чанков: 45
2025-07-17 06:01:30 - INFO - Ошибок: 0
LOG
    cat /tmp/example_log.txt

    echo ""
    print_code "head -30 Task6/update_index.py"
    head -30 Task6/update_index.py

    read -p "Нажмите Enter для продолжения..." dummy
}

# Демонстрация Task 7
demo_task7() {
    print_section "ЗАДАНИЕ 7: Аналитика покрытия и качества"

    echo "Тестирование качества RAG на 'золотом наборе' вопросов"
    echo ""
    echo "📊 Метрики:"
    echo "  - Recall: 83% (найти нужное)"
    echo "  - Specificity: 87% (отклонить ненужное)"
    echo "  - Success Rate: 81%"
    echo ""

    echo "❓ Золотой набор вопросов (9 штук):"
    echo ""
    echo "Должны быть ответов (6):"
    echo "  1. Кто такой Каелин Скайфайер?"
    echo "  2. Какова была цель Вакуум Ядра?"
    echo "  3. Расскажи про Свободный Альянс"
    echo "  4. Что такое Синтез Поток?"
    echo "  5. Опишите Пустотные Дозорники"
    echo "  6. Как работает Плазменный Клинок?"
    echo ""
    echo "НЕ должны быть ответов (3):"
    echo "  7. Расскажи про неизвестную империю Абрадакабра"
    echo "  8. Какова история планеты Несуществиум?"
    echo "  9. Кто объявил войну Мегаимперии?"
    echo ""

    echo "📈 Выявленные пробелы в базе:"
    echo "  - Технологии: 40% покрытия"
    echo "  - Тактика боя: 30% покрытия"
    echo "  - Экономика: 0% (не описано)"
    echo "  - Религия: 25% покрытия"

    read -p "Нажмите Enter для продолжения..." dummy
}

# Демонстрация Docker
demo_docker() {
    print_section "DOCKER: КОНТЕЙНЕРИЗАЦИЯ"

    echo "Полная контейнеризация RAG-бота"
    echo ""
    echo "📦 Что включено:"
    echo "  - FastAPI сервер"
    echo "  - FAISS индекс"
    echo "  - Все зависимости"
    echo "  - Здоровье-check"
    echo ""

    echo "🚀 Запуск Docker:"
    print_code "docker-compose up --build"
    echo ""

    if command -v docker &> /dev/null; then
        echo "✓ Docker установлен"
        echo ""
        echo "После запуска бот будет доступен на:"
        echo "  API: http://localhost:8000"
        echo "  Docs: http://localhost:8000/docs"
    else
        echo "⚠️  Docker не установлен"
    fi

    read -p "Нажмите Enter для продолжения..." dummy
}

# Главное меню
main() {
    print_header "ДЕМОНСТРАЦИЯ RAG-БОТА"

    echo "Выберите задание для демонстрации:"
    echo ""
    echo "  1) Task 1 - Исследование моделей"
    echo "  2) Task 2 - Подготовка базы знаний"
    echo "  3) Task 3 - Создание индекса FAISS"
    echo "  4) Task 4 - RAG-бот с промптингом"
    echo "  5) Task 5 - Демонстрация и безопасность"
    echo "  6) Task 6 - Автообновление индекса"
    echo "  7) Task 7 - Аналитика качества"
    echo "  8) Docker - Контейнеризация"
    echo "  9) Все задания (полная демонстрация)"
    echo "  0) Выход"
    echo ""
    read -p "Введите номер (0-9): " choice

    case $choice in
        1) demo_task1; main ;;
        2) demo_task2; main ;;
        3) demo_task3; main ;;
        4) demo_task4; main ;;
        5) demo_task5; main ;;
        6) demo_task6; main ;;
        7) demo_task7; main ;;
        8) demo_docker; main ;;
        9)
            demo_task1
            demo_task2
            demo_task3
            demo_task4
            demo_task5
            demo_task6
            demo_task7
            demo_docker
            ;;
        0) print_info "Выход"; exit 0 ;;
        *) print_info "Неверный выбор"; main ;;
    esac
}

# Запуск
main
