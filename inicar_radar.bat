@echo off
title Radar Minecraft by Gilasexe
echo ===================================================
echo     Iniciando o Radar - Gilasexe
echo ===================================================
echo.
echo [1/2] Verificando as ferramentas no sistema...
pip install streamlit requests pandas > nul 2>&1

echo [2/2] Ligando os motores...
echo O site vai abrir no seu navegador em alguns segundos!
echo.
streamlit run radar_minecraft.py