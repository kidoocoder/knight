import sys
print('Python path:')
print('\n'.join(sys.path))

print('\nTrying to import PyTgCalls:')
try:
    from py_tgcalls import PyTgCalls
    print('Successfully imported PyTgCalls')
except ImportError as e:
    print('ImportError:', e)
    try:
        import py_tgcalls
        print('Module exists but wrong import path')
    except ImportError:
        print('Module does not exist')

print('\nChecking ntgcalls package:')
try:
    import ntgcalls
    print('Successfully imported ntgcalls:', ntgcalls.__version__ if hasattr(ntgcalls, '__version__') else 'Unknown version')
except ImportError as e:
    print('ImportError:', e)

print('\nChecking installed packages:')
import subprocess
result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
print(result.stdout)