"""Hand-picked color palettes. primary / secondary / text (dark) / bg (light), plus mood tags used by the idea maker."""
import colorsys

P = lambda id, name, primary, secondary, text, bg, tags: {"id": id, "name": name, "primary": primary, "secondary": secondary, "text": text, "bg": bg, "tags": tags.split()}

PALETTES = [
    P("tomato", "Tomato & Basil", "#D62828", "#2E7D32", "#2B1B17", "#FFF8EE", "food warm bright"),
    P("terracotta", "Terracotta", "#C8553D", "#F2A65A", "#2D2A32", "#FFF6EC", "food warm earthy"),
    P("olive", "Olive Grove", "#6B8F3A", "#E9C46A", "#2F3A1C", "#FBF8EC", "food earthy fresh"),
    P("espresso", "Espresso", "#4A2C2A", "#C69C6D", "#2A1A18", "#FBF4EA", "food warm luxury earthy"),
    P("saffron", "Saffron", "#F4A300", "#B5271D", "#231F20", "#FFFAEB", "food warm bright playful"),
    P("berry", "Berry Bistro", "#8E1B4B", "#F2B5C4", "#2A1020", "#FFF4F7", "food warm luxury beauty"),
    P("electric", "Electric Blue", "#1F6FEB", "#12D1B4", "#0B1F3A", "#F4F8FF", "tech cool bright"),
    P("violet", "Midnight Violet", "#5B3CC4", "#FF6B9A", "#1A1033", "#F7F4FF", "tech cool playful"),
    P("mint", "Mint Tech", "#0FA38F", "#1F2A44", "#13202F", "#F7F1FB", "tech fresh cool"),
    P("lime", "Graphite & Lime", "#222B38", "#8FD21E", "#10161E", "#F5F7F4", "tech bright minimal"),
    P("ocean", "Ocean", "#0A6EBD", "#7ED6E8", "#0A2540", "#F1F9FD", "cool fresh tech"),
    P("gold", "Black & Gold", "#111111", "#C9A227", "#111111", "#FBF8F0", "luxury dark minimal"),
    P("navygold", "Navy & Gold", "#12263F", "#D4AF37", "#0B1829", "#FAF8F2", "luxury dark cool"),
    P("burgundy", "Burgundy", "#5B1A2B", "#D9B99B", "#2A0D14", "#FBF5F0", "luxury warm dark"),
    P("emerald", "Emerald & Gold", "#0B4F3C", "#C9A227", "#08281F", "#F6F8F2", "luxury earthy dark"),
    P("rose", "Rose Gold", "#B76E79", "#4A2C35", "#3A2228", "#FFF5F5", "beauty luxury warm"),
    P("forest", "Forest", "#1E5B3A", "#9BC53D", "#10281B", "#F4F9F1", "nature fresh earthy"),
    P("teal", "Fresh Teal", "#00808A", "#F4A261", "#0A2E33", "#F5EFFA", "fresh nature cool"),
    P("sage", "Sage", "#826B94", "#463A4F", "#2B2331", "#F4F7F2", "nature earthy minimal"),
    P("medical", "Clean Care", "#0E7C86", "#3FB6C4", "#0B2F33", "#F0FAFB", "health cool fresh"),
    P("sunny", "Sunny", "#FF7A00", "#FFC400", "#1B1B1B", "#FFFAF0", "playful bright warm"),
    P("candy", "Candy", "#FF4F8B", "#6C5CE7", "#2B1740", "#FFF5FA", "playful bright beauty"),
    P("pop", "Primary Pop", "#2D6CDF", "#FFC400", "#101B33", "#F6F9FF", "playful bright"),
    P("limepop", "Lime Pop", "#4CAF1A", "#1A8A5A", "#10331E", "#F5FBEF", "playful fresh nature"),
    P("ink", "Ink", "#111827", "#6B7280", "#111827", "#F9FAFB", "minimal dark"),
    P("slate", "Slate", "#334155", "#94A3B8", "#1E293B", "#F8FAFC", "minimal cool"),
    P("warmgray", "Warm Stone", "#3F3A36", "#B8A99A", "#2A2522", "#FAF7F3", "minimal warm earthy"),
    P("safety", "Safety Orange", "#F26B1D", "#2B2D31", "#1F2024", "#FFF7F0", "bold warm"),
    P("steel", "Steel & Amber", "#2B4C7E", "#F2A900", "#13233D", "#F5F8FC", "bold cool"),
    P("blush", "Blush", "#D8869B", "#7A4B5C", "#4B2A35", "#FFF7F8", "beauty warm"),
    P("lavender", "Lavender", "#7D6BB8", "#C9B6E8", "#2B2347", "#F8F5FF", "beauty cool playful"),
    P("digonto", "Digonto Green", "#C2395C", "#E0662A", "#0F3D2E", "#F4FAF7", "fresh nature bright"),
    P("coral", "Coral Reef", "#FF6B5E", "#1B998B", "#1D2B3A", "#FFF7F5", "playful fresh warm"),
    P("sunset", "Sunset", "#E4572E", "#F3A712", "#2B1B2E", "#FFF6EA", "warm bright playful"),
    P("peach", "Peach Fizz", "#FF8C69", "#FFD1A9", "#4A2A26", "#FFF8F3", "warm beauty playful"),
    P("plum", "Plum Wine", "#6A1B4D", "#E3A6C8", "#2A0F20", "#FCF5F9", "luxury beauty dark"),
    P("copper", "Copper", "#B4532A", "#2E4057", "#231A15", "#FBF5EF", "warm earthy luxury"),
    P("denim", "Denim", "#27476E", "#E8C07D", "#14253A", "#F6F8FB", "cool bold earthy"),
    P("matcha", "Matcha", "#6F9A4B", "#F2E8CF", "#233018", "#FBFCF6", "nature fresh earthy"),
    P("pine", "Pine & Cream", "#14452F", "#F2E6C9", "#0B2218", "#FBF8EE", "nature luxury earthy"),
    P("lagoon", "Lagoon", "#007F8C", "#FFB86B", "#05343A", "#F2FBFB", "fresh cool playful"),
    P("neon", "Neon Night", "#7C3AED", "#22D3EE", "#0F0A24", "#F6F3FF", "tech bright playful"),
    P("cyber", "Cyber Pink", "#FF2E88", "#00E5FF", "#12062B", "#FFF3F9", "tech bright playful"),
    P("graphite", "Graphite Red", "#2B2B2E", "#E63946", "#161618", "#F7F7F8", "bold dark minimal"),
    P("mono", "Pure Mono", "#000000", "#777777", "#000000", "#FFFFFF", "minimal dark"),
    P("sand", "Desert Sand", "#C49A6C", "#6B4F3A", "#2E2218", "#FCF7EF", "earthy warm minimal"),
    P("cherry", "Cherry", "#C1121F", "#FDF0D5", "#2B0509", "#FFFAF4", "food warm bold"),
    P("mustard", "Mustard & Navy", "#E1AD01", "#1B2A49", "#101A2E", "#FFFBEA", "bold warm cool"),
    P("aqua", "Aqua Pop", "#00B8D9", "#FF6F91", "#073B4C", "#F2FCFE", "bright playful fresh"),
    P("orchid", "Orchid", "#A24BA7", "#F7B2D9", "#35113A", "#FCF4FC", "beauty playful"),
    P("moss", "Moss", "#55612B", "#C8B560", "#242A0E", "#F9F8EC", "earthy nature"),
    P("ruby", "Ruby & Pearl", "#9B1236", "#EDE3D6", "#2E0814", "#FBF7F1", "luxury warm"),
    P("arctic", "Arctic", "#5AA9E6", "#CAD9E6", "#1D3557", "#F5FAFF", "cool minimal fresh"),
    P("bubble", "Bubblegum", "#FF77B7", "#7AD7F0", "#3A1A52", "#FFF5FB", "playful bright"),
    P("coffee", "Latte", "#7B5A44", "#E8D5BF", "#2C1E15", "#FBF6F0", "food warm earthy"),
    P("royal", "Royal Blue", "#1D3FBB", "#E5C07B", "#0C1B5C", "#F5F7FF", "luxury cool bold"),
    P("tropic", "Tropic", "#00A676", "#FF9F1C", "#073B2D", "#F3FCF8", "fresh bright playful"),
    P("slategreen", "Slate Green", "#3C5A4F", "#D4A373", "#1C2B25", "#F6F8F5", "nature minimal earthy"),
    P("flamingo", "Flamingo", "#F2547D", "#FFC2D1", "#4A1530", "#FFF5F8", "beauty playful warm"),
    P("carbon", "Carbon & Lime", "#1C1C1E", "#C6F432", "#0A0A0B", "#F6F7F2", "tech bold dark"),
    P("honey", "Honey", "#F2A900", "#7B3F00", "#2B1700", "#FFFAEA", "food warm earthy"),
    P("wisteria", "Wisteria", "#8E7CC3", "#F4D6E8", "#2E2748", "#FAF7FF", "beauty cool"),
    P("cobalt", "Cobalt & Coral", "#0047AB", "#FF7F6E", "#08224F", "#F5F8FF", "bold bright cool"),
    P("sky", "Sky", "#3B9AE1", "#FFD166", "#12304A", "#F3FAFF", "bright cool playful"),
]
BY_ID = {p["id"]: p for p in PALETTES}


