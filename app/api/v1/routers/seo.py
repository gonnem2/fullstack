"""
SEO-роутер: sitemap.xml, robots.txt.
Подключить в main.py: app.include_router(seo_router) — без префикса /api/v1.
"""

from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter(tags=["SEO"])


@router.get("/robots.txt")
def robots_txt():
    content = """User-agent: *
Allow: /login
Allow: /register
Disallow: /dashboard
Disallow: /stats
Disallow: /transactions
Disallow: /spending
Disallow: /income
Disallow: /admin/
Disallow: /api/

Sitemap: https://financetrack.example.com/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")


@router.get("/sitemap.xml")
def sitemap_xml():
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://financetrack.example.com/login</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://financetrack.example.com/register</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
</urlset>
"""
    return Response(content=content, media_type="application/xml")
