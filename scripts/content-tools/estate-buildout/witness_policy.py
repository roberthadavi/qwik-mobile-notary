"""2026-11-20 — witness policy change: QWIK now brings two disinterested witnesses on request (quoted with the visit).

Rewrites the old "we do not bring witnesses unless arranged / ask whether witnesses can be arranged for an
additional fee" sentences in the existing part files, textually, so the compact JSON formatting is untouched.
Also refreshes the estate-planning hub copy (title tags untouched) and the related[] cross-links to the five
new estate-planning pages.  Run from the repo root.
"""
import json
import os
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
P = lambda *a: os.path.join(ROOT, 'src', 'content', 'parts', *a)  # noqa: E731

EDITS = {
    P('business', 'attorneys-law-firms.json'): [
        ("We do not supply witnesses unless arranged when booking, do not draft, and never explain a document's legal effect to a client — that conversation belongs to the attorney.",
         "We bring two disinterested witnesses when the firm asks for them at booking (itemized), do not draft, and never explain a document's legal effect to a client — that conversation belongs to the attorney."),
        ("No proporcionamos testigos salvo que se acuerde al reservar, no redactamos, y nunca explicamos al cliente el efecto legal de un documento — esa conversación es del abogado.",
         "Llevamos dos testigos sin interés cuando el despacho los pide al reservar (detallados aparte), no redactamos, y nunca explicamos al cliente el efecto legal de un documento — esa conversación es del abogado."),
        ("the firm supplies the witnesses, or asks when booking whether witnesses can be arranged for an additional fee.",
         "the firm supplies the witnesses or asks us at booking to bring two disinterested witnesses, itemized with the signing."),
        ("el despacho aporta los testigos, o pregunta al reservar si pueden conseguirse por una tarifa adicional.",
         "el despacho aporta los testigos o nos pide al reservar que llevemos dos testigos sin interés, detallados junto con la firma."),
    ],
    P('estate-planning', 'hub.json'): [
        ("Mobile notary for wills, powers of attorney and medical directives in El Paso. Bilingual, same-day, we come to you. Call or text (915) 302-0902.",
         "Mobile notary for wills, trusts, powers of attorney and medical directives in El Paso. Witnesses available. Bilingual. Call or text (915) 302-0902."),
        ("Notarizamos testamentos, cartas poder y poderes médicos a domicilio en El Paso. Bilingüe, el mismo día con cita. Llame o envíe un texto al (915) 302-0902.",
         "Notarizamos testamentos, fideicomisos, cartas poder y poderes médicos a domicilio en El Paso, con testigos disponibles. Llame o envíe un texto al (915) 302-0902."),
        ("Estate Planning Notary in El Paso — Wills, Powers of Attorney and Advance Directives",
         "Estate Planning Notary in El Paso — Wills, Trusts, Powers of Attorney, Directives"),
        ("Testamentos, Cartas Poder y Poderes Médicos en El Paso — Notarización a Domicilio",
         "Testamentos, Fideicomisos, Cartas Poder y Poderes Médicos en El Paso — Notarización a Domicilio"),
        ("Wills, powers of attorney, medical directives and trust documents notarized at your home, office, hospital room or nursing home anywhere in El Paso County. You bring the documents your attorney prepared; we handle the acknowledgment, the oath or the self-proving affidavit.",
         "Wills and will signings with witnesses, powers of attorney, medical directives, living trust packages, transfer on death deeds and declarations of guardian notarized at your home, office, hospital room or nursing home anywhere in El Paso County — plus a signing-agent service for attorneys and online-will customers. You bring the documents your attorney prepared; we handle the acknowledgment, the oath, the witnesses and the self-proving affidavit."),
        ("Testamentos, cartas poder, poderes médicos y documentos de fideicomiso notarizados en su casa, oficina, cuarto de hospital o asilo en todo el condado de El Paso. Usted trae los documentos que preparó su abogado; nosotros hacemos el reconocimiento (acknowledgment), el juramento (jurat) o la declaración jurada.",
         "Testamentos y firmas de testamento con testigos, cartas poder, poderes médicos, paquetes de fideicomiso, escrituras de transferencia al fallecimiento y declaraciones de tutor notarizados en su casa, oficina, cuarto de hospital o asilo en todo el condado de El Paso — además de un servicio de agente de firma para abogados y clientes de testamentos en línea. Usted trae los documentos que preparó su abogado; nosotros hacemos el reconocimiento (acknowledgment), el juramento (jurat), los testigos y la declaración jurada."),
        ("QWIK Mobile Notary brings the notary to the signing, not the other way around.",
         "QWIK Mobile Notary brings the notary — and, when you need them, two witnesses — to the signing, not the other way around."),
        ("QWIK Mobile Notary lleva la notarización a donde está la firma, no al revés.",
         "QWIK Mobile Notary lleva la notarización — y, cuando usted los necesita, dos testigos — a donde está la firma, no al revés."),
        ("a will needs two witnesses age 14 or older, with the notary taking the self-proving affidavit under chapter 251;",
         "a will needs two witnesses age 14 or older — we can bring them — with the notary taking the self-proving affidavit under chapter 251; a transfer on death deed is acknowledged and recorded before death under chapter 114;"),
        ("el testamento requiere dos testigos de 14 años o más, y el Notary Public toma la declaración jurada de autenticidad (self-proving affidavit) del capítulo 251;",
         "el testamento requiere dos testigos de 14 años o más — podemos llevarlos — y el Notary Public toma la declaración jurada de autenticidad (self-proving affidavit) del capítulo 251; la escritura de transferencia al fallecimiento se reconoce y se registra antes del fallecimiento (capítulo 114);"),
        ("Bring your witnesses, or ask when booking whether witnesses can be arranged for an additional fee.",
         "Bring your witnesses, or ask when booking and we bring two qualified witnesses, quoted with the visit."),
        ("Traiga a sus testigos o pregunte al agendar si podemos conseguirlos por un costo adicional.",
         "Traiga a sus testigos o pídalos al agendar y llevamos dos testigos calificados, cotizados junto con la visita."),
    ],
    P('estate-planning', 'wills-and-trusts.json'): [
        ("Everyone signing needs unexpired photo ID and your two witnesses must be there — ask when booking whether witnesses can be arranged for an additional fee.",
         "Everyone signing needs unexpired photo ID and two witnesses must be there — bring your own or ask when booking and we bring two qualified witnesses, quoted with the visit."),
        ("Todos los que firman necesitan identificación vigente con fotografía y sus dos testigos deben estar presentes — pregunte al agendar si podemos conseguir testigos por un costo adicional.",
         "Todos los que firman necesitan identificación vigente con fotografía y dos testigos deben estar presentes — traiga los suyos o pídalos al agendar y llevamos dos testigos calificados, cotizados junto con la visita."),
        ("We do not bring witnesses unless it is arranged in advance; ask when booking whether witnesses can be arranged for an additional fee, especially for evening signings in Horizon City or the far East Side.",
         "If you have no witnesses, ask when booking and we bring two disinterested adults, quoted with the visit — a relief for evening signings in Horizon City or the far East Side."),
        ("No llevamos testigos a menos que se acuerde con anticipación; pregunte al agendar si podemos conseguir testigos por un costo adicional, sobre todo para firmas por la tarde en Horizon City o en el extremo del East Side.",
         "Si no tiene testigos, pídalos al agendar y llevamos dos adultos sin interés en el testamento, cotizados junto con la visita — un alivio para las firmas por la tarde en Horizon City o en el extremo del East Side."),
        ("Two witnesses age 14 or older who are not beneficiaries — or ask when booking whether witnesses can be arranged for an additional fee",
         "Two witnesses age 14 or older who are not beneficiaries — or ask us to bring them, quoted with the visit"),
        ("Dos testigos de 14 años o más que no sean beneficiarios — o pregunte al agendar si podemos conseguir testigos por un costo adicional",
         "Dos testigos de 14 años o más que no sean beneficiarios — o pídanos que los llevemos, cotizados junto con la visita"),
        ("We do not bring witnesses by default; ask when booking whether witnesses can be arranged for an additional fee.",
         "Yes, we can bring them: ask when booking and two disinterested witnesses come with the notary, quoted with the visit."),
        ("No llevamos testigos de manera automática; pregunte al agendar si podemos conseguir testigos por un costo adicional.",
         "Sí, podemos llevarlos: pídalos al agendar y dos testigos sin interés en el testamento llegan con el Notary Public, cotizados junto con la visita."),
    ],
    P('family-documents', 'guardianship-adoption.json'): [
        ("Bring your own two credible witnesses when the document calls for them, or ask when booking whether witnesses can be arranged for an additional fee.",
         "Bring your own two credible witnesses when the document calls for them, or ask when booking and we bring two disinterested witnesses, quoted with the visit."),
        ("Traiga sus propios dos testigos creíbles cuando el documento los requiera, o pregunte al reservar si se pueden conseguir testigos por una cuota adicional.",
         "Traiga sus propios dos testigos creíbles cuando el documento los requiera, o pídalos al reservar y llevamos dos testigos sin interés, cotizados junto con la visita."),
        ("Two credible adult witnesses when the document requires them, or ask when booking whether witnesses can be arranged for an additional fee",
         "Two credible adult witnesses when the document requires them, or ask us to bring them, quoted with the visit"),
        ("Dos testigos adultos creíbles cuando el documento los exija, o pregunte al reservar si se pueden conseguir testigos por una cuota adicional",
         "Dos testigos adultos creíbles cuando el documento los exija, o pídanos que los llevemos, cotizados junto con la visita"),
        ("Not by default. The two credible witnesses a relinquishment affidavit requires are usually adults you bring — neighbors, coworkers or friends who are not parties to the adoption — and your attorney can confirm who qualifies. When booking, ask whether witnesses can be arranged for an additional fee; with enough notice it is often possible.",
         "Yes, when you ask for them at booking. The two credible witnesses a relinquishment affidavit requires can be adults you bring — neighbors, coworkers or friends who are not parties to the adoption — or two disinterested witnesses we bring with the notary, quoted with the visit; your attorney can confirm who qualifies."),
        ("No de forma automática. Los dos testigos creíbles que exige una declaración de renuncia normalmente son adultos que usted trae — vecinos, compañeros de trabajo o amigos que no sean parte de la adopción — y su abogado puede confirmar quién califica. Al reservar, pregunte si se pueden conseguir testigos por una cuota adicional; con suficiente aviso muchas veces es posible.",
         "Sí, cuando usted los pide al reservar. Los dos testigos creíbles que exige una declaración de renuncia pueden ser adultos que usted trae — vecinos, compañeros de trabajo o amigos que no sean parte de la adopción — o dos testigos sin interés que llevamos junto con el Notary Public, cotizados con la visita; su abogado puede confirmar quién califica."),
    ],
    P('real-estate', 'timeshare.json'): [
        ("so line up neighbors or friends if needed; ask when booking whether witnesses can be arranged for an additional fee.",
         "so line up neighbors or friends if needed, or ask when booking and we bring two witnesses, quoted with the visit."),
        ("así que consiga vecinos o amigos si hace falta; pregunte al agendar si podemos conseguir testigos por un costo adicional.",
         "así que consiga vecinos o amigos si hace falta, o pídalos al agendar y llevamos dos testigos, cotizados junto con la visita."),
        ("Two witnesses if the packet requires them, or ask when booking whether witnesses can be arranged for an additional fee",
         "Two witnesses if the packet requires them, or ask us to bring them, quoted with the visit"),
        ("Dos testigos si el paquete los exige, o pregunte al agendar si podemos conseguir testigos por un costo adicional",
         "Dos testigos si el paquete los exige, o pídanos que los llevemos, cotizados junto con la visita"),
        ("Not by default. Deeds recorded in some states,",
         "Yes, when you ask for them at booking. Deeds recorded in some states,"),
        ("Ask when booking whether witnesses can be arranged for an additional fee.",
         "Ask when booking and we bring two witnesses, quoted with the visit."),
        ("No de manera automática. Las escrituras que se registran en algunos estados,",
         "Sí, cuando los pide al agendar. Las escrituras que se registran en algunos estados,"),
        ("Pregunte al agendar si podemos conseguir testigos por un costo adicional.",
         "Pídalos al agendar y llevamos dos testigos, cotizados junto con la visita."),
    ],
}

