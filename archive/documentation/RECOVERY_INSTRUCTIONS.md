# Recovery Instructions for Legacy TechZip Code
**Date**: 2025-08-06  
**Project**: Technical Fountain Series Support Tool  
**Archive Version**: 1.0

## Overview

This document provides step-by-step instructions for recovering legacy code components if needed. The current system uses `python .\main.py` as the primary entry point with Qt6-based GUI components.

## Recovery Scenarios

### Scenario 1: Emergency Full System Recovery

If the current `main.py` system fails completely:

#### Option A: Clean Qt6 Recovery (Recommended)
```bash
# Navigate to project root
cd /mnt/c/Users/tky99/dev/technical-fountain-series-support-tool/

# Copy the most compatible legacy entry point
cp archive/legacy_entry_points/main_clean.py ./main_legacy.py

# Restore associated GUI component
cp archive/legacy_gui/main_window_qt6.py ./gui/

# Test the legacy system
python main_legacy.py
```

#### Option B: No-Google Recovery
If Google Sheets integration is causing issues:
```bash
# Copy the no-Google version
cp archive/legacy_entry_points/main_no_google.py ./main_no_google_recovered.py

# Restore no-Google GUI
cp archive/legacy_gui/main_window_no_google.py ./gui/

# Note: This version may have encoding issues (mojibake)
python main_no_google_recovered.py
```

### Scenario 2: Specific Feature Recovery

#### Recover Tkinter Test Interface
If you need the old Tkinter-based test interface:

```bash
# Restore Tkinter GUI
cp archive/legacy_gui/integrated_test_gui.py ./gui/

# Restore GUI launcher entry point
cp archive/legacy_entry_points/main_gui.py ./main_test_gui.py

# Run Tkinter interface
python main_test_gui.py
```

#### Recover Legacy Qt6 Components
If current Qt6 components are corrupted:

```bash
# Restore legacy Qt6 components
cp archive/legacy_components/input_panel_qt6.py ./gui/components/
cp archive/legacy_components/log_panel_qt6.py ./gui/components/
cp archive/legacy_components/progress_bar_qt6.py ./gui/components/

# Update imports in main GUI to use _qt6 versions
# Edit gui/main_window.py to import from *_qt6 modules
```

### Scenario 3: Migration Tool Recovery

If you need to run Qt5-to-Qt6 migration again:

```bash
# Restore migration tools
cp archive/migration_tools/*.ps1 ./

# Available tools:
# - migrate_to_qt6_properly.ps1
# - convert_to_qt6.ps1  
# - restore_and_migrate_qt6.ps1

# Run migration (PowerShell)
./migrate_to_qt6_properly.ps1
```

## Recovery Verification Steps

### After Any Recovery:

1. **Verify Python Environment**:
   ```bash
   python -m pip install -r requirements.txt
   ```

2. **Test GUI Startup**:
   ```bash
   python [recovered_main_file].py
   ```

3. **Check Import Dependencies**:
   ```bash
   python -c "import gui.main_window; print('GUI imports OK')"
   ```

4. **Verify Core Functions**:
   - Test file selection
   - Test log panel
   - Test progress bar
   - Test basic workflow

## Dependency Resolution

### Import Error Resolution

#### If you get "ModuleNotFoundError":

1. **Missing GUI Components**:
   ```bash
   # Check what's missing
   python -c "from gui.main_window import MainWindow"
   
   # Common fixes:
   cp archive/legacy_gui/main_window_qt6.py ./gui/
   cp archive/legacy_components/* ./gui/components/
   ```

2. **Missing Core Modules**:
   ```bash
   # Core modules are preserved and should not need recovery
   # If missing, check backup directories:
   ls backup*/core/
   ```

### Version Compatibility Issues

#### Qt6 vs Qt5 Import Errors:
```bash
# If you see PyQt5 references after recovery:
# Run migration script on recovered files:
./archive/migration_tools/convert_to_qt6.ps1
```

#### Python Version Issues:
```bash
# Check Python version
python --version

# TechZip requires Python 3.8+
# If using older Python, update or use backup environment
```

## Recovery File Manifest

### Archived Entry Points
Located in `archive/legacy_entry_points/`:
- `main_gui.py` - Tkinter-based test interface launcher
- `main_clean.py` - Clean Qt6 version (BEST RECOVERY OPTION)
- `main_no_google.py` - No Google Sheets integration (has encoding issues)
- `main_qt6.py` - Basic Qt6 version

### Archived GUI Components  
Located in `archive/legacy_gui/`:
- `main_window_qt6.py` - Legacy Qt6 main window
- `main_window_no_google.py` - No Google integration window
- `main_window_refactored.py` - Refactored version (unused)
- `integrated_test_gui.py` - Tkinter test interface
- `config_integration_test.py` - Configuration test GUI

### Archived Component Libraries
Located in `archive/legacy_components/`:
- `input_panel_qt6.py` - Legacy Qt6 input panel
- `log_panel_qt6.py` - Legacy Qt6 log panel  
- `progress_bar_qt6.py` - Legacy Qt6 progress bar

### Migration Tools
Located in `archive/migration_tools/`:
- `migrate_to_qt6_properly.ps1` - Main migration script
- `convert_to_qt6.ps1` - Import conversion script
- `restore_and_migrate_qt6.ps1` - Restore and migrate combo

## Emergency Contacts & Resources

### Backup Locations
If archive is corrupted, check these backup directories:
- `backup/` - General backup
- `backup_20250725_195532/` - Timestamped backup
- `backup_qt5_20250725_193233/` - Qt5 version backup
- `backup_before_restore_20250725_195926/` - Pre-restore backup

### Git History Recovery
```bash
# If you need to recover from Git history:
git log --oneline --grep="Qt6"
git show [commit_hash]
git checkout [commit_hash] -- [file_path]
```

### Requirements Recovery
If requirements.txt is corrupted:
```bash
# Current requirements (Qt6-based):
pip install PyQt6==6.7.0 requests==2.31.0 python-dotenv==1.0.0

# Check backup requirements:
cat backup*/requirements.txt
```

## Troubleshooting

### Common Issues After Recovery

1. **"No module named PyQt6"**:
   ```bash
   pip install PyQt6==6.7.0
   ```

2. **"Application failed to start"**:
   - Check if you recovered the right main window file
   - Verify all GUI components are present
   - Check console for specific error messages

3. **Japanese text shows as garbled (mojibake)**:
   - This is a known issue with `main_no_google.py`
   - Use `main_clean.py` instead if possible
   - Or edit the file to fix encoding declarations

4. **"DI Container initialization error"**:
   - This is expected for legacy versions
   - The error is handled gracefully and doesn't break functionality

### Performance Issues After Recovery

Legacy versions may be slower than the current system due to:
- Older GUI implementation patterns
- Missing optimization features
- Different event handling approaches

Consider these temporary solutions until current system is restored.

## Return to Current System

### When Current System is Fixed

1. **Remove recovered files**:
   ```bash
   rm main_legacy.py main_test_gui.py main_no_google_recovered.py
   ```

2. **Ensure current system works**:
   ```bash
   python main.py
   ```

3. **Clean up any temporary GUI files**:
   ```bash
   # Only if you copied legacy GUI files to current locations
   git checkout -- gui/
   ```

## Notes

- Legacy versions lack the latest features like enhanced startup logging
- Recovery is intended as temporary measure only  
- Current `main.py` system is the supported version
- Keep archive structure intact for future recovery needs

## Version History

- v1.0 (2025-08-06): Initial recovery instructions for Qt6 migration archive