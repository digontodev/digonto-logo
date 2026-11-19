"""The idea maker: a short brief (name, what you do, style) -> many different, well-formed logo specs."""
import random
import re
import copy

from . import compose, icons, marks, palettes, textkit
from . import generate as gen

INDUSTRIES = {
    "food": {"label": "Restaurant, cafe, food", "tags": "food warm",
             "kw": "pizza pizzeria restaurant ristorante trattoria osteria cafe café kaffee coffee bar bakery baeckerei bäckerei panificio burger kebab doner döner sushi food essen cucina catering bistro grill gelato eis imbiss kitchen küche cook chef pasta bbq steak diner brunch",
             "icons": "pizza fork-knife chef-hat coffee bread hamburger cooking-pot ice-cream wine beer-stein bowl-food cake cookie carrot fish popcorn martini coffee-bean egg cheese avocado knife grains orange-slice"},
    "tech": {"label": "Technology, software, IT", "tags": "tech cool",
             "kw": "software app apps digital it web code coding ai data cloud cyber tech technology online saas startup computer network hosting developer dev systems robot automation platform cloud server",
             "icons": "code terminal-window cpu database globe wifi-high shield-check lock desktop-tower device-mobile robot brain atom lightning rocket-launch cloud"},
    "beauty": {"label": "Beauty, hair, fashion", "tags": "beauty warm luxury",
               "kw": "hair friseur salon beauty nails makeup kosmetik cosmetics fashion boutique kleidung mode parrucchiere spa massage tattoo barber style stylist skincare nail lash",
               "icons": "scissors hair-dryer sparkle t-shirt dress handbag diamond crown flower-lotus eyeglasses mask-happy heart"},
    "health": {"label": "Health, medical, care", "tags": "health cool fresh",
               "kw": "clinic doctor arzt praxis health medical zahn dental dentist pharmacy apotheke therapy physio physiotherapy care pflege medicine hospital clinic wellness nurse",
               "icons": "stethoscope first-aid heartbeat tooth pill syringe hospital bandaids thermometer heart-straight plant"},
    "trades": {"label": "Construction, repair, trades", "tags": "bold warm",
               "kw": "construction bau builder plumber plumbing electric electrician elektro handwerk repair roof roofing paint maler cleaning reinigung garden gartenbau carpenter tischler build renovation handyman installation",
               "icons": "hammer wrench paint-roller paint-brush ruler wall toolbox hard-hat plug lightbulb broom house-line"},
    "fitness": {"label": "Fitness, sport", "tags": "bold bright",
                "kw": "gym fitness yoga sport sports trainer training run running crossfit boxing martial pilates dance football soccer club coach",
                "icons": "barbell person-simple-run soccer-ball basketball trophy medal heart-straight lightning yin-yang"},
    "finance": {"label": "Finance, law, consulting", "tags": "luxury dark minimal",
                "kw": "finance bank tax steuer consulting beratung law anwalt lawyer insurance versicherung accounting accountant invest investment capital advisor legal notar trust",
                "icons": "bank coins chart-line-up briefcase scales handshake calculator receipt gavel shield-check"},
    "education": {"label": "Education, kids", "tags": "playful bright",
                  "kw": "school schule academy learn learning kurs course tutor kita kids kinder child children baby toy education university student teacher nursery",
                  "icons": "graduation-cap book-open books pencil student chalkboard-teacher backpack baby balloon star"},
    "travel": {"label": "Travel, hotel, transport", "tags": "cool fresh bright",
               "kw": "travel reise hotel tour tourism hostel airline flight holiday vacation trip booking transport taxi delivery logistik car auto garage cab bike rental",
               "icons": "suitcase map-pin compass bed tent campfire binoculars globe-hemisphere-west airplane-tilt car taxi truck bicycle boat"},
    "creative": {"label": "Creative, print, media", "tags": "playful bright",
                 "kw": "photo photography design studio art music film video agency marketing print printing druck dtf textile shirt graphic media creative production podcast band",
                 "icons": "camera film-slate music-notes palette printer pen-nib vector-three paint-bucket microphone headphones sparkle"},
    "nature": {"label": "Nature, eco, garden", "tags": "nature fresh earthy",
               "kw": "eco green bio organic farm garden flower plant nature forest tree energy solar recycling sustainable wood bauernhof natur blume pflanze",
               "icons": "leaf tree flower plant mountains drop sun recycle windmill butterfly campfire"},
    "retail": {"label": "Shop, retail", "tags": "bright warm",
               "kw": "shop store market laden supermarket kiosk retail boutique ecommerce mall gift shopping wholesale trading import export",
               "icons": "shopping-cart storefront bag tag gift package basket"},
    "community": {"label": "Community, charity, faith", "tags": "warm earthy",
                  "kw": "charity verein foundation community church mosque temple nonprofit ngo association faith family club social volunteer",
                  "icons": "users-three hands-praying hand-heart handshake heart flag church"},
    "pets": {"label": "Pets, animals", "tags": "playful warm",
             "kw": "pet pets dog cat vet animal tier hund katze zoo horse bird",
             "icons": "paw-print dog cat bird butterfly horse fish-simple heart"},
}
NOISE = set("arrow arrows slash check x plus minus warning question cursor caret download upload cloud-slash prohibit".split()) | {"slash", "download", "upload", "arrow"}
GENERIC_ICONS = "star sparkle diamond crown lightning heart shield-check leaf sun compass key flame cube hexagon circle-notch infinity planet rocket-launch lighthouse anchor"

