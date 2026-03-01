# KlyrSignals v1.6 - Requirements Document

**Version:** 1.6.0  
**Status:** Complete  
**Date:** 2026-03-01  
**Author:** Tony (Lead Architect)  

---

## 1. Overview

### 1.1 Purpose

This document defines the functional and non-functional requirements for KlyrSignals v1.6, which introduces authentication, authorization, database persistence, and user management to the existing v1.5 application.

### 1.2 Scope

**In Scope:**
- User registration and authentication (email/password + OAuth)
- JWT-based session management
- PostgreSQL database with Prisma ORM
- User profile management
- Password reset functionality
- Portfolio data migration from localStorage to database
- Protected API endpoints
- Audit logging
- Rate limiting and security measures

**Out of Scope (Future Versions):**
- Two-factor authentication (2FA)
- Email verification (currently optional)
- Multi-portfolio support (currently one per user)
- Portfolio sharing/collaboration
- Advanced role-based access control (RBAC)
- Mobile app

### 1.3 Definitions

| Term | Definition |
|------|------------|
| **Access Token** | Short-lived JWT (15 min) for API authentication |
| **Refresh Token** | Long-lived JWT (7 days) for obtaining new access tokens |
| **OAuth** | Open Authorization protocol for third-party login |
| **bcrypt** | Password hashing algorithm |
| **CORS** | Cross-Origin Resource Sharing |
| **GDPR** | General Data Protection Regulation (EU privacy law) |
| **JWT** | JSON Web Token |
| **PII** | Personally Identifiable Information |

---

## 2. User Requirements

### 2.1 User Stories

#### Authentication

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|---------------------|
| US-001 | As a user, I want to create an account with email/password so I can save my portfolio to the cloud | Must Have | - Registration form with email, password, name<br>- Password strength validation<br>- Email uniqueness check<br>- Account created in database |
| US-002 | As a user, I want to login with my credentials so I can access my account | Must Have | - Login form with email/password<br>- Successful login redirects to dashboard<br>- Failed login shows error message<br>- Rate limiting on failed attempts |
| US-003 | As a user, I want to login with Google so I don't need to remember another password | Should Have | - "Login with Google" button<br>- OAuth flow completes successfully<br>- New account created if doesn't exist<br>- Existing account linked |
| US-004 | As a user, I want to login with GitHub so I can use my developer account | Should Have | - "Login with GitHub" button<br>- OAuth flow completes successfully<br>- New account created if doesn't exist<br>- Existing account linked |
| US-005 | As a user, I want to logout securely so my account is protected | Must Have | - Logout button in UI<br>- Session invalidated on backend<br>- Redirect to login page<br>- Refresh token deleted |

#### Password Management

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|---------------------|
| US-006 | As a user, I want to reset my password if I forget it so I can regain access to my account | Must Have | - "Forgot password?" link on login<br>- Email input for reset request<br>- Reset email sent with token<br>- Token expires after 1 hour<br>- New password must meet requirements |
| US-007 | As a user, I want to change my password so I can update my credentials | Should Have | - Change password form in profile<br>- Requires current password<br>- New password validation<br>- All sessions invalidated after change |

#### Profile Management

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|---------------------|
| US-008 | As a user, I want to update my profile information so I can keep my account current | Should Have | - Edit name field<br>- Upload/change avatar<br>- Changes saved to database<br>- Display updated info immediately |
| US-009 | As a user, I want to delete my account and data so I can exercise my right to be forgotten (GDPR) | Must Have | - Delete account option in settings<br>- Confirmation required (type "DELETE_MY_ACCOUNT")<br>- All data cascade deleted<br>- Audit log entry created |

