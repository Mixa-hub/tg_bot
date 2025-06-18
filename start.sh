#!/bin/bash
export PORT=8080
python3 bot.py &  # запускає бота у фоновому режимі
python3 web.py    # запускає Flask для Render
