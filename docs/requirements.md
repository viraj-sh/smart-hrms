# Smart HR System — Functional Requirements and Assumptions

**Project:** Qveto Smart HR & Employee Management System  
**Implementation plan:** Four weeks  
**Document scope:** Functional requirements, role scope, and assumptions for Week 1 planning.

## 1. System purpose

Build a web application that centralizes employee records, attendance, leave requests, departments, payroll records, notifications, and workforce reporting. The system should provide separate Admin, HR, and Employee experiences with role-based authorization.

## 2. Functional requirements by role

### 2.1 Admin

- Manage user accounts and role assignments.
- View and manage employee profiles, employment records, and departments.
- View workforce-wide attendance records and reports.
- Approve/reject leave requests and handle authorized cancellation/reopening exceptions.
- Access salary components, payroll periods, payslips, and payroll records.
- Perform special approval for attendance corrections after payroll-period closure.
- Review sensitive audit history and authorized reports.
- Access system-wide workforce dashboards and reporting.

### 2.2 HR

- Register and manage employee profiles and employment information.
- Manage department information as permitted by the application policy.
- View attendance and produce monthly attendance summaries.
- Correct attendance records within the permitted payroll-period window.
- Approve/reject leave requests; decision remarks are required.
- Adjust leave balances with justification and audit logging.
- Manage payroll records and payslips at company-wide scope as specified by the project rules.
- Review relevant notifications, audit events, and workforce reports.

### 2.3 Employee

- Access their own account and employee profile.
- Use the attendance check-in/check-out workflow and view own attendance history.
- Submit leave requests, view request status, and provide request remarks.
- Cancel their own approved leave only before the start date and within the cancellation allowance; additional cancellations require HR approval.
- View their own leave balance and receive warnings for requests exceeding the available balance; excess submission is not blocked by the schema rule.
- View and download their own payslips and the component breakdown available to them.
- View and mark their own notifications as read.

## 3. Core functional requirements

### 3.1 User accounts and employee records

- Support Admin, HR, and Employee roles.
- Use Django's custom user model extending `AbstractUser`.
- Link each employee profile one-to-one to a user account.
- Store unique employee ID, job title, employment status, joining date, verification status, optional photo, and optional department.
- Permit employees to exist without a department assignment.
- Store department name, unique code, optional description, optional department head, and active status.

### 3.2 Attendance

- Store daily attendance date, check-in/out times, status, total hours, late minutes, early minutes, and correction metadata.
- Enforce one attendance record per employee per date.
- Use provisional official hours of 9:00 AM–5:00 PM and a 15-minute grace period.
- Check-in through 9:15 AM is Present with zero late minutes; after 9:15 AM, status is Late and minutes are counted from 9:15 AM.
- After 10:00 AM, default behavior remains Late with hour-level tracking unless the team adopts a different absence policy.
- If check-out is missing, assume 8.0 hours and Present, notify the employee, and alert HR after three or more such occurrences in a month. Do not automatically deduct leave or pay.
- Only HR/Admin may correct submitted records. Corrections within a payroll period are allowed; after period closure, special Admin approval is required.
- Keep before/after values, correction actor, and timestamp in audit data.

### 3.3 Leave management

- Maintain leave types with yearly entitlement, carry-forward, approval requirement, and paid/unpaid status.
- Employees can submit requests with leave type, start/end dates, total days, and remarks.
- HR/Admin alone approve or reject requests; direct managers do not approve their reports' requests.
- Decisions require remarks and audit logging.
- Track leave balances per employee per year. Warn about excess requests but do not block submission.
- `balance_deducted` may be null.
- Employees may cancel approved leave before its start date, up to two cancellations per quarter. Further cancellations require HR approval.
- HR/Admin may reopen cancelled requests with justification.
- HR balance adjustments require justification and audit logging.

**Known design gap:** the initial ER diagram's status choices are only `PENDING`, `APPROVED`, and `REJECTED`, which does not represent the cancellation/reopening rules. The schema also does not explicitly include annual balance, quarterly cancellation counter, or leave status history tables. Resolve this with the team before implementation.

