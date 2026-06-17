#!/usr/bin/env python3
"""Interactive REPL for RAG Bot"""

import sys
sys.path.insert(0, '/Users/shademang/Projects/new/ai-homework')

try:
    from Task4.rag_bot import RAGBot

    print("╔════════════════════════════════════════════════════════╗")
    print("║        RAG-БОТ: ИНТЕРАКТИВНЫЙ РЕЖИМ                   ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    print("Загрузка индекса...")
    bot = RAGBot(index_dir="../Task3/index_output")
    print("✓ БОТ ГОТОВ!\n")
    print("Введите вопрос (или 'выход' для выхода):\n")

    while True:
        try:
            question = input("Вы: ")

            if question.lower() in ['выход', 'exit', 'quit', 'q']:
                print("\nДо свидания!")
                break

            if not question.strip():
                continue

            print("\n⟳ Обработка запроса...\n")
            result = bot.answer(question, top_k=3)

            print("┌─────────────────────────────────────────┐")
            print("│ НАЙДЕННЫЕ ИСТОЧНИКИ:                    │")
            print("└─────────────────────────────────────────┘")

            if result["context"]:
                for i, doc in enumerate(result["context"], 1):
                    print(f"\n{i}. [{doc['source']}] {doc['title']}")
                    print(f"   {doc['text'][:150]}...")
            else:
                print("Информация не найдена в базе знаний")

            print("\n┌─────────────────────────────────────────┐")
            print("│ СОЗДАННЫЙ ПРОМПТ (первые 300 символов): │")
            print("└─────────────────────────────────────────┘")
            prompt_preview = result["prompt"][:300] + "..." if len(result["prompt"]) > 300 else result["prompt"]
            print(prompt_preview)
            print("\n" + "="*50 + "\n")

        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем")
            break
        except Exception as e:
            print(f"Ошибка: {e}\n")

except Exception as e:
    print(f"✗ Ошибка при загрузке бота: {e}")
    import traceback
    traceback.print_exc()
