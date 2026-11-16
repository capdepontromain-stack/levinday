#!/usr/bin/env python3
"""Génère le blog du site Le Vinday.

Chaque article est un fichier _articles/<slug>.html :
  ligne 1 : métadonnées JSON {"titre","description","date","categorie","image","w","h","alt"}
  ligne 2 : ---
  reste   : corps HTML de l'article (h2, p, ul...)
Lancer : python3 _outils/genblog.py  (depuis ~/site-levinday)
Puis git add/commit/push. Les dossiers _articles et _outils ne sont pas publiés (Jekyll ignore les dossiers en _).
"""
import json, os, glob, html, datetime

BASE = "https://levinday.re/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

CSS = """:root{--red:#EA2839;--blue:#1A206D;--navy:#11154a;--yellow:#FFD500;--green:#00A551;--cream:#F4EEE1;--paper:#FBF8F1;--ink:#14173a;--muted:#5b5f80}
*{box-sizing:border-box}body{margin:0;font-family:Outfit,Arial,sans-serif;background:var(--cream);color:var(--ink);line-height:1.7;font-size:18px;overflow-x:hidden}
img{max-width:100%;display:block}img[width]{height:auto}a{color:inherit}
.flag{height:6px;background:linear-gradient(90deg,var(--red) 0 25%,var(--blue) 25% 50%,var(--yellow) 50% 75%,var(--green) 75%)}
header{background:var(--navy);color:#fff;position:sticky;top:0;z-index:20}
.nav{max-width:1180px;margin:0 auto;padding:0 20px;height:66px;display:flex;align-items:center;justify-content:space-between;gap:14px}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none}.brand img{width:42px;height:42px}.brand span{font-family:'Bowlby One';letter-spacing:.04em}
.nav nav a{text-decoration:none;margin-left:22px;font-weight:500;opacity:.85}.nav nav a:hover{opacity:1;color:var(--yellow)}
.btn{display:inline-flex;align-items:center;gap:8px;padding:13px 24px;border-radius:99px;font-weight:700;text-decoration:none;white-space:nowrap}
.btn-y{background:var(--yellow);color:var(--navy)}.btn-g{background:var(--green);color:#fff}.btn-r{background:var(--red);color:#fff}
.hero{background:var(--navy);color:#fff;padding:56px 20px 64px;text-align:center}
.hero h1{font-family:'Bowlby One';text-transform:uppercase;font-weight:400;font-size:clamp(1.9rem,4.6vw,3.2rem);line-height:1.05;max-width:900px;margin:12px auto 0}
.hero p{color:#c3c7ee;max-width:700px;margin:16px auto 0}
.cat{display:inline-block;background:var(--yellow);color:var(--navy);font-weight:700;font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;padding:5px 14px;border-radius:99px}
.crumb{font-size:.88rem;color:#c3c7ee}.crumb a{color:#fff}
article.post{max-width:780px;margin:-34px auto 0;padding:0 20px 40px}
article.post>img{border-radius:24px;box-shadow:0 24px 50px -24px rgba(17,21,74,.6);border:6px solid #fff;width:100%;aspect-ratio:16/10;object-fit:cover}
.post h2{font-family:'Bowlby One';font-weight:400;text-transform:uppercase;color:var(--navy);font-size:1.55rem;line-height:1.15;margin:42px 0 6px}
.post h3{color:var(--red);font-size:1.15rem;margin:26px 0 4px}
.post li{margin:6px 0}.post a{color:var(--red);font-weight:600}
.post .note{background:var(--paper);border-left:6px solid var(--yellow);padding:16px 20px;border-radius:12px}
.cta{background:var(--navy);color:#fff;border-radius:26px;padding:34px 28px;text-align:center;margin:46px 0 10px}
.cta h2{color:#fff;margin:0 0 8px}.cta p{color:#c3c7ee;margin:0 0 20px}.cta .b{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.more{max-width:1180px;margin:0 auto;padding:30px 20px 70px}
.more h2,.list h2{font-family:'Bowlby One';font-weight:400;text-transform:uppercase;color:var(--navy);text-align:center;font-size:1.7rem;margin:0 0 26px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.card{background:#fff;border-radius:22px;overflow:hidden;text-decoration:none;box-shadow:0 10px 30px -18px rgba(17,21,74,.4);transition:.25s;display:flex;flex-direction:column}
.card:hover{transform:translateY(-4px)}.card img{width:100%;aspect-ratio:16/10;object-fit:cover}
.card .cat{margin:18px 22px 0;align-self:flex-start}.card h3{font-weight:800;font-size:1.15rem;color:var(--navy);margin:10px 22px 6px;line-height:1.25}
.card p{color:var(--muted);font-size:.95rem;margin:0 22px 22px;line-height:1.5}
.list{max-width:1180px;margin:0 auto;padding:50px 20px 70px}
footer{background:var(--navy);color:#b9bcd9;text-align:center;padding:34px 20px 40px;font-size:.92rem}footer a{color:#fff}
.evin{font-size:.8rem}
@media(max-width:860px){.grid{grid-template-columns:1fr}.nav nav{display:none}footer{padding-bottom:100px}
.callbar{display:flex;position:fixed;bottom:0;left:0;right:0;gap:8px;padding:10px;background:#fff;box-shadow:0 -6px 20px rgba(0,0,0,.12);z-index:30}.callbar a{flex:1;text-align:center;padding:13px;border-radius:99px;font-weight:700;text-decoration:none}}
@media(min-width:861px){.callbar{display:none}}
@media(max-width:560px){.nav .btn{display:none}body{font-size:17px}}
"""


