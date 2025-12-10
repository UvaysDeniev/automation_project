"""
Mappings and normalization helpers for item names and IDs.
This keeps the main automation script cleaner and easier to read.
"""

from __future__ import annotations
from typing import Dict, Optional
import re

# --- Item name normalization map ---
NAME_MAP: Dict[str, str] = {
    "otg six 31 mid back operator chair":                   "OTG Six31 Operator Chair, Mid-Back, Fabric Black",
    "stretch wrap red":                                   "Stretch Wrap, 3\" × 1 000′ roll (Red)",
    "uncorded earplugs":                                   "Uncorded Earplugs, Neon Yellow",
    "10 grams dpd powder":                                 "10 grams DPD Powder",
    "apple lightning":                                     "Apple Lightning 3.5 Headphone Jack",
    "bath towel white FtinessCo logo":                    "Bath Towels 25 x 50",
    "board dry erase":                                    "Board, Dry Erase",
    "black garbage can lid":                               "Black Garbage Can Lid",
    "clipboard":                                           "Clipboard, Masonite, Legal Size",
    "clax master":                                         "Clax Master, 18.9L Detergent",
    "cleaner toilet super crew 946ml crew super blue":      "Toilet Bowl Cleaner, Mild Acid",
    "toilet tissue jumbo 1000 box":                         "Toilet Paper",
    "remover stain clax hypo":                             "Clax Hypo, 18.9L Bleach",
    "hypo":                                                "Clax Hypo, 18.9L Bleach",
    "clockwise cleaner shower foaming":                    "Clockwise Shower Foaming Pops, 2 L",
    "ankle cuff replaces":                                 "COREFX Ankle Cuffs",
    # COREFX Kettlebells
    "corefx kettlebell 35lbs":                           "COREFX Kettlebell, 35 lbs",
    "premium vinyl dipped kettlebell": None,               # legacy—will never match if you strip SKU note
    "corefx kettlebell 60 lbs":                          "COREFX Kettlebell, 60 lbs",
    # COREFX Strength Bands (colors)
    'corefx strength band (41 x 13)  purple':          "COREFX Strength Band, Purple",
    "corefx strength band - red":             "COREFX Strength Band, Red",
    'corefx strength band (41" x 0.86") - black':          "COREFX Strength Band, Black",
    'corefx strength band (41" x 2.5") - green':           "COREFX Strength Band, Green",
    'corefx strength band (41" x 1.8") - orange':          "COREFX Strength Band, Orange",
    'corefx strength band (41" x 3.3") - blue':            "COREFX Strength Band, Blue",
    "corefx battle rope":                                  "COREFX Battle Rope",
    # COREFX Medicine Balls
    "corefx medicine ball 6lbs":                           "COREFX Medicine Ball, 6 lbs",
    "corefx medicine ball 10lbs":                          "COREFX Medicine Ball, 10 lbs",
    "corefx medicine ball 15lbs":                          "COREFX Medicine Ball, 15 lbs",
    "corefx medicine ball 20lbs":                          "COREFX Medicine Ball, 20 lbs",
    "deb instantfoam alcohol hand sanitizer":              "Deb Instant Foam Hand Sanitizer",
    "deb clear foam wash 1 litre":                         "Deb Clear Foam Wash",
    "deb hair body wash":                                  "Deb Hair & Body Wash",
    "deb hair conditioner 1 litre":                        "Deb Hair Conditioner",
    "deb pure restore 1 litre":                            "Deb Pure Restore Moisturizer",
    "dispenser towel tork elevation":                       "Dispenser Paper Towels",
    "dispenser deb pure restore":                          "Disenser Deb Pure Restore Moisturizer",
    "dispenser deb proline restore":                       "Dispenser Deb Proline Moisturizer",
    "dispenser deb proline hair body":                     "Dispenser Deb Proline Hair & Body Wash",
    "dispenser deb proline hair conditioner transparent":  "Dispenser Deb Proline Hair Conditioner",
    "dispenser deb proline hand soap":                     "Dispenser Deb Proline Hand Soap",
    "dispenser deb proline moisturizer":                   "Dispenser Deb Proline Moisturizer",
    "diversey clax deosoft":                               "Diversey CLAX Deosoft Fabric Softener",
    "dry erase marker expo fine":                          "Dry Erase Marker, Expo, Fine",
    "duracell procell aa alkaline":                        "Duracell Procell AA Batteries, 24-pack",
    "duracell procell aaa":                                "Duracell Procell AAA Batteries, 24-pack",
    "birthday card":                                       "FtinessCo Birthday Card",
    "equipment repair tags":                               "Equipment Repair Tags",
    "facial tissue tork advance":                          "Facial Tissue",
    "fit fix signs":                                       "Fit Fix Signs",
    "fitness planners":                                    "Fitness Planners",
    "give the gift of fitness":                            "Give The Gift Of Fitness Referral Sheet, Package of 100",
    "gloves small":                                        "Gloves, Small",
    "glance glass multi surface cleaner":                  "Glance Glass Cleaner SC , 2.5 L",
    "FtinessCo fitness sport bag":                          "FtinessCo Fitness Sport Bag",
    # --- WOMEN'S SHIRTS ---
    # FtinessCo Ladies All Associate 1/4 Zip Polo
    "FtinessCo ladies all associate 1 4 zip polo x small":    "FtinessCo Ladies All Associate 1/4 Zip Polo, X Small",
    "FtinessCo ladies all associate 1 4 zip polo small":      "FtinessCo Ladies All Associate 1/4 Zip Polo, Small",
    "FtinessCo ladies all associate 1 4 zip polo medium":     "FtinessCo Ladies All Associate 1/4 Zip Polo, Medium",
    "FtinessCo ladies all associate 1 4 zip polo large":      "FtinessCo Ladies All Associate 1/4 Zip Polo, Large",
    "FtinessCo ladies all associate 1 4 zip polo x large":    "FtinessCo Ladies All Associate 1/4 Zip Polo, X Large",
    "FtinessCo ladies all associate 1 4 zip polo 2x large":   "FtinessCo Ladies All Associate 1/4 Zip Polo, 2X Large",
    "FtinessCo ladies all associate 1 4 zip polo 3x large":   "FtinessCo Ladies All Associate 1/4 Zip Polo, 3X Large",

    # FtinessCo Ladies All Associate Polo
    "FtinessCo ladies all associate polo x small":    "FtinessCo Ladies All Associate Polo, X Small",
    "FtinessCo ladies all associate polo small":      "FtinessCo Ladies All Associate Polo, Small",
    "FtinessCo ladies all associate polo medium":     "FtinessCo Ladies All Associate Polo, Medium",
    "FtinessCo ladies all associate polo large":      "FtinessCo Ladies All Associate Polo, Large",
    "FtinessCo ladies all associate polo x large":    "FtinessCo Ladies All Associate Polo, X Large",
    "FtinessCo ladies all associate polo 2x large":   "FtinessCo Ladies All Associate Polo, 2X Large",
    "FtinessCo ladies all associate polo 3x large":   "FtinessCo Ladies All Associate Polo, 3X Large",

    # --- MEN'S SHIRTS ---
    # FtinessCo Mens All Associate 1/4 Zip Polo
    "FtinessCo mens all associate 1 4 zip polo x small":    "FtinessCo Mens All Associate 1/4 Zip Polo, X Small",
    "FtinessCo mens all associate 1 4 zip polo small":      "FtinessCo Mens All Associate 1/4 Zip Polo, Small",
    "FtinessCo mens all associate 1 4 zip polo medium":     "FtinessCo Mens All Associate 1/4 Zip Polo, Medium",
    "FtinessCo mens all associate 1 4 zip polo large":      "FtinessCo Mens All Associate 1/4 Zip Polo, Large",
    "FtinessCo mens all associate 1 4 zip polo x large":    "FtinessCo Mens All Associate 1/4 Zip Polo, X Large",
    "FtinessCo mens all associate 1 4 zip polo 2x large":   "FtinessCo Mens All Associate 1/4 Zip Polo, 2X Large",
    "FtinessCo mens all associate 1 4 zip polo 3x large":   "FtinessCo Mens All Associate 1/4 Zip Polo, 3X Large",

    # FtinessCo Mens All Associate 1/4 Zip Polo Slim
    "FtinessCo mens all associate 1 4 zip polo slim x small":    "FtinessCo Mens All Associate 1/4 Zip Polo Slim, X Small",
    "FtinessCo mens all associate 1 4 zip polo slim small":      "FtinessCo Mens All Associate 1/4 Zip Polo Slim, Small",
    "FtinessCo mens all associate 1 4 zip polo slim medium":     "FtinessCo Mens All Associate 1/4 Zip Polo Slim, Medium",
    "FtinessCo mens all associate 1 4 zip polo slim large":      "FtinessCo Mens All Associate 1/4 Zip Polo Slim, Large",
    "FtinessCo mens all associate 1 4 zip polo slim x large":    "FtinessCo Mens All Associate 1/4 Zip Polo Slim, X Large",
    "FtinessCo mens all associate 1 4 zip polo slim 2x large":   "FtinessCo Mens All Associate 1/4 Zip Polo Slim, 2X Large",
    "FtinessCo mens all associate 1 4 zip polo slim 3x large":   "FtinessCo Mens All Associate 1/4 Zip Polo Slim, 3X Large",

    # FtinessCo Mens All Associate Polo
    "FtinessCo mens all associate polo x small":    "FtinessCo Mens All Associate Polo, X Small",
    "FtinessCo mens all associate polo small":      "FtinessCo Mens All Associate Polo, Small",
    "FtinessCo mens all associate polo medium":     "FtinessCo Mens All Associate Polo, Medium",
    "FtinessCo mens all associate polo large":      "FtinessCo Mens All Associate Polo, Large",
    "FtinessCo mens all associate polo x large":    "FtinessCo Mens All Associate Polo, X Large",
    "FtinessCo mens all associate polo 2x large":   "FtinessCo Mens All Associate Polo, 2X Large",
    "FtinessCo mens all associate polo 3x large":   "FtinessCo Mens All Associate Polo, 3X Large",

    "FtinessCo name badge":                                 "FtinessCo Name Badge",
    "FtinessCo typhoon shaker bottle red":                  "FtinessCo Typhoon Shaker Bottle, Red",
    "FtinessCo typhoon shaker bottle white":                "FtinessCo Typhoon Shaker Bottle, White",
    "FtinessCo typhoon shaker bottle mixed":                "FtinessCo Typhoon Shaker Bottle, Mixed",
    "gp forward sc j-fill general purpose cleaner":        "GP General Purpose Cleaner",
    "general purpose cleaner":                             "GP General Purpose Cleaner",
    "grout brush":                                         "Grout Brush",
    "hair dryer":                                          "Hair Dryer",
    "ipod cord audio cable":                               "iPod Cord Audio Cable 3.5mm",
    "laminating film":                                     "Laminating Film, Letter 3 mil, Pack of 50",
    "lat bar attachment length":                           "Lat Bar Attachment, 35.5″",
    "letter tray":                                         "Letter Tray, Letter Size",
    "living the good life book":                           "Living The Good Life Book",
    "marker caddy dry erase":                              "Marker Caddy, Dry Erase",
    "marino trigger sprayer":                              "Marino Trigger Sprayer",
    "medicine ball rack":                                  "Medicine Ball Rack, Double-Sided",
    "membership card":                                     "Membership Cards, Pack of 100",
    "microtuff microfibre cloth blue":                     "Microfibre Cloth, Blue",
    "microtuff microfibre cloth yellow":                   "Microfibre Cloth, Yellow",
    "microtuff microfibre cloth green":                    "Microfibre Cloth, Green",
    "microtuff microfibre cloth red":                      "Microfibre Cloth, Red",
    "microtuff microfibre cloth orange":                   "Microfibre Cloth, Orange",
    "mop loop":                                            "Mop Loop, Band, 1\" Large",
    "mop, sentrex, synthetic, cut end, wet":               "Mop Head",
    "nitrile powder free medical gloves small":            "Nitrile Gloves, Small",
    "nitrile powder free medical gloves large":            "Nitrile Gloves, Large",
    "nitrile powder free medical gloves medium":           "Nitrile Gloves, Medium",
    "nitrile powder free medical gloves x large":          "Nitrile Gloves, X Large",
    "notebook  wire bound":                                "Notebook, Wire Bound",
    "ovi choc cleaner drain enzyme":                       "Ovi-Choc Cleaner Drain Enzyme, 1L",
    "pad self stick notes":                                "Self-Stick Notes, Recycled",
    "towel tork universal natural":                        "Paper Towels",
    "pen ball point round stick medium black":             "Pens Ballpoint, Black",
    "pen ball point round stick medium blue":              "Pens Ballpoint, Blue",
    "pen ballpoint medium black box of 12 pentel":         "Pens Pentel R.S.V.P., Black",
    "pen ballpoint medium blue box of 12 pentel":          "Pens Pentel R.S.V.P., Blue",
    "pen ballpoint medium red box of 12 pentel":           "Pens Pentel R.S.V.P., Red",
    "telephone message pads":                              "Telephone Message Pads, Pack of 10",
    "you were out message pads":                           "Telephone Message Pads, Pack of 10",
    "pilates ball":                                        "Pilates Ball",
    "washable water repellent shower curtain":             "Shower Curtain, grey",
    "prominence heavy duty floor cleaner":                 "Prominence Floor Cleaner, 2.5 L",
    "remove footwear decal":                               "Remove Footwear Sign",
    "scent awareness cling":                               "Scent Awareness Sign",
    "scotch magic tape":                                   "Scotch Magic Tape, 19 mm×32.9 m",
    "black foam windscreen for groupfitness":              "Black Foam for Group Fitness Mics",
    "marker sharpie permanent fine black":              "Sharpie Fine Tip Permanent Marker, Black",
    "marker sharpie permanent fine blue":               "Sharpie Fine Tip Permanent Marker, Blue",
    "marker sharpie permanent fine red":                "Sharpie Fine Tip Permanent Marker, Red",
    "shower curtain heavy duty white":                   "Shower Curtain, white",
    "sign holder stand up":                               "Standing Sign Holder",
    "duraframe pocket":                                    "Sign Pouch",
    "single powder coat black bottle holder":              "Single Powder Coat Black Bottle Holder",
    "speed rope":                                          "Speed Rope, 9′",
    "garbage bags strong":                                 "Garbage bags, Strong, 30″×38, clear",
    "stability ball pump":                                 "Stability Ball Pump",
    "staples garbage bags black":                          "Garbage Bags, Black, 42″×48″ (Box of 100)",
    "garbage bags regular clear":                           "Staples Garbage Bags, Clear, 26″×36″ (250 pack)",
    "staples heat seal":                                   "Staples Heat Seal Laminator",
    "laminator":                                           "Staples Heat Seal Laminator",
    "scrub brush floor and deck":                          "Globe Floor & Deck Scrub Brush, 10″",
    "suma mineral oil lubricant":                          "Suma Mineral Oil Lubricant",
    "toilet tissue dispenser":                              "Dispense Toilet tissue",
    "tru red tank dry erase markers chisel tip":           "TRU RED Tank Dry Erase Markers",
    "twinkle stainless steel cleaner":                     "Twinkle Stainless Steel Cleaner & Polish, 482 g",
    "visitor lanyard":                                     "Visitor Lanyard",
    "wet mop synthetic":                                   "Wet Mop, Synthetic",
    "cleaner white board expo 2 8 oz":                     "White Board Cleaner, 8oz",
    "floor and deck scrub brush":                          "Floor and Deck Scrub Brush w/Metal Handle", 
    "master massage 30":                                   "Portable Massage Table 30''",
    "nitrile glove, large, blue":                          "Nitrile Gloves, Large, Blue, Powder Free (Blood & Needle Kit Only)",
    "instant cold pack, large":                            "Instant Cold Pack, Large, 25 cm × 15 cm",
    "gauze roll, 5cm x 4.5m":                              "Gauze Roll, 5 cm × 4.5 m, 4/Box",
    "wasip conform bandage, 5 cm x 4.5 m":                 "Wasip Conform Bandage, 5 cm × 4.5 m",
    "conform bandage, 7.5cm x 4.5cm":                      "Conform Bandage, 7.5 cm × 4.5 m, 1 Roll",
    "gauze pads, 7.5 x 7.5cm":                             "Gauze Pads, 7.5 cm × 7.5 cm, Pack of 25",
    "wasip triangular bandage":                            "Wasip Triangular Bandage, 102 cm × 102 cm × 142 cm",
    "abdominal pad, sterile":                              "Abdominal Pad, Sterile, 20 cm × 25 cm",
    "fabric strip bandage, 7.5 x 2.2cm":                   "Fabric Strip Bandage, 7.5 cm × 2.2 cm, 50/Box",
    "fabric knuckle, bandage, 7.5 x 3.75cm":               "Fabric Knuckle Bandage, 7.5 cm × 3.75 cm, 50/Box",
    "fabric patch bandage, large":                         "Fabric Patch Bandage, Large, 5 cm × 7.5 cm, 50/Box",
    "butterfly closures, medium":                          "Butterfly Closures, Medium, 100/Box",
    "cloth tape,  2.5cm x 4.5m":                           "Cloth Tape, 2.5 cm × 4.5 m",
    "black handle universal scissors":                     "Black Handle Universal Scissors, 15 cm",
    "oxivir plus disinfectant cleaner concentrate":        "Oxivir Plus Disinfectant Cleaner Concentrate, 1.5 L (Box of 2)",
    "cf x pro loops , set of 4":                           "CFX Pro Loops, Set of 4",
    "nitrile glove large blue powder free pair":           "Nitrile Glove, Large, Pair",
    "ballot box pens coil tether pens":                    "Ballot Box Pens, Coil Tether",
    "curved splinter forceps":                             "Curved Splinter Forceps, 4.5″",
    "plastic emesis basin":                                "Plastic Emesis Basin, 23 cm × 500 ml",
    "pio splint, 91 cm x 11 cm":                           "PIO Splint, 91 cm × 11 cm",
    "emergency survival blanket":                          "Emergency Survival Blanket",
    "taylor reagent ph indicator solution":                "Taylor Reagent pH Indicator Solution, 470 ml",
    "16 oz total alkalinity indicator":                    "Total Alkalinity Indicator, 470 ml",
    "16 oz sulfuric acid .12n":                            "Sulfuric Acid 0.12 N, 470 ml",
    "whistle laundry detergent":                           "Whistle Laundry Detergent, 7.57 L (Case of 2)",
    "shower curtain hook stainless":                       "Shower Curtain Hooks, Stainless Steel",
    "desktop tc m75q gen 5":                               "DESKTOP TC M75Q GEN 5 A5P8500GE 16G 512G",
    
}

