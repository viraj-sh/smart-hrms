# Smart HR System — Database Design

**Project:** Qveto Smart HR & Employee Management System  
**Database:** PostgreSQL  
**ORM:** Django ORM  
**Status:** Week 1 schema design

## 1. Scope

This document defines the proposed relational schema for user accounts, employee profiles, departments, attendance, leave management, payroll records, notifications, and audit history. Payroll totals are stored records; payroll calculations are outside the scope of this schema.

## 2. Conventions

- `PK`: primary key.
- `FK`: foreign key.
- `UK`: unique constraint.
- Unless noted otherwise, Django-managed models should include `created_at` and `updated_at` timestamps where useful.
- Use Django's `settings.AUTH_USER_MODEL` / `CustomUser` for user references.
- Use PostgreSQL constraints and indexes in addition to application validation.
- Suggested Django field names and types are shown below. Actual inherited `AbstractUser` fields are not repeated in full.

## 3. Tables and fields

### 3.1 `accounts_customuser` — CustomUser

Django `AbstractUser` plus the role field.

| Field | Suggested Django type | Constraints / notes |
|---|---|---|
| `id` | `BigAutoField` (or project default) | PK |
| `username`, `password`, `email`, `first_name`, `last_name` | Inherited from `AbstractUser` | Keep Django's built-in authentication behavior |
| `is_staff` | `BooleanField` | Inherited; Django admin access flag, not a substitute for app role checks |
| `is_superuser` | `BooleanField` | Inherited; Django permission bypass flag |
| `last_login`, `date_joined` | Inherited fields | Authentication metadata |
| `role` | `CharField(max_length=20)` | Required; choices `ADMIN`, `HR`, `EMPLOYEE` |
| `created_at` | `DateTimeField` | Optional project-managed timestamp if added |
| `updated_at` | `DateTimeField` | Optional project-managed timestamp if added |

**Note:** The supplied ER diagram shows `created_at` and `updated_at`; Django `AbstractUser` does not provide these two fields by default, so add them explicitly if they are required.

### 3.2 `employees_employee` — Employee

| Field | Suggested Django type | Constraints / notes |
|---|---|---|
| `id` | `BigAutoField` | PK |
| `user` | `OneToOneField(CustomUser)` | FK, unique, required; one profile per user |
| `employee_id` | `CharField(max_length=20)` | UK, required |
| `job_title` | `CharField(max_length=100)` | Required |
| `employment_status` | `CharField(max_length=20)` | Required; e.g. `ACTIVE`, `PROBATION`, `TERMINATED`; define choices |
| `joining_date` | `DateField` | Required |
| `is_verified` | `BooleanField(default=False)` | Required |
| `department` | `ForeignKey(Department, null=True, blank=True)` | Optional; unassigned employees are allowed |
| `profile_photo` | `ImageField(null=True, blank=True)` | Optional; configure media storage |
| `created_at`, `updated_at` | `DateTimeField` | Timestamps |

### 3.3 `employees_department` — Department

| Field | Suggested Django type | Constraints / notes |
|---|---|---|
| `id` | `BigAutoField` | PK |
| `name` | `CharField(max_length=100)` | Required |
| `code` | `CharField(max_length=10)` | UK, required |
| `description` | `TextField(null=True, blank=True)` | Optional |
| `head` | `ForeignKey(CustomUser, null=True, blank=True)` | Optional; organizational reporting only |
| `is_active` | `BooleanField(default=True)` | Required |
| `created_at`, `updated_at` | `DateTimeField` | Timestamps |

Department head assignment does not automatically grant extra permissions. If department-level access is later needed, implement it explicitly in authorization logic.

### 3.4 `leave_management_leavetype` — LeaveType

| Field | Suggested Django type | Constraints / notes |
|---|---|---|
| `id` | `BigAutoField` | PK |
| `name` | `CharField(max_length=50)` | UK recommended |
| `max_days_per_year` | `PositiveIntegerField` | Required; minimum 1 |
| `carry_forward_allowed` | `BooleanField(default=False)` | Required |
| `requires_approval` | `BooleanField(default=True)` | Required |
| `is_paid` | `BooleanField(default=True)` | Required |
| `created_at`, `updated_at` | `DateTimeField` | Timestamps |

The ER diagram does not show a `description` field consistently; add one only if required by the implementation.

### 3.5 `leave_management_leaverequest` — LeaveRequest

