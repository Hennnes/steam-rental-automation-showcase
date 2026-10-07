# Architecture

Production-система логически разделена на несколько слоёв:

```text
FunPay/Cardinal order events
          |
          v
 order validation / lot mapping
          |
          v
 thread-safe rental allocation
          |
     +----+----+
     |         |
     v         v
 account     rental
  pool       state
     |         |
     +----+----+
          |
          v
 expiration scheduler
          |
          v
 credential rotation / return to pool
```

## Concurrency

Критическая операция — выбор свободного аккаунта и фиксация аренды. Если два
заказа приходят одновременно, обычная схема `find free -> mark busy` может
выдать один аккаунт дважды.

В production-контуре критические участки защищены `threading.RLock`, а
обработка заказов ограничена небольшим `ThreadPoolExecutor`.

Showcase воспроизводит именно этот принцип: выбор аккаунта и изменение его
состояния выполняются атомарно под одной блокировкой.

## State

Аккаунт в showcase имеет два основных состояния:

```text
available -> rented -> available
```

Аренда содержит собственный идентификатор, account_id, order_id и срок
окончания. Истёкшие аренды освобождаются планировщиком.

## Production-only integrations

В публичную версию намеренно не включены:

- Steam authentication / Steam Guard;
- смена реальных паролей;
- FunPay/Cardinal callbacks;
- Telegram admin UI;
- реальные JSON/Excel/Google Sheets данные;
- backup archives с account secrets;
- buyer/order history.
