# KlyrSignals v1.6 - Implementation Tasks

**Version:** 1.6.0  
**Status:** Ready for Implementation  
**Date:** 2026-03-01  
**Author:** Tony (Lead Architect)  
**Assigned To:** Peter (Developer)  
**Estimated Time:** 40-50 hours  

---

## Overview

This document breaks down the v1.6 implementation into discrete, actionable tasks for Peter. Tasks are organized by phase and include acceptance criteria for verification.

**Total Phases:** 6  
**Total Tasks:** 47  
**Estimated Time:** 40-50 hours  

---

## Phase 1: Database Setup (Week 1)

**Estimated Time:** 4-6 hours  
**Priority:** Critical  
**Dependencies:** None  

### Task 1.1: Set Up PostgreSQL Database

**Description:** Create and configure PostgreSQL database instance.

**Steps:**
1. Choose provider (Railway or Supabase)
2. Create database instance
3. Configure connection string
4. Test connection from local machine

**Acceptance Criteria:**
- [ ] Database instance created
- [ ] Connection string working
- [ ] Can connect via psql or database client

**Files:**
- `.env` (backend) - DATABASE_URL

**Estimated Time:** 1 hour

---

### Task 1.2: Install and Configure Prisma ORM

**Description:** Set up Prisma ORM in the backend project.

**Steps:**
1. Install Prisma dependencies: `pip install prisma psycopg2-binary`
2. Initialize Prisma: `prisma init`
3. Configure `schema.prisma` with database connection
4. Define all models (User, Account, Session, Portfolio, Holding, AuditLog)

**Acceptance Criteria:**
- [ ] Prisma CLI installed
- [ ] `schema.prisma` file created
- [ ] All 6 models defined correctly
- [ ] Schema validates without errors

**Files:**
- `backend/schema.prisma`
- `backend/requirements.txt`

**Estimated Time:** 2 hours

---

### Task 1.3: Run Initial Migration

**Description:** Create and run database migrations.

**Steps:**
1. Generate migration: `prisma migrate dev --name init`
2. Review generated SQL
3. Apply migration to database
4. Verify tables created

**Acceptance Criteria:**
- [ ] Migration file created
- [ ] All tables created in database
- [ ] Indexes created correctly
- [ ] Foreign key constraints working

**Files:**
- `backend/prisma/migrations/<timestamp>_init/`

**Estimated Time:** 1 hour

---

### Task 1.4: Test Database Connection

**Description:** Write and run database connection test.

**Steps:**
1. Create test script to query database
2. Test CRUD operations on User model
3. Verify Prisma Client generation
4. Document connection status

**Acceptance Criteria:**
- [ ] Prisma Client generated successfully
- [ ] Can create/read/update/delete User records
- [ ] No connection errors
- [ ] Test script passes

**Files:**
- `backend/tests/test_db_connection.py`

**Estimated Time:** 1-2 hours

---

## Phase 2: Backend Auth Implementation (Week 2)

**Estimated Time:** 12-15 hours  
**Priority:** Critical  
**Dependencies:** Phase 1 complete  

### Task 2.1: Implement Password Hashing Utilities

**Description:** Create password hashing and verification functions.

**Steps:**
1. Install bcrypt: `pip install bcrypt passlib`
2. Create `utils/password.py` module
3. Implement `hash_password()` function
4. Implement `verify_password()` function
5. Write unit tests

**Acceptance Criteria:**
- [ ] Passwords hashed with bcrypt (12 rounds)
- [ ] Verification works correctly
- [ ] Unit tests pass
- [ ] Constant-time comparison used

**Files:**
- `backend/utils/password.py`
- `backend/tests/test_password.py`

**Estimated Time:** 2 hours

---

### Task 2.2: Implement JWT Token Utilities

**Description:** Create JWT token generation and validation functions.

**Steps:**
1. Install dependencies: `pip install python-jose[cryptography]`
2. Create `utils/jwt.py` module
3. Implement `create_access_token()` function
4. Implement `create_refresh_token()` function
5. Implement `verify_token()` function
6. Configure JWT settings (secret, algorithm, expiry)