| Field | Suggested Django type | Constraints / notes |
|---|---|---|
| `id` | `BigAutoField` | PK |
| `employee` | `ForeignKey(Employee)` | FK, required |
| `leave_type` | `ForeignKey(LeaveType)` | FK, required |
| `start_date`, `end_date` | `DateField` | Required; `end_date >= start_date` |
| `total_days` | `DecimalField(max_digits=5, decimal_places=2)` | Required; inclusive day count per current design |
| `status` | `CharField(max_length=20)` | Required; `PENDING`, `APPROVED`, `REJECTED`; see status gap below |
| `remarks` | `TextField(null=True, blank=True)` | Optional request/decision notes |
| `approved_by` | `ForeignKey(CustomUser, null=True, blank=True)` | FK; HR/Admin decision-maker |
| `approval_date` | `DateTimeField(null=True, blank=True)` | Nullable until decision |
| `balance_deducted` | `DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)` | Nullable; supports balance tracking without blocking submission |
| `created_at`, `updated_at` | `DateTimeField` | Timestamps |

**Business-rule gaps to resolve before implementation:**
- Cancellation is required by the business rules, but the supplied status choices do not include `CANCELLED`. Add it (and any reopening state) if cancellation/reopening will be represented on the request.
- The two-cancellations-per-quarter allowance, yearly balances, HR balance adjustments, and reopening justification need persistence. Consider separate `LeaveBalance` and `LeaveRequestStatusHistory` tables, plus cancellation metadata or a cancellation-event table. These entities are not present in the supplied ER diagram.
- Decisions by HR/Admin require remarks and before/after audit logging.

### 3.6 `attendance_attendance` — Attendance

| Field | Suggested Django type | Constraints / notes |
|---|---|---|
| `id` | `BigAutoField` | PK |
| `employee` | `ForeignKey(Employee)` | FK, required |
| `date` | `DateField` | Required |
| `check_in_time`, `check_out_time` | `TimeField(null=True, blank=True)` | Nullable |
| `attendance_status` | `CharField(max_length=20)` | Required; `PRESENT`, `LATE`, `ABSENT`, `HALF_DAY` |
| `total_hours` | `DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)` | Nullable; policy can assign 8.0 if check-out is missing |
| `late_minutes`, `early_minutes` | `PositiveIntegerField` (or `IntegerField`) | Nullable; define whether negative values are allowed (normally not) |
| `corrected_by` | `ForeignKey(CustomUser, null=True, blank=True)` | FK; HR/Admin correction actor |
| `correction_date` | `DateTimeField(null=True, blank=True)` | Nullable if not corrected |
| `created_at`, `updated_at` | `DateTimeField` | Timestamps |

**Constraints:** add `UniqueConstraint(fields=["employee", "date"], name="uniq_attendance_employee_date")` to enforce one daily record per employee. Validate that checkout is not earlier than check-in when both values are present.

### 3.7 `payroll_salarycomponent` — SalaryComponent

| Field | Suggested Django type | Constraints / notes |
|---|---|---|
| `id` | `BigAutoField` | PK |
| `name` | `CharField(max_length=50)` | UK recommended |
| `type` | `CharField(max_length=20)` | `EARNINGS` or `DEDUCTIONS` |
| `calculation_method` | `CharField(max_length=20)` | `FIXED`, `PERCENTAGE`, `FORMULA` |
| `value` | `DecimalField(max_digits=10, decimal_places=2)` | Required |
| `is_taxable` | `BooleanField` | Required |
| `is_active` | `BooleanField(default=True)` | Required |
| `created_at`, `updated_at` | `DateTimeField` | Timestamps |

The schema stores component definitions; it does not calculate payroll amounts.

### 3.8 `payroll_payrollperiod` — PayrollPeriod

| Field | Suggested Django type | Constraints / notes |
|---|---|---|
| `id` | `BigAutoField` | PK |
| `name` | `CharField(max_length=50)` | UK recommended |
| `start_date`, `end_date` | `DateField` | Required; validate end date is not before start date |
| `status` | `CharField(max_length=20)` | `OPEN`, `CLOSED`, `LOCKED` |
| `generated_by` | `ForeignKey(CustomUser)` | FK, required |
| `generated_date` | `DateTimeField` | Required |
| `created_at`, `updated_at` | `DateTimeField` | Timestamps |

### 3.9 `payroll_payslip` — Payslip

