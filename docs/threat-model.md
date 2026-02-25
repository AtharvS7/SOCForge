# SOCForge Threat Model

## Overview
This threat model addresses the SOCForge platform itself — identifying potential threats, attack surfaces, and mitigations.

## STRIDE Analysis

### Spoofing
| Threat | Mitigation |
|--------|-----------|
| Token theft/replay | JWT with expiration, HTTPS enforcement |
| Credential stuffing | Rate limiting on auth endpoints |
| Session hijacking | Secure token storage, short expiration |

### Tampering
| Threat | Mitigation |
|--------|-----------|
| Event data modification | Input validation, audit logging |
| Rule tampering | RBAC (admin-only for critical changes) |
| DB manipulation | Parameterized queries via ORM |

### Repudiation
| Threat | Mitigation |
|--------|-----------|
| Deny performing actions | Audit log middleware on all requests |
| Unauthorized changes | JWT identity tracking on changes |

### Information Disclosure
| Threat | Mitigation |
|--------|-----------|
| Sensitive data in errors | Generic error messages in production |
| Credential exposure | Bcrypt hashing, env-based secrets |
| API enumeration | Rate limiting, auth required |

### Denial of Service
| Threat | Mitigation |
|--------|-----------|
| API flooding | Rate limiting middleware |
| Large payload attacks | Request size limits, pagination |
| DB exhaustion | Connection pooling, query limits |

### Elevation of Privilege
| Threat | Mitigation |
|--------|-----------|
| Role bypass | Server-side RBAC enforcement |
| JWT manipulation | Strong secret, algorithm validation |
| SQL injection | SQLAlchemy ORM, Pydantic validation |

## Attack Surface
1. **API endpoints** — All require JWT (except auth, health)
2. **Database** — No direct external access, internal Docker network only
3. **Redis** — Password-protected, internal network only
4. **Frontend** — Client-side only, no sensitive data stored