WORDS = {  # Italian / German name words -> icon search words
    "nuvola": "cloud", "sole": "sun", "luna": "moon", "stella": "star", "mare": "waves", "fiore": "flower", "albero": "tree", "casa": "house",
    "cuore": "heart", "fuoco": "fire", "montagna": "mountains", "onda": "waves", "foglia": "leaf", "chiave": "key", "corona": "crown",
    "wolke": "cloud", "sonne": "sun", "mond": "moon", "stern": "star", "meer": "waves", "blume": "flower", "baum": "tree", "haus": "house",
    "herz": "heart", "feuer": "fire", "berg": "mountains", "welle": "waves", "blatt": "leaf", "schlüssel": "key", "krone": "crown",
    "wasser": "drop", "kaffee": "coffee", "brot": "bread", "pizza": "pizza", "uhr": "clock", "anker": "anchor", "vogel": "bird", "fisch": "fish",
    "tavola": "fork-knife", "forno": "fire", "pane": "bread", "vino": "wine", "caffè": "coffee", "gelato": "ice-cream", "dolce": "cake",
}

STYLES = {
    "modern": {"label": "Modern", "fonts": "montserrat poppins outfit sora manrope dm-sans urbanist league-spartan space-grotesk work-sans inter rubik",
               "cases": ["", "upper", "lower"], "conts": ["none", "rounded", "circle", "squircle"], "tags": "tech bright minimal cool", "serif": False},
    "classic": {"label": "Classic", "fonts": "playfair-display cormorant-garamond lora libre-baskerville merriweather bitter cinzel dm-serif-display roboto-slab",
                "cases": ["title", "upper"], "conts": ["none", "shield", "circle", "arch"], "tags": "luxury earthy dark", "serif": True},
    "playful": {"label": "Playful", "fonts": "nunito quicksand righteous lobster pacifico rubik outfit dancing-script",
                "cases": ["", "title"], "conts": ["circle", "leaf", "squircle", "badge8"], "tags": "playful bright", "serif": False},
    "elegant": {"label": "Elegant", "fonts": "cormorant-garamond playfair-display cinzel dm-serif-display great-vibes sacramento josefin-sans raleway",
                "cases": ["upper", "title"], "conts": ["none", "ring", "arch", "diamond"], "tags": "luxury beauty dark", "serif": True},
    "bold": {"label": "Bold", "fonts": "anton bebas-neue oswald archivo-black league-spartan montserrat poppins roboto-slab",
             "cases": ["upper"], "conts": ["none", "shield", "hexagon", "badge8", "rounded"], "tags": "bold warm bright", "serif": False},
    "minimal": {"label": "Minimal", "fonts": "inter dm-sans manrope work-sans josefin-sans raleway urbanist space-grotesk",
                "cases": ["lower", "", "upper"], "conts": ["none", "none", "circle", "ring"], "tags": "minimal dark cool", "serif": False},
    "handmade": {"label": "Handmade", "fonts": "caveat dancing-script satisfy sacramento pacifico roboto-slab space-mono arvo",
                 "cases": ["", "title"], "conts": ["none", "circle", "leaf", "badge8"], "tags": "earthy warm playful", "serif": False},
}
SCRIPT = {"pacifico", "dancing-script", "great-vibes", "satisfy", "caveat", "sacramento", "lobster"}
CALM_TAG_FONTS = "inter dm-sans work-sans josefin-sans montserrat raleway manrope".split()


