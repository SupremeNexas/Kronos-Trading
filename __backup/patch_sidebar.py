import re

with open("frontend/components/Sidebar.tsx", "r") as f:
    content = f.read()

# I will add the icon to the imports
if "Zap," not in content:
    content = content.replace("ShieldCheck,", "ShieldCheck,\n  Zap,")

# Add the new NavItem to navItems
nav_items_split = content.split("const navItems: NavItem[] = [")
new_item = """
  { label: "Strategies", href: "/strategies", icon: Zap, badge: "New" },
"""
content = nav_items_split[0] + "const navItems: NavItem[] = [" + new_item + nav_items_split[1]

with open("frontend/components/Sidebar.tsx", "w") as f:
    f.write(content)
print("Sidebar patched.")
