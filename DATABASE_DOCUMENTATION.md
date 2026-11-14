# BridgeEscrow V2 — Database Documentation

## 1. Engine & Design Principles

- **Engine Support**: MySQL 8.0+ (Production) and SQLite (Local / Unit Testing).
- **Charset & Collation**: `utf8mb4` with `utf8mb4_unicode_ci`.
- **Financial Precision**: All monetary values are strictly stored as `BigInteger` cents / minor units (e.g., KES 100.50 is stored as integer `10050`). No floating-point types (`FLOAT`, `DOUBLE`) are used for currency calculations.
- **Double-Entry Bookkeeping**: Every balance movement produces corresponding debit and credit records in `ledger_entries` grouped by an optional `batch_reference`.
- **Migrations**: Managed via Flask-Migrate and Alembic (`backend/migrations`).

---

## 2. Core Tables

### `users`
Represents customer, merchant, and admin user accounts.
- `id`: `INTEGER`, PRIMARY KEY, AUTO_INCREMENT.
- `account_number`: `VARCHAR(16)`, UNIQUE, INDEX (e.g. `BE3602351`).
- `card_number`: `VARCHAR(16)`, UNIQUE, INDEX (Virtual payment card).
- `card_cvv`: `VARCHAR(3)`, NOT NULL.
- `full_name`: `VARCHAR(120)`, NOT NULL.
- `email`: `VARCHAR(190)`, UNIQUE, INDEX.
- `national_id`: `VARCHAR(32)`, UNIQUE, NULLABLE, INDEX.
- `phone`: `VARCHAR(20)`, UNIQUE, INDEX.
- `phone_verified`: `BOOLEAN`, DEFAULT FALSE.
- `password_hash`: `VARCHAR(255)`, NOT NULL.
- `pin_hash`: `VARCHAR(128)`, NULLABLE (PBKDF2/scrypt hash).
- `pin_salt`: `VARCHAR(64)`, NULLABLE.
- `pin_attempts`: `INTEGER`, DEFAULT 0.
- `pin_locked_until`: `DATETIME`, NULLABLE.
- `role`: `VARCHAR(16)`, DEFAULT 'customer' ('customer', 'merchant', 'admin').
- `is_active`: `BOOLEAN`, DEFAULT TRUE.
- `email_verified`: `BOOLEAN`, DEFAULT TRUE.
- `created_at`, `updated_at`: `DATETIME`.

### `wallets`
Stores the financial balances for each user account.
- `id`: `INTEGER`, PRIMARY KEY, AUTO_INCREMENT.
- `user_id`: `INTEGER`, FOREIGN KEY (`users.id`), UNIQUE, INDEX.
- `available_cents`: `BIGINT`, NOT NULL, DEFAULT 0.
- `escrow_cents`: `BIGINT`, NOT NULL, DEFAULT 0.
- `currency`: `VARCHAR(3)`, DEFAULT 'KES'.
- `created_at`, `updated_at`: `DATETIME`.

### `ledger_entries`
Immutable double-entry transaction record.
- `id`: `INTEGER`, PRIMARY KEY, AUTO_INCREMENT.
- `wallet_id`: `INTEGER`, FOREIGN KEY (`wallets.id`), INDEX.
- `entry_type`: `VARCHAR(24)`, NOT NULL (`deposit`, `withdrawal`, `transfer`, `hold`, `release`, `fee`).
- `direction`: `VARCHAR(8)`, NOT NULL (`debit`, `credit`).
- `amount_cents`: `BIGINT`, NOT NULL.
- `reference`: `VARCHAR(64)`, NOT NULL.
- `batch_reference`: `VARCHAR(64)`, NULLABLE, INDEX.
- `idempotency_key`: `VARCHAR(80)`, NULLABLE, INDEX.
- `description`: `VARCHAR(255)`.
- `created_at`: `DATETIME`.

### `escrows`
Records both legacy and Hold-Escro protected contracts.
- `id`: `INTEGER`, PRIMARY KEY, AUTO_INCREMENT.
- `reference`: `VARCHAR(32)`, UNIQUE, INDEX (e.g. `ESC95B2D2B8C6`).
- `buyer_id`: `INTEGER`, FOREIGN KEY (`users.id`), INDEX.
- `seller_id`: `INTEGER`, FOREIGN KEY (`users.id`), INDEX.
- `amount_cents`: `BIGINT`, NOT NULL.
- `fee_cents`: `BIGINT`, NOT NULL, DEFAULT 0.
- `title`: `VARCHAR(160)`, NOT NULL.
- `status`: `VARCHAR(24)`, NOT NULL (`draft`, `hold`, `funded`, `submitted`, `released`, `refunded`, `disputed`, `cancelled`).
- `category`: `VARCHAR(32)`, NULLABLE.
- `rules`: `JSON`, NULLABLE.
- `created_at`, `updated_at`: `DATETIME`.

### `notifications`
Account-isolated notifications feed.
- `id`: `INTEGER`, PRIMARY KEY, AUTO_INCREMENT.
- `user_id`: `INTEGER`, FOREIGN KEY (`users.id`), INDEX.
- `escrow_id`: `INTEGER`, FOREIGN KEY (`escrows.id`), NULLABLE.
- `key`: `VARCHAR(80)`, UNIQUE, INDEX (deduplication key).
- `message`: `VARCHAR(255)`, NOT NULL.
- `read_at`: `DATETIME`, NULLABLE.
- `created_at`: `DATETIME`.

### `developer_apps` & `api_keys`
Merchant registration and API credentials.
- `developer_apps`: `id`, `owner_id`, `name`, `website`, `status`.
- `api_keys`: `id`, `app_id`, `key_hash`, `prefix`, `mode` (`sandbox`, `live`), `revoked_at`.

### `webhook_endpoints` & `webhook_deliveries`
Merchant webhook subscriptions and delivery attempts.

---

## 3. Database Maintenance & Backup Commands

### Backup (MySQL)
```bash
mysqldump -u bridge -p --single-transaction --quick --routines --triggers \
  bridgeescrow_v2 > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore (MySQL)
```bash
mysql -u bridge -p bridgeescrow_v2 < backup_file.sql
```