ITEM_ID_MAP2: Dict[str, str] = {
    "CR-0870-J (1081787)": "Taylor Reagent, Chlorine DPD Powder, 113 grams",
    "CR-0870-I (1081794)": "Taylor Reagent, Chlorine DPD Powder, 10 grams",
    "CR-0871-E (1081788)": "FAS-DPD Titrating Reagent, Chlorine, .47L",
    "CR-0871-C (1081795)": "FAS-DPD Titrating Reagent, Chlorine, 60 ml",
    "CR-0003-C (1081786)": "Taylor DPD Reagent #3, 60 ml, Total Chlorine",
    "CR-0004-C (1081796)": "Taylor Reagent, pH Indicator Solution, 60 ml",
    "CR-0007-C (1081797)": "Taylor Reagent, Thiosulfate N/10, 60 ml",
    "CR-0007-E (1081791)": "Taylor Reagent, Thiosulfate N/10, 470 ml",
    "CR-0008-C (1081798)": "Taylor Reagent, Total Alkalinity Indicator, 60 ml",
    "CR-0009-C (1081799)": "Taylor Reagent, Sulfuric Acid 0.12N, 60 ml"
}

def rename_desc(desc: str) -> str:
    low = desc.lower()
    # remove punctuation so “6-lbs” → “6 lbs”, “cfx-pro” → “cfx pro”
    low = re.sub(r'[^a-z0-9 ]+', ' ', low)
    low = re.sub(r'\s+', ' ', low).strip()

    for pat, replacement in NAME_MAP.items():
        # your NAME_MAP keys should all be lower-cased, punctuation-free substrings
        if pat in low:
            return replacement
    return desc  # fallback if nothing matched

def truncate_desc(desc):
    """Truncate at first '(' or '['."""
    idxs = [desc.find("("), desc.find("[")]
    idxs = [i for i in idxs if i != -1]
    if idxs:
        return desc[:min(idxs)].strip().rstrip(",")
    return desc.strip()

def normalize_name(raw_desc: str, item_id: Optional[str] = None) -> str:
    """
    Normalize an item description using NAME_MAP and (optionally)
    an ID-based override in ITEM_ID_MAP2. Falls back to the
    stripped original description if no mapping is found.
    """
    if item_id and item_id in ITEM_ID_MAP2:
        return ITEM_ID_MAP2[item_id]

    key = raw_desc.strip().lower()
    return NAME_MAP.get(key, raw_desc.strip())
