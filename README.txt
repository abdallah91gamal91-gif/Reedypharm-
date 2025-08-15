
EL REEDY PHARMACY (Kivy, EN/AR, Light/Dark)
===========================================
- main.py        : App code
- medicines.csv  : 520+ medicines (sample prices in EGP)
- logo.png       : Red/white logo
- buildozer.spec : For building APK with Buildozer

Run on Android (Pydroid 3):
1) Copy all files to one folder on your phone.
2) Open Pydroid 3 → open "main.py".
3) Press ▶ Run. The app loads the CSV and the logo automatically.
4) Use "Reload CSV" after editing "medicines.csv".
5) Receipts (TXT/CSV) are saved in the same folder.

Build APK (Linux/Termux/Cloud):
- Zip this folder and use Buildozer:
    pip install buildozer
    buildozer -v android debug
- The APK will be in "bin/".

Notes:
- Prices are sample values. Replace with official/latest when needed.
- Switch language and theme from the header buttons.
- Add/Delete items from "Add Item" and "Manage DB".

Generated: 2025-08-15T21:48:37