**Acceptance Criteria:**
- [ ] Access tokens created with 15-min expiry
- [ ] Refresh tokens created with 7-day expiry
- [ ] Token verification works
- [ ] Unit tests pass

**Files:**
- `backend/utils/jwt.py`
- `backend/tests/test_jwt.py`

**Estimated Time:** 3 hours

---

### Task 2.3: Implement User Repository

**Description:** Create database repository for User operations.

**Steps:**
1. Create `repositories/user_repository.py`
2. Implement `create_user()` method
3. Implement `get_user_by_email()` method
4. Implement `get_user_by_id()` method
5. Implement `update_user()` method
6. Implement `delete_user()` method
7. Write unit tests

**Acceptance Criteria:**
- [ ] All CRUD operations implemented
- [ ] Email uniqueness enforced
- [ ] Password hashing integrated
- [ ] Unit tests pass

**Files:**
- `backend/repositories/user_repository.py`
- `backend/tests/test_user_repository.py`

**Estimated Time:** 2 hours

---

### Task 2.4: Implement Auth Endpoints

**Description:** Create authentication API endpoints.

**Steps:**
1. Create `routers/auth.py`
2. Implement `POST /auth/register` endpoint
3. Implement `POST /auth/login` endpoint
4. Implement `POST /auth/logout` endpoint
5. Implement `POST /auth/refresh` endpoint
6. Add request/response validation (Pydantic)
7. Add error handling
8. Write integration tests

**Acceptance Criteria:**
- [ ] All endpoints functional
- [ ] Input validation working
- [ ] Error responses correct
- [ ] Integration tests pass
- [ ] Swagger docs updated

**Files:**
- `backend/routers/auth.py`
- `backend/schemas/auth.py`
- `backend/tests/test_auth.py`

**Estimated Time:** 4 hours

---

### Task 2.5: Implement OAuth (Google)

**Description:** Add Google OAuth authentication.

**Steps:**
1. Register OAuth app with Google Cloud Console
2. Get client ID and secret
3. Install Authlib: `pip install authlib httpx`
4. Create `routers/oauth.py`
5. Implement Google OAuth flow
6. Handle callback
7. Link OAuth account to User or create new User
8. Write tests (mocked)

**Acceptance Criteria:**
- [ ] Google OAuth button works
- [ ] OAuth flow completes successfully
- [ ] User account created/linked
- [ ] Tokens issued after OAuth
- [ ] Tests pass (with mocks)

**Files:**
- `backend/routers/oauth.py`
- `backend/tests/test_oauth.py`

**Estimated Time:** 3 hours

---

### Task 2.6: Implement OAuth (GitHub)

**Description:** Add GitHub OAuth authentication.

**Steps:**
1. Register OAuth app with GitHub
2. Get client ID and secret
3. Extend `routers/oauth.py` with GitHub provider
4. Implement GitHub OAuth flow
5. Handle callback
6. Write tests (mocked)

**Acceptance Criteria:**
- [ ] GitHub OAuth button works
- [ ] OAuth flow completes successfully
- [ ] User account created/linked
- [ ] Tokens issued after OAuth
- [ ] Tests pass (with mocks)

**Files:**
- `backend/routers/oauth.py` (extend)

**Estimated Time:** 2 hours

---

### Task 2.7: Implement Rate Limiting

**Description:** Add rate limiting to auth endpoints.

**Steps:**
1. Install dependencies: `pip install fastapi-limiter redis`
2. Set up Redis (local or managed)
3. Initialize FastAPILimiter on startup
4. Add rate limit decorators to auth endpoints
5. Configure limits (5 login attempts/min, etc.)
6. Test rate limiting

**Acceptance Criteria:**
- [ ] Redis connection working
- [ ] Rate limiting active on auth endpoints
- [ ] 429 response after limit exceeded
- [ ] Retry-After header included

**Files:**
- `backend/main.py` (startup event)
- `backend/routers/auth.py` (rate limit decorators)

**Estimated Time:** 2 hours

---

### Task 2.8: Implement Password Reset Flow

**Description:** Add password reset functionality.