#### Portfolio Management

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|---------------------|
| US-010 | As a user, I want my portfolio saved to the cloud so I don't lose my data | Must Have | - Portfolio automatically saved to database<br>- Data persists across sessions<br>- Backup/restore capability |
| US-011 | As a user, I want to access my portfolio from any device so I can check my investments anywhere | Must Have | - Login from different device shows same data<br>- Real-time sync (on page load)<br>- No device-specific limitations |
| US-012 | As an existing v1.5 user, I want to migrate my localStorage data to the cloud so I don't lose my portfolio | Must Have | - Migration prompt on first login<br>- One-click migration<br>- Data integrity verification<br>- localStorage cleared after success |

#### Session Management

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|---------------------|
| US-013 | As a user, I want to stay logged in for 7 days so I don't have to login every time | Should Have | - "Remember me" option (default on)<br>- Refresh token valid for 7 days<br>- Automatic token refresh<br>- Session persists across browser restarts |
| US-014 | As a user, I want to see my active sessions so I can monitor account access | Could Have | - List of active sessions (device, location, time)<br>- Logout from individual sessions<br>- "Logout from all devices" option |

---

## 3. System Requirements

### 3.1 Functional Requirements

#### Authentication System

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | System shall hash passwords using bcrypt with minimum 12 rounds | Must Have |
| FR-002 | System shall issue JWT access tokens with 15-minute expiry | Must Have |
| FR-003 | System shall issue JWT refresh tokens with 7-day expiry | Must Have |
| FR-004 | System shall validate JWT tokens on every protected API request | Must Have |
| FR-005 | System shall support OAuth 2.0 authentication with Google | Should Have |
| FR-006 | System shall support OAuth 2.0 authentication with GitHub | Should Have |
| FR-007 | System shall refresh access tokens using refresh tokens | Must Have |
| FR-008 | System shall invalidate refresh tokens on logout | Must Have |
| FR-009 | System shall rate limit authentication endpoints (5 attempts/min) | Must Have |

#### Authorization System

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-010 | System shall require authentication for all portfolio operations | Must Have |
| FR-011 | System shall enforce user-scoped data access (users can only access their own data) | Must Have |
| FR-012 | System shall return 401 Unauthorized for missing/invalid tokens | Must Have |
| FR-013 | System shall return 403 Forbidden for insufficient permissions | Must Have |

#### Data Management

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-014 | System shall store user data in PostgreSQL database | Must Have |
| FR-015 | System shall use Prisma ORM for database operations | Must Have |
| FR-016 | System shall cascade delete user data when account is deleted | Must Have |
| FR-017 | System shall migrate existing localStorage data to database | Must Have |
| FR-018 | System shall verify data integrity after migration | Must Have |

#### Audit & Logging

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-019 | System shall log all authentication events (login, logout, failed attempts) | Must Have |
| FR-020 | System shall log all data modification events (create, update, delete) | Should Have |
| FR-021 | System shall store IP address and user agent in audit logs | Should Have |
| FR-022 | System shall retain audit logs for 90 days | Should Have |

#### Email System

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-023 | System shall send password reset emails via SendGrid | Must Have |
| FR-024 | System shall generate secure reset tokens (1-hour expiry) | Must Have |
| FR-025 | System shall use email templates for consistency | Should Have |

---

### 3.2 Non-Functional Requirements

#### Security

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-001 | System shall use HTTPS for all production traffic | Must Have |
| NFR-002 | System shall implement CORS with whitelisted origins | Must Have |
| NFR-003 | System shall hash passwords with bcrypt (12+ rounds) | Must Have |
| NFR-004 | System shall sign JWT tokens with HS256 or RS256 | Must Have |
| NFR-005 | System shall store refresh tokens as httpOnly cookies | Must Have |
| NFR-006 | System shall implement rate limiting (100 req/hour per user) | Must Have |
| NFR-007 | System shall validate all inputs (backend and frontend) | Must Have |
| NFR-008 | System shall prevent SQL injection (use Prisma ORM) | Must Have |
| NFR-009 | System shall prevent XSS (React escapes by default) | Must Have |
| NFR-010 | System shall prevent CSRF (sameSite cookies) | Must Have |

