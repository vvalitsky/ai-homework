#!/bin/bash

# Task 7: Knowledge Base Coverage Analytics & Quality Assessment
# Tests RAG system with golden questions, logs results, analyzes gaps

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Functions
print_header() {
    echo -e "\n${MAGENTA}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║ $1${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════╝${NC}\n"
}

print_section() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_section "Проверка предусловий"

    if [ ! -d "../.venv" ]; then
        print_error "Виртуальное окружение не создано"
        exit 1
    fi

    if [ ! -f "../Task3/index_output/faiss.index" ]; then
        print_error "FAISS индекс не построен"
        exit 1
    fi

    if [ ! -f "evaluate_rag.py" ]; then
        print_error "Скрипт evaluate_rag.py не найден"
        exit 1
    fi

    if [ ! -f "golden_questions.txt" ]; then
        print_error "Файл golden_questions.txt не создан"
        print_info "Создайте файл: touch golden_questions.txt"
        exit 1
    fi

    print_success "Все предусловия выполнены"
}

# Run evaluation
run_evaluation() {
    print_header "ОЦЕНКА КАЧЕСТВА RAG-СИСТЕМЫ"

    source ../.venv/bin/activate

    print_info "Запуск скрипта оценки..."
    echo ""

    python3 -u evaluate_rag.py

    deactivate

    print_success "Оценка завершена!"
}

# View logs
view_logs() {
    print_header "ПРОСМОТР ЛОГОВ ТЕСТИРОВАНИЯ"

    if [ ! -f "logs.jsonl" ] && [ ! -f "logs.csv" ]; then
        print_error "Логи не найдены - запустите оценку сначала"
        return
    fi

    if [ -f "logs.jsonl" ]; then
        print_section "Логи (JSONL)"
        wc -l logs.jsonl
        echo ""
        tail -10 logs.jsonl | python3 -m json.tool 2>/dev/null || tail -10 logs.jsonl
    fi

    if [ -f "logs.csv" ]; then
        print_section "Логи (CSV)"
        head -20 logs.csv
    fi
}

# Show statistics
show_statistics() {
    print_header "СТАТИСТИКА ТЕСТИРОВАНИЯ"

    if [ ! -f "logs.jsonl" ] && [ ! -f "logs.csv" ]; then
        print_error "Логи не найдены - запустите оценку сначала"
        return
    fi

    source ../.venv/bin/activate

    python3 << 'PYTHON'
import json
import csv
from pathlib import Path

# Try to load and analyze logs
try:
    if Path("logs.jsonl").exists():
        print("Анализ JSONL логов:\n")

        with open("logs.jsonl") as f:
            logs = [json.loads(line) for line in f]

        total = len(logs)
        successful = sum(1 for log in logs if log.get("success", False))
        with_context = sum(1 for log in logs if log.get("found_chunks", False))

        print(f"  Всего запросов: {total}")
        print(f"  Успешных ответов: {successful} ({successful/total*100:.1f}%)")
        print(f"  С найденными чанками: {with_context} ({with_context/total*100:.1f}%)")
        print(f"  Средняя длина ответа: {sum(log.get('answer_length', 0) for log in logs)/total:.0f} символов")

        print(f"\n  По источникам:")
        sources = {}
        for log in logs:
            for source in log.get("sources", []):
                sources[source] = sources.get(source, 0) + 1

        for source, count in sorted(sources.items(), key=lambda x: -x[1])[:5]:
            print(f"    - {source}: {count} раз")

except Exception as e:
    print(f"Ошибка при анализе логов: {e}")
PYTHON

    deactivate
}

