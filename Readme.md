````markdown
# 🏠 My Domos Africa – Escrow Node System

## Overview

The Escrow Node System is a core financial feature of **My Domos Africa**, a multi-sided housing trust platform that connects Tenants, Landlords, and Housing Agents.

It ensures secure rental transactions by holding tenant funds in escrow until predefined conditions (inspection, confirmation, or dispute resolution) are met.

This system prevents fraud, protects tenants, and guarantees landlords receive verified payments.

---

## 🚀 Features

- Create escrow transactions between tenant and landlord
- Hold funds securely in escrow
- Confirm property inspection (trigger event)
- Release funds to landlord
- Refund funds to tenant in case of failure or dispute
- Query escrow status
- Full state machine enforcement
- Idempotent payment release and refund protection
- Authentication required for all endpoints

---

## 🧱 Tech Stack

- Python 3
- Django
- Django REST Framework (DRF)
- SQLite / PostgreSQL (configurable)

---

## 🧠 System Design Summary

### Core Entities

- **Escrow**
  - Represents a rental transaction between tenant and landlord
  - Tracks amount, status, and participants

- **EscrowEvent**
  - Logs lifecycle events (created, funded, triggered)
  - Provides audit trail for escrow actions

---

## 🔄 Escrow Lifecycle

```text
CREATED → HELD → TRIGGERED → RELEASED
                     ↘ REFUNDED
                     ↘ DISPUTED
````

---

## 📌 Business Rules

* Only escrow participants can interact with an escrow
* Tenant can fund and request refunds
* Landlord can trigger inspection and release funds
* Funds cannot be released or refunded after final settlement
* State transitions are strictly enforced

---

## 🔐 Security Features

* Token-based authentication required
* Ownership-based authorization (tenant/landlord validation)
* Prevents unauthorized access to escrow transactions
* Idempotency keys prevent duplicate payments and refunds
* Atomic database transactions ensure consistency

---

## 📡 API Endpoints

### 1. Create Escrow

```
POST /escrow/create/
```

### 2. Fund Escrow (Tenant)

```
POST /escrow/{escrow_id}/fund/
Headers:
Idempotency-Key: <unique-key>
```

### 3. Trigger Inspection (Landlord/Agent)

```
POST /escrow/{escrow_id}/trigger/
```

### 4. Release Funds (Landlord)

```
POST /escrow/{escrow_id}/release/
Headers:
Idempotency-Key: <unique-key>
```

### 5. Refund Funds (Tenant)

```
POST /escrow/{escrow_id}/refund/
Headers:
Idempotency-Key: <unique-key>
```

### 6. Get Escrow Status

```
GET /escrow/{escrow_id}/status/
```

---

## 🧾 Idempotency Handling

To prevent duplicate financial operations:

* Each sensitive operation (fund, release, refund) requires an `Idempotency-Key`
* Repeated requests with the same key will NOT re-process payments
* Ensures safe retries in case of network failure

---

## ⚙️ State Management

Invalid transitions are blocked.

Example:

* Cannot release before trigger
* Cannot refund after release

---

## 🧪 Example Flow

1. Tenant creates escrow
2. Tenant funds escrow
3. Landlord confirms inspection
4. Funds released OR refunded depending on outcome

---

## 🔒 Authorization Rules

| Action  | Allowed User |
| ------- | ------------ |
| Fund    | Tenant       |
| Trigger | Landlord     |
| Release | Landlord     |
| Refund  | Tenant       |
| Status  | Both parties |

---

## 📦 Installation

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 👨‍💻 Author

Built as part of backend engineering assessment for DomosHQ.

Focus: Secure escrow system design, state machines, and idempotent financial operations.

```