def words(text):
    return re.findall(r"[a-zäöüßàèéìòù]+", text.lower())


def detect(brief):
    t = set(words(" ".join([brief.get("name", ""), brief.get("desc", ""), brief.get("tagline", "")])))
    if brief.get("industry") in INDUSTRIES:
        return [brief["industry"]]
    scores = []
    for k, v in INDUSTRIES.items():
        sc = len(t & set(v["kw"].split()))
        if sc:
            scores.append((-sc, k))
    scores.sort()
    return [k for _, k in scores[:2]]


def icon_pool(brief, inds):
    have = {i["n"] for i in icons.db()}
    pool, seen = [], set()

    def push(n):
        if n in have and n not in seen:
            seen.add(n)
            pool.append(n)
    nw = words(brief.get("name", ""))
    for w in nw:                                   # words from the business name first
        w2 = WORDS.get(w, w)
        cand = [n for n in icons.search(w2, 60) if w2 in icons.base(n).split("-") and not (set(icons.base(n).split("-")) & NOISE)]
        cand.sort(key=lambda n: (icons.base(n) != w2, ":" in n, len(n)))
        for n in cand[:3]:
            push(n)
    for w in words(brief.get("desc", "")) + words(brief.get("tagline", "")):
        w2 = WORDS.get(w, w)
        if len(w2) > 3:
            cand = [n for n in icons.search(w2, 60) if w2 in icons.base(n).split("-") and not (set(icons.base(n).split("-")) & NOISE)]
            cand.sort(key=lambda n: (icons.base(n) != w2, ":" in n, len(n)))
            for n in cand[:3]:
                push(n)
    for k in inds:
        for n in INDUSTRIES[k]["icons"].split():
            push(n)
    for n in GENERIC_ICONS.split():
        push(n)
    return pool


def palette_pool(brief, inds, style_keys):
    p = brief.get("palette")
    if isinstance(p, str) and p.startswith("#") and len(p) in (4, 7):
        return [palettes.from_base(palettes.norm(p))]
    if p in palettes.BY_ID:
        return [palettes.BY_ID[p]]
    want = set()
    for k in inds:
        want |= set(INDUSTRIES[k]["tags"].split())
    for s in style_keys:
        want |= set(STYLES[s]["tags"].split())
    scored = sorted(palettes.PALETTES, key=lambda x: -len(want & set(x["tags"])))
    top = [x for x in scored if want & set(x["tags"])]
    return (top or palettes.PALETTES)[:16] if want else palettes.PALETTES


def dark_variant(pal):
    bg = pal["text"] if palettes.luminance(pal["text"]) < 0.12 else palettes.shade(pal["text"], -0.5)
    prim = pal["primary"]
    if palettes.contrast(prim, bg) < 3.2:
        prim = pal["secondary"] if palettes.contrast(pal["secondary"], bg) >= 3.2 else palettes.shade(prim, 0.55)
    sec = pal["secondary"] if prim != pal["secondary"] else palettes.shade(pal["primary"], 0.4)
    return {"primary": prim, "secondary": sec, "text": pal["bg"] if palettes.luminance(pal["bg"]) > 0.6 else "#FFFFFF", "bg": bg}


def colors_of(pal, dark=False):
    if dark:
        return dark_variant(pal)
    return {"primary": pal["primary"], "secondary": pal["secondary"], "text": pal["text"], "bg": pal["bg"]}


KINDS = ["icon", "badge", "abstract", "split", "monogram", "frame", "wordmark", "icon", "emblem", "swap", "icon", "split", "mark", "monogram", "abstract",
         "stamp", "frame", "icon", "emblem", "badge", "mark", "swap", "icon", "wordmark", "monogram", "stamp", "abstract", "frame", "mark", "split"]
MONO_PICK = ["plain", "overlap", "interlock", "linked", "stacked", "cutout", "shield", "outline", "inline", "stripe", "shadow", "split", "diamond", "ribbon"]
FREE_MONO = {"stacked", "cutout", "shield", "diamond", "ribbon", "overlap", "shadow", "split"}   # look good without a container


