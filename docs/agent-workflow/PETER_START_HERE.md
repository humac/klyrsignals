# KlyrSignals v1.6 - Quick Start Guide for Peter

**Created:** 2026-03-01  
**Author:** Tony (Lead Architect)  
**For:** Peter (Developer)  

---

## 🎯 Your Mission

Implement full authentication, authorization, database, and user management for KlyrSignals v1.6.

**Current State (v1.5):**
- Client-side only (localStorage)
- No user accounts
- No database
- No authentication

**Target State (v1.6):**
- PostgreSQL database
- User accounts with email/password + OAuth
- JWT-based authentication
- Cloud-synced portfolios
- GDPR compliance

---

## 📚 Documentation

**Read these in order:**

1. **ARCH_V1.6.md** (55KB) - Complete architecture specification
   - Database schema
   - API design
   - Security architecture
   - Frontend architecture

2. **REQ_V1.6.md** (22KB) - Requirements document
   - User stories
   - Functional requirements
   - Non-functional requirements
   - Acceptance criteria

3. **TASKS_V1.6.md** (27KB) - **YOUR TASK LIST**
   - 38 tasks across 6 phases
   - Estimated 40-50 hours
   - Acceptance criteria for each task

4. **DECISIONS.md** - Architecture decisions
   - DEC-007: PostgreSQL + Prisma
   - DEC-008: JWT Authentication
   - DEC-009: bcrypt Password Hashing
   - DEC-010: GDPR Compliance

---

## 📋 Implementation Phases

### Phase 1: Database Setup (4-6 hours)
- Set up PostgreSQL (Railway or Supabase)
- Install Prisma ORM
- Define schema (User, Account, Session, Portfolio, Holding, AuditLog)
- Run migrations
- Test connection

**Deliverable:** Database with all tables created

---

### Phase 2: Backend Auth (12-15 hours)
- Password hashing (bcrypt)
- JWT token utilities
- User repository
- Auth endpoints (register, login, logout, refresh)
- OAuth (Google, GitHub)
- Rate limiting
- Password reset flow
- Auth middleware
- Audit logging

**Deliverable:** Working authentication API

---

### Phase 3: Frontend Auth (12-15 hours)
- AuthContext
- ProtectedRoute component
- Login page
- Register page
- Forgot password page
- Reset password page
- Profile page
- Settings page
- Update existing pages with auth

**Deliverable:** Working auth UI

---

### Phase 4: Portfolio Migration (6-8 hours)
- Migration endpoint
- Migration UI modal
- Data integrity verification
- Mode indicator (local vs cloud)

**Deliverable:** Users can migrate localStorage data to database

---

### Phase 5: QA & Security (6-8 hours)
- Backend unit tests (>80% coverage)
- Frontend component tests
- Security audit (OWASP Top 10)
- Performance testing
- User acceptance testing

**Deliverable:** Production-ready code

---

### Phase 6: Deployment (4-6 hours)
- Deploy to staging
- Deploy frontend to staging
- Final testing
- Deploy to production
- Post-deployment monitoring

**Deliverable:** Live in production

---

## 🛠️ Tech Stack

### Backend
- Python 3.12 + FastAPI
- PostgreSQL 15 (managed)
- Prisma ORM
- bcrypt (password hashing)
- python-jose (JWT)
- Authlib (OAuth)
- SendGrid (email)
- Redis (rate limiting)

### Frontend
- Next.js 14 + TypeScript
- next-auth
- react-hook-form
- zod (validation)
- Tailwind CSS

### Infrastructure
- Railway/Supabase (PostgreSQL)
- Railway/Render (backend)
- Vercel/Netlify (frontend)
- SendGrid (email)

---

## 🔐 Security Requirements

**MUST IMPLEMENT:**
- ✅ bcrypt password hashing (12 rounds)
- ✅ JWT tokens (HS256, 15min access, 7day refresh)
- ✅ httpOnly cookies for refresh tokens
- ✅ Rate limiting (5 login attempts/min)
- ✅ CORS (whitelist origins)
- ✅ Input validation (Pydantic + Zod)
- ✅ HTTPS in production
- ✅ Audit logging

