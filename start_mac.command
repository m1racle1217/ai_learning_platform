#!/bin/bash
set -u
set -o pipefail
cd "$(dirname "$0")" || exit 1

LOG_FILE="/tmp/ai_learning_platform.log"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "AI Learning Platform"
echo "Project: $(pwd)"
echo "Log: ${LOG_FILE}"
echo

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "没有找到 python3，所以本地学习平台还不能启动。"
  echo
  echo "请先安装 Python 3.11+，任选一种方式："
  echo "1. 官网安装包：https://www.python.org/downloads/macos/"
  echo "2. 如果已经安装 Homebrew：brew install python@3.11"
  echo
  echo "安装后重新打开这个文件，或者在终端执行："
  echo "cd \"$(pwd)\""
  echo "python3 --version"
  echo "python3 -m pip install --upgrade pip"
  echo "python3 -m pip install -e \".[dev]\""
  echo "./start_mac.command"
  echo
  read -r -p "按回车关闭窗口..."
  exit 1
fi

"$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import fastapi, uvicorn, sqlalchemy, openpyxl
PY
if [ $? -ne 0 ]; then
  echo "检测到 Python 已安装，但项目依赖还没安装。正在自动安装依赖..."
  echo "这一步第一次运行可能需要几分钟。"
  echo
  : > "$LOG_FILE"
  "$PYTHON_BIN" -m pip install --upgrade pip 2>&1 | tee -a "$LOG_FILE"
  PIP_UPGRADE_STATUS=${PIPESTATUS[0]}
  "$PYTHON_BIN" -m pip install -e ".[dev]" 2>&1 | tee -a "$LOG_FILE"
  PIP_INSTALL_STATUS=${PIPESTATUS[0]}
  if [ "$PIP_UPGRADE_STATUS" -ne 0 ] || [ "$PIP_INSTALL_STATUS" -ne 0 ]; then
    echo
    echo "依赖安装失败。请检查网络，或手动执行："
    if [ -f "$LOG_FILE" ] && grep -q "CERTIFICATE_VERIFY_FAILED" "$LOG_FILE"; then
      echo
      echo "检测到 macOS Python 证书错误：CERTIFICATE_VERIFY_FAILED"
      echo "优先修复方式："
      echo "1. 打开 Finder"
      echo "2. 进入 /Applications/Python 3.12/"
      echo "3. 双击 Install Certificates.command"
      echo "4. 重新运行 ./start_mac.command"
      echo
      echo "如果暂时只想绕过证书问题，也可以手动执行："
      echo "python3 -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --upgrade pip"
      echo "python3 -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -e \".[dev]\""
      echo
    fi
    echo "cd \"$(pwd)\""
    echo "python3 -m pip install --upgrade pip"
    echo "python3 -m pip install -e \".[dev]\""
    echo
    read -r -p "按回车关闭窗口..."
    exit 1
  fi
  echo
fi

APP_URL="$($PYTHON_BIN scripts/start_app.py --print-url 2>"$LOG_FILE")"
if [ -z "$APP_URL" ]; then
  echo "启动前检查失败，错误日志如下："
  tail -n 80 "$LOG_FILE"
  echo
  read -r -p "按回车关闭窗口..."
  exit 1
fi

echo "正在启动：${APP_URL}"
"$PYTHON_BIN" scripts/start_app.py >"$LOG_FILE" 2>&1 &
APP_PID=$!

sleep 2
if ! kill -0 "$APP_PID" >/dev/null 2>&1; then
  echo "服务启动失败，错误日志如下："
  tail -n 120 "$LOG_FILE"
  echo
  read -r -p "按回车关闭窗口..."
  exit 1
fi

open "$APP_URL"
echo "已打开浏览器。关闭网页后，本地服务会自动退出。"
echo "如果浏览器没有打开，请手动访问：${APP_URL}"
echo
read -r -p "按回车关闭这个启动窗口..."