def page(title, desc, canon, depth, body, ld, image=None):
    up = "../" * depth
    og = f'<meta property="og:image" content="{BASE}images/{image}">' if image else ""
    lds = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#1A206D">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="article">
<meta property="og:locale" content="fr_FR">
{og}
<link rel="icon" href="{up}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bowlby+One&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}blog/blog.css">
{lds}
</head>
<body>
<div class="flag"></div>
<header><div class="nav">
<a class="brand" href="{up}"><img src="{up}images/logo-le-vinday.svg" width="42" height="42" alt="Logo Le Vinday"><span>LE VINDAY</span></a>
<nav><a href="{up}#specialites">Spécialités</a><a href="{up}#formules">Commander</a><a href="{up}blog/">Blog</a><a href="{up}#contact">Contact</a></nav>
<a class="btn btn-y" href="tel:+262692270237">📞 06 92 27 02 37</a>
</div></header>
{body}
<footer><p><b style="color:#fff">Le Vinday</b> · Traiteur mauricien à Saint-Paul, Ouest de La Réunion · 140 route du Vieux Flamboyant, Bernica, 97435 Saint-Paul<br>
<a href="tel:+262692270237">06 92 27 02 37</a> · <a href="mailto:levinday974@gmail.com">levinday974@gmail.com</a> · <a href="https://www.facebook.com/levindaysnack" rel="noopener">Facebook</a> · <a href="https://www.instagram.com/levindaysnack" rel="noopener">Instagram</a></p>
<p class="evin">L'abus d'alcool est dangereux pour la santé, à consommer avec modération.<br>Crédits photos : Unsplash ; dholl puri : Yoann74, CC BY-SA 4.0, Wikimedia Commons.</p></footer>
<div class="callbar"><a class="btn-r" href="tel:+262692270237">📞 Appeler</a><a class="btn-g" href="https://wa.me/262692270237">💬 WhatsApp</a></div>
</body></html>
"""


def fdate(d):
    y, m, j = map(int, d.split("-"))
    return f"{j} {MOIS[m-1]} {y}"


def card(a, up):
    return (f'<a class="card" href="{up}blog/{a["slug"]}/"><img src="{up}images/{a["image"]}" width="{a["w"]}" height="{a["h"]}" alt="{html.escape(a["alt"])}" loading="lazy">'
            f'<span class="cat">{a["categorie"]}</span><h3>{html.escape(a["titre"])}</h3><p>{html.escape(a["description"])}</p></a>')


def main():
    arts = []
    for f in glob.glob(os.path.join(ROOT, "_articles", "*.html")):
        raw = open(f, encoding="utf-8").read()
        meta, body = raw.split("\n---\n", 1)
        a = json.loads(meta)
        a["slug"] = os.path.splitext(os.path.basename(f))[0]
        a["body"] = body
        arts.append(a)
    arts.sort(key=lambda a: (a["date"], a["slug"]), reverse=True)
    org = {"@type": "Organization", "name": "Le Vinday", "url": BASE, "logo": BASE + "images/logo-le-vinday.svg"}

    for a in arts:
        url = f"{BASE}blog/{a['slug']}/"
        others = [x for x in arts if x["slug"] != a["slug"]][:3]
        body = f"""<div class="hero"><p class="crumb"><a href="../../">Accueil</a> › <a href="../">Blog</a></p><span class="cat">{a['categorie']}</span><h1>{html.escape(a['titre'])}</h1><p>{fdate(a['date'])} · Le Vinday, traiteur à Saint-Paul</p></div>