### 3.4 Payroll and payslips

- Store salary components with type, calculation method, value, taxable flag, and active flag.
- Store payroll periods with date range, status, creator, and generation date.
- Store payslip employee, payroll period, generation date, recorded gross pay, deductions, net pay, optional PDF file, and download tracking.
- Payroll totals are stored values; calculations are outside this schema.
- Admin has access to all salary records, payslips, and components.
- HR has company-wide salary record and payslip access.
- Employees can access only their own payslips and component breakdown.

### 3.5 Notifications and audit history

- Create notifications for relevant events such as leave decisions, attendance updates, payslip readiness, and system announcements.
- Store recipient, type, title, message, read status, timestamp, and optional related entity reference.
- Record audit events for sensitive employee/employment, leave status/balance, attendance correction, payroll, payslip, and payroll-period changes.
- Audit records include actor, timestamp, action, entity type/ID, before/after JSON changes, and optional IP address.
- Default audit retention is indefinite; provide monthly statistics and manual export/review. Any cleanup should require explicit confirmation.

### 3.6 Dashboards and reporting

- Provide separate role-aware dashboards.
- Support dashboard indicators for headcount, department distribution, attendance summaries, pending leave requests, and payroll-period summaries, subject to role access.
- Support search, filtering, pagination, and CSV/Excel/PDF exports for authorized reports.
- Restrict report contents and downloads using the same authorization scope as the underlying records.

### 3.7 Security, testing, and reproducibility

- Apply authentication and least-privilege authorization to every protected operation.
- Use server-side validation, database migrations, consistent error handling, and structured logging.
- Store secrets in environment variables and provide `.env.example` with placeholders only.
- Use synthetic or anonymized demo data; do not commit private employee data, credentials, or secrets.
- Test critical business rules, role permissions, validation, state transitions, integrations, and failure paths.
- Document installation, environment variables, database setup, seed data, run/test commands, and deployment steps.

## 4. Data domains

| Domain | Records in scope |
|---|---|
| Users and roles | Custom user accounts and role values |
| Employees and departments | Employee profile, employment status, job title, joining date, department and optional head |
| Attendance | Daily check-in/out, status, hours, late/early minutes, correction metadata |
| Leave management | Leave types, requests, decisions, remarks, balance tracking, cancellation rules |
| Payroll and payslips | Salary components, payroll periods, recorded payslip totals and PDF metadata |
| Notifications and audit history | Notification records and selective audit events |

## 5. Assumptions and unresolved decisions

1. **Working hours:** 9:00 AM–5:00 PM and 15-minute grace period are provisional policy values.
2. **Absence after 10 AM:** current default is still Late with hour-level tracking; a definitive Absent rule has not been specified.
3. **Leave days:** `total_days` is intended as an inclusive day count, but holiday/weekend treatment is not defined.
4. **Leave cancellation:** two cancellations per quarter, HR approval beyond that, and HR/Admin reopening with justification are specified; storage and status choices need to be added to the schema.
5. **Leave balance:** yearly balances and adjustments are required, but a dedicated balance/history model is not shown in the initial ER diagram.
6. **Payroll computation:** outside schema scope; gross pay, deductions, and net pay are stored values.
7. **Payslip uniqueness:** enforce one payslip per employee per payroll period if this is the team's intended business rule.
8. **Department head:** organizational reporting only; no extra permissions by virtue of head assignment.
9. **Deletion policy:** preserve sensitive history. The team should confirm FK deletion behavior and whether employee records should be deactivated instead of deleted.
10. **Payment status:** the broader project data requirements mention payment status where in scope, but the supplied schema does not include it. Add only if the team confirms it is needed.
11. **Email delivery:** relevant email notifications are a project objective; delivery provider and retry behavior remain implementation decisions.

## 6. Week 1 boundaries

This documentation covers the schema, requirements, and role-permission design. Django/DRF setup, authentication implementation, dashboard shells, and permission test implementation are separate implementation tasks assigned within the team. The schema should be reviewed against the actual codebase before migrations are finalized.