**Steps:**
1. Install SendGrid: `pip install sendgrid`
2. Create `routers/password_reset.py`
3. Implement `POST /auth/password/reset` (request reset)
4. Implement `POST /auth/password/reset/:token` (reset password)
5. Create email template
6. Generate secure reset tokens (1-hour expiry)
7. Store token hashes in database
8. Write tests

**Acceptance Criteria:**
- [ ] Reset request sends email
- [ ] Reset link works
- [ ] Password updated successfully
- [ ] Token expires after 1 hour
- [ ] All sessions invalidated after reset
- [ ] Tests pass

**Files:**
- `backend/routers/password_reset.py`
- `backend/templates/password_reset.html`
- `backend/tests/test_password_reset.py`

**Estimated Time:** 3 hours

---

### Task 2.9: Implement Auth Middleware

**Description:** Create middleware for token validation.

**Steps:**
1. Create `middleware/auth.py`
2. Implement `get_current_user()` dependency
3. Validate access token on every request
4. Extract user from token
5. Handle expired/invalid tokens
6. Add to protected routes

**Acceptance Criteria:**
- [ ] Protected routes require valid token
- [ ] 401 returned for missing token
- [ ] 401 returned for expired token
- [ ] User object available in route handlers
- [ ] Tests pass

**Files:**
- `backend/middleware/auth.py`

**Estimated Time:** 2 hours

---

### Task 2.10: Implement Audit Logging

**Description:** Add audit logging for security events.

**Steps:**
1. Create `services/audit_log.py`
2. Implement `log_audit()` function
3. Log auth events (login, logout, failed attempts)
4. Log data modification events
5. Add to relevant endpoints
6. Write tests

**Acceptance Criteria:**
- [ ] Audit logs created for all auth events
- [ ] IP address and user agent captured
- [ ] Timestamps accurate
- [ ] Can query audit logs by user
- [ ] Tests pass

**Files:**
- `backend/services/audit_log.py`
- `backend/tests/test_audit_log.py`

**Estimated Time:** 2 hours

---

## Phase 3: Frontend Auth Implementation (Week 3)

**Estimated Time:** 12-15 hours  
**Priority:** Critical  
**Dependencies:** Phase 2 complete  

### Task 3.1: Install Frontend Dependencies

**Description:** Install required npm packages.

**Steps:**
1. Install next-auth: `npm install next-auth`
2. Install jose: `npm install jose`
3. Install zod: `npm install zod`
4. Install react-hook-form: `npm install react-hook-form @hookform/resolvers`
5. Update `package.json`

**Acceptance Criteria:**
- [ ] All dependencies installed
- [ ] No version conflicts
- [ ] Build succeeds

**Files:**
- `frontend/package.json`

**Estimated Time:** 0.5 hours

---

### Task 3.2: Create Auth Context

**Description:** Implement React context for authentication state.

**Steps:**
1. Create `context/AuthContext.tsx`
2. Implement User interface
3. Implement AuthContextType interface
4. Implement AuthProvider component
5. Add login, register, logout methods
6. Add OAuth login method
7. Add password reset methods
8. Add updateUser, deleteAccount methods
9. Handle token storage (httpOnly cookies)
10. Write tests

**Acceptance Criteria:**
- [ ] AuthContext provides all required methods
- [ ] User state managed correctly
- [ ] httpOnly cookies used for refresh token
- [ ] Error handling implemented
- [ ] Tests pass

**Files:**
- `frontend/context/AuthContext.tsx`
- `frontend/context/AuthContext.test.tsx`

**Estimated Time:** 3 hours

---

### Task 3.3: Create Protected Route Component

**Description:** Implement wrapper for protected pages.

**Steps:**
1. Create `components/ProtectedRoute.tsx`
2. Check authentication status
3. Redirect to login if not authenticated
4. Show loading state while checking
5. Render children if authenticated

**Acceptance Criteria:**
- [ ] Unauthenticated users redirected to login
- [ ] Loading state shown during auth check
- [ ] Authenticated users see content
- [ ] Redirect preserves intended destination

**Files:**
- `frontend/components/ProtectedRoute.tsx`

**Estimated Time:** 1 hour

---

### Task 3.4: Build Login Page

**Description:** Create login page with email/password and OAuth.