# Show coverage gaps
show_gaps() {
    print_header "ВЫЯВЛЕННЫЕ ПРОБЕЛЫ В БАЗЕ ЗНАНИЙ"

    if [ ! -f "gaps_analysis.json" ]; then
        print_error "Анализ пробелов не найден"
        return
    fi

    python3 << 'PYTHON'
import json

try:
    with open("gaps_analysis.json") as f:
        gaps = json.load(f)

    print("Темы с плохим покрытием:\n")

    if "poorly_covered_topics" in gaps:
        for topic in gaps["poorly_covered_topics"]:
            print(f"  ✗ {topic['name']}")
            print(f"    Успешных ответов: {topic['success_rate']}%")
            print(f"    Примеры вопросов: {', '.join(topic['sample_questions'][:2])}")
            print()

    if "missing_entities" in gaps:
        print("Отсутствующие сущности:\n")
        for entity in gaps["missing_entities"]:
            print(f"  • {entity}")

    print(f"\nОбщая статистика:")
    print(f"  - Пробелов выявлено: {gaps.get('total_gaps', 'N/A')}")
    print(f"  - Рекомендованных улучшений: {gaps.get('recommendations_count', 'N/A')}")

except Exception as e:
    print(f"Ошибка: {e}")
PYTHON
}

# Show golden questions
show_golden_questions() {
    print_header "ЗОЛОТЫЕ ВОПРОСЫ (GOLDEN SET)"

    if [ ! -f "golden_questions.txt" ]; then
        print_error "Файл golden_questions.txt не найден"
        return
    fi

    print_section "Описание набора"
    wc -l golden_questions.txt | awk '{print "  Всего вопросов: " $1}'
    echo ""

    print_section "Первые 10 вопросов"
    head -10 golden_questions.txt | nl
}

# View sequence diagram
show_sequence_diagram() {
    print_header "ДИАГРАММА ПОСЛЕДОВАТЕЛЬНОСТИ (SEQUENCE DIAGRAM)"

    if [ -f "sequence_diagram.txt" ]; then
        cat sequence_diagram.txt
    elif [ -f "sequence_diagram.puml" ]; then
        echo "Диаграмма в формате PlantUML:"
        echo ""
        cat sequence_diagram.puml
    else
        print_info "Диаграмма будет создана после первого запуска оценки"
    fi
}

# Generate report
generate_report() {
    print_header "ГЕНЕРИРОВАНИЕ ОТЧЕТА"

    source ../.venv/bin/activate

    python3 << 'PYTHON'
import json
from pathlib import Path
from datetime import datetime

print("Генерирование отчета о качестве RAG-системы...")
print()

# Collect data
report = {
    "timestamp": datetime.now().isoformat(),
    "sections": []
}

# 1. Overview
if Path("logs.jsonl").exists():
    with open("logs.jsonl") as f:
        logs = [json.loads(line) for line in f]

    total = len(logs)
    successful = sum(1 for log in logs if log.get("success", False))

    report["sections"].append({
        "title": "Обзор тестирования",
        "content": f"Протестировано: {total} вопросов\nУспешных ответов: {successful} ({successful/total*100:.1f}%)"
    })

# 2. Covered topics
if Path("gaps_analysis.json").exists():
    with open("gaps_analysis.json") as f:
        gaps = json.load(f)

    covered = gaps.get("covered_topics_count", 0)
    poorly = gaps.get("poorly_covered_topics_count", 0)

    report["sections"].append({
        "title": "Покрытие базы знаний",
        "content": f"Хорошо покрыто: {covered} тем\nПлохо покрыто: {poorly} тем"
    })

# Save report
with open("quality_report.json", "w") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("✓ Отчет сохранен: quality_report.json")
PYTHON

    deactivate
}

# Main menu
main() {
    print_header "ЗАДАНИЕ 7: Аналитика покрытия и качества базы знаний"

    echo "Выберите действие:"
    echo ""
    echo "  1) Запустить оценку качества"
    echo "  2) Просмотреть логи тестирования"
    echo "  3) Показать статистику"
    echo "  4) Показать найденные пробелы"
    echo "  5) Показать золотые вопросы"
    echo "  6) Показать диаграмму последовательности"
    echo "  7) Генерировать отчет"
    echo "  0) Выход"
    echo ""
    read -p "Введите номер (0-7): " choice

    case $choice in
        1) run_evaluation; main ;;
        2) view_logs; main ;;
        3) show_statistics; main ;;
        4) show_gaps; main ;;
        5) show_golden_questions; main ;;
        6) show_sequence_diagram; main ;;
        7) generate_report; main ;;
        0) print_info "Выход"; exit 0 ;;
        *) print_info "Неверный выбор"; main ;;
    esac
}

# Run main
check_prerequisites
main