**DO NOT:**
- ❌ Store plain text passwords
- ❌ Store tokens in localStorage
- ❌ Use `allow_origins=["*"]` in production
- ❌ Skip input validation
- ❌ Log sensitive data

---

## 📊 Database Schema

**6 Tables:**
1. **User** - Core authentication entity
2. **Account** - OAuth provider links
3. **Session** - Refresh token management
4. **Portfolio** - User's portfolio
5. **Holding** - Individual investments
6. **AuditLog** - Security event tracking

See `ARCH_V1.6.md` Section 2.2 for complete Prisma schema.

---

## 🌐 API Endpoints

### Auth Endpoints
- `POST /api/v1/auth/register` - Create account
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/oauth/:provider` - OAuth login
- `POST /api/v1/auth/password/reset` - Request reset
- `POST /api/v1/auth/password/reset/:token` - Reset password

### Protected Endpoints
- `GET /api/v1/protected/portfolio` - Get portfolio
- `POST /api/v1/protected/portfolio/import` - Import holdings
- `GET /api/v1/protected/analysis` - Get analysis

### User Management
- `GET /api/v1/users/me` - Get profile
- `PATCH /api/v1/users/me` - Update profile
- `DELETE /api/v1/users/me` - Delete account

See `ARCH_V1.6.md` Section 3 for complete API spec.

---

## ✅ Acceptance Criteria

**Phase 1 Complete When:**
- [ ] PostgreSQL database created
- [ ] All 6 tables created with correct schema
- [ ] Can perform CRUD operations via Prisma

**Phase 2 Complete When:**
- [ ] Users can register with email/password
- [ ] Users can login with email/password
- [ ] OAuth login works (Google, GitHub)
- [ ] JWT tokens issued and validated
- [ ] Rate limiting active
- [ ] Unit tests passing (>80% coverage)

**Phase 3 Complete When:**
- [ ] All auth pages functional (login, register, reset, profile, settings)
- [ ] Protected routes redirect to login
- [ ] No console errors

**Phase 4 Complete When:**
- [ ] Migration prompt displays on first login
- [ ] Data migrates successfully
- [ ] localStorage cleared after migration

**Phase 5 Complete When:**
- [ ] No critical/high security vulnerabilities
- [ ] All user stories verified
- [ ] Performance acceptable (<500ms response time)

**Phase 6 Complete When:**
- [ ] Production deployment successful
- [ ] Monitoring active
- [ ] Users can access app

---

## 🚀 Getting Started

1. **Read ARCH_V1.6.md** - Understand the architecture
2. **Read TASKS_V1.6.md** - Review your task list
3. **Start with Phase 1, Task 1.1** - Set up PostgreSQL
4. **Update RUN_STATE.md** - Mark tasks as complete
5. **Ask for help if stuck** - Jarvis will coordinate

---

## 📞 Support

**Architecture Questions:** Tony designed this - check ARCH_V1.6.md  
**Requirements Questions:** Check REQ_V1.6.md  
**Task Details:** Check TASKS_V1.6.md  
**Decisions:** Check DECISIONS.md (DEC-007 to DEC-010)

**Escalation:** If blocked, Jarvis will coordinate with Tony for clarification.

---

## ⏱️ Timeline

**Estimated:** 40-50 hours  
**Phases:** 6  
**Tasks:** 38  
**Start Date:** 2026-03-01  
**Target Completion:** 2026-04-12 (6 weeks)

---

## 🎯 Success Metrics

- **Code Coverage:** >80%
- **API Response Time:** <500ms (p95)
- **Error Rate:** <1%
- **Security:** No critical/high vulnerabilities
- **User Satisfaction:** >4/5

---

**Good luck, Peter! You've got this! 🚀**

All the architecture is laid out - just follow the tasks in order and you'll build something amazing.
