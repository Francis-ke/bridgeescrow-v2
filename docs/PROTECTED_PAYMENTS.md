# Hold-Escro protected payments

Choose **Buy goods and services** on the home page to open the eight categories:
Delivery, Services, Events, Deposits, Contracts, Freelancing Payment, Booking
Payment, and Other Protected Payments. Choose a registered, active, verified
provider. The client and provider both explicitly accept the saved terms before
the client can secure the total amount from their available wallet balance.

## Freelancing

The client supplies the job description, completion deadline, revision limit,
revision turnaround, release rule, cancellation deadline, refund percentages,
and maximum extension. Optional milestone amounts must equal the total and
have ordered deadlines within the job deadline. Without milestones there is
one deliverable for the full amount. The freelancer submits work, the client
requests revisions or approves it, and only approved milestones pay out.
Milestones must complete in order. The 1% provider fee is allocated cumulatively
so partial approvals cannot overcharge or omit rounding pennies.

Expired work needs a mutually accepted extension before a new submission.
An agreed revision has its own deadline. Deadline expiry never automatically
releases money. A funded freelance cancellation requires the other party's
acceptance, and refunds apply only to remaining funds, not paid milestones.

## Booking

Booking requires future start/end dates and a cancellation deadline on or
before the start. The provider's acceptance confirms the reservation. Accepted
reservations cannot overlap for the same provider; funding rechecks availability.
By default both the client and provider confirm attendance/service after the
booked period ends before settlement. The creator can explicitly choose client
confirmation instead; both parties accept that release rule before funding.

Booking has its own explicit early/late refund percentages. The default late
percentage is zero, not the general 80/20 split, and API creation requires an
explicit late percentage. Client cancellation uses these agreed percentages;
provider cancellation refunds remaining funds in full. Confirmed/completed
service must use disputes instead of cancellation. Agreed booking extensions
shift the reservation and cancellation dates and recheck provider conflicts.

## Disputes and reporting

Either party may dispute secured funds. Submission, approval, cancellation and
extensions stop while disputed. The existing administrator dispute route can
resume the prior workflow, release remaining funds, refund them, or explicitly
split them, recording a resolution reason and audit event. Already approved
milestones remain paid. Administrators can review descriptions, work submissions,
revision history, terms and audit events in their portal. The review is read-only.

Categories and workflow states appear in escrow history, wallet statements,
merchant sales reports, personal analytics and administrator analytics. Reports
include actual released, refunded and earned-fee amounts, including partial work.

## Accounting and authorization

New protected workflows reuse users, wallets, escrows, ledger entries,
notifications, authentication and disputes. Every new funding/settlement writes
balanced debit/credit batches. `account_bucket` distinguishes available from
held funds. Fees credit a non-login platform account. Legacy ledger rows retain
their original representation. Row locks serialize state transitions and wallet
changes; SQLite uses immediate write transactions. Legacy release, refund,
funding, cancellation and receipt-hold paths cannot bypass protected workflows.

Every action validates its actor and persisted state. Events are recorded and
the counterparty is notified. A hold extension is not an automatic payout.

## API and setup

Run `flask --app wsgi db upgrade` in `backend` to apply migration 18. The
SQLAlchemy models and migration support MySQL; the local project currently
uses the SQLite database configured in `.env`.

- `GET /api/protected/categories` and `/api/protected/providers`
- `POST /api/protected` and `GET /api/protected/<escrow_id>`
- `POST /api/protected/<escrow_id>/<action>`: accept, fund, submit, revise,
  approve, confirm, request-extension, decide-extension, cancel, decide-cancel,
  dispute. Decision payloads use `decision: accept` or `decision: decline`.
- `GET /api/admin/protected/<escrow_id>`: administrator evidence review
- `POST /api/admin/disputes/<dispute_id>/resolve`: outcome is resume, release,
  refund or split; include resolution and, for split, refund_percent.

Run backend tests with `.venv/bin/python -m pytest tests -q`. To use MySQL,
create an isolated test database and set `TEST_DATABASE_URL`; never point the
suite at production because test fixtures create/drop tables. React tests use
`npm test` in `frontend`; `npm run build` validates the complete app. The backend
suite also enforces fewer than 80 lines per handwritten source file.

## Delivery shortcut

Delivery uses duration/amount followed by a receiving-card form. The amount is
carried over unchanged. `POST /api/protected/delivery` accepts `recipient_card`,
`account_holder`, `duration_hours` (1–2160) and `amount`. The authenticated client
selects the provider by its registered virtual card; the server checks the card
and account-holder name. CVV and expiry are not needed for the receiving account.
The earlier provider-ID/password API remains supported for compatibility.
Creation does not debit the wallet; both parties still accept the saved terms
before funding.
