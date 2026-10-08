with open("frontend/app/strategies/page.tsx", "r") as f:
    text = f.read()

text = text.replace("Performance Tracking\n        </button>", "Performance (Coming Soon)\n        </button>")
text = text.replace("Strategy Performance Tracking", "Strategy Performance (Coming Soon)")
text = text.replace("Awaiting completed manual trades...", "Metrics processing pipeline under construction. (Coming Soon)")

with open("frontend/app/strategies/page.tsx", "w") as f:
    f.write(text)