#### Performance

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-011 | System shall respond to API requests in <500ms (p95) | Should Have |
| NFR-012 | System shall support 100 concurrent users | Should Have |
| NFR-013 | System shall handle database queries in <100ms (p95) | Should Have |
| NFR-014 | System shall load pages in <2 seconds (on 4G) | Should Have |

#### Reliability

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-015 | System shall have 99.9% uptime (excluding maintenance) | Should Have |
| NFR-016 | System shall perform daily database backups | Must Have |
| NFR-017 | System shall have error tracking (Sentry) | Should Have |
| NFR-018 | System shall have session replay for debugging (LogRocket) | Could Have |

#### Scalability

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-019 | System shall support 10,000 users without architecture changes | Could Have |
| NFR-020 | System shall support read replicas for database scaling | Future |
| NFR-021 | System shall support horizontal scaling for backend | Future |

#### Usability

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-022 | System shall provide clear error messages to users | Must Have |
| NFR-023 | System shall show loading states during async operations | Must Have |
| NFR-024 | System shall be responsive (mobile, tablet, desktop) | Must Have |
| NFR-025 | System shall be accessible (WCAG 2.1 AA) | Should Have |

#### Compliance

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-026 | System shall comply with GDPR (right to access, deletion, rectification) | Must Have |
| NFR-027 | System shall have a privacy policy | Must Have |
| NFR-028 | System shall obtain consent for PII storage | Must Have |
| NFR-029 | System shall have a data retention policy | Must Have |

---

## 4. Data Requirements

### 4.1 Data Models

#### User
- id (UUID, primary key)
- email (string, unique, required)
- passwordHash (string, nullable - null for OAuth users)
- name (string, optional)
- avatarUrl (string, optional)
- emailVerified (datetime, optional)
- createdAt (datetime)
- updatedAt (datetime)

#### Account (OAuth)
- id (UUID, primary key)
- userId (UUID, foreign key)
- type (string: "oauth2" | "oidc")
- provider (string: "google" | "github")
- providerAccountId (string)
- refresh_token (string, optional)
- access_token (string, optional)
- expires_at (int, optional)
- token_type (string, optional)
- scope (string, optional)
- id_token (string, optional)

#### Session
- id (UUID, primary key)
- userId (UUID, foreign key)
- token (string, unique - hashed refresh token)
- expiresAt (datetime)
- createdAt (datetime)
- userAgent (string, optional)
- ipAddress (string, optional)

#### Portfolio
- id (UUID, primary key)
- userId (UUID, foreign key)
- name (string, default "My Portfolio")
- description (string, optional)
- isPublic (boolean, default false)
- createdAt (datetime)
- updatedAt (datetime)

#### Holding
- id (UUID, primary key)
- portfolioId (UUID, foreign key)
- symbol (string)
- quantity (float)
- purchasePrice (float)
- purchaseDate (datetime, optional)
- assetClass (string: "stock" | "etf" | "crypto" | "mutual_fund", default "stock")
- createdAt (datetime)
- updatedAt (datetime)

#### AuditLog
- id (UUID, primary key)
- userId (UUID, foreign key, optional)
- action (string)
- resource (string, optional)
- resourceId (string, optional)
- ipAddress (string, optional)
- userAgent (string, optional)
- timestamp (datetime)
- metadata (JSON, optional)

### 4.2 Data Validation Rules

| Field | Validation |
|-------|------------|
| email | Valid email format, unique, max 255 chars |
| password | Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char |
| name | Max 100 chars, alphanumeric + spaces |
| symbol | Max 20 chars, uppercase letters and numbers |
| quantity | Positive number, max 10 decimal places |
| purchasePrice | Positive number, max 2 decimal places |

### 4.3 Data Retention

| Data Type | Retention Period | Deletion Trigger |
|-----------|------------------|------------------|
| User accounts | Indefinite (until user deletion) | Account deletion request |
| Session tokens | 7 days | Expiry or logout |
| Audit logs | 90 days | Automatic purge |
| Deleted accounts | 30 days (backup) | Permanent purge after 30 days |