**Steps:**
1. Create `app/login/page.tsx`
2. Create LoginForm component
3. Add email and password inputs
4. Add form validation (zod)
5. Add "Remember me" checkbox
6. Add "Forgot password?" link
7. Add OAuth buttons (Google, GitHub)
8. Add "Don't have an account? Register" link
9. Handle login submission
10. Handle errors
11. Redirect to dashboard on success

**Acceptance Criteria:**
- [ ] Form validates correctly
- [ ] Login works with email/password
- [ ] OAuth buttons functional
- [ ] Error messages displayed
- [ ] Redirects to dashboard on success
- [ ] Responsive design

**Files:**
- `frontend/app/login/page.tsx`
- `frontend/components/LoginForm.tsx`

**Estimated Time:** 3 hours

---

### Task 3.5: Build Register Page

**Description:** Create registration page.

**Steps:**
1. Create `app/register/page.tsx`
2. Create RegisterForm component
3. Add name, email, password, confirm password inputs
4. Add password strength indicator
5. Add real-time validation
6. Add terms of service checkbox
7. Add privacy policy link
8. Add OAuth buttons
9. Add "Already have an account? Login" link
10. Handle registration submission
11. Handle errors

**Acceptance Criteria:**
- [ ] Form validates correctly
- [ ] Password strength indicator works
- [ ] Registration works
- [ ] OAuth buttons functional
- [ ] Error messages displayed
- [ ] Redirects to dashboard on success
- [ ] Responsive design

**Files:**
- `frontend/app/register/page.tsx`
- `frontend/components/RegisterForm.tsx`
- `frontend/components/PasswordStrengthIndicator.tsx`

**Estimated Time:** 3 hours

---

### Task 3.6: Build Forgot Password Page

**Description:** Create password reset request page.

**Steps:**
1. Create `app/forgot-password/page.tsx`
2. Create ForgotPasswordForm component
3. Add email input
4. Add submit button
5. Handle submission
6. Show success message (generic)
7. Handle errors

**Acceptance Criteria:**
- [ ] Form validates email
- [ ] Request sends successfully
- [ ] Success message shown (generic)
- [ ] Error handling works
- [ ] Responsive design

**Files:**
- `frontend/app/forgot-password/page.tsx`
- `frontend/components/ForgotPasswordForm.tsx`

**Estimated Time:** 1.5 hours

---

### Task 3.7: Build Reset Password Page

**Description:** Create password reset page with token.

**Steps:**
1. Create `app/reset-password/page.tsx`
2. Extract token from URL query params
3. Create ResetPasswordForm component
4. Add new password and confirm password inputs
5. Add password strength indicator
6. Handle submission
7. Validate token
8. Handle errors (expired/invalid token)
9. Redirect to login on success

**Acceptance Criteria:**
- [ ] Token extracted from URL
- [ ] Form validates passwords
- [ ] Reset works with valid token
- [ ] Error shown for invalid/expired token
- [ ] Redirects to login on success
- [ ] Responsive design

**Files:**
- `frontend/app/reset-password/page.tsx`
- `frontend/components/ResetPasswordForm.tsx`

**Estimated Time:** 2 hours

---

### Task 3.8: Build Profile Page

**Description:** Create user profile page.

**Steps:**
1. Create `app/profile/page.tsx`
2. Create ProfileForm component
3. Display user info (name, email, avatar)
4. Add avatar upload/change
5. Add name edit field
6. Add change password section
7. Add delete account section (with confirmation)
8. Handle updates
9. Handle errors

**Acceptance Criteria:**
- [ ] User info displayed correctly
- [ ] Avatar upload works
- [ ] Name update works
- [ ] Password change works
- [ ] Delete account requires confirmation
- [ ] Error handling works
- [ ] Responsive design

**Files:**
- `frontend/app/profile/page.tsx`
- `frontend/components/ProfileForm.tsx`
- `frontend/components/DeleteAccountModal.tsx`

**Estimated Time:** 3 hours

---

### Task 3.9: Build Settings Page

**Description:** Create account settings page.

**Steps:**
1. Create `app/settings/page.tsx`
2. Create Settings component with sections:
   - Notification preferences
   - Privacy settings
   - Connected OAuth accounts
   - Session management
