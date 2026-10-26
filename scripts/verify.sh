#!/bin/bash
echo "=== 1. Cek Syntax (py_compile) ==="
find app -name "*.py" -exec venv/bin/python -m py_compile {} \;
if [ $? -ne 0 ]; then echo "❌ Syntax Error!"; exit 1; fi
echo "✅ Syntax OK"

echo "=== 2. Cek Import & Startup ==="
venv/bin/python -c "import app.main; print('✅ Import OK')"
if [ $? -ne 0 ]; then echo "❌ Import Error!"; exit 1; fi

echo "=== SEMUA VERIFIKASI LOLOS ==="
