# RUN_STATE.md - Development Pipeline State

**Last Updated:** 2026-02-28T18:45:00Z  
**Current Phase:** 🌱 jarvis_intake (Bootstrap)  
**Owner:** Jarvis (Coordinator)  
**Project:** KlyrSignals

---

## Active Pipeline

| Phase | Agent | Session Key | Status | Started | Completed |
|-------|-------|-------------|--------|---------|-----------|
| **jarvis_intake** | Jarvis | — | 🔄 ACTIVE | 18:45 | — |
| **pepper_reqs** | Pepper | — | ⏳ QUEUED | — | — |
| **tony_design** | Tony | — | ⏳ QUEUED | — | — |
| **peter_build** | Peter | — | ⏳ QUEUED | — | — |
| **heimdall_test** | Heimdall | — | ⏳ QUEUED | — | — |
| **pepper_closeout** | Pepper | — | ⏳ QUEUED | — | — |

---

## Project Reset Summary

**Date:** 2026-02-28  
**Reason:** Re-bootstrap with correct requirements (hybrid architecture)

### Previous State (Deleted)
- **Stack:** Python-only (FastAPI)
- **Commits:** 3 (initial commit + docs updates)
- **Status:** Incomplete, wrong architecture

### New State (Current)
- **Stack:** Hybrid (Next.js frontend + Python backend)
- **Commits:** 0 (fresh start)
- **Status:** Bootstrap in progress

---

## Project Overview

**Name:** KlyrSignals  
**Description:** AI-powered financial portfolio analyst for blind spot detection and over-exposure warnings  
**Architecture:** Hybrid (Next.js 16 + Python FastAPI)  
**Target Users:** Retail investors, financial advisors  

### Key Features (v1.0)
1. Portfolio import (CSV, manual entry)
2. Asset allocation visualization
3. Over-exposure detection
4. AI-powered blind spot detection
5. Risk scoring (0-100)
6. Rebalancing recommendations
7. Real-time monitoring
8. Performance tracking

### Tech Stack
- **Frontend:** Next.js 16, TypeScript, Tailwind CSS, Recharts
- **Backend:** Python 3.12, FastAPI, pandas, numpy, scikit-learn
- **Market Data:** Yahoo Finance, Alpha Vantage
- **Deployment:** Vercel (frontend), Railway (backend)
- **Database:** PostgreSQL (optional for v1.0)

---

## Next Action

**Spawn Pepper (Requirements)** to:
1. Review and refine REQ.md (already drafted)
2. Clarify open questions (market data provider, auth timing, database needs)
3. Finalize acceptance criteria
4. Update RUN_STATE.md → pepper_reqs DONE
5. Handoff to Tony (Architecture)

---

## Notes

- Requirements document (REQ.md) pre-drafted during bootstrap
- Hybrid architecture confirmed with user (2026-02-28 18:41 UTC)
- Old Python-only project deleted and replaced
- Ready to start full pipeline

---

## 🚨 JARVIS: Spawn Pepper for requirements refinement

**Task:** Review REQ.md, clarify open questions, finalize for Tony handoff