---

## 5. Interface Requirements

### 5.1 User Interfaces

#### Login Page
- URL: `/login`
- Components: Email input, password input, login button, OAuth buttons, forgot password link, register link
- Validation: Email format, required fields
- Error handling: Invalid credentials, rate limiting, network errors

#### Register Page
- URL: `/register`
- Components: Name input, email input, password input, confirm password, password strength indicator, terms checkbox, register button, OAuth buttons, login link
- Validation: Email format, password requirements, terms acceptance
- Error handling: Email exists, weak password, network errors

#### Forgot Password Page
- URL: `/forgot-password`
- Components: Email input, submit button, success message
- Validation: Email format
- Error handling: Network errors

#### Reset Password Page
- URL: `/reset-password?token=...`
- Components: New password input, confirm password, password strength indicator, submit button
- Validation: Password requirements, token validity
- Error handling: Invalid/expired token, weak password

#### Profile Page
- URL: `/profile`
- Components: Avatar display/upload, name input, email display, change password section, delete account section
- Validation: Name length, password requirements
- Error handling: Network errors, confirmation for delete

#### Settings Page
- URL: `/settings`
- Components: Notification preferences, privacy settings, connected accounts, session management
- Validation: N/A
- Error handling: Network errors

### 5.2 API Interfaces

See `ARCH_V1.6.md` Section 3 for complete API specification.

### 5.3 External Interfaces

| Interface | Purpose | Protocol |
|-----------|---------|----------|
| Google OAuth | OAuth authentication | OAuth 2.0 |
| GitHub OAuth | OAuth authentication | OAuth 2.0 |
| SendGrid | Email delivery | REST API |
| PostgreSQL | Database | TCP (5432) |
| Redis | Rate limiting storage | TCP (6379) |

---

## 6. Migration Requirements

### 6.1 v1.5 to v1.6 Migration

| Requirement | Description |
|-------------|-------------|
| MR-001 | Detect existing localStorage data on first login |
| MR-002 | Display migration prompt to users with existing data |
| MR-003 | Migrate holdings from localStorage to database |
| MR-004 | Verify data integrity after migration |
| MR-005 | Clear localStorage after successful migration |
| MR-006 | Support both local and cloud modes simultaneously |
| MR-007 | Provide UI indicator for current mode (local vs cloud) |

### 6.2 Migration Flow

1. User logs in for first time
2. Frontend checks localStorage for existing portfolio
3. If found: Display migration modal
4. User accepts migration
5. Frontend sends localStorage data to backend
6. Backend saves to database
7. Frontend verifies migration success
8. Frontend clears localStorage
9. User redirected to dashboard

---

## 7. Testing Requirements

### 7.1 Unit Testing

| Requirement | Coverage Target |
|-------------|-----------------|
| Backend unit tests | >80% code coverage |
| Frontend component tests | Critical components only |
| Auth flow tests | 100% coverage |

### 7.2 Integration Testing

| Requirement | Description |
|-------------|-------------|
| IT-001 | Test complete auth flow (register → login → protected request → logout) |
| IT-002 | Test OAuth flow (Google, GitHub) |
| IT-003 | Test password reset flow |
| IT-004 | Test token refresh flow |
| IT-005 | Test migration flow (localStorage → database) |

### 7.3 Security Testing

| Requirement | Description |
|-------------|-------------|
| ST-001 | Penetration testing (OWASP Top 10) |
| ST-002 | SQL injection testing |
| ST-003 | XSS testing |
| ST-004 | CSRF testing |
| ST-005 | Rate limiting testing |
| ST-006 | JWT token validation testing |

### 7.4 Performance Testing

| Requirement | Target |
|-------------|--------|
| PT-001 | Load test with 100 concurrent users |
| PT-002 | Measure API response times (p95 <500ms) |
| PT-003 | Measure database query times (p95 <100ms) |
| PT-004 | Identify bottlenecks |

---

