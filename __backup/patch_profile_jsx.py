with open("frontend/app/profile/page.tsx", "r") as f:
    text = f.read()

text = text.replace("         </div>\n      </div>\n\n      <div className=", "      </div>\n\n      <div className=")

with open("frontend/app/profile/page.tsx", "w") as f:
    f.write(text)
