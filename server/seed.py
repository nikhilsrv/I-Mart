#!/usr/bin/env python3
"""Seed database with categories and ~200 products across 8 domains."""

import asyncio
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "app"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings
from db.models.category import Category
from db.models.product import Product

engine = create_async_engine(settings.DATABASE_URL, echo=False)
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# (name, slug, description, image_url, parent_slug or None)
CATEGORIES = [
    # --- Parents ---
    ("Electronics", "electronics", "Latest gadgets and tech", "https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&q=80", None),
    ("Clothing & Fashion", "clothing-fashion", "Apparel for every style", "https://images.unsplash.com/photo-1445205170230-053b83016050?w=400&q=80", None),
    ("Food & Groceries", "food-groceries", "Fresh and packaged essentials", "https://images.unsplash.com/photo-1542838132-92c53300491e?w=400&q=80", None),
    ("Home & Kitchen", "home-kitchen", "Furnish and equip your home", "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&q=80", None),
    ("Books & Stationery", "books-stationery", "Books and study supplies", "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&q=80", None),
    ("Sports & Fitness", "sports-fitness", "Gear up for an active life", "https://images.unsplash.com/photo-1547919307-1ecb10702e6f?w=400&q=80", None),
    ("Beauty & Personal Care", "beauty-personal-care", "Skincare, haircare and more", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=400&q=80", None),
    ("Toys & Games", "toys-games", "Fun for all ages", "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=400&q=80", None),
    # --- Children ---
    ("Smartphones", "smartphones", "Latest mobile phones", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&q=80", "electronics"),
    ("Laptops", "laptops", "Powerful portable computers", "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&q=80", "electronics"),
    ("Headphones & Audio", "headphones-audio", "Headphones, earbuds and speakers", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80", "electronics"),
    ("Cameras", "cameras", "DSLR, mirrorless and action cams", "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400&q=80", "electronics"),
    ("Smartwatches", "smartwatches", "Wearables and fitness trackers", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&q=80", "electronics"),
    ("Men's Wear", "mens-wear", "Shirts, trousers and more", "https://images.unsplash.com/photo-1490578474895-699cd4e2cf59?w=400&q=80", "clothing-fashion"),
    ("Women's Wear", "womens-wear", "Dresses, tops and more", "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&q=80", "clothing-fashion"),
    ("Footwear", "footwear", "Shoes, sandals and boots", "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80", "clothing-fashion"),
    ("Fresh Produce", "fresh-produce", "Fruits and vegetables", "https://images.unsplash.com/photo-1540420773420-3bd48dbb4da4?w=400&q=80", "food-groceries"),
    ("Snacks & Beverages", "snacks-beverages", "Packaged snacks and drinks", "https://images.unsplash.com/photo-1621939182374-56b2424855ea?w=400&q=80", "food-groceries"),
    ("Dairy & Eggs", "dairy-eggs", "Milk, cheese and eggs", "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80", "food-groceries"),
    ("Furniture", "furniture", "Sofas, beds and tables", "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&q=80", "home-kitchen"),
    ("Kitchen Appliances", "kitchen-appliances", "Blenders, ovens and more", "https://images.unsplash.com/photo-1585515656781-44eed0b73900?w=400&q=80", "home-kitchen"),
    ("Fiction", "fiction", "Novels and stories", "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80", "books-stationery"),
    ("Non-Fiction", "non-fiction", "Self-help and knowledge", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80", "books-stationery"),
    ("Exercise Equipment", "exercise-equipment", "Dumbbells, mats and machines", "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=400&q=80", "sports-fitness"),
    ("Supplements", "supplements", "Protein, vitamins and nutrition", "https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=400&q=80", "sports-fitness"),
    ("Skincare", "skincare", "Creams, serums and cleansers", "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&q=80", "beauty-personal-care"),
    ("Haircare", "haircare", "Shampoos, conditioners and oils", "https://images.unsplash.com/photo-1585232350483-f24dabd2b2f2?w=400&q=80", "beauty-personal-care"),
    ("Board Games & Puzzles", "board-games-puzzles", "Family and strategy games", "https://images.unsplash.com/photo-1606503825008-909a67e63c3d?w=400&q=80", "toys-games"),
]

# (name, slug, price, compare_price, sku, stock, image_url, category_slug)
PRODUCTS = [
    # ── SMARTPHONES (15) ──────────────────────────────────────────────────────
    ("iPhone 15 Pro", "iphone-15-pro", "999.99", "1099.99", "APL-IP15P", 50, "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400&q=80", "smartphones"),
    ("Samsung Galaxy S24 Ultra", "samsung-galaxy-s24-ultra", "1199.99", "1299.99", "SAM-GS24U", 40, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&q=80", "smartphones"),
    ("Google Pixel 8 Pro", "google-pixel-8-pro", "999.99", "1099.99", "GOG-PX8P", 45, "https://images.unsplash.com/photo-1601784551446-5498fd0b8083?w=400&q=80", "smartphones"),
    ("OnePlus 12", "oneplus-12", "649.99", "729.99", "OPL-12", 60, "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400&q=80", "smartphones"),
    ("Xiaomi 14 Pro", "xiaomi-14-pro", "599.99", "699.99", "XMI-14P", 80, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&q=80", "smartphones"),
    ("iPhone 14", "iphone-14", "699.99", "799.99", "APL-IP14", 55, "https://images.unsplash.com/photo-1601784551446-5498fd0b8083?w=400&q=80", "smartphones"),
    ("Samsung Galaxy A54", "samsung-galaxy-a54", "399.99", "449.99", "SAM-A54", 100, "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400&q=80", "smartphones"),
    ("Realme 11 Pro+", "realme-11-pro-plus", "349.99", "399.99", "RLM-11PP", 90, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&q=80", "smartphones"),
    ("Motorola Edge 50", "motorola-edge-50", "449.99", "499.99", "MOT-E50", 70, "https://images.unsplash.com/photo-1601784551446-5498fd0b8083?w=400&q=80", "smartphones"),
    ("Vivo V30 Pro", "vivo-v30-pro", "499.99", "559.99", "VIV-V30P", 65, "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400&q=80", "smartphones"),
    ("Nokia G42 5G", "nokia-g42-5g", "249.99", "299.99", "NOK-G42", 120, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&q=80", "smartphones"),
    ("Oppo Reno 11 Pro", "oppo-reno-11-pro", "499.99", "579.99", "OPP-R11P", 85, "https://images.unsplash.com/photo-1601784551446-5498fd0b8083?w=400&q=80", "smartphones"),
    ("iQOO 12 5G", "iqoo-12-5g", "549.99", "649.99", "IQO-12", 40, "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400&q=80", "smartphones"),
    ("Samsung Galaxy Z Flip 5", "samsung-galaxy-z-flip-5", "999.99", "1099.99", "SAM-ZF5", 30, "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&q=80", "smartphones"),
    ("Nothing Phone 2a", "nothing-phone-2a", "349.99", "399.99", "NTH-P2A", 75, "https://images.unsplash.com/photo-1601784551446-5498fd0b8083?w=400&q=80", "smartphones"),

    # ── LAPTOPS (12) ──────────────────────────────────────────────────────────
    ("MacBook Pro 14-inch M3", "macbook-pro-14-m3", "1999.99", "2199.99", "APL-MBP14M3", 30, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&q=80", "laptops"),
    ("Dell XPS 15", "dell-xps-15", "1599.99", "1799.99", "DEL-XPS15", 40, "https://images.unsplash.com/photo-1541807084-db929da4f1ef?w=400&q=80", "laptops"),
    ("HP Spectre x360 14", "hp-spectre-x360-14", "1399.99", "1599.99", "HP-SX360", 35, "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&q=80", "laptops"),
    ("Lenovo ThinkPad X1 Carbon", "lenovo-thinkpad-x1-carbon", "1499.99", "1699.99", "LEN-TPX1C", 25, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&q=80", "laptops"),
    ("ASUS ROG Zephyrus G14", "asus-rog-zephyrus-g14", "1299.99", "1499.99", "ASU-ROGZG14", 20, "https://images.unsplash.com/photo-1541807084-db929da4f1ef?w=400&q=80", "laptops"),
    ("Microsoft Surface Pro 9", "microsoft-surface-pro-9", "1099.99", "1299.99", "MSF-SP9", 45, "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&q=80", "laptops"),
    ("MacBook Air M2", "macbook-air-m2", "1099.99", "1299.99", "APL-MBAM2", 50, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&q=80", "laptops"),
    ("Acer Swift 3 OLED", "acer-swift-3-oled", "649.99", "749.99", "ACR-SW3O", 60, "https://images.unsplash.com/photo-1541807084-db929da4f1ef?w=400&q=80", "laptops"),
    ("Razer Blade 15", "razer-blade-15", "2499.99", "2699.99", "RZR-B15", 15, "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&q=80", "laptops"),
    ("HP Pavilion 15", "hp-pavilion-15", "549.99", "649.99", "HP-PAV15", 80, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&q=80", "laptops"),
    ("Lenovo IdeaPad Slim 5", "lenovo-ideapad-slim-5", "699.99", "799.99", "LEN-IDS5", 55, "https://images.unsplash.com/photo-1541807084-db929da4f1ef?w=400&q=80", "laptops"),
    ("Dell Inspiron 14 2-in-1", "dell-inspiron-14-2in1", "799.99", "899.99", "DEL-INS14", 45, "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&q=80", "laptops"),

    # ── HEADPHONES & AUDIO (10) ───────────────────────────────────────────────
    ("Sony WH-1000XM5", "sony-wh-1000xm5", "349.99", "399.99", "SNY-WH1000XM5", 100, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80", "headphones-audio"),
    ("Apple AirPods Pro 2nd Gen", "apple-airpods-pro-2", "249.99", "279.99", "APL-APP2", 150, "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=400&q=80", "headphones-audio"),
    ("Bose QuietComfort 45", "bose-quietcomfort-45", "329.99", "379.99", "BOS-QC45", 80, "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400&q=80", "headphones-audio"),
    ("Samsung Galaxy Buds2 Pro", "samsung-galaxy-buds2-pro", "199.99", "229.99", "SAM-GB2P", 120, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80", "headphones-audio"),
    ("JBL Charge 5 Speaker", "jbl-charge-5-speaker", "179.99", "199.99", "JBL-C5", 90, "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=400&q=80", "headphones-audio"),
    ("Sennheiser HD 450BT", "sennheiser-hd-450bt", "149.99", "199.99", "SEN-HD450BT", 70, "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400&q=80", "headphones-audio"),
    ("Sony WF-1000XM5 Earbuds", "sony-wf-1000xm5-earbuds", "279.99", "299.99", "SNY-WF1000XM5", 110, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80", "headphones-audio"),
    ("Marshall Emberton II Speaker", "marshall-emberton-ii", "149.99", "179.99", "MRS-EB2", 60, "https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=400&q=80", "headphones-audio"),
    ("Jabra Elite 85h", "jabra-elite-85h", "249.99", "299.99", "JBR-E85H", 55, "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400&q=80", "headphones-audio"),
    ("Anker Soundcore Q45", "anker-soundcore-q45", "79.99", "99.99", "ANK-SCQ45", 200, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80", "headphones-audio"),

    # ── CAMERAS (8) ───────────────────────────────────────────────────────────
    ("Canon EOS R6 Mark II", "canon-eos-r6-mark-ii", "2499.99", "2799.99", "CAN-EOSR6M2", 20, "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400&q=80", "cameras"),
    ("Sony Alpha A7 IV", "sony-alpha-a7-iv", "2499.99", "2699.99", "SNY-A7IV", 18, "https://images.unsplash.com/photo-1502982720700-bfff97f2ecac?w=400&q=80", "cameras"),
    ("Nikon Z6 III", "nikon-z6-iii", "1999.99", "2299.99", "NIK-Z6III", 22, "https://images.unsplash.com/photo-1585652757173-349571e57e21?w=400&q=80", "cameras"),
    ("Fujifilm X-T5", "fujifilm-x-t5", "1699.99", "1899.99", "FUJ-XT5", 25, "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400&q=80", "cameras"),
    ("GoPro Hero 12 Black", "gopro-hero-12-black", "399.99", "449.99", "GOP-H12B", 75, "https://images.unsplash.com/photo-1502982720700-bfff97f2ecac?w=400&q=80", "cameras"),
    ("Canon EOS M50 Mark II", "canon-eos-m50-mark-ii", "649.99", "749.99", "CAN-M50M2", 40, "https://images.unsplash.com/photo-1585652757173-349571e57e21?w=400&q=80", "cameras"),
    ("DJI Osmo Pocket 3", "dji-osmo-pocket-3", "519.99", "599.99", "DJI-OP3", 50, "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400&q=80", "cameras"),
    ("Sony ZV-E10 Vlog Camera", "sony-zv-e10", "749.99", "849.99", "SNY-ZVE10", 35, "https://images.unsplash.com/photo-1502982720700-bfff97f2ecac?w=400&q=80", "cameras"),

    # ── SMARTWATCHES (8) ──────────────────────────────────────────────────────
    ("Apple Watch Series 9 45mm", "apple-watch-series-9-45mm", "429.99", "499.99", "APL-AWS9-45", 80, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&q=80", "smartwatches"),
    ("Samsung Galaxy Watch 6 Classic", "samsung-galaxy-watch-6-classic", "349.99", "399.99", "SAM-GW6C", 70, "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400&q=80", "smartwatches"),
    ("Garmin Forerunner 965", "garmin-forerunner-965", "599.99", "649.99", "GAR-FR965", 35, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&q=80", "smartwatches"),
    ("Fitbit Charge 6", "fitbit-charge-6", "159.99", "179.99", "FIT-CHG6", 120, "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400&q=80", "smartwatches"),
    ("Google Pixel Watch 2", "google-pixel-watch-2", "349.99", "399.99", "GOG-PW2", 60, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&q=80", "smartwatches"),
    ("Amazfit GTR 4", "amazfit-gtr-4", "179.99", "219.99", "AMZ-GTR4", 90, "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400&q=80", "smartwatches"),
    ("Garmin Venu 3S", "garmin-venu-3s", "449.99", "499.99", "GAR-VEN3S", 40, "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&q=80", "smartwatches"),
    ("Noise ColorFit Ultra 3", "noise-colorfit-ultra-3", "79.99", "99.99", "NSE-CFU3", 150, "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400&q=80", "smartwatches"),

    # ── MEN'S WEAR (12) ───────────────────────────────────────────────────────
    ("Classic White Oxford Shirt", "classic-white-oxford-shirt", "49.99", "69.99", "MNS-CWS01", 150, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80", "mens-wear"),
    ("Slim Fit Navy Chinos", "slim-fit-navy-chinos", "59.99", "79.99", "MNS-SNC01", 120, "https://images.unsplash.com/photo-1490578474895-699cd4e2cf59?w=400&q=80", "mens-wear"),
    ("Classic Denim Jacket", "classic-denim-jacket", "89.99", "119.99", "MNS-CDJ01", 80, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80", "mens-wear"),
    ("Formal Black Blazer", "formal-black-blazer", "149.99", "199.99", "MNS-FBB01", 60, "https://images.unsplash.com/photo-1490578474895-699cd4e2cf59?w=400&q=80", "mens-wear"),
    ("Cotton Polo T-Shirt", "cotton-polo-t-shirt", "29.99", "39.99", "MNS-CPT01", 200, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80", "mens-wear"),
    ("Casual Linen Shirt", "casual-linen-shirt", "44.99", "59.99", "MNS-CLS01", 130, "https://images.unsplash.com/photo-1490578474895-699cd4e2cf59?w=400&q=80", "mens-wear"),
    ("Stretch Fit Jeans", "stretch-fit-jeans", "69.99", "89.99", "MNS-SFJ01", 100, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80", "mens-wear"),
    ("Wool Crew Neck Sweater", "wool-crew-neck-sweater", "79.99", "99.99", "MNS-WCS01", 90, "https://images.unsplash.com/photo-1490578474895-699cd4e2cf59?w=400&q=80", "mens-wear"),
    ("Cargo Shorts", "cargo-shorts", "39.99", "49.99", "MNS-CRS01", 140, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80", "mens-wear"),
    ("Graphic Print Tee", "graphic-print-tee", "24.99", "34.99", "MNS-GPT01", 200, "https://images.unsplash.com/photo-1490578474895-699cd4e2cf59?w=400&q=80", "mens-wear"),
    ("Hooded Sweatshirt", "hooded-sweatshirt", "54.99", "74.99", "MNS-HSW01", 110, "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80", "mens-wear"),
    ("Formal Dress Trousers", "formal-dress-trousers", "74.99", "94.99", "MNS-FDT01", 70, "https://images.unsplash.com/photo-1490578474895-699cd4e2cf59?w=400&q=80", "mens-wear"),

    # ── WOMEN'S WEAR (12) ─────────────────────────────────────────────────────
    ("Floral Summer Dress", "floral-summer-dress", "59.99", "79.99", "WMN-FSD01", 120, "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&q=80", "womens-wear"),
    ("Silk Blouse", "silk-blouse", "69.99", "89.99", "WMN-SBL01", 80, "https://images.unsplash.com/photo-1568252542512-9fe8fe9c87bb?w=400&q=80", "womens-wear"),
    ("High-Waist Skinny Jeans", "high-waist-skinny-jeans", "79.99", "99.99", "WMN-HWJ01", 100, "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&q=80", "womens-wear"),
    ("Knit Cardigan", "knit-cardigan", "64.99", "84.99", "WMN-KCD01", 90, "https://images.unsplash.com/photo-1568252542512-9fe8fe9c87bb?w=400&q=80", "womens-wear"),
    ("Elegant Maxi Dress", "elegant-maxi-dress", "89.99", "119.99", "WMN-EMD01", 70, "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&q=80", "womens-wear"),
    ("Crop Top", "crop-top", "24.99", "34.99", "WMN-CTP01", 200, "https://images.unsplash.com/photo-1568252542512-9fe8fe9c87bb?w=400&q=80", "womens-wear"),
    ("Wide Leg Trousers", "wide-leg-trousers", "69.99", "89.99", "WMN-WLT01", 85, "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&q=80", "womens-wear"),
    ("Women's Blazer Jacket", "womens-blazer-jacket", "124.99", "159.99", "WMN-BJK01", 55, "https://images.unsplash.com/photo-1568252542512-9fe8fe9c87bb?w=400&q=80", "womens-wear"),
    ("Denim Skirt", "denim-skirt", "44.99", "59.99", "WMN-DSK01", 110, "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&q=80", "womens-wear"),
    ("Printed Kurta Set", "printed-kurta-set", "54.99", "74.99", "WMN-PKS01", 130, "https://images.unsplash.com/photo-1568252542512-9fe8fe9c87bb?w=400&q=80", "womens-wear"),
    ("Linen Co-ord Set", "linen-co-ord-set", "79.99", "99.99", "WMN-LCS01", 75, "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=400&q=80", "womens-wear"),
    ("Sports Leggings", "sports-leggings", "39.99", "49.99", "WMN-SPL01", 180, "https://images.unsplash.com/photo-1568252542512-9fe8fe9c87bb?w=400&q=80", "womens-wear"),

    # ── FOOTWEAR (10) ─────────────────────────────────────────────────────────
    ("Nike Air Max 270", "nike-air-max-270", "129.99", "159.99", "FTW-NAM270", 100, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80", "footwear"),
    ("Adidas Ultraboost 23", "adidas-ultraboost-23", "179.99", "199.99", "FTW-AUB23", 80, "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&q=80", "footwear"),
    ("Puma RS-X Sneakers", "puma-rs-x-sneakers", "99.99", "129.99", "FTW-PRSX", 110, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80", "footwear"),
    ("Leather Oxford Shoes", "leather-oxford-shoes", "119.99", "149.99", "FTW-LOX01", 60, "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&q=80", "footwear"),
    ("Women's Ballet Flats", "womens-ballet-flats", "49.99", "69.99", "FTW-WBF01", 130, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80", "footwear"),
    ("Chelsea Boots", "chelsea-boots", "139.99", "169.99", "FTW-CHB01", 70, "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&q=80", "footwear"),
    ("Flip Flops & Slippers", "flip-flops-slippers", "19.99", "29.99", "FTW-FFS01", 300, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80", "footwear"),
    ("New Balance 574", "new-balance-574", "89.99", "109.99", "FTW-NB574", 90, "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&q=80", "footwear"),
    ("Running Shoes Pro", "running-shoes-pro", "74.99", "94.99", "FTW-RSP01", 120, "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80", "footwear"),
    ("Ankle Strap Sandals", "ankle-strap-sandals", "44.99", "59.99", "FTW-ASS01", 100, "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=400&q=80", "footwear"),

    # ── FRESH PRODUCE (13) ────────────────────────────────────────────────────
    ("Organic Bananas (1 kg)", "organic-bananas-1kg", "1.99", "2.49", "PRD-OBN01", 500, "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400&q=80", "fresh-produce"),
    ("Red Apples (1 kg)", "red-apples-1kg", "2.99", "3.49", "PRD-RAP01", 400, "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400&q=80", "fresh-produce"),
    ("Mixed Salad Greens (250g)", "mixed-salad-greens-250g", "3.49", "3.99", "PRD-MSG01", 200, "https://images.unsplash.com/photo-1540420773420-3bd48dbb4da4?w=400&q=80", "fresh-produce"),
    ("Cherry Tomatoes (500g)", "cherry-tomatoes-500g", "2.49", "2.99", "PRD-CTM01", 300, "https://images.unsplash.com/photo-1561136594-7f68813d8d4b?w=400&q=80", "fresh-produce"),
    ("Avocados (2 pack)", "avocados-2-pack", "3.99", "4.99", "PRD-AVO01", 250, "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?w=400&q=80", "fresh-produce"),
    ("Baby Carrots (500g)", "baby-carrots-500g", "1.79", "2.29", "PRD-BCR01", 400, "https://images.unsplash.com/photo-1540420773420-3bd48dbb4da4?w=400&q=80", "fresh-produce"),
    ("Broccoli (500g)", "broccoli-500g", "2.29", "2.79", "PRD-BRC01", 300, "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400&q=80", "fresh-produce"),
    ("Mango (1 kg)", "mango-1kg", "3.99", "4.99", "PRD-MNG01", 200, "https://images.unsplash.com/photo-1567306226416-28f0efdc88ce?w=400&q=80", "fresh-produce"),
    ("Spinach Leaves (200g)", "spinach-leaves-200g", "2.49", "2.99", "PRD-SPN01", 350, "https://images.unsplash.com/photo-1540420773420-3bd48dbb4da4?w=400&q=80", "fresh-produce"),
    ("Oranges (1 kg)", "oranges-1kg", "2.99", "3.49", "PRD-ORG01", 450, "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400&q=80", "fresh-produce"),
    ("Strawberries (400g)", "strawberries-400g", "4.49", "4.99", "PRD-STW01", 180, "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=400&q=80", "fresh-produce"),
    ("Sweet Corn (3 pack)", "sweet-corn-3-pack", "2.99", "3.49", "PRD-SCN01", 220, "https://images.unsplash.com/photo-1540420773420-3bd48dbb4da4?w=400&q=80", "fresh-produce"),
    ("Watermelon (whole)", "watermelon-whole", "6.99", "7.99", "PRD-WML01", 80, "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400&q=80", "fresh-produce"),

    # ── SNACKS & BEVERAGES (10) ───────────────────────────────────────────────
    ("Lay's Classic Chips (200g)", "lays-classic-chips-200g", "2.49", "2.99", "SNK-LCC01", 500, "https://images.unsplash.com/photo-1621939182374-56b2424855ea?w=400&q=80", "snacks-beverages"),
    ("Coca-Cola 6-pack (330ml)", "coca-cola-6pack-330ml", "4.99", "5.99", "BEV-CCL06", 300, "https://images.unsplash.com/photo-1561758033-7e924f619b47?w=400&q=80", "snacks-beverages"),
    ("Cadbury Dairy Milk (200g)", "cadbury-dairy-milk-200g", "3.49", "3.99", "SNK-CDM01", 400, "https://images.unsplash.com/photo-1621939182374-56b2424855ea?w=400&q=80", "snacks-beverages"),
    ("Tropicana Orange Juice (1L)", "tropicana-orange-juice-1l", "3.99", "4.49", "BEV-TOJ01", 250, "https://images.unsplash.com/photo-1561758033-7e924f619b47?w=400&q=80", "snacks-beverages"),
    ("Pringles Original (165g)", "pringles-original-165g", "2.99", "3.49", "SNK-PRO01", 350, "https://images.unsplash.com/photo-1621939182374-56b2424855ea?w=400&q=80", "snacks-beverages"),
    ("Green Tea Bags (25 pack)", "green-tea-bags-25pack", "4.99", "5.99", "BEV-GTB25", 300, "https://images.unsplash.com/photo-1561758033-7e924f619b47?w=400&q=80", "snacks-beverages"),
    ("Mixed Nuts Assorted (500g)", "mixed-nuts-assorted-500g", "8.99", "10.99", "SNK-MNA01", 200, "https://images.unsplash.com/photo-1621939182374-56b2424855ea?w=400&q=80", "snacks-beverages"),
    ("Sparkling Water 6-pack", "sparkling-water-6pack", "3.49", "3.99", "BEV-SPW06", 400, "https://images.unsplash.com/photo-1561758033-7e924f619b47?w=400&q=80", "snacks-beverages"),
    ("Dark Chocolate Bar (100g)", "dark-chocolate-bar-100g", "2.49", "2.99", "SNK-DCB01", 600, "https://images.unsplash.com/photo-1621939182374-56b2424855ea?w=400&q=80", "snacks-beverages"),
    ("Energy Drink 4-pack (250ml)", "energy-drink-4pack-250ml", "5.99", "7.99", "BEV-END04", 250, "https://images.unsplash.com/photo-1561758033-7e924f619b47?w=400&q=80", "snacks-beverages"),

    # ── DAIRY & EGGS (8) ──────────────────────────────────────────────────────
    ("Full Cream Milk (2L)", "full-cream-milk-2l", "2.99", "3.29", "DAI-FCM02", 300, "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80", "dairy-eggs"),
    ("Greek Yogurt (500g)", "greek-yogurt-500g", "3.49", "3.99", "DAI-GYG01", 200, "https://images.unsplash.com/photo-1571212515416-fef01fc43637?w=400&q=80", "dairy-eggs"),
    ("Cheddar Cheese Block (400g)", "cheddar-cheese-400g", "4.99", "5.99", "DAI-CCB01", 150, "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80", "dairy-eggs"),
    ("Free Range Eggs (12 pack)", "free-range-eggs-12pack", "4.49", "4.99", "DAI-FRE12", 400, "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?w=400&q=80", "dairy-eggs"),
    ("Unsalted Butter (250g)", "unsalted-butter-250g", "2.49", "2.99", "DAI-BUT01", 250, "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80", "dairy-eggs"),
    ("Cream Cheese (200g)", "cream-cheese-200g", "2.99", "3.49", "DAI-CCH01", 180, "https://images.unsplash.com/photo-1571212515416-fef01fc43637?w=400&q=80", "dairy-eggs"),
    ("Almond Milk (1L)", "almond-milk-1l", "3.99", "4.49", "DAI-ALM01", 200, "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80", "dairy-eggs"),
    ("Fresh Mozzarella (250g)", "fresh-mozzarella-250g", "3.49", "3.99", "DAI-MOZ01", 160, "https://images.unsplash.com/photo-1571212515416-fef01fc43637?w=400&q=80", "dairy-eggs"),

    # ── FURNITURE (8) ─────────────────────────────────────────────────────────
    ("3-Seater Fabric Sofa", "3-seater-fabric-sofa", "699.99", "899.99", "FRN-3SF01", 20, "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&q=80", "furniture"),
    ("Queen Size Bed Frame", "queen-size-bed-frame", "549.99", "699.99", "FRN-QBF01", 15, "https://images.unsplash.com/photo-1617325247661-675ab4b64ae2?w=400&q=80", "furniture"),
    ("Wooden Dining Table (6-seat)", "wooden-dining-table-6seat", "799.99", "999.99", "FRN-WDT06", 10, "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&q=80", "furniture"),
    ("Ergonomic Office Chair", "ergonomic-office-chair", "349.99", "449.99", "FRN-EOC01", 40, "https://images.unsplash.com/photo-1617325247661-675ab4b64ae2?w=400&q=80", "furniture"),
    ("Bookshelf 5-Tier", "bookshelf-5-tier", "199.99", "249.99", "FRN-BSH05", 30, "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&q=80", "furniture"),
    ("Glass-Top Coffee Table", "glass-top-coffee-table", "279.99", "349.99", "FRN-CTG01", 25, "https://images.unsplash.com/photo-1617325247661-675ab4b64ae2?w=400&q=80", "furniture"),
    ("3-Door Wardrobe", "3-door-wardrobe", "649.99", "799.99", "FRN-W3D01", 12, "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&q=80", "furniture"),
    ("TV Cabinet with Storage", "tv-cabinet-with-storage", "299.99", "379.99", "FRN-TVC01", 20, "https://images.unsplash.com/photo-1617325247661-675ab4b64ae2?w=400&q=80", "furniture"),

    # ── KITCHEN APPLIANCES (12) ───────────────────────────────────────────────
    ("Instant Pot Duo 7-in-1 (6L)", "instant-pot-duo-7in1-6l", "99.99", "129.99", "KCH-IPD01", 60, "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&q=80", "kitchen-appliances"),
    ("Ninja Professional Blender", "ninja-professional-blender", "79.99", "99.99", "KCH-NPB01", 80, "https://images.unsplash.com/photo-1585515656781-44eed0b73900?w=400&q=80", "kitchen-appliances"),
    ("Philips Air Fryer XL (6.2L)", "philips-air-fryer-xl", "149.99", "189.99", "KCH-PAF01", 50, "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&q=80", "kitchen-appliances"),
    ("KitchenAid Stand Mixer 4.8L", "kitchenaid-stand-mixer-4-8l", "399.99", "479.99", "KCH-KSM01", 25, "https://images.unsplash.com/photo-1585515656781-44eed0b73900?w=400&q=80", "kitchen-appliances"),
    ("Breville Espresso Machine", "breville-espresso-machine", "599.99", "699.99", "KCH-BEM01", 20, "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&q=80", "kitchen-appliances"),
    ("Microwave Oven 30L", "microwave-oven-30l", "129.99", "159.99", "KCH-MWO01", 45, "https://images.unsplash.com/photo-1585515656781-44eed0b73900?w=400&q=80", "kitchen-appliances"),
    ("Electric Kettle 1.7L", "electric-kettle-1-7l", "39.99", "49.99", "KCH-EKT01", 150, "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&q=80", "kitchen-appliances"),
    ("Non-Stick Cookware Set 5pc", "non-stick-cookware-set-5pc", "89.99", "119.99", "KCH-NSC05", 70, "https://images.unsplash.com/photo-1585515656781-44eed0b73900?w=400&q=80", "kitchen-appliances"),
    ("4-Slice Toaster", "4-slice-toaster", "49.99", "64.99", "KCH-TST04", 100, "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&q=80", "kitchen-appliances"),
    ("Food Processor 2L", "food-processor-2l", "119.99", "149.99", "KCH-FPR01", 40, "https://images.unsplash.com/photo-1585515656781-44eed0b73900?w=400&q=80", "kitchen-appliances"),
    ("Rice Cooker 1.8L", "rice-cooker-1-8l", "59.99", "79.99", "KCH-RC18", 90, "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&q=80", "kitchen-appliances"),
    ("Hand Mixer 5-Speed", "hand-mixer-5-speed", "34.99", "44.99", "KCH-HMX05", 80, "https://images.unsplash.com/photo-1585515656781-44eed0b73900?w=400&q=80", "kitchen-appliances"),

    # ── FICTION (8) ───────────────────────────────────────────────────────────
    ("The Midnight Library", "the-midnight-library", "14.99", "18.99", "BK-TML01", 100, "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80", "fiction"),
    ("The Alchemist", "the-alchemist", "12.99", "15.99", "BK-TAL01", 200, "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&q=80", "fiction"),
    ("Dune", "dune-frank-herbert", "14.99", "17.99", "BK-DUN01", 120, "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80", "fiction"),
    ("1984 by George Orwell", "1984-george-orwell", "10.99", "13.99", "BK-1984", 180, "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&q=80", "fiction"),
    ("The Great Gatsby", "the-great-gatsby", "9.99", "12.99", "BK-TGG01", 160, "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80", "fiction"),
    ("Harry Potter Box Set (7 books)", "harry-potter-box-set", "89.99", "109.99", "BK-HPB01", 50, "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&q=80", "fiction"),
    ("The Hunger Games Trilogy", "hunger-games-trilogy", "34.99", "44.99", "BK-HGT01", 75, "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80", "fiction"),
    ("Project Hail Mary", "project-hail-mary", "15.99", "19.99", "BK-PHM01", 90, "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=400&q=80", "fiction"),

    # ── NON-FICTION (8) ───────────────────────────────────────────────────────
    ("Atomic Habits", "atomic-habits", "16.99", "19.99", "BK-AHB01", 150, "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80", "non-fiction"),
    ("Sapiens: A Brief History of Humankind", "sapiens-brief-history", "17.99", "21.99", "BK-SAP01", 120, "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80", "non-fiction"),
    ("The Power of Now", "the-power-of-now", "14.99", "17.99", "BK-PON01", 90, "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80", "non-fiction"),
    ("Rich Dad Poor Dad", "rich-dad-poor-dad", "13.99", "16.99", "BK-RDP01", 200, "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80", "non-fiction"),
    ("Deep Work", "deep-work", "15.99", "18.99", "BK-DPW01", 80, "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80", "non-fiction"),
    ("The 7 Habits of Highly Effective People", "7-habits-effective-people", "14.99", "17.99", "BK-7HH01", 100, "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80", "non-fiction"),
    ("The Psychology of Money", "psychology-of-money", "15.99", "18.99", "BK-POM01", 110, "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80", "non-fiction"),
    ("Thinking, Fast and Slow", "thinking-fast-and-slow", "16.99", "19.99", "BK-TFS01", 100, "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=400&q=80", "non-fiction"),

    # ── EXERCISE EQUIPMENT (10) ───────────────────────────────────────────────
    ("Adjustable Dumbbell Set (20kg)", "adjustable-dumbbell-set-20kg", "129.99", "169.99", "SPT-ADS20", 40, "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=400&q=80", "exercise-equipment"),
    ("Yoga Mat with Carry Strap", "yoga-mat-with-carry-strap", "29.99", "39.99", "SPT-YMS01", 200, "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&q=80", "exercise-equipment"),
    ("Resistance Bands Set (5pc)", "resistance-bands-set-5pc", "24.99", "34.99", "SPT-RBS05", 300, "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=400&q=80", "exercise-equipment"),
    ("Door-Mounted Pull-Up Bar", "door-mounted-pull-up-bar", "34.99", "44.99", "SPT-PUB01", 150, "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&q=80", "exercise-equipment"),
    ("Speed Skipping Rope", "speed-skipping-rope", "14.99", "19.99", "SPT-SRS01", 400, "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=400&q=80", "exercise-equipment"),
    ("Foam Roller 60cm", "foam-roller-60cm", "24.99", "34.99", "SPT-FR60", 100, "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&q=80", "exercise-equipment"),
    ("Stationary Exercise Bike", "stationary-exercise-bike", "399.99", "499.99", "SPT-EBS01", 15, "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=400&q=80", "exercise-equipment"),
    ("Kettlebell Cast Iron 16kg", "kettlebell-cast-iron-16kg", "59.99", "79.99", "SPT-KB16", 60, "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&q=80", "exercise-equipment"),
    ("Battle Rope 15m", "battle-rope-15m", "89.99", "119.99", "SPT-BR15", 30, "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=400&q=80", "exercise-equipment"),
    ("Ab Roller Wheel", "ab-roller-wheel", "19.99", "29.99", "SPT-ABR01", 200, "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&q=80", "exercise-equipment"),

    # ── SUPPLEMENTS (8) ───────────────────────────────────────────────────────
    ("Whey Protein Powder Chocolate (1kg)", "whey-protein-chocolate-1kg", "49.99", "64.99", "SUP-WPC01", 120, "https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=400&q=80", "supplements"),
    ("Creatine Monohydrate (500g)", "creatine-monohydrate-500g", "29.99", "39.99", "SUP-CRM01", 150, "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&q=80", "supplements"),
    ("BCAA Powder Watermelon (400g)", "bcaa-powder-watermelon-400g", "34.99", "44.99", "SUP-BCA01", 100, "https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=400&q=80", "supplements"),
    ("Multivitamin Tablets (90 count)", "multivitamin-tablets-90", "19.99", "24.99", "SUP-MV90", 250, "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&q=80", "supplements"),
    ("Omega-3 Fish Oil (60 caps)", "omega-3-fish-oil-60caps", "22.99", "29.99", "SUP-OM360", 200, "https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=400&q=80", "supplements"),
    ("Pre-Workout Energy Powder (300g)", "pre-workout-energy-powder-300g", "39.99", "49.99", "SUP-PWO01", 90, "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&q=80", "supplements"),
    ("Plant-Based Protein Powder (900g)", "plant-based-protein-900g", "54.99", "69.99", "SUP-PBP01", 70, "https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=400&q=80", "supplements"),
    ("Vitamin D3 + K2 Drops (30ml)", "vitamin-d3-k2-drops-30ml", "24.99", "34.99", "SUP-VDK01", 180, "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&q=80", "supplements"),

    # ── SKINCARE (10) ─────────────────────────────────────────────────────────
    ("CeraVe Moisturizing Cream (340g)", "cerave-moisturizing-cream-340g", "19.99", "24.99", "SKN-CVC01", 200, "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&q=80", "skincare"),
    ("The Ordinary Niacinamide 10% (30ml)", "ordinary-niacinamide-10-30ml", "7.99", "9.99", "SKN-TON01", 300, "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&q=80", "skincare"),
    ("Neutrogena Hydro Boost Gel (50ml)", "neutrogena-hydro-boost-gel-50ml", "22.99", "27.99", "SKN-NHB01", 150, "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&q=80", "skincare"),
    ("SPF 50+ Sunscreen (100ml)", "spf-50-sunscreen-100ml", "14.99", "18.99", "SKN-SPF50", 250, "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&q=80", "skincare"),
    ("Vitamin C Brightening Serum (30ml)", "vitamin-c-brightening-serum-30ml", "24.99", "34.99", "SKN-VCS01", 180, "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&q=80", "skincare"),
    ("Retinol Eye Cream (15ml)", "retinol-eye-cream-15ml", "29.99", "39.99", "SKN-REC01", 100, "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&q=80", "skincare"),
    ("Gentle Foaming Cleanser (200ml)", "gentle-foaming-cleanser-200ml", "12.99", "16.99", "SKN-GFC01", 200, "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&q=80", "skincare"),
    ("Hyaluronic Acid Serum (30ml)", "hyaluronic-acid-serum-30ml", "19.99", "24.99", "SKN-HAS01", 160, "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&q=80", "skincare"),
    ("Micellar Water (400ml)", "micellar-water-400ml", "10.99", "13.99", "SKN-MWA01", 220, "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&q=80", "skincare"),
    ("Kaolin Clay Face Mask (100ml)", "kaolin-clay-face-mask-100ml", "15.99", "19.99", "SKN-CFM01", 130, "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&q=80", "skincare"),

    # ── HAIRCARE (8) ──────────────────────────────────────────────────────────
    ("Pantene Pro-V Shampoo (400ml)", "pantene-pro-v-shampoo-400ml", "8.99", "10.99", "HRC-PPS01", 300, "https://images.unsplash.com/photo-1585232350483-f24dabd2b2f2?w=400&q=80", "haircare"),
    ("L'Oreal Elvive Conditioner (400ml)", "loreal-elvive-conditioner-400ml", "9.99", "11.99", "HRC-LEC01", 250, "https://images.unsplash.com/photo-1618160702438-9b02ab6515c9?w=400&q=80", "haircare"),
    ("Argan Oil Deep Hair Mask (200ml)", "argan-oil-deep-hair-mask-200ml", "17.99", "22.99", "HRC-AOH01", 150, "https://images.unsplash.com/photo-1585232350483-f24dabd2b2f2?w=400&q=80", "haircare"),
    ("Dyson Airwrap Complete Styler", "dyson-airwrap-complete-styler", "499.99", "599.99", "HRC-DAS01", 25, "https://images.unsplash.com/photo-1618160702438-9b02ab6515c9?w=400&q=80", "haircare"),
    ("Biotin Hair Growth Serum (50ml)", "biotin-hair-growth-serum-50ml", "24.99", "34.99", "HRC-BHG01", 200, "https://images.unsplash.com/photo-1585232350483-f24dabd2b2f2?w=400&q=80", "haircare"),
    ("Dry Shampoo Spray (200ml)", "dry-shampoo-spray-200ml", "11.99", "14.99", "HRC-DSS01", 300, "https://images.unsplash.com/photo-1618160702438-9b02ab6515c9?w=400&q=80", "haircare"),
    ("Ceramic Hair Straightener", "ceramic-hair-straightener", "79.99", "99.99", "HRC-HSC01", 60, "https://images.unsplash.com/photo-1585232350483-f24dabd2b2f2?w=400&q=80", "haircare"),
    ("Virgin Coconut Oil (200ml)", "virgin-coconut-oil-200ml", "9.99", "12.99", "HRC-COH01", 350, "https://images.unsplash.com/photo-1618160702438-9b02ab6515c9?w=400&q=80", "haircare"),

    # ── BOARD GAMES & PUZZLES (10) ────────────────────────────────────────────
    ("Catan Strategy Board Game", "catan-strategy-board-game", "44.99", "54.99", "TYG-CSB01", 60, "https://images.unsplash.com/photo-1606503825008-909a67e63c3d?w=400&q=80", "board-games-puzzles"),
    ("Monopoly Classic Edition", "monopoly-classic-edition", "29.99", "39.99", "TYG-MCE01", 80, "https://images.unsplash.com/photo-1606503825008-909a67e63c3d?w=400&q=80", "board-games-puzzles"),
    ("1000-Piece Jigsaw Puzzle", "1000-piece-jigsaw-puzzle", "19.99", "24.99", "TYG-JPZ01", 150, "https://images.unsplash.com/photo-1606503825008-909a67e63c3d?w=400&q=80", "board-games-puzzles"),
    ("Scrabble Deluxe Edition", "scrabble-deluxe-edition", "39.99", "49.99", "TYG-SDE01", 50, "https://images.unsplash.com/photo-1606503825008-909a67e63c3d?w=400&q=80", "board-games-puzzles"),
    ("Jenga Classic Wooden Game", "jenga-classic-wooden-game", "19.99", "24.99", "TYG-JCG01", 100, "https://images.unsplash.com/photo-1606503825008-909a67e63c3d?w=400&q=80", "board-games-puzzles"),
    ("Chess Set Wooden (12-inch)", "chess-set-wooden-12in", "34.99", "44.99", "TYG-CSW01", 70, "https://images.unsplash.com/photo-1606503825008-909a67e63c3d?w=400&q=80", "board-games-puzzles"),
    ("Pandemic Cooperative Game", "pandemic-cooperative-game", "44.99", "54.99", "TYG-PCG01", 45, "https://images.unsplash.com/photo-1606503825008-909a67e63c3d?w=400&q=80", "board-games-puzzles"),
    ("UNO Card Game", "uno-card-game", "9.99", "12.99", "TYG-UCG01", 250, "https://images.unsplash.com/photo-1606503825008-909a67e63c3d?w=400&q=80", "board-games-puzzles"),
    ("Ticket to Ride Board Game", "ticket-to-ride-board-game", "49.99", "59.99", "TYG-TTR01", 40, "https://images.unsplash.com/photo-1606503825008-909a67e63c3d?w=400&q=80", "board-games-puzzles"),
    ("Codenames Card Game", "codenames-card-game", "19.99", "24.99", "TYG-CDN01", 90, "https://images.unsplash.com/photo-1606503825008-909a67e63c3d?w=400&q=80", "board-games-puzzles"),
]


async def seed() -> None:
    async with Session() as session:
        # ── 1. Seed categories ────────────────────────────────────────────────
        cat_map: dict[str, Category] = {}

        for name, slug, desc, img, parent_slug in CATEGORIES:
            existing = (
                await session.execute(select(Category).where(Category.slug == slug))
            ).scalar_one_or_none()

            if existing:
                cat_map[slug] = existing
                continue

            parent_id = cat_map[parent_slug].id if parent_slug else None
            cat = Category(name=name, slug=slug, description=desc, image_url=img, parent_id=parent_id)
            session.add(cat)
            await session.flush()
            cat_map[slug] = cat

        # ── 2. Seed products ──────────────────────────────────────────────────
        seeded = skipped = 0

        for name, slug, price, compare_price, sku, stock, img, cat_slug in PRODUCTS:
            existing = (
                await session.execute(select(Product).where(Product.slug == slug))
            ).scalar_one_or_none()

            if existing:
                skipped += 1
                continue

            product = Product(
                name=name,
                slug=slug,
                price=Decimal(price),
                compare_price=Decimal(compare_price),
                sku=sku,
                stock_quantity=stock,
                image_url=img,
                category_id=cat_map[cat_slug].id,
            )
            session.add(product)
            seeded += 1

        await session.commit()
        print(f"Done — {seeded} products seeded, {skipped} already existed.")


if __name__ == "__main__":
    asyncio.run(seed())