## 8. Deployment Requirements

### 8.1 Infrastructure

| Component | Requirement |
|-----------|-------------|
| Database | PostgreSQL 15 (managed: Railway or Supabase) |
| Backend | Python/FastAPI (Railway or Render) |
| Frontend | Next.js (Vercel or Netlify) |
| Email | SendGrid (free tier: 100 emails/day) |
| Rate Limiting | Redis (managed or self-hosted) |
| Monitoring | Sentry (error tracking), LogRocket (session replay) |

### 8.2 Environment Variables

See `ARCH_V1.6.md` Section 9 for complete list.

### 8.3 Deployment Checklist

- [ ] Database created and accessible
- [ ] Migrations run successfully
- [ ] Environment variables set
- [ ] HTTPS enabled
- [ ] CORS configured for production domain
- [ ] Rate limiting active
- [ ] Monitoring tools configured
- [ ] Backups enabled
- [ ] Rollback plan documented

---

## 9. Documentation Requirements

| Document | Purpose | Owner |
|----------|---------|-------|
| ARCH_V1.6.md | Architecture specification | Tony |
| REQ_V1.6.md | Requirements (this document) | Tony |
| TASKS_V1.6.md | Implementation tasks | Tony |
| API.md | API documentation (auto-generated) | Peter |
| USER_GUIDE.md | User documentation | Pepper |
| ADMIN_GUIDE.md | Admin documentation | Pepper |
| DECISIONS.md | Architecture decisions log | Tony |

---

## 10. Acceptance Criteria

### 10.1 Phase 1: Database Setup
- [ ] PostgreSQL database created
- [ ] Prisma ORM configured
- [ ] All tables created with correct schema
- [ ] Database connection tested

### 10.2 Phase 2: Backend Auth
- [ ] Users can register with email/password
- [ ] Users can login with email/password
- [ ] OAuth login works (Google, GitHub)
- [ ] JWT tokens issued and validated
- [ ] Rate limiting active
- [ ] Unit tests passing (>80% coverage)

### 10.3 Phase 3: Frontend Auth
- [ ] Login page functional
- [ ] Register page functional
- [ ] Forgot/reset password pages functional
- [ ] Profile/settings pages functional
- [ ] Protected routes redirect to login
- [ ] No console errors

### 10.4 Phase 4: Portfolio Migration
- [ ] Migration prompt displays on first login
- [ ] Data migrates successfully
- [ ] Data integrity verified
- [ ] localStorage cleared after migration
- [ ] Users can continue using app seamlessly

### 10.5 Phase 5: QA & Security
- [ ] No critical/high security vulnerabilities
- [ ] All user stories verified
- [ ] Performance acceptable (<500ms response time)
- [ ] Ready for production deployment

### 10.6 Phase 6: Deployment
- [ ] Production deployment successful
- [ ] No downtime during deployment
- [ ] Monitoring active
- [ ] Users can access app

---

## 11. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Data loss during migration | High | Low | Backup localStorage data before migration, verify integrity after |
| Security vulnerability | High | Medium | Security audit, penetration testing, follow OWASP guidelines |
| OAuth provider downtime | Medium | Low | Support multiple providers, fallback to email/password |
| Database performance issues | Medium | Low | Index optimization, query optimization, connection pooling |
| Email deliverability issues | Medium | Medium | Use SendGrid (reputable provider), monitor bounce rates |
| Rate limiting too aggressive | Low | Medium | Monitor rate limit hits, adjust thresholds as needed |

---

## 12. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| User registration success rate | >95% | Analytics tracking |
| Login success rate | >98% | Analytics tracking |
| Migration success rate | >99% | Backend logs |
| API response time (p95) | <500ms | Monitoring (Sentry) |
| Error rate | <1% | Monitoring (Sentry) |
| User satisfaction | >4/5 | User feedback |

---

**Document Version:** 1.0  
**Last Updated:** 2026-03-01  
**Approved By:** Tony (Lead Architect)
