# Задание 2. Подготовка базы знаний

## Описание

Создана собственная база знаний из 36 документов, полученных из Star Wars вселенной с полной заменой ключевых терминов на вымышленные названия.

## Исходный материал

- **Источник:** Star Wars фандом
- **Тип:** Фантастическая вселенная с известными персонажами, планетами и технологиями
- **Выбран этот источник для того, чтобы:** позволить нам создать условия, максимально приближённые к реальной корпоративной базе знаний. LLM не будет знать отредактированный контент.

## Структура подстановок

Все ключевые члены вселенной заменены на вымышленные названия:

### Персонажи (Characters)
- Darth Vader → Xarn Velgor
- Luke Skywalker → Kael Starfire
- Leia Organa → Sera Lightborn
- Han Solo → Drix Void
- Obi-Wan Kenobi → Thran Wise
- Yoda → Zoras
- Anakin Skywalker → Kaelin Skyfire
- Padmé Amidala → Lyria Nightshade
- И 8 других персонажей

### Локации (Locations)
- Death Star → Void Core
- Tatooine → Skarron Prime
- Coruscant → Nexus Crown
- Naboo → Lumina Realm
- Alderaan → Crystal Haven
- Hoth → The Frozen Abyss
- Endor → The Green Sanctuary
- Cloud City → Sky Citadel
- И 4 других локации

### Технология (Technology)
- The Force → Synth Flux
- Lightsaber → Plasma Blade
- Blaster → Void Rifle
- Hyperspace → Phase Drift
- Warp Drive → Quantum Leap
- Millennium Falcon → The Silver Phantom
- TIE Fighter → Void Viper
- X-Wing → Star Arrow
- И 4 других технологии

### Термины (Terms)
- Rebellion → The Free Alliance
- Empire → The Void Order
- Republic → The United Dominion
- Clone → Synthetic Being
- Padawan → Apprentice of the Way
- Master → Sage Conductor
- Dark Side → The Void Path
- Light Side → The Bright Way
- Chosen One → The Balance Bearer

**Всего заменено уникальных терминов: 49**

## Содержимое папки `knowledge_base/`

### Файлы:
- `document_001.txt` - `document_036.txt` - 36 текстовых документов
- `terms_map.json` - словарь всех подстановок (исходное → вымышленное)

### Размер индекса:
- **Файлы документов:** ~280 KB
- **Словарь замен:** ~2 KB
- **Общий объем:** ~282 KB

## Примеры заменённых документов

### Документ 1: The Birth of the Void Darklings
Оригинал:
```
The fall of Anakin Skywalker is one of the most tragic tales in galactic history.
A gifted Jedi with unprecedented command of the Force, Anakin believed he could save lives
through power. When the Jedi Council refused him the rank of Master, he fell into despair.
```

После замены:
```
The fall of Kaelin Skyfire is one of the most tragic tales in galactic history.
A gifted Void Sentinels with unprecedented command of Synth Flux, Kaelin Skyfire believed he could save lives
through power. When the Void Sentinels Council refused him the rank of Sage Conductor, he fell into despair.
```

## Почему этот подход работает?

1. **Модель не узнаёт контент по памяти** – переименованные термины не в её обучающих данных
2. **Логика и структура сохранены** – статьи остаются читаемыми и структурированно осмысленными
3. **Проверка работы RAG** – если бот отвечает правильно, он явно использует вашу базу знаний, а не память
4. **Реалистичный сценарий** – имитирует корпоративную базу знаний с внутренней терминологией

## Как использовать

1. Установите Python зависимости (если не установлены)
2. Запустите скрипт:
   ```bash
   python3 create_knowledge_base.py
   ```
3. Используйте папку `knowledge_base/` в следующих заданиях:
   - Task 3: Создание векторного индекса
   - Task 4: RAG-бот
   - Task 5: Демонстрация и безопасность

## Проверка

Используйте `terms_map.json` чтобы:
- Проверить правильность замен при анализе ответов бота
- Обратить замены при нужде декодировать ответы
- Убедиться, что все ключевые термины заменены

## Дополнительная информация

- **Документация:** каждый документ содержит логически связанный контент
- **Тестирование:** база готова к индексации и поиску
- **Масштабируемость:** легко добавить больше документов следуя той же структуре
- **Воспроизводимость:** скрипт полностью автоматизирован

