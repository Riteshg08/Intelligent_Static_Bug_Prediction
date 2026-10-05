# Hotspot Rules Catalog

Hotspots represent risky patterns in code. They are not necessarily "bugs" but patterns that frequently lead to defects or security vulnerabilities.

## Complexity & Maintainability
- `deep-nesting`: Deeply nested code (depth >= 4) (warning)
- `very-deep-nesting`: Very deeply nested code (depth >= 6) (high)
- `long-parameter-list`: Function has 6 or more parameters (warning)
- `long-function`: Function is unusually long (warning)
- `many-branches`: Function has too many branches (warning)

## Logic & Control Flow
- `switch-fall-through`: Missing break in switch case (warning)
- `bare-except`: Catch-all or bare except handler (warning)
- `empty-except`: Swallowed exception (empty error handler) (warning)
- `loop-off-by-one`: Possible off-by-one error in loop condition (warning)
- `assignment-in-condition`: Assignment used within a condition (warning)
- `noop-comparison`: Comparison used as a statement has no effect (warning)
- `always-true`: Condition with literal OR is always true (warning)
- `wrong-equality`: Loose equality used incorrectly (e.g. `== null`, Java string `==`) (warning)

## Language Specific
- `mutable-default`: Mutable default argument is shared across calls (Python) (high)
- `unclosed-resource`: Resource opened but not closed (high)

## Security
- `hardcoded-secret`: Hardcoded secret detected (high)
- `sql-injection`: Possible SQL injection from formatted string (high)
- `command-injection`: Command injection vulnerability (high)
- `insecure-eval`: Insecure use of eval/exec (high)
- `insecure-pickle`: Insecure deserialization with pickle (high)
- `disabled-tls`: TLS verification disabled (high)
- `weak-hash`: Weak hashing algorithm used (MD5/SHA1) (warning)