3. Implement toggles for preferences
4. List connected accounts with connect/disconnect
5. List active sessions with logout options
6. Add "Logout from all devices" button
7. Handle updates
8. Handle errors

**Acceptance Criteria:**
- [ ] All settings sections present
- [ ] Toggles work
- [ ] Connected accounts displayed
- [ ] Active sessions displayed
- [ ] Logout from session works
- [ ] Error handling works
- [ ] Responsive design

**Files:**
- `frontend/app/settings/page.tsx`
- `frontend/components/Settings/NotificationSettings.tsx`
- `frontend/components/Settings/PrivacySettings.tsx`
- `frontend/components/Settings/ConnectedAccounts.tsx`
- `frontend/components/Settings/SessionManagement.tsx`

**Estimated Time:** 3 hours

---

### Task 3.10: Update Existing Pages with Auth

**Description:** Add auth checks to existing pages.

**Steps:**
1. Wrap dashboard page with ProtectedRoute
2. Wrap portfolio page with ProtectedRoute
3. Wrap analysis page with ProtectedRoute
4. Update API calls to include credentials
5. Handle 401 responses (redirect to login)
6. Update navigation (show login/register or user menu)

**Acceptance Criteria:**
- [ ] All protected pages require auth
- [ ] Unauthenticated users redirected to login
- [ ] API calls include credentials
- [ ] 401 responses handled correctly
- [ ] Navigation shows correct state
- [ ] No console errors

**Files:**
- `frontend/app/dashboard/page.tsx`
- `frontend/app/portfolio/page.tsx`
- `frontend/components/Navigation.tsx`

**Estimated Time:** 2 hours

---

## Phase 4: Portfolio Migration (Week 4)

**Estimated Time:** 6-8 hours  
**Priority:** High  
**Dependencies:** Phase 3 complete  

### Task 4.1: Create Migration Endpoint

**Description:** Create backend endpoint for localStorage data migration.

**Steps:**
1. Create `routers/migration.py`
2. Implement `POST /protected/portfolio/migrate` endpoint
3. Accept localStorage data format
4. Validate holdings data
5. Save to database
6. Return migration result
7. Write tests

**Acceptance Criteria:**
- [ ] Endpoint accepts localStorage format
- [ ] Data validated correctly
- [ ] Holdings saved to database
- [ ] Response includes count of migrated items
- [ ] Tests pass

**Files:**
- `backend/routers/migration.py`
- `backend/tests/test_migration.py`

**Estimated Time:** 2 hours

---

### Task 4.2: Build Migration UI

**Description:** Create migration prompt modal.

**Steps:**
1. Create `components/MigrationModal.tsx`
2. Detect localStorage data on mount
3. Show modal if data exists
4. Display migration explanation
5. Add "Import" and "Skip" buttons
6. Show progress during migration
7. Show success/error message
8. Clear localStorage after success

**Acceptance Criteria:**
- [ ] Modal shows on first login (if data exists)
- [ ] Migration explanation clear
- [ ] Import button works
- [ ] Skip button works
- [ ] Progress shown during migration
- [ ] Success message shown
- [ ] localStorage cleared after success
- [ ] Error handling works

**Files:**
- `frontend/components/MigrationModal.tsx`

**Estimated Time:** 2 hours

---

### Task 4.3: Implement Data Integrity Verification

**Description:** Verify migrated data matches source.

**Steps:**
1. Compare before/after migration
2. Validate all holdings migrated
3. Check quantities and prices match
4. Log any discrepancies
5. Show verification result to user

**Acceptance Criteria:**
- [ ] All holdings verified
- [ ] Discrepancies logged
- [ ] User notified of verification result
- [ ] Rollback option if verification fails

**Files:**
- `frontend/utils/verifyMigration.ts`
- `backend/services/migration_verification.py`

**Estimated Time:** 2 hours

---

### Task 4.4: Add Mode Indicator

**Description:** Show UI indicator for local vs cloud mode.

**Steps:**
1. Create `components/ModeIndicator.tsx`
2. Detect current mode (local vs cloud)
3. Show badge in header
4. Add tooltip explaining mode
5. Allow switching between modes (if both available)

