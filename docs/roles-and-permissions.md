# Smart HR System — Roles and Permissions

**Purpose:** Define the intended access boundaries for Admin, HR, and Employee roles. These are application authorization rules; database foreign keys do not enforce them by themselves.

## 1. Role definitions

- **Admin:** system-wide administrative access, including special approval for corrections after a payroll period is closed.
- **HR:** company-wide workforce and payroll operations, leave decisions, and attendance corrections.
- **Employee:** access to their own employee information, attendance, leave requests, notifications, and payslips.

Django `is_staff` and `is_superuser` are authentication/admin-site flags and should not be treated as substitutes for the application's `role` field. Use server-side checks for every protected view, API endpoint, and download.

## 2. Permission matrix

Legend: **All** = company-wide scope; **Own** = only the signed-in employee's records; **Assigned** = explicitly scoped by application logic; **—** = not permitted by default.

| Resource / action | Admin | HR | Employee |
|---|---|---|---|
| User accounts: view | All | Limited to legitimate HR needs | Own account |
| User accounts: create/update | All | As authorized for onboarding and HR operations | Update only allowed own profile fields |
| User accounts: delete/deactivate | All, with audit | As explicitly authorized; prefer deactivation | — |
| Employee profiles: view | All | All | Own profile |
| Employee profiles: create | All | All | — |
| Employee profiles: update | All | All, subject to field policy | Own permitted self-service fields only |
| Employee profiles: verify | All | As assigned by the application | — |
| Departments: view | All | All | Read-only information only if exposed |
| Departments: create/update/deactivate | All | As authorized by project policy | — |
| Department head assignment | All | As authorized by project policy | — |
| Attendance: view | All | All | Own records |
| Attendance: create/check-in/out | As needed for administration | As needed for administration | Own attendance workflow |
| Attendance: correct records | All | All | — |
| Closed-period attendance correction | Special Admin approval required | — | — |
| Leave types: view | All | All | Available types only |
| Leave types: create/update/deactivate | All | As authorized by project policy | — |
| Leave requests: submit | — | If also an employee, through own employee identity | Own requests |
| Leave requests: view | All | All | Own requests |
| Leave requests: approve/reject | All | All | — |
| Leave requests: cancel approved leave | Admin/HR may handle exceptions and reopenings | HR handles exception approvals/reopenings | Own request, only before start date and within quarterly allowance |
| Leave balances: view | All | All | Own balance |
| Leave balances: adjust | All | HR may adjust with justification and audit | — |
| Salary components: view | All | All | Only own payslip component breakdown, not the company-wide component administration list |
| Salary components: create/update/deactivate | All | As authorized for payroll operations | — |
| Payroll periods: view | All | All | — |
| Payroll periods: create/update/close/lock | All | As authorized by payroll workflow | — |
| Payslips: view/download | All | All | Own payslips only |
| Payslips: generate/manage | All | As authorized by payroll workflow | — |
| Notifications: view/mark read | All for administration where needed | Relevant notifications | Own notifications |
| Audit logs: view/export | All | Limited to authorized HR review | — |
| Audit logs: create | System/application service only | System/application service only | System/application service only |
| Reports: workforce/attendance/leave | All | All | Own information or explicitly published reports |
| Reports: payroll | All | All | Own payslip/report only |
| System configuration | All | — unless explicitly delegated | — |

## 3. Scope and enforcement rules

1. **Deny by default.** Every protected endpoint must check authentication, role, and record-level scope.
2. **Employee ownership:** derive the employee profile from the authenticated user; never trust a client-supplied `employee_id` to authorize access.
3. **Payroll privacy:** employee requests must be filtered to their own payslips. Do not expose other employees' salaries through IDs, filters, exports, file URLs, or error messages.
4. **Leave decisions:** only HR/Admin may approve or reject. Direct managers do not gain approval authority because they are department heads.
5. **Attendance corrections:** only HR/Admin may correct records. Corrections after the relevant payroll period closes require special Admin approval.
6. **Department heads:** assignment is organizational reporting only and does not grant extra permissions.
7. **Auditability:** sensitive changes should record actor, timestamp, entity, and before/after values. Users must not be able to edit or delete audit records through ordinary application endpoints.
8. **Downloads and exports:** apply the same permission checks as detail pages and APIs; a hard-to-guess file URL is not authorization.
9. **Field-level permissions:** restrict employee self-service edits to approved fields; do not allow employees to change role, verification status, salary, payroll, or approval metadata.
10. **Notifications:** users may read/mark read their own notifications. Admin/HR visibility should be limited to legitimate operational needs.

## 4. Suggested permission tests

- Anonymous users cannot access protected resources.
- Employee A cannot view, edit, export, or download Employee B's profile, attendance, leave request, notification, or payslip.
- Employee cannot approve/reject a leave request or alter leave balances.
- Department head without HR/Admin role cannot approve a report's leave request or correct attendance merely because they are head.
- HR can approve/reject leave and correct attendance, but cannot perform closed-period corrections requiring Admin approval.
- Employee cannot access company-wide salary components, payroll-period management, or other employees' payslips.
- Every sensitive change creates the expected audit entry.
- API list, detail, search, filter, export, and download endpoints enforce equivalent scope.
- Inactive or terminated employee behavior is explicit and tested.
- Role changes and deactivation are restricted to authorized users.

## 5. Decisions requiring team confirmation

The project requirements specify Admin, HR, and Employee roles and payroll scope, but do not completely define every create/update/delete permission. The rows marked “as authorized by project policy” are proposed defaults and should be confirmed by the team before implementation. Keep this file aligned with the actual permission classes and tests.
