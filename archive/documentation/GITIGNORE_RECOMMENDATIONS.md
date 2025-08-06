# Git Configuration Recommendations for Archive

## .gitignore Considerations

The `archive/` directory should be **tracked in Git** to ensure recovery capability. 

### Recommended .gitignore entries:

```gitignore
# DO NOT ignore the archive directory - it's needed for recovery
# archive/  <-- DO NOT ADD THIS LINE

# But you may want to ignore temporary recovery files:
main_legacy.py
main_test_gui.py  
main_no_google_recovered.py
*_recovered.py
```

## Git Commit Recommendations

When committing the archival:

```bash
git add archive/
git add LEGACY_ARCHIVAL_SUMMARY.md
git commit -m "Archive legacy entry points and GUI components

- Archive 4 legacy main_*.py entry points
- Archive 8 legacy GUI components  
- Archive 3 migration tools
- Add comprehensive recovery documentation
- Preserve current main.py functionality

Legacy code is fully recoverable via archive/documentation/RECOVERY_INSTRUCTIONS.md"
```

## Branch Strategy

Consider creating a recovery branch if you need to test legacy components:

```bash
# Create recovery branch
git checkout -b legacy-recovery-test

# Restore some legacy files for testing
cp archive/legacy_entry_points/main_clean.py ./main_test.py

# Test and then delete when done
git checkout main
git branch -D legacy-recovery-test
```

This keeps the main branch clean while allowing safe legacy testing.