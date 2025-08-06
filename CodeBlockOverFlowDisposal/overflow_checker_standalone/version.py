# -*- coding: utf-8 -*-
'''
Version information file
Auto-generated at build time - do not edit
'''

VERSION = '1.0.0'
BUILD_DATE = '2025-07-30'
BUILD_TIME = '22:52:21'
BUILD_TYPE = 'Release'

# Git info (if available)
try:
    import subprocess
    COMMIT_HASH = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], 
                                        stderr=subprocess.DEVNULL).decode().strip()
except:
    COMMIT_HASH = 'unknown'

# Application info
APP_NAME = 'Overflow Checker'
APP_NAME_EN = 'Overflow Checker'
DESCRIPTION = 'PDF Code Block Overflow Detection Tool'
AUTHOR = 'Claude Code Assistant'
COPYRIGHT = 'ﾂｩ 2025 Claude Code Assistant'

def get_version_string():
    '''Get version string'''
    return f'{APP_NAME} v{VERSION} ({BUILD_DATE})'

def get_full_version_info():
    '''Get complete version info'''
    return {
        'version': VERSION,
        'build_date': BUILD_DATE,
        'build_time': BUILD_TIME,
        'build_type': BUILD_TYPE,
        'commit_hash': COMMIT_HASH,
        'app_name': APP_NAME,
        'app_name_en': APP_NAME_EN,
        'description': DESCRIPTION,
        'author': AUTHOR,
        'copyright': COPYRIGHT
    }
