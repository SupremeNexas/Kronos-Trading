with open("frontend/components/Header.tsx", "r") as f:
    text = f.read()

text = text.replace('{ label: "TRADES", href: "/trades" },', 
                    '{ label: "SCANNER", href: "/scanner" },\n  { label: "TRADES", href: "/trades" },')

with open("frontend/components/Header.tsx", "w") as f:
    f.write(text)

