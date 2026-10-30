
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

url = "https://rowdy.blokuje.cz/rss/"

print("TEST RSS – ROWDY")
print("Adresa:", url)

try:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "BlogoSvodFeedReader/0.1"}
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        print("HTTP status:", response.status)
        print("Konečná adresa:", response.url)
        print("Content-Type:", response.headers.get("Content-Type"))
        data = response.read(2_000_000)

    print("Staženo bajtů:", len(data))
    
    print("\n--- ZAČÁTEK ODPOVĚDI SERVERU ---")
    print(data[:1500].decode("utf-8", errors="replace"))
    print("--- KONEC UKÁZKY ---\n")
    print("Je to RSS?", data.lstrip().startswith(b"<?xml"))


    root = ET.fromstring(data)
    print("Kořen XML:", root.tag)

    items = root.findall(".//item")
    print("Počet článků:", len(items))

    if items:
        print("První článek:", items[0].findtext("title"))
        print("Datum:", items[0].findtext("pubDate"))

except Exception as e:
    print("CHYBA:", type(e).__name__, str(e))