def norm(c):
    c = c.strip()
    if len(c) == 4:
        c = "#" + "".join(ch * 2 for ch in c[1:])
    return c.upper()


def mix(a, b, t):
    """blend two #rrggbb colors; t = 0 gives a, 1 gives b"""
    a, b = norm(a), norm(b)
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * t) for x, y in zip(ca, cb))


def shade(c, t):
    """t < 0 darker, t > 0 lighter"""
    return mix(c, "#000000", -t) if t < 0 else mix(c, "#FFFFFF", t)


def luminance(c):
    c = norm(c)
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(c[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def from_base(hexcolor):
    """make a palette around one color the user picked"""
    h = hexcolor.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)[0], colorsys.rgb_to_hls(r, g, b)[1], colorsys.rgb_to_hls(r, g, b)[2]
    r2, g2, b2 = colorsys.hls_to_rgb((hh + 0.5) % 1.0 if ss > 0.25 else hh, 0.5, max(0.45, ss))
    sec = "#%02X%02X%02X" % (round(r2 * 255), round(g2 * 255), round(b2 * 255))
    base = "#" + h.upper()
    return {"id": "custom", "name": "Your color", "primary": base, "secondary": sec, "text": shade(base, -0.78),
            "bg": mix("#FFFFFF", base, 0.06), "tags": ["custom"]}