| Field | Suggested Django type | Constraints / notes |
|---|---|---|
| `id` | `BigAutoField` | PK |
| `employee` | `ForeignKey(Employee)` | FK, required |
| `payroll_period` | `ForeignKey(PayrollPeriod)` | FK, required |
| `generated_date` | `DateTimeField` | Required |
| `gross_pay` | `DecimalField(max_digits=12, decimal_places=2)` | Required; stored value |
| `total_deductions` | `DecimalField(max_digits=12, decimal_places=2)` | Required; stored value |
| `net_pay` | `DecimalField(max_digits=12, decimal_places=2)` | Required; stored value |
| `pdf_file` | `FileField(upload_to="payslips/", null=True, blank=True)` | Optional |
| `is_downloaded` | `BooleanField(default=False)` | Required |
| `download_count` | `PositiveIntegerField(default=0)` | Required |
| `created_at`, `updated_at` | `DateTimeField` | Timestamps |

If the rule is one payslip per employee per period, add `UniqueConstraint(fields=["employee", "payroll_period"], name="uniq_payslip_employee_period")`. The practical relationship is one period to many payslips and one employee to many payslips.

### 3.10 `audit_auditlog` — AuditLog

| Field | Suggested Django type | Constraints / notes |
|---|---|---|
| `id` | `BigAutoField` | PK |
| `user` | `ForeignKey(CustomUser)` | FK; actor |
| `action` | `CharField(max_length=20)` | `CREATE`, `UPDATE`, `DELETE` |
| `entity_type` | `CharField(max_length=30)` | e.g. `EMPLOYEE`, `LEAVE`, `ATTENDANCE`, `PAYROLL`, `DEPARTMENT` |
| `entity_id` | `PositiveIntegerField` | Required; affected record ID |
| `changes` | `JSONField(null=True, blank=True)` | Before/after values |
| `timestamp` | `DateTimeField` | Required |
| `ip_address` | `GenericIPAddressField(null=True, blank=True)` | Optional |

Log sensitive employee/employment, leave status/balance, attendance correction, payroll, payslip, and payroll-period events. Retain indefinitely by default; consider partitioning/archiving at scale. Avoid logging passwords, tokens, or other secrets.

### 3.11 `notifications_notification` — Notification

| Field | Suggested Django type | Constraints / notes |
|---|---|---|
| `id` | `BigAutoField` | PK |
| `recipient` | `ForeignKey(CustomUser)` | FK, required |
| `related_employee` | `ForeignKey(Employee, null=True, blank=True)` | Optional relationship shown in the detailed schema |
| `notification_type` | `CharField(max_length=30)` | e.g. `LEAVE_APPROVED`, `LEAVE_REJECTED`, `ATTENDANCE_UPDATE`, `PAYSLIP_READY`, `SYSTEM_ANNOUNCEMENT` |
| `title` | `CharField(max_length=100)` | Required |
| `message` | `TextField` | Required |
| `is_read` | `BooleanField(default=False)` | Required |
| `created_at` | `DateTimeField` | Required |
| `related_entity_id` | `PositiveIntegerField(null=True, blank=True)` | Optional related record ID |
| `related_entity_type` | `CharField(max_length=30, null=True, blank=True)` | Optional related record type |
| `updated_at` | `DateTimeField` | If included in implementation |

## 4. Relationships and cardinality

| Parent | Child / relationship | Cardinality | Notes |
|---|---|---|---|
| `CustomUser` | `Employee.user` | 1:1 | Each employee profile belongs to one user; `user` is unique |
| `Department` | `Employee.department` | 1:N | Department assignment is optional |
| `CustomUser` | `Department.head` | 1:N | Head is optional and receives no extra role permissions automatically |
| `Employee` | `LeaveRequest.employee` | 1:N | One employee can submit many requests |
| `LeaveType` | `LeaveRequest.leave_type` | 1:N | Each request has one leave type |
| `Employee` | `Attendance.employee` | 1:N | One employee can have many daily records; employee/date unique |
| `Employee` | `Payslip.employee` | 1:N | Payslips over time |
| `PayrollPeriod` | `Payslip.payroll_period` | 1:N | A period includes payslips for employees |
| `CustomUser` | `PayrollPeriod.generated_by` | 1:N | One user may generate multiple periods |
| `CustomUser` | `AuditLog.user` | 1:N | One actor may create many audit entries |
| `CustomUser` | `Notification.recipient` | 1:N | One user may receive many notifications |
| `CustomUser` | `LeaveRequest.approved_by` | 1:N | Optional HR/Admin decision-maker |
| `CustomUser` | `Attendance.corrected_by` | 1:N | Optional correction actor |

