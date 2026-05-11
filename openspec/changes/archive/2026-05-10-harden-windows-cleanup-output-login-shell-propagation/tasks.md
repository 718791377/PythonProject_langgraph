## 1. Implementation

- [x] Set a scoped cleanup shim directory environment bridge in the wrapped launcher.
- [x] Teach the managed PowerShell profile block to re-prepend the shim directory for login shells when the bridge is present.
- [x] Preserve taskkill EXE/CMD shim fallback behavior and restore the bridge after launcher exit.

## 2. Validation

- [x] Update checker markers for the login-shell profile bridge.
- [x] Add tests for generated profile behavior after PATH reset.
- [x] Run focused checker and installer tests.
- [x] Run OpenSpec guard before publication.