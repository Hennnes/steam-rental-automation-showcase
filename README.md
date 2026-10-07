# Steam Rental Automation — sanitized showcase

Публичная showcase-версия production-системы автоматизации аренды Steam-аккаунтов.

Это **не рабочий rental-bot и не копия production-кода**. Из репозитория
намеренно исключены реальные аккаунты, пароли, Steam Guard secrets, maFile,
Telegram/FunPay credentials, история заказов и интеграционная логика, которую
можно было бы использовать как готовый коммерческий инструмент.

## Production-проект

Рабочая версия системы:

- управляла пулом примерно из **176 Steam-аккаунтов**;
- за 3 месяца обработала около **10 000 реальных аренд**;
- пиковая нагрузка достигала примерно **260 заказов в сутки**;
- автоматически резервировала и выдавала свободный аккаунт;
- отслеживала срок аренды и освобождала аккаунт после завершения;
- поддерживала Steam Guard и ротацию пароля в production-контуре;
- синхронизировала состояние с локальным учётом / Google Sheets;
- защищала параллельную выдачу от race condition и double booking;
- использовала ограниченный worker pool вместо отдельного потока на каждый заказ;
- применялась не только мной: решение использовали ещё **5 пользователей**.

## Что показано в этом репозитории

Showcase демонстрирует безопасную часть архитектуры:

- thread-safe пул аккаунтов;
- атомарное резервирование аккаунта;
- создание аренды;
- защита от двойной выдачи одного аккаунта;
- возврат истёкших аренд в пул;
- отделение domain logic от внешних интеграций;
- unit tests для конкурентного сценария.

## Stack production-версии

`Python` · `ThreadPoolExecutor` · `threading.RLock` · `Telegram Bot API` ·
FunPay/Cardinal · Steam Guard · Google Sheets API · JSON/Excel tracking

## Быстрый запуск

Требуется Python 3.11+.

```bash
python -m unittest -v test_rental_core.py
python demo.py
```

## Файлы

```text
README.md
architecture.md
rental_core.py
demo.py
tests/
  test_rental_core.py
```

## Почему production-код закрыт

Исходная система содержит чувствительные данные и интеграционную логику:
Steam/e-mail credentials, Steam Guard secrets, browser/API sessions, account
inventory, реальные заказы и автоматизацию выдачи.

Публичная версия поэтому показывает архитектуру и проверяемую concurrency-
логику, но не раскрывает production credentials и готовый коммерческий bot.