**Acceptance Criteria:**
- [ ] Mode indicator visible
- [ ] Correct mode shown
- [ ] Tooltip explains mode
- [ ] Mode switching works (if implemented)

**Files:**
- `frontend/components/ModeIndicator.tsx`

**Estimated Time:** 1-2 hours

---

## Phase 5: QA & Security Audit (Week 5)

**Estimated Time:** 6-8 hours  
**Priority:** High  
**Dependencies:** Phase 4 complete  

### Task 5.1: Write Backend Unit Tests

**Description:** Achieve >80% code coverage for backend.

**Steps:**
1. Review existing tests
2. Add missing tests for auth endpoints
3. Add tests for OAuth flow
4. Add tests for password reset
5. Add tests for protected endpoints
6. Run coverage report
7. Fix failing tests

**Acceptance Criteria:**
- [ ] Code coverage >80%
- [ ] All tests passing
- [ ] No skipped tests
- [ ] Coverage report generated

**Files:**
- `backend/tests/` (all test files)

**Estimated Time:** 3 hours

---

### Task 5.2: Write Frontend Component Tests

**Description:** Test critical frontend components.

**Steps:**
1. Test LoginForm component
2. Test RegisterForm component
3. Test AuthContext
4. Test ProtectedRoute
5. Test MigrationModal
6. Run tests

**Acceptance Criteria:**
- [ ] Critical components tested
- [ ] All tests passing
- [ ] No console errors

**Files:**
- `frontend/components/*.test.tsx`

**Estimated Time:** 2 hours

---

### Task 5.3: Security Audit

**Description:** Perform security audit (OWASP Top 10).

**Steps:**
1. Review password hashing implementation
2. Review JWT token handling
3. Review OAuth implementation
4. Test for SQL injection (should be safe with Prisma)
5. Test for XSS (React escapes by default)
6. Test for CSRF (sameSite cookies)
7. Review rate limiting
8. Review input validation
9. Document findings

**Acceptance Criteria:**
- [ ] All OWASP Top 10 checked
- [ ] No critical/high vulnerabilities
- [ ] Findings documented
- [ ] Remediation plan for any issues

**Files:**
- `docs/agent-workflow/SECURITY_AUDIT_V1.6.md`

**Estimated Time:** 3 hours

---

### Task 5.4: Performance Testing

**Description:** Test performance under load.

**Steps:**
1. Set up load testing tool (locust or k6)
2. Create test scenarios (login, portfolio load, etc.)
3. Run load test with 100 concurrent users
4. Measure response times
5. Identify bottlenecks
6. Document results

**Acceptance Criteria:**
- [ ] Load test completed
- [ ] Response times <500ms (p95)
- [ ] No errors under load
- [ ] Bottlenecks identified
- [ ] Results documented

**Files:**
- `tests/load_test.py` or `tests/load_test.js`
- `docs/agent-workflow/PERFORMANCE_REPORT_V1.6.md`

**Estimated Time:** 2 hours

---

### Task 5.5: User Acceptance Testing

**Description:** Test all user stories.

**Steps:**
1. Create UAT checklist
2. Test each user story
3. Verify acceptance criteria
4. Document results
5. Report bugs

**Acceptance Criteria:**
- [ ] All user stories tested
- [ ] Acceptance criteria verified
- [ ] Bugs documented
- [ ] Critical bugs fixed

**Files:**
- `docs/agent-workflow/UAT_CHECKLIST_V1.6.md`

**Estimated Time:** 2 hours

---

## Phase 6: Deployment (Week 6)

**Estimated Time:** 4-6 hours  
**Priority:** High  
**Dependencies:** Phase 5 complete  

### Task 6.1: Deploy Backend to Staging

**Description:** Deploy backend to staging environment.

**Steps:**
1. Set up Railway/Render project
2. Configure environment variables
3. Deploy backend
4. Run migrations on staging DB
5. Test deployment
6. Document deployment process

**Acceptance Criteria:**
- [ ] Backend deployed to staging
- [ ] Environment variables set
- [ ] Migrations run successfully
- [ ] Health check passes
- [ ] API accessible

**Files:**
- `.env.staging` (backend)

**Estimated Time:** 1.5 hours

---