## 5. Key constraints and validation

1. `Employee.user` is one-to-one and `Employee.employee_id` is unique.
2. `Department.code` is unique. Consider making department name unique only if the business requires it.
3. `Attendance(employee, date)` is unique.
4. `Payslip(employee, payroll_period)` should be unique if only one payslip per employee per period is allowed.
5. `LeaveRequest.end_date >= LeaveRequest.start_date`.
6. `LeaveType.max_days_per_year >= 1`; monetary values and duration values should be non-negative.
7. Validate enum fields against the listed choices at both model/form/API level.
8. Use nullable FKs only where the business rules explicitly allow missing relationships.
9. Choose `on_delete` behavior deliberately. The supplied notes mention cascading leave requests on employee removal; for HR/payroll/audit history, consider `PROTECT` or soft-deactivation instead of deleting historical records.
10. Add database indexes for frequent filters, described below.

## 6. Business rules represented by or affecting the schema

### Leave
- Employees may cancel approved leave before its start date, up to two cancellations per quarter.
- Further cancellations require HR approval.
- HR/Admin may reopen cancelled requests with justification.
- Only HR/Admin approve/reject; direct managers do not approve leave.
- Decisions require remarks and before/after audit logging.
- Track balances per employee per year; warn on excess requests rather than blocking submission.
- HR balance adjustments require justification and audit logging.
- `balance_deducted` is nullable.

**Implementation note:** the supplied core schema does not fully persist annual balances, quarterly cancellation counts, status history, or reopening justification. Add supporting models/tables if these rules must be enforceable and auditable.

### Attendance
- Provisional official hours are 9:00 AM–5:00 PM with a 15-minute grace period.
- Check-in through 9:15 AM is `PRESENT` with `late_minutes = 0`; after 9:15 AM, mark `LATE` and calculate minutes after 9:15 AM.
- After 10:00 AM, default behavior remains `LATE` with hour-level tracking unless policy changes.
- Only HR/Admin correct records; corrections are within the same monthly payroll period. After closure, special Admin approval is required.
- Keep before/after correction values, actor, and timestamp in audit data.
- Missing check-out: assume 8.0 hours and `PRESENT`, notify employee; alert HR at three or more occurrences in a month. No automatic leave/pay deduction.

The `Attendance` table alone does not persist the monthly missing-checkout count or payroll-period closure approval; implement those in application logic and audit records.

### Payroll
- Admin: all salary records, payslips, and components.
- HR: company-wide salary records and payslips.
- Employee: own payslips and component breakdown only.
- Salary components can be entered manually or imported.
- `gross_pay`, `total_deductions`, and `net_pay` are recorded fields; calculations are outside this schema.

### Departments
- Employees may remain unassigned.
- Department head is organizational reporting only.
- Department-specific permissions must be explicitly implemented in application logic.

### Audit history
- Log sensitive changes with actor, timestamp, action, entity type/ID, before/after JSON, and optional IP.
- Retention is indefinite by default; monthly statistics and manual export/review are planned.

## 7. Recommended indexes

| Model | Suggested index |
|---|---|
| Employee | `(department, employment_status)` |
| LeaveRequest | `(status, employee, leave_type, approval_date)` |
| Attendance | `(employee, date, attendance_status)` |
| Payslip | `(employee, payroll_period, is_downloaded)` |
| AuditLog | `(entity_type, entity_id, timestamp)` |
| CustomUser | `(role, is_staff)` |

Create indexes using Django `Meta.indexes`; do not duplicate indexes already created by PK, unique, or FK fields without a query-performance reason.

## 8. Normalization

The intended design follows 1NF by storing atomic attributes and avoiding repeating groups. Related entities are separated into their own tables, supporting 2NF/3NF. Repeated business history (leave status changes, balance adjustments) should be stored in related history records rather than packed into a single current-state field.

## 9. Django / PostgreSQL implementation checklist

- Set `AUTH_USER_MODEL = "accounts.CustomUser"` before initial migrations are created.
- Define explicit `on_delete` behavior for every FK.
- Add `UniqueConstraint` and `CheckConstraint` where appropriate.
- Generate and review migrations; do not edit applied migrations casually.
- Keep secrets and database credentials in environment variables.
- Use synthetic demo data only.
- Add tests for constraints, status transitions, date validation, access scope, and audit creation.
