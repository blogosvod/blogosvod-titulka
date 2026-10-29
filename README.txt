BlogoSvod – technický prototyp, 10 blogů

Soubory:
- blogs.csv: testovací seznam blogů
- update.py: načtení posledního článku z RSS/Atom a sestavení index.html
- .github/workflows/update.yml: naplánované spouštění každých 6 hodin po nasazení na GitHub

Zatím není nasazeno ani živě otestováno (pracovní prostředí nemá přístup k doménám blogů).
Při neúspěchu se kanál zaznamená do status.json. Bez přístupu k síti se vytvoří prázdný přehled.

Pro první místní spuštění (na PC s Pythonem): python update.py
Pro zveřejnění: nahrát soubory do GitHub repozitáře, zapnout GitHub Pages z hlavní větve,
spustit workflow ručně a zkontrolovat status.json a index.html.
Teprve poté lze adresu publikované titulky vložit do stránky Bloggeru jako iframe.

Upozornění: prototyp je určen k ověření; před rozšířením na 450 blogů je potřeba doplnit
lepší detekci RSS, uchování posledních úspěšných výsledků a řízení zátěže.
