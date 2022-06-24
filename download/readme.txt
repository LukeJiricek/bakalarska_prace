OBRÁZKOVÝ DATASET S ATRIBUTY
- kategorie objektů: Nábytek
- počet objektů: 57
- počet atributů: 90


KOMPLETNÍ DATASET
- ZIP obsahující:
    - Kompletní JSON data
    - Zjednodušená JSON data
    - CSV data
    - img.zip - soubor obsahující všechny obrázky


KOMPLETNÍ JSON DATA - popis dat
- "id" : označuje identifikační číslo objektu
- "source" : zdroj objektu v rámci creative commons licence
- "author": autor obrázku
- "type" : typ objektu
- "filename" : odkaz na obrázek objektu
- "title": titul obrázku, popsaný autorem, uvedený v rámci Creative Commons licence
- "attributes" seznam atributů:
    - U každého atributu je uveden:
        - "Value" :  hodnota v rozpětí 0.00 a 1.00 popisující nakolik daná vlastnost popisuje objekt:
            - 1.00 = každý tazatel uvedl, že vlastnost popisuje objektu
            - 0.00 = každý tazatel uvedl, že vlasnost nepopisuje objekt
        - počet kladných odpovědí (Tazatel uvedl, že daná vlastnost popisuje objekt)
        - počet záporných odpovědí (Tazatel uvedl, že daná vlastnost nepopisuje objekt)


ZJEDNODUŠENÁ JSON DATA - popis dat
- "id" : označuje identifikační číslo objektu
- "Objekt" : odkaz na obrázek objektu
- Seznam atributů s hodnotou v rozpětí 0.00 a 1.00 popisující nakolik daná vlastnost popisuje objekt:
    - 1.00 = každý tazatel uvedl, že vlastnost popisuje objektu
    - 0.00 = každý tazatel uvedl, že vlasnost nepopisuje objekt


ZJEDNODUŠENÁ CSV DATA - popis dat
- "id" : označuje identifikační číslo objektu
- "Objekt" : odkaz na obrázek objektu
- Seznam atributů s hodnotou v rozpětí 0.00 a 1.00 popisující nakolik daná vlastnost popisuje objekt:
    - 1.00 = každý tazatel uvedl, že vlastnost popisuje objektu
    - 0.00 = každý tazatel uvedl, že vlasnost nepopisuje objekt