### Task 6.2: Deploy Frontend to Staging

**Description:** Deploy frontend to staging environment.

**Steps:**
1. Set up Vercel/Netlify project
2. Configure environment variables
3. Deploy frontend
4. Test deployment
5. Verify auth flow on staging
6. Document deployment process

**Acceptance Criteria:**
- [ ] Frontend deployed to staging
- [ ] Environment variables set
- [ ] Auth flow works on staging
- [ ] No console errors
- [ ] Responsive design verified

**Files:**
- `.env.staging` (frontend)

**Estimated Time:** 1.5 hours

---

### Task 6.3: Final Testing on Staging

**Description:** Perform final testing on staging environment.

**Steps:**
1. Smoke test all pages
2. Test auth flow end-to-end
3. Test migration flow
4. Test OAuth login
5. Test password reset
6. Verify API responses
7. Check monitoring tools

**Acceptance Criteria:**
- [ ] All pages load correctly
- [ ] Auth flow works end-to-end
- [ ] Migration flow works
- [ ] OAuth login works
- [ ] Password reset works
- [ ] API responses correct
- [ ] Monitoring active

**Files:**
- `docs/agent-workflow/STAGING_TEST_RESULTS_V1.6.md`

**Estimated Time:** 2 hours

---

### Task 6.4: Deploy to Production

**Description:** Deploy to production environment.

**Steps:**
1. Update DNS records (if needed)
2. Enable HTTPS (Let's Encrypt)
3. Deploy backend to production
4. Deploy frontend to production
5. Run migrations on production DB
6. Verify deployment
7. Monitor for issues

**Acceptance Criteria:**
- [ ] Backend deployed to production
- [ ] Frontend deployed to production
- [ ] HTTPS enabled
- [ ] Migrations run successfully
- [ ] Health checks pass
- [ ] Monitoring active
- [ ] No critical errors

**Files:**
- `.env.production` (backend and frontend)

**Estimated Time:** 2 hours

---

### Task 6.5: Post-Deployment Monitoring

**Description:** Monitor for issues after deployment.

**Steps:**
1. Set up Sentry alerts
2. Monitor error rates
3. Monitor response times
4. Monitor database performance
5. Check user feedback
6. Document any issues
7. Create rollback plan

**Acceptance Criteria:**
- [ ] Monitoring active
- [ ] Alerts configured
- [ ] Error rates acceptable (<1%)
- [ ] Response times acceptable (<500ms)
- [ ] Rollback plan documented

**Files:**
- `docs/agent-workflow/DEPLOYMENT_RUNBOOK_V1.6.md`

**Estimated Time:** 1 hour

---

## Summary

### Task Breakdown by Phase

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 1: Database Setup | 4 | 4-6 hours |
| Phase 2: Backend Auth | 10 | 12-15 hours |
| Phase 3: Frontend Auth | 10 | 12-15 hours |
| Phase 4: Portfolio Migration | 4 | 6-8 hours |
| Phase 5: QA & Security | 5 | 6-8 hours |
| Phase 6: Deployment | 5 | 4-6 hours |
| **Total** | **38** | **40-50 hours** |

### Critical Path

1. Phase 1 (Database Setup) - Must complete first
2. Phase 2 (Backend Auth) - Required for frontend
3. Phase 3 (Frontend Auth) - Required for user testing
4. Phase 4 (Migration) - Required for existing users
5. Phase 5 (QA) - Required before deployment
6. Phase 6 (Deployment) - Final phase

### Dependencies

- Phase 2 depends on Phase 1
- Phase 3 depends on Phase 2
- Phase 4 depends on Phase 3
- Phase 5 depends on Phase 4
- Phase 6 depends on Phase 5

### Risk Mitigation

- **Data loss:** Backup localStorage before migration
- **Security vulnerabilities:** Security audit in Phase 5
- **OAuth issues:** Support email/password as fallback
- **Performance issues:** Load testing in Phase 5
- **Deployment issues:** Staging deployment first, rollback plan

---

**Ready for Implementation:** ✅  
**Assigned To:** Peter (Developer)  
**Estimated Start:** 2026-03-01  
**Estimated Completion:** 2026-04-12 (6 weeks)