<article class="post">
<img src="../../images/{a['image']}" width="{a['w']}" height="{a['h']}" alt="{html.escape(a['alt'])}">
{a['body']}
<div class="cta"><h2>Une envie de cuisine mauricienne ?</h2><p>De la simple barquette au repas complet, de 10 à 400 personnes, livré partout sur l'île. Devis gratuit, adapté à votre budget.</p>
<div class="b"><a class="btn btn-g" href="https://wa.me/262692270237" rel="noopener">💬 WhatsApp</a><a class="btn btn-y" href="../../#formules">Composer ma commande</a></div></div>
</article>
<section class="more"><h2>À lire aussi</h2><div class="grid">{''.join(card(o, '../../') for o in others)}</div></section>"""
        ld = [
            {"@context": "https://schema.org", "@type": "BlogPosting", "headline": a["titre"], "description": a["description"],
             "image": BASE + "images/" + a["image"], "datePublished": a["date"], "dateModified": a["date"], "inLanguage": "fr-FR",
             "mainEntityOfPage": url, "author": org, "publisher": org},
            {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Accueil", "item": BASE},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": BASE + "blog/"},
                {"@type": "ListItem", "position": 3, "name": a["titre"], "item": url}]}]
        os.makedirs(os.path.join(ROOT, "blog", a["slug"]), exist_ok=True)
        open(os.path.join(ROOT, "blog", a["slug"], "index.html"), "w", encoding="utf-8").write(
            page(a["titre"] + " | Le Vinday", a["description"], url, 2, body, ld, a["image"]))

    body = f"""<div class="hero"><p class="crumb"><a href="../">Accueil</a> › Blog</p><span class="cat">Le blog du Vinday</span><h1>Recettes, bons plans et conseils de traiteur</h1><p>Le briani, les box repas en entreprise, la livraison à domicile et sur la plage : tout ce qu'il faut savoir pour bien manger à plusieurs, dans l'Ouest de La Réunion et partout sur l'île.</p></div>
<section class="list"><div class="grid">{''.join(card(a, '../') for a in arts)}</div></section>"""
    ld = [{"@context": "https://schema.org", "@type": "Blog", "name": "Le blog du Vinday", "url": BASE + "blog/", "publisher": org,
           "blogPost": [{"@type": "BlogPosting", "headline": a["titre"], "url": f"{BASE}blog/{a['slug']}/", "datePublished": a["date"]} for a in arts]}]
    open(os.path.join(ROOT, "blog", "index.html"), "w", encoding="utf-8").write(
        page("Blog Le Vinday | Recettes mauriciennes et conseils de traiteur à La Réunion",
             "Recettes mauriciennes (briani, mine frites), box repas en entreprise, livraison de repas à domicile et sur la plage : le blog du traiteur Le Vinday, Saint-Paul.",
             BASE + "blog/", 1, body, ld))
    open(os.path.join(ROOT, "blog", "blog.css"), "w", encoding="utf-8").write(CSS)

    today = datetime.date.today().isoformat()
    urls = [(BASE, today), (BASE + "blog/", arts[0]["date"] if arts else today)] + [(f"{BASE}blog/{a['slug']}/", a["date"]) for a in arts]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"<url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n"
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(sm)
    print(f"{len(arts)} articles générés")


if __name__ == "__main__":
    main()