def one(brief, rng, kind, ctx, i):
    name = brief["name"].strip() or "Your Brand"
    nw = len(name.split())
    sk = rng.choice(ctx["styles"])
    st = STYLES[sk]
    pal = ctx["pals"][i % len(ctx["pals"])] if len(ctx["pals"]) < 4 else rng.choice(ctx["pals"])
    dark = rng.random() < 0.16 and ctx["allow_dark"]
    fid = rng.choice(st["fonts"].split())
    script = fid in SCRIPT
    case = "" if script else rng.choice(st["cases"])
    bold = textkit.has_bold(fid) and (rng.random() < (0.8 if st["serif"] is False else 0.6))
    if fid in ("anton", "bebas-neue", "archivo-black", "righteous"):
        bold = False
    track = 0.0 if script else (rng.choice([0.04, 0.08, 0.14]) if case == "upper" else rng.choice([0, 0, 0.01]))
    two = "none"
    if nw >= 2 and not script and rng.random() < 0.5:
        two = rng.choice(["first", "last", "weight"]) if textkit.has_bold(fid) else rng.choice(["first", "last"])
    tfid = rng.choice(CALM_TAG_FONTS)
    if kind == "badge":
        fid = rng.choice("montserrat poppins archivo-black oswald league-spartan work-sans outfit".split())
        case, script = "upper", False
        bold = textkit.has_bold(fid) and fid != "archivo-black"
        track = rng.choice([0.04, 0.1])
    elif kind == "frame":
        fid = rng.choice("playfair-display cormorant-garamond cinzel lora josefin-sans raleway dm-serif-display".split())
        case, script, bold, track = "upper", False, False, rng.choice([0.1, 0.16])
    layout = {"icon": rng.choice(["horizontal", "stacked", "horizontal", "twoline" if nw >= 2 else "stacked"]),
              "mark": rng.choice(["horizontal", "stacked", "twoline" if nw >= 2 else "horizontal"]),
              "monogram": rng.choice(["horizontal", "stacked"]), "abstract": rng.choice(["horizontal", "stacked", "horizontal"]),
              "swap": "wordmark", "wordmark": "wordmark", "emblem": "emblem", "stamp": "stamp", "badge": "badge",
              "frame": "frame", "split": rng.choice(["horizontal", "stacked", "horizontal"])}[kind]
    if len(name) > 20 and kind in ("emblem",):
        layout = "stacked"
    sym = {"kind": "none", "scale": 1.0, "grad": False, "container": "none", "cmode": "solid"}
    if kind in ("icon", "emblem", "stamp", "frame", "split") or (kind == "badge" and rng.random() < 0.6):
        pl = ctx["pool"]
        sym.update(kind="icon", icon=pl[min(int(rng.random() ** 2.0 * len(pl) * 0.6), len(pl) - 1)], iw="bold" if rng.random() < 0.22 else "fill")
    elif kind == "mark":
        sym.update(kind="mark", mark=rng.choice(list(marks.MARKS)))
    elif kind == "monogram":
        sym.update(kind="monogram", mstyle=rng.choice(MONO_PICK))
    elif kind == "abstract":
        sym.update(kind="abstract", astyle=rng.choice([k for k, _ in gen.ABSTRACT_STYLES]), avar=rng.randint(0, 3))
    if kind in ("icon", "mark") and rng.random() < 0.15:
        sym["line"] = rng.choice(["line", "double"])
    if sym["kind"] != "none":
        if kind == "monogram":
            sym["container"] = "none" if sym["mstyle"] in FREE_MONO else rng.choice([c for c in st["conts"] if c != "none"] or ["rounded"])
        elif kind == "icon" and layout != "symbol":
            sym["container"] = rng.choice(st["conts"])
        elif kind == "mark" and rng.random() < 0.25:
            sym["container"] = rng.choice(["circle", "rounded"])
        if sym["container"] != "none":
            sym["cmode"] = rng.choices(["solid", "duo", "outline", "soft"], [5, 2, 2, 2])[0]
        sym["grad"] = bool(rng.random() < 0.14 and sk in ("modern", "playful"))
        if kind in ("frame", "badge", "split"):
            sym["container"], sym["cmode"] = "none", "solid"
            sym["grad"] = False
        if kind == "split":
            sym["split"] = True
            sym["iw"] = "fill"
    spec = {
        "name": name, "tagline": brief.get("tagline", "").strip(), "layout": layout, "symbol": sym,
        "font": {"id": fid, "bold": bold, "case": case, "track": track, "two": two, "size": 1.0},
        "tfont": {"id": tfid, "bold": False, "case": "upper" if case == "upper" else "", "track": 0.2 if case == "upper" else 0.03,
                  "scale": 1.0, "fit": case == "upper"},
        "colors": colors_of(pal, dark), "palette": pal["id"],
        "name_role": "primary" if rng.random() < 0.28 else "text", "tag_role": "muted",
        "gap": 1.0, "divider": bool(layout == "horizontal" and rng.random() < 0.18), "fill": bool(rng.random() < 0.55),
        "deco": rng.choice(["none", "bar", "lines", "underline"]) if layout == "wordmark" else "none",
        "style": sk, "kind": kind,
    }
    if kind == "swap":                              # a letter of the name becomes the icon
        pl = ctx["pool"]
        spec["swap"] = {"on": True, "letter": "", "icon": pl[min(int(rng.random() ** 2.0 * len(pl) * 0.4), len(pl) - 1)], "iw": "fill"}
        spec["font"]["case"] = spec["font"]["case"] or "upper"
        spec["deco"] = "none"
    if kind == "monogram" and spec["tagline"] == "" and layout == "stacked":
        pass
    return spec