# related[] cross-links to the new pages (compact one-line arrays in the part files)
RELATED = {
    P('estate-planning', 'wills-and-trusts.json'): ('"related": ["power-of-attorney", "medical-power-of-attorney", "deeds"]',
                                                    '"related": ["will-signing", "living-trust-signing", "transfer-on-death-deed", "power-of-attorney"]'),
    P('estate-planning', 'medical-power-of-attorney.json'): ('"related": ["hospital-notary", "power-of-attorney", "wills-and-trusts"]',
                                                             '"related": ["hospital-notary", "power-of-attorney", "wills-and-trusts", "declaration-of-guardian"]'),
    P('notary-services', 'hospital-notary.json'): ('"related": ["medical-power-of-attorney", "power-of-attorney", "wills-and-trusts"]',
                                                   '"related": ["medical-power-of-attorney", "power-of-attorney", "will-signing", "transfer-on-death-deed"]'),
    P('business', 'attorneys-law-firms.json'): ('"related": [\n    "affidavits",\n    "jail-notary",\n    "hospital-notary",\n    "acknowledgments-and-jurats"\n  ]',
                                                '"related": [\n    "estate-planning-signing-agent",\n    "affidavits",\n    "jail-notary",\n    "hospital-notary"\n  ]'),
    P('family-documents', 'guardianship-adoption.json'): ('"related": [\n    "child-travel-consent",\n    "apostille-mexico",\n    "power-of-attorney"\n  ]',
                                                          '"related": [\n    "declaration-of-guardian",\n    "child-travel-consent",\n    "apostille-mexico",\n    "power-of-attorney"\n  ]'),
    P('real-estate', 'deeds.json'): ('"related": ["seller-packages", "liens-and-releases", "wills-and-trusts", "power-of-attorney"]',
                                     '"related": ["transfer-on-death-deed", "seller-packages", "wills-and-trusts", "power-of-attorney"]'),
}


def apply(path, pairs):
    s = open(path, encoding='utf-8').read()
    for old, new in pairs:
        n = s.count(old)
        if n == 0 and s.count(new) == 1:
            continue  # already applied (idempotent re-run)
        if n != 1:
            sys.exit(f'{os.path.relpath(path, ROOT)}: expected 1 match, found {n}: {old[:70]}…')
        s = s.replace(old, new)
    json.loads(s)  # still valid JSON
    open(path, 'w', encoding='utf-8').write(s)
    print(f'{os.path.relpath(path, ROOT)}: {len(pairs)} edit(s)')


for path, pairs in EDITS.items():
    apply(path, pairs)
for path, pair in RELATED.items():
    apply(path, [pair])