def signature(s):
    sy = s["symbol"]
    return (s["layout"], sy.get("icon") or sy.get("mark") or sy.get("mstyle") or sy.get("astyle") or sy["kind"], s["font"]["id"], s["palette"], sy.get("container"))


def generate(brief, n=18, seed=0):
    rng = random.Random(hash((brief.get("name", ""), brief.get("desc", ""), seed)) & 0xFFFFFFFF)
    inds = detect(brief)
    styles = [s for s in brief.get("styles", []) if s in STYLES]
    if not styles:
        styles = ["modern", "classic", "playful", "bold"] if not inds else {"food": ["classic", "playful", "bold", "handmade"], "tech": ["modern", "minimal", "bold"],
                                                                         "beauty": ["elegant", "minimal", "playful"], "finance": ["classic", "minimal", "elegant"],
                                                                         "trades": ["bold", "modern", "classic"], "health": ["modern", "minimal", "classic"],
                                                                         "education": ["playful", "modern", "handmade"]}.get(inds[0], ["modern", "classic", "bold", "playful"])
    ctx = {"styles": styles, "pool": icon_pool(brief, inds), "pals": palette_pool(brief, inds, styles), "ix": 0,
           "allow_dark": not (isinstance(brief.get("palette"), str) and brief.get("palette", "").startswith("#")) or True}
    if len(ctx["pals"]) == 1:
        # one chosen palette: still vary by swapping main/second color
        base = ctx["pals"][0]
        sw = dict(base, primary=base["secondary"], secondary=base["primary"], id=base["id"] + "-swap")
        ctx["pals"] = [base, base, sw]
    out, seen, tries, k = [], set(), 0, 0
    kinds = KINDS[:]
    while len(out) < n and tries < n * 8:
        kind = kinds[k % len(kinds)]
        k += 1
        tries += 1
        if kind == "wordmark" and "icon" in [o["kind"] for o in out[-1:]] and False:
            pass
        s = one(brief, rng, kind, ctx, len(out))
        sig = signature(s)
        if sig in seen:
            continue
        seen.add(sig)
        out.append(s)
    return out


def variations(spec, n=12, seed=0):
    """other takes on one chosen idea: same symbol, other layouts, palettes and fonts"""
    rng = random.Random(seed + 7)
    base = compose.merged(spec)
    out = []
    lays = ["horizontal", "stacked", "twoline", "wordmark", "emblem", "stamp"]
    rng.shuffle(lays)
    for lay in lays[:4]:
        s = copy.deepcopy(base)
        s["layout"] = lay
        out.append(s)
    pals = rng.sample(palettes.PALETTES, 5)
    for p in pals:
        s = copy.deepcopy(base)
        s["colors"] = colors_of(p, rng.random() < 0.2)
        s["palette"] = p["id"]
        out.append(s)
    fonts = [f for f in textkit.FONTS if f["cat"] in ("sans", "serif", "display", "slab")]
    for f in rng.sample(fonts, 3):
        s = copy.deepcopy(base)
        s["font"]["id"] = f["id"]
        s["font"]["bold"] = "bold" in f
        out.append(s)
    return out[:n]
