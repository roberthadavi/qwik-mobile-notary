#!/usr/bin/env python3
"""Remove every dollar amount from src/content/parts/**/*.json (EN + ES), replacing price copy with
quote / prices-vary language. Exact-key replacements for short fields; sentence-level replacements
(keyed by full sentence or unique prefix) for intros, FAQs, steps and sections. Fails loudly on any
unmapped sentence that still carries a $ amount."""
import json, glob, re, sys, collections

ROOT = '/home/claude/work/qwik-mobile-notary/'
SENT_RE = re.compile(r'(?<=[.!?])(?<!\bTex\.)(?<!\bU\.S\.)\s+(?=[A-ZÁÉÍÓÚÑ¿¡"“(])')
DOLLAR = re.compile(r'\$\d')

# ---------------------------------------------------------------- feeModel (exact)
FEEMODEL = {
    '$10 first signature + $1 each additional, plus $39 travel fee': 'Prices vary — call or text for a quote',
    '$10 la primera firma + $1 cada firma adicional, más $39 de traslado': 'Los precios varían — llame o envíe un texto para cotizar',
    'Service fee + $15 Texas SOS fee per document — call or text for a quote': 'Service fee + state fee per document — call or text for a quote',
    'Tarifa de servicio + $15 por documento de la Secretaría de Estado — llame o envíe un texto para cotizar': 'Tarifa de servicio + cuota estatal por documento — llame o envíe un texto para cotizar',
    '$10 per oath or first signature, $1 each additional signature, plus $39 travel fee': 'Prices vary — call or text for a quote',
    '$10 por juramento o primera firma, $1 cada firma adicional, más $39 de traslado': 'Los precios varían — llame o envíe un texto para cotizar',
    '$10 oath + $39 travel fee for the notarization; apostille service fee + $15 Texas SOS fee — call or text for a quote': 'Notarization and apostille package quoted together — call or text for a quote',
    '$10 por el juramento + $39 de traslado por la notarización; tarifa de servicio de apostilla + $15 de la Secretaría de Estado — llame o envíe un texto para cotizar': 'Notarización y paquete de apostilla cotizados juntos — llame o envíe un texto para cotizar',
    '$10 per oath or first acknowledged signature + $1 each additional, plus $39 travel fee — firm accounts invoiced': 'Prices vary — call or text for a quote; firm accounts invoiced',
    '$10 por juramento o primera firma reconocida + $1 cada firma adicional, más $39 de traslado — cuentas con factura para despachos': 'Los precios varían — llame o envíe un texto para cotizar; cuentas con factura para despachos',
    '$10 first signature + $1 each additional ($10 per oath), plus $39 travel fee': 'Prices vary — call or text for a quote',
    '$10 la primera firma + $1 cada firma adicional ($10 por juramento), más $39 de traslado': 'Los precios varían — llame o envíe un texto para cotizar',
    '$10 per oath or acknowledgment ($1 each additional signature), plus $39 travel fee': 'Prices vary — call or text for a quote',
    '$10 por juramento o reconocimiento ($1 por firma adicional), más $39 de traslado': 'Los precios varían — llame o envíe un texto para cotizar',
    '$10 per oath or acknowledgment (+$1 each additional signature), plus $39 travel fee': 'Prices vary — call or text for a quote',
    '$10 por juramento o reconocimiento (+$1 por firma adicional), más $39 de traslado': 'Los precios varían — llame o envíe un texto para cotizar',
    '$10 per oath or first signature + $1 each additional, plus $39 travel fee': 'Prices vary — call or text for a quote',
    '$10 por juramento o primera firma + $1 cada firma adicional, más $39 de traslado': 'Los precios varían — llame o envíe un texto para cotizar',
    '$10 first signature + $1 each additional ($10 per sworn affidavit), plus $39 travel fee': 'Prices vary — call or text for a quote',
    '$10 la primera firma + $1 cada firma adicional ($10 por declaración jurada), más $39 de traslado': 'Los precios varían — llame o envíe un texto para cotizar',
    '$10 first signature + $1 each additional, plus $39 travel fee; after-hours and holiday trips quoted — call or text': 'Prices vary; after-hours and holiday trips quoted — call or text',
    '$10 la primera firma + $1 cada firma adicional, más $39 de traslado; fuera de horario y festivos se cotiza — llame o envíe un texto': 'Los precios varían; fuera de horario y festivos se cotiza — llame o envíe un texto',
    '$10 first signature + $1 each additional (acknowledgment) or $10 per oath (jurat), plus $39 travel fee': 'Prices vary — call or text for a quote',
    '$10 la primera firma + $1 cada firma adicional (reconocimiento) o $10 por juramento, más $39 de traslado': 'Los precios varían — llame o envíe un texto para cotizar',
    '$10 per oath or affirmation, plus $39 travel fee': 'Prices vary — call or text for a quote',
    '$10 por juramento, más $39 de traslado': 'Los precios varían — llame o envíe un texto para cotizar',
    '$10 per certified copy + $1 per page copied, plus $39 travel fee': 'Prices vary by page count — call or text for a quote',
    '$10 por copia certificada + $1 por página copiada, más $39 de traslado': 'Los precios varían según el número de páginas — llame o envíe un texto para cotizar',
    '$25 per online notarization (Texas maximum), no travel fee': 'Online notarization, no travel fee — call or text for a quote',
    '$25 por notarización en línea (máximo en Texas), sin traslado': 'Notarización en línea, sin traslado — llame o envíe un texto para cotizar',
    '$10 first signature + $1 each additional per document, plus $39 travel fee': 'Prices vary — call or text for a quote',
    '$10 la primera firma + $1 cada firma adicional por documento, más $39 de traslado': 'Los precios varían — llame o envíe un texto para cotizar',
}

# ---------------------------------------------------------------- bring (exact)
BRING = {
    'Payment for the statutory fees and the $39 travel fee, confirmed when you book': 'Payment for the quoted total, confirmed when you book',
    'El pago de las tarifas oficiales y los $39 de traslado, confirmado al agendar': 'El pago del total cotizado, confirmado al agendar',
    'Payment for the statutory fee and the $39 travel fee, confirmed when you book': 'Payment for the quoted total, confirmed when you book',
    'Payment for the notarial fees and the $39 travel fee, confirmed when you book': 'Payment for the quoted total, confirmed when you book',
    'El pago de las tarifas de notarización y los $39 de traslado, confirmado al agendar': 'El pago del total cotizado, confirmado al agendar',
    'Payment for the itemized quote, including the $15 Secretary of State fee per document': "Payment for the itemized quote, including the Secretary of State's per-document fee",
    'Payment for the quoted package: our fee, $15 per document for the Secretary of State, and shipping': "Payment for the quoted package: our fee, the Secretary of State's per-document fee, and shipping",
    'Billing details for the firm account, or payment for the statutory fee and the $39 travel fee': 'Billing details for the firm account, or payment for the quoted total',
    'A payment method for the statutory fees and the $39 travel fee (confirmed when you book)': 'A payment method for the quoted total (confirmed when you book)',
    'Payment for the notarial fee and the $39 travel fee — ask about accepted methods when booking': 'Payment for the quoted total — ask about accepted methods when booking',
    'Payment for the notarial fees and the $39 travel fee': 'Payment for the quoted total',
    'Payment for the notarial fee and the $39 travel fee — we confirm the total when you book': 'Payment for the quoted total — we confirm it when you book',
    'Payment for the statutory fee, the $39 travel fee and any quoted after-hours charge': 'Payment for the quoted total, including any after-hours charge',
    'Payment for the $10 oath fee and the $39 travel fee, confirmed when you book': 'Payment for the quoted total, confirmed when you book',
    'Payment for $10 per certified copy, $1 per page and the $39 travel fee, confirmed when you book': 'Payment for the quoted total, based on the page count, confirmed when you book',
    'Payment for the statutory fee plus the $39 travel fee — we confirm the total by text before we come': 'Payment for the quoted total — we confirm it by text before we come',
    'Payment for the statutory fee plus the $39 travel fee — the family usually pays, and we confirm the total by text before the visit': 'Payment for the quoted total — the family usually pays, and we confirm it by text before the visit',
    'El pago según la cotización desglosada, incluidos los $15 por documento de la Secretaría de Estado': 'El pago según la cotización desglosada, incluida la cuota por documento de la Secretaría de Estado',
    'Forma de pago para el paquete cotizado: nuestra tarifa, $15 por documento para la Secretaría de Estado y el envío': 'Forma de pago para el paquete cotizado: nuestra tarifa, la cuota por documento de la Secretaría de Estado y el envío',
    'Los datos de facturación de la cuenta del despacho, o el pago de la tarifa legal y los $39 de traslado': 'Los datos de facturación de la cuenta del despacho, o el pago del total cotizado',
    'Forma de pago para las tarifas legales y los $39 de traslado (se confirma al reservar)': 'Forma de pago para el total cotizado (se confirma al reservar)',
    'El pago de la tarifa legal y los $39 de traslado, confirmados al reservar': 'El pago del total cotizado, confirmado al reservar',
    'El pago de la cuota de notarización y los $39 de traslado; pregunte por las formas de pago al reservar': 'El pago del total cotizado; pregunte por las formas de pago al reservar',
    'El pago de las cuotas de notarización y los $39 de traslado': 'El pago del total cotizado',
    'El pago de la tarifa de notarización y los $39 de traslado — confirmamos el total al agendar': 'El pago del total cotizado — lo confirmamos al agendar',
    'El pago de la tarifa legal, los $39 de traslado y el cargo fuera de horario cotizado': 'El pago del total cotizado, incluido cualquier cargo fuera de horario',
    'El pago de la tarifa legal y los $39 de traslado, confirmado al agendar': 'El pago del total cotizado, confirmado al agendar',
    'El pago de los $10 por juramento y los $39 de traslado, confirmado al agendar': 'El pago del total cotizado, confirmado al agendar',
    'El pago de $10 por copia certificada, $1 por página y $39 de traslado, confirmado al agendar': 'El pago del total cotizado según el número de páginas, confirmado al agendar',
    'El pago de la tarifa que fija la ley más los $39 de traslado — le confirmamos el total por texto antes de ir': 'El pago del total cotizado — se lo confirmamos por texto antes de ir',
    'El pago de la tarifa que fija la ley más los $39 de traslado — normalmente paga la familia, y confirmamos el total por texto antes de la visita': 'El pago del total cotizado — normalmente paga la familia, y lo confirmamos por texto antes de la visita',
}

# ---------------------------------------------------------------- summary / metaDescription (exact)
FULL = {
    "Taking a UTEP or EPCC degree abroad? We notarize the copy or the registrar's statement, submit it to the Texas Secretary of State for the $15 apostille, and return it to you in El Paso — bilingual, mobile, by appointment.":
        "Taking a UTEP or EPCC degree abroad? We notarize the copy or the registrar's statement, submit it to the Texas Secretary of State for the apostille, and return it to you in El Paso — bilingual, mobile, by appointment.",
    '¿Se lleva su título de UTEP o EPCC al extranjero? Notarizamos la copia o la constancia del registrar, la presentamos ante la Secretaría de Estado de Texas para la apostilla de $15 y se la devolvemos en El Paso — bilingüe, a domicilio, con cita.':
        '¿Se lleva su título de UTEP o EPCC al extranjero? Notarizamos la copia o la constancia del registrar, la presentamos ante la Secretaría de Estado de Texas para la apostilla y se la devolvemos en El Paso — bilingüe, a domicilio, con cita.',
    'Apostille for UTEP, EPCC and Texas diplomas and transcripts from El Paso, TX: notarized copy, $15 SOS fee, tracked return. Call or text (915) 302-0902.':
        'Apostille for UTEP, EPCC and Texas diplomas and transcripts from El Paso, TX: notarized copy, filed in Austin, tracked return. Call or text (915) 302-0902.',
    'Certified copies of passports, IDs, diplomas and contracts — El Paso mobile notary, $10 + $1 per page, we come to you. Call or text (915) 302-0902.':
        'Certified copies of passports, IDs, diplomas and contracts — El Paso mobile notary, we come to you. Call or text (915) 302-0902 for a quote.',
    'Copias certificadas de pasaportes, diplomas y contratos en El Paso: $10 más $1 por página, a domicilio y en español. Llame o envíe un texto al (915) 302-0902.':
        'Copias certificadas de pasaportes, diplomas y contratos en El Paso: a domicilio y en español, cotización por texto. Llame o envíe un texto al (915) 302-0902.',
}

Q_EN = 'call or text (915) 302-0902 for a quote'
Q_ES = 'llame o envíe un texto al (915) 302-0902 para cotizar'

# ---------------------------------------------------------------- sentences: key = full sentence or unique prefix; value = replacement ('' deletes)
SENT = {
# apostille / birth certificate
"Second, only the Texas Secretary of State's Authentications Unit in Austin may issue the apostille, for a fee of $15 per document,":
    "Second, only the Texas Secretary of State's Authentications Unit in Austin may issue the apostille, for a per-document state fee, and it will only authenticate a certified copy bearing the signature of a current official; the Secretary of State may require a recently issued copy rather than the decades-old original in your safe.",
"Segunda, solo la Unidad de Autenticaciones de la Secretaría de Estado de Texas en Austin puede emitir la apostilla, por una cuota de $15 por documento,":
    "Segunda, solo la Unidad de Autenticaciones de la Secretaría de Estado de Texas en Austin puede emitir la apostilla, por una cuota estatal por documento, y solo autenticará una copia certificada con la firma de un funcionario actual; la Secretaría de Estado puede exigir una copia emitida recientemente en lugar del original de hace décadas que guarda en su caja fuerte.",
"We confirm whether your copy will be accepted or whether a fresh certified copy needs to be ordered, quote the total — our service fee plus the $15 state fee per document and shipping —":
    "We confirm whether your copy will be accepted or whether a fresh certified copy needs to be ordered, quote the total — our service fee plus the state fee per document and shipping — and pick up the document anywhere in El Paso or start from a copy you order online.",
"Confirmamos si su copia será aceptada o si hay que pedir una copia certificada nueva, cotizamos el total — nuestra tarifa de servicio más los $15 estatales por documento y el envío —":
    "Confirmamos si su copia será aceptada o si hay que pedir una copia certificada nueva, cotizamos el total — nuestra tarifa de servicio más la cuota estatal por documento y el envío — y recogemos el documento en cualquier parte de El Paso o partimos de una copia que usted pida en línea.",
"We pick up the document anywhere in El Paso, prepare the request form and the $15 state fee per document,":
    "We pick up the document anywhere in El Paso, prepare the request form and the state fee per document, ship the package to Austin with tracking, and follow it until the apostille is attached.",
"Recogemos el documento en cualquier parte de El Paso, preparamos la solicitud y la cuota estatal de $15 por documento,":
    "Recogemos el documento en cualquier parte de El Paso, preparamos la solicitud y la cuota estatal por documento, enviamos el paquete a Austin con rastreo y le damos seguimiento hasta que la apostilla esté adjunta.",
"The Texas Secretary of State charges $15 per document.":
    "The Texas Secretary of State charges a fee for each document, itemized in your quote.",
"La Secretaría de Estado de Texas cobra $15 por documento.":
    "La Secretaría de Estado de Texas cobra una cuota por cada documento, detallada en su cotización.",
# apostille / diploma & transcripts
"Either a school official, usually the registrar, signs a statement that the copy or transcript is genuine":
    "Either a school official, usually the registrar, signs a statement that the copy or transcript is genuine and that signature is notarized, or our notary certifies a copy of your original diploma under Tex. Gov't Code §406.016, which allows certified copies of documents not recordable in public records, at the fee Texas caps by statute (Tex. Gov't Code §406.024).",
"O un funcionario de la escuela, normalmente el registrar, firma una constancia de que la copia o el certificado de estudios es genuino":
    "O un funcionario de la escuela, normalmente el registrar, firma una constancia de que la copia o el certificado de estudios es genuino y esa firma se notariza, o nuestro Notary Public certifica una copia de su diploma original conforme al Código de Gobierno de Texas §406.016, que permite copias certificadas de documentos que no se inscriben en registros públicos, por la tarifa que la ley de Texas limita (§406.024).",
"The Secretary of State then attaches the apostille for $15 per document.":
    "The Secretary of State then attaches the apostille for a per-document fee.",
"Después la Secretaría de Estado adhiere la apostilla por $15 por documento.":
    "Después la Secretaría de Estado adhiere la apostilla por una cuota por documento.",
"Text or call (915) 302-0902 with the school, the document and the destination country, and we confirm the itemized fee:":
    "Text or call (915) 302-0902 with the school, the document and the destination country, and we confirm the itemized quote: notarial fee, travel in El Paso, the Secretary of State's per-document fee and our handling fee.",
"Envíe un texto o llame al (915) 302-0902 con la escuela, el documento y el país destino, y le confirmamos el costo desglosado:":
    "Envíe un texto o llame al (915) 302-0902 con la escuela, el documento y el país destino, y le confirmamos la cotización desglosada: tarifa de notarización, traslado en El Paso, la cuota por documento de la Secretaría de Estado y nuestra tarifa de gestión.",
"Finally, order more than one set if you are applying to several countries or institutions: each apostille is $15":
    "Finally, order more than one set if you are applying to several countries or institutions: each apostille carries its own state fee and attaches to one document, and a Spanish university and a Mexican employer will each want their own original.",
"Por último, pida más de un juego si va a aplicar a varios países o instituciones: cada apostilla cuesta $15":
    "Por último, pida más de un juego si va a aplicar a varios países o instituciones: cada apostilla paga su propia cuota estatal y se adhiere a un solo documento, y una universidad española y un empleador mexicano querrán cada uno su propio original.",
"We explain the two preparations the Secretary of State accepts, a registrar's notarized statement or a notarized certified copy, and quote the itemized total including the $15 fee per document.":
    "We explain the two preparations the Secretary of State accepts, a registrar's notarized statement or a notarized certified copy, and quote the itemized total, including the state fee per document.",
"Le explicamos las dos preparaciones que acepta la Secretaría de Estado, constancia notarizada del registrar o copia certificada notarizada, y cotizamos el total desglosado, incluidos los $15 por documento.":
    "Le explicamos las dos preparaciones que acepta la Secretaría de Estado, constancia notarizada del registrar o copia certificada notarizada, y cotizamos el total desglosado, incluida la cuota estatal por documento.",
"Then we submit the document to the Secretary of State with the $15 fee per document, track it, and return the apostilled document to you in El Paso.":
    "Then we submit the document to the Secretary of State with its per-document fee, track it, and return the apostilled document to you in El Paso.",
"Luego presentamos el documento ante la Secretaría de Estado con los $15 por documento, le damos seguimiento y le devolvemos el documento apostillado en El Paso.":
    "Luego presentamos el documento ante la Secretaría de Estado con su cuota por documento, le damos seguimiento y le devolvemos el documento apostillado en El Paso.",
"The parts are fixed by law and itemized: $10 for the notary's certified copy plus $1 per page copied,":
    "Prices vary by document and destination, and every quote is itemized: the notarial fee for the certified copy or the registrar's acknowledgment (capped by Texas statute), travel anywhere in El Paso, the Texas Secretary of State's per-document fee, our handling fee and shipping — " + Q_EN + ".",
"Los componentes están fijados por ley y se desglosan: $10 por la copia certificada del Notary Public más $1 por página copiada,":
    "Los precios varían según el documento y el destino, y cada cotización se desglosa: la tarifa de notarización por la copia certificada o el reconocimiento (acknowledgment) de la constancia del registrar (con tope en la ley de Texas), el traslado en cualquier punto de El Paso, la cuota por documento de la Secretaría de Estado de Texas, nuestra tarifa de gestión y el envío — " + Q_ES + ".",
# apostille / FBI
"A Texas DPS criminal history record, a certified copy from an El Paso County district court or any affidavit sworn before a Texas notary is a Texas document and goes to the Texas Secretary of State for a $15 apostille.":
    "A Texas DPS criminal history record, a certified copy from an El Paso County district court or any affidavit sworn before a Texas notary is a Texas document and goes to the Texas Secretary of State for its apostille.",
"Un historial criminal del DPS de Texas, una copia certificada de una corte de distrito del Condado de El Paso o cualquier declaración jurada firmada ante un Notary Public de Texas es un documento de Texas y va a la Secretaría de Estado de Texas para una apostilla de $15.":
    "Un historial criminal del DPS de Texas, una copia certificada de una corte de distrito del Condado de El Paso o cualquier declaración jurada firmada ante un Notary Public de Texas es un documento de Texas y va a la Secretaría de Estado de Texas para su apostilla.",
"If your recipient has told you in writing that it accepts a sworn statement instead, bring that instruction and we will notarize the statement properly at $10 per jurat plus the $39 travel fee.":
    "If your recipient has told you in writing that it accepts a sworn statement instead, bring that instruction and we will notarize the statement properly — the oath and travel are quoted when you book.",
"Si su destinatario le indicó por escrito que acepta una declaración jurada en su lugar, traiga esa instrucción y la notarizamos como corresponde: $10 por juramento más $39 de traslado.":
    "Si su destinatario le indicó por escrito que acepta una declaración jurada en su lugar, traiga esa instrucción y la notarizamos como corresponde — el juramento y el traslado se cotizan al agendar.",
# apostille / Mexico
"The Secretary of State then certifies the notary's signature and seal for $15 per document (Tex. Gov't Code ch. 406 governs the notarization).":
    "The Secretary of State then certifies the notary's signature and seal for a per-document fee (Tex. Gov't Code ch. 406 governs the notarization).",
"Después, la Secretaría de Estado certifica la firma y el sello del Notary Public, a $15 por documento.":
    "Después, la Secretaría de Estado certifica la firma y el sello del Notary Public, por una cuota por documento.",
"Text or call (915) 302-0902, tell us the document and the office in Mexico receiving it, and we quote the complete package: our service fee, $15 per document for the Secretary of State and shipping.":
    "Text or call (915) 302-0902, tell us the document and the office in Mexico receiving it, and we quote the complete package: our service fee, the Secretary of State's per-document fee and shipping.",
"Envíe un texto o llame al (915) 302-0902, díganos qué documento tiene y a qué oficina de México va, y le cotizamos el paquete: tarifa de servicio, $15 por documento de la Secretaría de Estado y envío.":
    "Envíe un texto o llame al (915) 302-0902, díganos qué documento tiene y a qué oficina de México va, y le cotizamos el paquete: tarifa de servicio, la cuota por documento de la Secretaría de Estado y envío.",
"The notarization beforehand costs $10 for the first signature and $1 for each additional signature, plus the $39 travel fee in El Paso.":
    "The notarization beforehand is quoted separately — it depends on the number of signatures and your location in El Paso.",
"La notarización previa cuesta $10 por la primera firma y $1 por cada firma adicional, más $39 de traslado en El Paso.":
    "La notarización previa se cotiza por separado — depende del número de firmas y de su ubicación en El Paso.",
# apostille / single status
"The Texas Secretary of State then attaches the apostille, authenticating the notary's commission for the receiving country, for $15 per document.":
    "The Texas Secretary of State then attaches the apostille, authenticating the notary's commission for the receiving country, for a per-document fee.",
"La Secretaría de Estado de Texas adjunta después la apostilla, que autentica la comisión del Notary Public ante el país receptor, por $15 por documento.":
    "La Secretaría de Estado de Texas adjunta después la apostilla, que autentica la comisión del Notary Public ante el país receptor, por una cuota por documento.",
"We confirm which document the registry wants, quote the notarization ($10 for the oath plus the $39 travel fee anywhere in El Paso)":
    "We confirm which document the registry wants, quote the notarization and the apostille service together (our fee plus the state fee and shipping), and come to your home or office anywhere in El Paso to administer the oath.",
"Confirmamos qué documento quiere el registro, cotizamos la notarización ($10 por el juramento más $39 de traslado en cualquier parte de El Paso)":
    "Confirmamos qué documento quiere el registro, cotizamos juntos la notarización y el servicio de apostilla (nuestra tarifa más la cuota estatal y el envío), y vamos a su casa u oficina en cualquier parte de El Paso para tomar el juramento.",
"We prepare the Secretary of State request and $15 fee, ship to Austin with tracking,":
    "We prepare the Secretary of State request and fee, ship to Austin with tracking, and return the apostilled affidavit to you or directly to your wedding coordinator abroad, with a photo of the apostille the day it arrives.",
"Preparamos la solicitud y la cuota de $15 de la Secretaría de Estado, enviamos a Austin con rastreo":
    "Preparamos la solicitud y la cuota de la Secretaría de Estado, enviamos a Austin con rastreo y le regresamos la constancia apostillada a usted o directamente a su coordinador de bodas en el extranjero, con una foto de la apostilla el día que llega.",
"The notarization is $10 for the oath plus our $39 travel fee anywhere in El Paso.":
    "Prices vary — the notarization depends on the number of oaths and your location in El Paso, and we quote it before we come.",
"La notarización cuesta $10 por el juramento más $39 de traslado en cualquier parte de El Paso.":
    "Los precios varían — la notarización depende del número de juramentos y de su ubicación en El Paso, y se la cotizamos antes de ir.",
"The apostille is $15 to the Texas Secretary of State per document plus our service fee for preparing, shipping and tracking the request.":
    "The apostille adds the Texas Secretary of State's per-document fee plus our service fee for preparing, shipping and tracking the request; " + Q_EN + ".",
"La apostilla cuesta $15 por documento para la Secretaría de Estado de Texas más nuestra tarifa de servicio por preparar, enviar y rastrear la solicitud.":
    "La apostilla suma la cuota por documento de la Secretaría de Estado de Texas más nuestra tarifa de servicio por preparar, enviar y rastrear la solicitud; " + Q_ES + ".",
"Both of you can sign at the same appointment in El Paso; each oath is a separate $10 fee and each document a separate $15 state fee.":
    "Both of you can sign at the same appointment in El Paso; each oath is a separate notarial act and each document a separate state fee, all itemized in your quote.",
"Los dos pueden firmar en la misma cita en El Paso; cada juramento es una tarifa separada de $10 y cada documento una cuota estatal separada de $15.":
    "Los dos pueden firmar en la misma cita en El Paso; cada juramento es un acto notarial aparte y cada documento una cuota estatal aparte, todo detallado en su cotización.",
# apostille / hub
"For documents issued or notarized in Texas, only the Texas Secretary of State issues apostilles, through its Authentications Unit in Austin, at $15 per document.":
    "For documents issued or notarized in Texas, only the Texas Secretary of State issues apostilles, through its Authentications Unit in Austin, for a per-document fee.",
"Para documentos expedidos o notarizados en Texas, únicamente la Secretaría de Estado emite apostillas, desde su Unidad de Autenticaciones en Austin, a $15 por documento.":
    "Para documentos expedidos o notarizados en Texas, únicamente la Secretaría de Estado emite apostillas, desde su Unidad de Autenticaciones en Austin, por una cuota por documento.",
"We quote the package: our service fee, the $15 Secretary of State fee per document and shipping.":
    "We quote the package: our service fee, the Secretary of State's per-document fee and shipping.",
"Le cotizamos el paquete: nuestra tarifa de servicio, los $15 por documento de la Secretaría de Estado y el envío.":
    "Le cotizamos el paquete: nuestra tarifa de servicio, la cuota por documento de la Secretaría de Estado y el envío.",
"Your notary comes to you anywhere in El Paso County — the Westside, the Northeast, the Lower Valley, Horizon City, Socorro, Fort Bliss — with statutory notarial fees, a nominal $39 travel fee":
    "Your notary comes to you anywhere in El Paso County — the Westside, the Northeast, the Lower Valley, Horizon City, Socorro, Fort Bliss — with notarial fees capped by Texas statute, a separate travel fee and a quoted package price for the Secretary of State handling.",
"Su Notary Public va a donde usted está en todo el condado de El Paso — Westside, Noreste, Lower Valley, Horizon City, Socorro, Fort Bliss — con las tarifas de notarización fijadas por ley, $39 de traslado":
    "Su Notary Public va a donde usted está en todo el condado de El Paso — Westside, Noreste, Lower Valley, Horizon City, Socorro, Fort Bliss — con las tarifas de notarización fijadas por ley, el traslado por separado y un precio cotizado por el trámite ante la Secretaría de Estado.",
"The Texas Secretary of State charges $15 per document for each apostille or certificate of authentication.":
    "The Texas Secretary of State charges a per-document fee for each apostille or certificate of authentication.",
"La Secretaría de Estado de Texas cobra $15 por documento por cada apostilla o certificado de autenticación.":
    "La Secretaría de Estado de Texas cobra una cuota por documento por cada apostilla o certificado de autenticación.",
"On top of that you pay QWIK's service fee and shipping, plus the statutory notarial fee ($10 for the first signature, $1 each additional) and the $39 El Paso travel fee if the document has to be notarized first.":
    "On top of that you pay QWIK's service fee and shipping, plus the notarial fee and El Paso travel fee if the document has to be notarized first — prices vary, so call or text (915) 302-0902 for an itemized quote.",
"A eso se suma la tarifa de servicio de QWIK y el envío, más la tarifa de notarización fijada por ley ($10 la primera firma, $1 cada firma adicional) y los $39 de traslado en El Paso si el documento primero debe notarizarse.":
    "A eso se suma la tarifa de servicio de QWIK y el envío, más la tarifa de notarización y el traslado en El Paso si el documento primero debe notarizarse — los precios varían, así que llame o envíe un texto al (915) 302-0902 para una cotización desglosada.",
# business / attorneys
"A paralegal texts or calls (915) 302-0902 with the document type, the number of signers, the location and the deadline":
    "A paralegal texts or calls (915) 302-0902 with the document type, the number of signers, the location and the deadline — a filing due at 8 a.m., a mediation that settled at 6 p.m. — and we confirm the quote, with the notarial fee and El Paso travel itemized separately.",
"Un paralegal llama o envía un texto al (915) 302-0902 con el tipo de documento, el número de firmantes, el lugar y el plazo":
    "Un paralegal llama o envía un texto al (915) 302-0902 con el tipo de documento, el número de firmantes, el lugar y el plazo — un escrito que vence a las 8 de la mañana, una mediación que se cerró a las 6 de la tarde — y confirmamos la cotización, con la tarifa de notarización y el traslado en El Paso detallados por separado.",
"We also notarize reporter certifications and affidavits that a receiving court or agency wants sworn, and certify copies of exhibits and other non-recordable documents at $10 plus $1 per page.":
    "We also notarize reporter certifications and affidavits that a receiving court or agency wants sworn, and certify copies of exhibits and other non-recordable documents.",
"También notarizamos certificaciones y declaraciones juradas del reportero que una corte o agencia receptora quiera bajo juramento, y certificamos copias de anexos y otros documentos no registrables a $10 más $1 por página.":
    "También notarizamos certificaciones y declaraciones juradas del reportero que una corte o agencia receptora quiera bajo juramento, y certificamos copias de anexos y otros documentos no registrables.",
"We confirm the statutory fee and the $39 travel fee, or bill the visit to the firm's account.":
    "We confirm the quote, or bill the visit to the firm's account.",
"Confirmamos la tarifa legal y los $39 de traslado, o cargamos la visita a la cuenta del despacho.":
    "Confirmamos la cotización, o cargamos la visita a la cuenta del despacho.",
"The notarial fees are fixed by Texas law: $10 per oath or affirmation with jurat,":
    "Prices vary by document, number of signatures and location; notarial fees are capped by Texas law (Tex. Gov't Code §406.024) and we itemize them on every invoice.",
"Las tarifas de notarización las fija la ley de Texas: $10 por juramento o afirmación con jurat,":
    "Los precios varían según el documento, el número de firmas y la ubicación; la ley de Texas fija topes a las tarifas de notarización (Código de Gobierno §406.024) y las detallamos en cada factura.",
"QWIK adds a nominal $39 travel fee within the El Paso area, itemized separately; after-hours and out-of-area trips are quoted.":
    "Travel within the El Paso area is itemized separately; after-hours and out-of-area trips are quoted — " + Q_EN + ".",
"QWIK agrega $39 de traslado dentro del área de El Paso, detallados por separado; las salidas fuera de horario o del área se cotizan.":
    "El traslado dentro del área de El Paso se detalla por separado; las salidas fuera de horario o del área se cotizan — " + Q_ES + ".",
# business / business documents
"Text or call (915) 302-0902 with the document type, the number of signers and your address; we confirm the statutory fee and the $39 El Paso travel fee up front.":
    "Text or call (915) 302-0902 with the document type, the number of signers and your address; we confirm your quote up front.",
"Llame o envíe un texto al (915) 302-0902 con el tipo de documento, el número de firmantes y su dirección; confirmamos por adelantado la tarifa legal y los $39 de traslado en El Paso.":
    "Llame o envíe un texto al (915) 302-0902 con el tipo de documento, el número de firmantes y su dirección; confirmamos la cotización por adelantado.",
"We confirm the statutory fee, the $39 travel fee and a time — same day, evening or weekend as needed.":
    "We confirm the quote and a time — same day, evening or weekend as needed.",
"Confirmamos la tarifa legal, los $39 de traslado y la hora — el mismo día, tarde o fin de semana.":
    "Confirmamos la cotización y la hora — el mismo día, tarde o fin de semana.",
"Texas caps notarial fees by statute: $10 for the first signature acknowledged on each document and $1 for each additional signature, $10 per oath or affirmation, and $10 plus $1 per page for a certified copy.":
    "Prices vary by the number of documents, signatures and oaths; Texas caps notarial fees by statute, and we quote the total before we come.",
"La ley de Texas limita las tarifas: $10 por la primera firma reconocida en cada documento y $1 por cada firma adicional, $10 por juramento (jurat), y $10 más $1 por página por una copia certificada.":
    "Los precios varían según el número de documentos, firmas y juramentos; la ley de Texas limita las tarifas de notarización, y cotizamos el total antes de ir.",
"QWIK adds a nominal $39 travel fee for the trip anywhere in El Paso, itemized separately, and one visit can cover a whole stack of documents.":
    "Travel anywhere in El Paso is itemized separately, and one visit can cover a whole stack of documents — " + Q_EN + ".",
"QWIK agrega $39 de traslado por el viaje a cualquier punto de El Paso, detallados por separado, y una sola visita puede cubrir todos sus documentos.":
    "El traslado a cualquier punto de El Paso se detalla por separado, y una sola visita puede cubrir todos sus documentos — " + Q_ES + ".",
"The fee is $10 for the certificate plus $1 per page copied.":
    "The fee depends on the page count and is quoted when you book.",
"La tarifa es $10 por el certificado más $1 por página copiada.":
    "La tarifa depende del número de páginas y se cotiza al agendar.",
# business / financial documents
"Text or call (915) 302-0902 with the form name, the number of signers and where you are; we confirm the statutory fee —":
    "Text or call (915) 302-0902 with the form name, the number of signers and where you are; we confirm the quote — notarial fee plus El Paso travel, itemized separately.",
"Llame o envíe un texto al (915) 302-0902 con el nombre del formulario, el número de firmantes y dónde se encuentra; confirmamos la tarifa legal —":
    "Llame o envíe un texto al (915) 302-0902 con el nombre del formulario, el número de firmantes y dónde se encuentra; confirmamos la cotización — tarifa de notarización más el traslado en El Paso, detallados por separado.",
"We tell you whether the form actually needs a notary and confirm the statutory fee plus the $39 travel fee before we come.":
    "We tell you whether the form actually needs a notary and confirm the quote before we come.",
"Le decimos si el formulario realmente necesita Notary Public y confirmamos la tarifa legal más los $39 de traslado antes de ir.":
    "Le decimos si el formulario realmente necesita Notary Public y confirmamos la cotización antes de ir.",
"Texas sets the notarial fees: $10 for the first signature acknowledged and $1 for each additional signature on the same document, $10 for each oath or affirmation with a jurat, and $10 plus $1 per page for a certified copy of a non-recordable document.":
    "Prices vary by form, number of signatures and location; Texas caps notarial fees by statute (Tex. Gov't Code §406.024).",
"Texas fija las tarifas de notarización: $10 por la primera firma reconocida y $1 por cada firma adicional en el mismo documento, $10 por cada juramento con jurat, y $10 más $1 por página por una copia certificada de un documento no registrable.":
    "Los precios varían según el formulario, el número de firmas y la ubicación; la ley de Texas fija topes a las tarifas de notarización (Código de Gobierno §406.024).",
"QWIK adds a nominal $39 travel fee anywhere in the El Paso area, always itemized separately.":
    "Travel anywhere in the El Paso area is always itemized separately — " + Q_EN + ".",
"QWIK agrega $39 de traslado en el área de El Paso, siempre detallados por separado.":
    "El traslado en el área de El Paso siempre se detalla por separado — " + Q_ES + ".",
# business / hub
"Fees are the statutory Texas amounts — $10 for the first signature, $1 for each additional signature, $10 per oath — plus a nominal $39 travel fee in El Paso, itemized separately.":
    "Prices vary by document, number of signatures and location; notarial fees are capped by Texas statute, travel in El Paso is itemized separately, and we confirm the total before we come.",
"Las tarifas son las que fija la ley de Texas — $10 por la primera firma, $1 por cada firma adicional, $10 por juramento — más $39 de traslado en El Paso, detallados por separado.":
    "Los precios varían según el documento, el número de firmas y la ubicación; la ley de Texas limita las tarifas de notarización, el traslado en El Paso se detalla por separado y confirmamos el total antes de ir.",
"You pay the statutory fee per signature or oath plus a single $39 travel fee for the visit.":
    "You pay the notarial fee per signature or oath plus a single travel fee for the visit, quoted when you book.",
"Usted paga la tarifa legal por firma o juramento más un solo cargo de traslado de $39 por la visita.":
    "Usted paga la tarifa de notarización por firma o juramento más un solo cargo de traslado por la visita, cotizado al agendar.",
"Texas sets notarial fees by statute: $10 for the first signature acknowledged on a document and $1 for each additional signature, $10 for an oath or affirmation, and $10 plus $1 per page for a certified copy.":
    "Prices vary by document, number of signatures and location; Texas caps notarial fees by statute and we itemize every charge.",
"La ley de Texas fija las tarifas de notarización: $10 por la primera firma reconocida en un documento y $1 por cada firma adicional, $10 por juramento (jurat), y $10 más $1 por página por una copia certificada.":
    "Los precios varían según el documento, el número de firmas y la ubicación; la ley de Texas fija topes a las tarifas de notarización y detallamos cada cargo.",
"QWIK adds a nominal $39 travel fee for the trip anywhere in El Paso, listed separately on your receipt.":
    "Travel anywhere in El Paso is listed separately on your receipt — " + Q_EN + ".",
"QWIK agrega $39 de traslado por el viaje a cualquier punto de El Paso, detallado por separado en su recibo.":
    "El traslado a cualquier punto de El Paso se detalla por separado en su recibo — " + Q_ES + ".",
# estate planning / hub
"Fees are the Texas statutory fees — $10 first signature, $1 each additional — plus a $39 travel fee in El Paso.":
    "Prices vary by document and number of signatures; notarial fees are capped by Texas statute, travel in El Paso is itemized separately, and we quote the total when you book.",
"Cobramos las tarifas oficiales de Texas — $10 la primera firma y $1 cada firma adicional — más $39 de traslado en todo El Paso.":
    "Los precios varían según el documento y el número de firmas; la ley de Texas limita las tarifas de notarización, el traslado en El Paso se detalla por separado y cotizamos el total al agendar.",
"Texas caps notary fees by law: $10 for the first signature acknowledged and $1 for each additional signature on the same document, and $10 per oath, such as the self-proving affidavit on a will.":
    "Prices vary by the number of documents, signatures and oaths — a self-proving affidavit on a will, for example, is a separate oath; Texas caps notarial fees by law.",
"La ley de Texas limita las tarifas: $10 por la primera firma que se reconoce y $1 por cada firma adicional en el mismo documento, y $10 por cada juramento (jurat), como la declaración jurada de autenticidad de un testamento.":
    "Los precios varían según el número de documentos, firmas y juramentos — la declaración jurada de autenticidad de un testamento, por ejemplo, es un juramento aparte; la ley de Texas limita las tarifas de notarización.",
"QWIK adds a nominal $39 travel fee for the visit anywhere in El Paso, itemized separately.":
    "Travel for the visit anywhere in El Paso is itemized separately — " + Q_EN + ".",
"QWIK agrega $39 de traslado por la visita a cualquier parte de El Paso, detallados por separado.":
    "El traslado por la visita a cualquier parte de El Paso se detalla por separado — " + Q_ES + ".",
# estate planning / medical POA
"We confirm the fee — Texas statutory fees plus a $39 travel fee in El Paso — and come to the home, room or care facility;":
    "We confirm the quote and come to the home, room or care facility anywhere in El Paso; a set of directives usually takes about 15 minutes once ID is checked.",
"Le confirmamos el costo — las tarifas oficiales de Texas más $39 de traslado en El Paso — y vamos a la casa, al cuarto o al centro de cuidados;":
    "Le confirmamos la cotización y vamos a la casa, al cuarto o al centro de cuidados en cualquier parte de El Paso; un juego de directivas suele tomar unos 15 minutos una vez revisada la identificación.",
"We confirm the fee — statutory notary fees plus a $39 El Paso travel fee — and schedule the visit, including evenings and weekends.":
    "We confirm the quote and schedule the visit, including evenings and weekends.",
"Le confirmamos el costo — tarifas oficiales más $39 de traslado en El Paso — y agendamos la visita, tardes y fines de semana incluidos.":
    "Le confirmamos la cotización y agendamos la visita, tardes y fines de semana incluidos.",
"The Texas statutory fee is $10 for the first signature on each document and $1 for each additional signature on that document, plus QWIK's nominal $39 travel fee anywhere in El Paso, itemized separately.":
    "Prices vary by the number of documents and signatures and by location; Texas caps the notarial fee by statute, travel anywhere in El Paso is itemized separately, and we confirm the total before the visit — " + Q_EN + ".",
"La tarifa oficial de Texas es $10 por la primera firma de cada documento y $1 por cada firma adicional en ese documento, más los $39 de traslado de QWIK a cualquier parte de El Paso, detallados por separado.":
    "Los precios varían según el número de documentos y firmas y según la ubicación; la ley de Texas limita la tarifa de notarización, el traslado a cualquier parte de El Paso se detalla por separado y confirmamos el total antes de la visita — " + Q_ES + ".",
# estate planning / POA
"We confirm the fee — Texas statutory fees plus a $39 travel fee in El Paso — and meet you at home, at work, at a hospital bedside or the jail.":
    "We confirm the quote and meet you at home, at work, at a hospital bedside or the jail anywhere in El Paso.",
"Le confirmamos el costo — las tarifas oficiales de Texas más $39 de traslado en El Paso — y nos vemos en su casa, su trabajo, la cama del hospital o la cárcel.":
    "Le confirmamos la cotización y nos vemos en su casa, su trabajo, la cama del hospital o la cárcel en cualquier parte de El Paso.",
"We confirm the fee — statutory notary fees plus a $39 El Paso travel fee — and hold your slot, evenings and weekends included.":
    "We confirm the quote and hold your slot, evenings and weekends included.",
"Le confirmamos el costo — tarifas oficiales más $39 de traslado en El Paso — y apartamos su cita, tardes y fines de semana incluidos.":
    "Le confirmamos la cotización y apartamos su cita, tardes y fines de semana incluidos.",
"The Texas statutory fee is $10 for the first signature acknowledged and $1 for each additional signature on the same document, plus QWIK's nominal $39 travel fee anywhere in El Paso, itemized separately.":
    "Prices vary by the number of documents and signatures and by location; Texas caps the notarial fee by statute and travel anywhere in El Paso is itemized separately.",
"La tarifa oficial de Texas es $10 por la primera firma que se reconoce y $1 por cada firma adicional en el mismo documento, más los $39 de traslado de QWIK a cualquier parte de El Paso, detallados por separado.":
    "Los precios varían según el número de documentos y firmas y según la ubicación; la ley de Texas limita la tarifa de notarización y el traslado a cualquier parte de El Paso se detalla por separado.",
"Two spouses each signing their own power of attorney is two documents, so two $10 fees and one travel fee.":
    "Two spouses each signing their own power of attorney is two documents, so two notarial fees and one travel fee — " + Q_EN + ".",
"Si dos esposos firman cada uno su propia carta poder, son dos documentos: dos tarifas de $10 y un solo traslado.":
    "Si dos esposos firman cada uno su propia carta poder, son dos documentos: dos tarifas de notarización y un solo traslado — " + Q_ES + ".",
"We notarize the power of attorney in El Paso — usually a Spanish-language document sent by the family's attorney or the receiving party in Mexico — and then the Texas Secretary of State issues an apostille ($15 per document)":
    "We notarize the power of attorney in El Paso — usually a Spanish-language document sent by the family's attorney or the receiving party in Mexico — and then the Texas Secretary of State issues an apostille (for a per-document state fee) so it is recognized in Mexico under the Hague Convention.",
"Notarizamos la carta poder en El Paso — por lo general un documento en español que envía el abogado de la familia o quien lo recibirá en México — y después la Secretaría de Estado de Texas le pone la apostilla ($15 por documento)":
    "Notarizamos la carta poder en El Paso — por lo general un documento en español que envía el abogado de la familia o quien lo recibirá en México — y después la Secretaría de Estado de Texas le pone la apostilla (por una cuota estatal por documento) para que se reconozca en México conforme al Convenio de La Haya.",
# estate planning / wills
"Text or call (915) 302-0902 with the list of documents and how many people will sign; we confirm the statutory fees plus the $39 El Paso travel fee and come to your home, the attorney's office or the hospital.":
    "Text or call (915) 302-0902 with the list of documents and how many people will sign; we confirm the quote and come to your home, the attorney's office or the hospital anywhere in El Paso.",
"Envíe un texto o llame al (915) 302-0902 con la lista de documentos y cuántas personas van a firmar; le confirmamos las tarifas oficiales más los $39 de traslado en El Paso y vamos a su casa, al despacho del abogado o al hospital.":
    "Envíe un texto o llame al (915) 302-0902 con la lista de documentos y cuántas personas van a firmar; le confirmamos la cotización y vamos a su casa, al despacho del abogado o al hospital en cualquier parte de El Paso.",
"We confirm the statutory fees plus the $39 El Paso travel fee and schedule a time when your witnesses can be there — evenings and weekends included.":
    "We confirm the quote and schedule a time when your witnesses can be there — evenings and weekends included.",
"Le confirmamos las tarifas oficiales más los $39 de traslado en El Paso y agendamos una hora en la que sus testigos puedan estar — tardes y fines de semana incluidos.":
    "Le confirmamos la cotización y agendamos una hora en la que sus testigos puedan estar — tardes y fines de semana incluidos.",
"Texas sets the fees: $10 per oath administered — the self-proving affidavit is sworn by the testator and both witnesses —":
    "Prices vary by the number of oaths and signatures — the self-proving affidavit is sworn by the testator and both witnesses, and a trust, deed or certificate is acknowledged separately; Texas caps every notarial fee by statute.",
"Texas fija las tarifas: $10 por cada juramento (jurat) — la declaración jurada de autenticidad la juran el testador y los dos testigos —":
    "Los precios varían según el número de juramentos y firmas — la declaración jurada de autenticidad la juran el testador y los dos testigos, y un fideicomiso, una escritura o un certificado se reconocen por separado; la ley de Texas limita cada tarifa de notarización.",
"QWIK adds a nominal $39 travel fee anywhere in El Paso, itemized separately.":
    "Travel anywhere in El Paso is itemized separately — " + Q_EN + ".",
"QWIK agrega $39 de traslado a cualquier parte de El Paso, detallados por separado.":
    "El traslado a cualquier parte de El Paso se detalla por separado — " + Q_ES + ".",
# family / child travel consent
"Text or call (915) 302-0902, tell us what you are signing and where you are — your home in Horizon City, your office downtown, a hospital room, a coffee shop near UTEP — and we confirm the fee:":
    "Text or call (915) 302-0902, tell us what you are signing and where you are — your home in Horizon City, your office downtown, a hospital room, a coffee shop near UTEP — and we confirm your quote up front; prices vary by the number of signatures and your location in El Paso County.",
"Envíe un texto o llame al (915) 302-0902, díganos qué va a firmar y dónde está — su casa en Horizon City, su oficina en el centro, un cuarto de hospital, un café cerca de UTEP — y confirmamos la tarifa:":
    "Envíe un texto o llame al (915) 302-0902, díganos qué va a firmar y dónde está — su casa en Horizon City, su oficina en el centro, un cuarto de hospital, un café cerca de UTEP — y le confirmamos la cotización por adelantado; los precios varían según el número de firmas y su ubicación en el Condado de El Paso.",
"We confirm the statutory fee and the $39 travel fee up front.":
    "We confirm your quote up front.",
"Confirmamos la cuota legal y los $39 de traslado desde el principio.":
    "Confirmamos la cotización desde el principio.",
"If both parents sign the same letter at one visit, the fee is $10 for the first signature and $1 for the second; a separate visit for the other parent is its own appointment.":
    "If both parents sign the same letter at one visit, it is a single notarization with two signatures; a separate visit for the other parent is its own appointment with its own travel.",
"Si ambos padres firman la misma carta en una visita, la tarifa es $10 por la primera firma y $1 por la segunda; una visita aparte para el otro padre es una cita distinta.":
    "Si ambos padres firman la misma carta en una visita, es una sola notarización con dos firmas; una visita aparte para el otro padre es una cita distinta con su propio traslado.",
"The notarial fee is the Texas statutory $10 for the signature, plus our nominal $39 travel fee anywhere in the El Paso area, itemized separately.":
    "Prices vary by location and timing; the notarial fee is capped by Texas statute and our travel anywhere in the El Paso area is itemized separately — " + Q_EN + ".",
"La cuota de notarización es la que fija la ley de Texas, $10 por la firma, más nuestros $39 de traslado en cualquier punto del área de El Paso, desglosados por separado.":
    "Los precios varían según la ubicación y el horario; la cuota de notarización tiene tope en la ley de Texas y nuestro traslado en el área de El Paso se desglosa por separado — " + Q_ES + ".",
"Online notarization is $25 with no travel fee.":
    "Online notarization has no travel fee.",
"La notarización en línea cuesta $25 sin traslado.":
    "La notarización en línea no tiene traslado.",
"If a Mexican government office will rely on the letter as an official document, it may require an apostille from the Texas Secretary of State ($15 per document), which we can handle.":
    "If a Mexican government office will rely on the letter as an official document, it may require an apostille from the Texas Secretary of State (a per-document state fee applies), which we can handle.",
"Si una dependencia del gobierno de México va a usar la carta como documento oficial, puede exigir una apostilla de la Secretaría de Estado de Texas ($15 por documento), trámite que podemos hacer por usted.":
    "Si una dependencia del gobierno de México va a usar la carta como documento oficial, puede exigir una apostilla de la Secretaría de Estado de Texas (aplica una cuota estatal por documento), trámite que podemos hacer por usted.",
# family / divorce custody name change
"We confirm the fee — $10 per oath or acknowledgment, $1 for each additional signature on the same document, plus a $39 travel fee in El Paso — and set a time, including evenings and weekends.":
    "We confirm the quote and set a time anywhere in El Paso, including evenings and weekends.",
"Confirmamos la tarifa — $10 por juramento o reconocimiento, $1 por cada firma adicional en el mismo documento, más $39 de traslado en El Paso — y fijamos una hora, incluso en la tarde o el fin de semana.":
    "Confirmamos la cotización y fijamos una hora en cualquier parte de El Paso, incluso en la tarde o el fin de semana.",
"We confirm the fee — statutory notarial fee plus the $39 El Paso travel fee — and set a time that works for everyone who signs, including evenings.":
    "We confirm the quote and set a time that works for everyone who signs, including evenings.",
"Confirmamos la tarifa — la tarifa legal más $39 de traslado en El Paso — y fijamos una hora que funcione para todos los que firman, incluso en la tarde.":
    "Confirmamos la cotización y fijamos una hora que funcione para todos los que firman, incluso en la tarde.",
"Texas sets the notarial fee: $10 for an oath or the first acknowledged signature and $1 for each additional signature on the same document.":
    "Prices vary by the number of oaths, signatures and documents; Texas caps the notarial fee by statute.",
"Texas fija la tarifa: $10 por un juramento o la primera firma reconocida y $1 por cada firma adicional en el mismo documento.":
    "Los precios varían según el número de juramentos, firmas y documentos; la ley de Texas limita la tarifa de notarización.",
"We add a nominal $39 travel fee anywhere in El Paso, itemized separately.":
    "Travel anywhere in El Paso is itemized separately.",
"Agregamos $39 de traslado en cualquier parte de El Paso, detallados por separado.":
    "El traslado en cualquier parte de El Paso se detalla por separado.",
"A typical waiver of service costs $10 plus travel; a packet with several affidavits is quoted before we come.":
    "A single waiver of service and a packet with several affidavits are both quoted before we come — call or text (915) 302-0902.",
"Una renuncia de citación típica cuesta $10 más el traslado; un paquete con varias declaraciones juradas se cotiza antes de ir.":
    "Una renuncia de citación sola o un paquete con varias declaraciones juradas se cotizan antes de ir — llame o envíe un texto al (915) 302-0902.",
# family / guardianship adoption
"Text or call (915) 302-0902, tell us which document you have and who will sign, and we confirm the fee: $10 per oath or acknowledgment,":
    "Text or call (915) 302-0902, tell us which document you have and who will sign, and we confirm your quote and come to you anywhere in El Paso County — at home, at your attorney's office, at the adoption agency, or in a hospital room at UMC or Las Palmas.",
"Envíe un texto o llame al (915) 302-0902, díganos qué documento tiene y quién va a firmar, y confirmamos la tarifa: $10 por juramento o reconocimiento,":
    "Envíe un texto o llame al (915) 302-0902, díganos qué documento tiene y quién va a firmar, y confirmamos la cotización y vamos a donde usted esté en cualquier punto del Condado de El Paso — en su casa, en el despacho de su abogado, en la agencia de adopción o en un cuarto de hospital en UMC o Las Palmas.",
"When an adoption dossier or guardianship document will be used in Mexico or another country, notarization is the first step, not the last: the notarized document then goes to the Texas Secretary of State for an apostille ($15 per document),":
    "When an adoption dossier or guardianship document will be used in Mexico or another country, notarization is the first step, not the last: the notarized document then goes to the Texas Secretary of State for an apostille (the state charges a per-document fee), a step QWIK can handle by mail for you.",
"Cuando un expediente de adopción o un documento de tutela se va a usar en México u otro país, la notarización es el primer paso, no el último: el documento notarizado pasa después a la Secretaría de Estado de Texas para la apostilla ($15 por documento),":
    "Cuando un expediente de adopción o un documento de tutela se va a usar en México u otro país, la notarización es el primer paso, no el último: el documento notarizado pasa después a la Secretaría de Estado de Texas para la apostilla (el estado cobra una cuota por documento), trámite que QWIK puede hacer por correo por usted.",
"We confirm the statutory fee per oath or acknowledgment and the $39 travel fee before we leave.":
    "We confirm the quote before we leave.",
"Confirmamos la cuota legal por juramento o reconocimiento y los $39 de traslado antes de salir.":
    "Confirmamos la cotización antes de salir.",
"Texas law caps the fee at $10 per oath or affirmation and $10 for the first acknowledged signature plus $1 for each additional signature on the same document.":
    "Prices vary by the number of oaths, signatures and documents and by location; Texas law caps each notarial fee by statute.",
"La ley de Texas fija un tope de $10 por juramento y de $10 por la primera firma reconocida más $1 por cada firma adicional en el mismo documento.":
    "Los precios varían según el número de juramentos, firmas y documentos y según la ubicación; la ley de Texas fija un tope a cada tarifa de notarización.",
"QWIK Mobile Notary Public charges those statutory fees plus a nominal $39 travel fee anywhere in the El Paso area, itemized separately; a relinquishment affidavit with one sworn signature, for example, is $10 plus travel.":
    "QWIK Mobile Notary Public itemizes the notarial fee and travel anywhere in the El Paso area separately and confirms the total before the visit — " + Q_EN + ".",
"QWIK Mobile Notary Public cobra esas cuotas legales más $39 de traslado en cualquier punto del área de El Paso, desglosados por separado; una declaración de renuncia con una sola firma jurada, por ejemplo, cuesta $10 más el traslado.":
    "QWIK Mobile Notary Public desglosa por separado la cuota de notarización y el traslado en cualquier punto del área de El Paso y confirma el total antes de la visita — " + Q_ES + ".",
"We notarize the affidavits, consents and powers in the dossier in El Paso, then the documents go to the Texas Secretary of State for an apostille at $15 per document —":
    "We notarize the affidavits, consents and powers in the dossier in El Paso, then the documents go to the Texas Secretary of State for an apostille (a per-document state fee applies) — Mexico is a Hague Convention country, so one apostille and no consular legalization.",
"Notarizamos en El Paso las declaraciones juradas, consentimientos y poderes del expediente, y después los documentos pasan a la Secretaría de Estado de Texas para la apostilla, a $15 por documento —":
    "Notarizamos en El Paso las declaraciones juradas, consentimientos y poderes del expediente, y después los documentos pasan a la Secretaría de Estado de Texas para la apostilla (aplica una cuota estatal por documento) — México es parte del Convenio de La Haya, así que basta una apostilla y no hace falta legalización consular.",
# family / hub
"You call or text (915) 302-0902, tell us which document you have and where you are — a home in the Lower Valley, an office on the Westside, a room at University Medical Center — and we confirm the fee:":
    "You call or text (915) 302-0902, tell us which document you have and where you are — a home in the Lower Valley, an office on the Westside, a room at University Medical Center — and we confirm your quote: prices vary by document, number of signatures and location, with the notarial fee and El Paso travel itemized separately.",
"Usted llama o envía un texto al (915) 302-0902, nos dice qué documento tiene y dónde está — una casa en el Valle Bajo (Lower Valley), una oficina en el Westside, un cuarto en el University Medical Center — y confirmamos la tarifa:":
    "Usted llama o envía un texto al (915) 302-0902, nos dice qué documento tiene y dónde está — una casa en el Valle Bajo (Lower Valley), una oficina en el Westside, un cuarto en el University Medical Center — y le confirmamos la cotización: los precios varían según el documento, el número de firmas y la ubicación, con la cuota de notarización y el traslado en El Paso detallados por separado.",
"If both parents sign the same letter at the same visit, the fee is $10 for the first signature and $1 for the second; a later visit for the other parent is a separate appointment with its own travel fee.":
    "If both parents sign the same letter at the same visit, it is one notarization with two signatures; a later visit for the other parent is a separate appointment with its own travel fee.",
"Si ambos padres firman la misma carta en la misma visita, la tarifa es $10 por la primera firma y $1 por la segunda; una visita posterior para el otro padre es una cita aparte con su propio traslado.":
    "Si ambos padres firman la misma carta en la misma visita, es una sola notarización con dos firmas; una visita posterior para el otro padre es una cita aparte con su propio traslado.",
"Texas caps notarial fees by law: $10 for the first signature acknowledged and $1 for each additional signature on the same document, $10 for each oath or affirmation (most affidavits), and $10 plus $1 per page for a certified copy of a non-recordable document.":
    "Prices vary by document, number of signatures or oaths, and location; Texas caps notarial fees by law (Tex. Gov't Code §406.024).",
"La ley de Texas fija un tope a las cuotas: $10 por la primera firma reconocida y $1 por cada firma adicional en el mismo documento, $10 por cada juramento (la mayoría de las declaraciones juradas) y $10 más $1 por página por una copia certificada de un documento no registrable.":
    "Los precios varían según el documento, el número de firmas o juramentos y la ubicación; la ley de Texas fija un tope a las cuotas de notarización (Código de Gobierno §406.024).",
"QWIK Mobile Notary Public charges those statutory fees plus a nominal $39 travel fee anywhere in the El Paso area, itemized separately.":
    "QWIK Mobile Notary Public itemizes the notarial fee and travel anywhere in the El Paso area separately — " + Q_EN + ".",
"QWIK Mobile Notary Public cobra esas cuotas legales más $39 de traslado en cualquier punto del área de El Paso, desglosados por separado.":
    "QWIK Mobile Notary Public desglosa por separado la cuota de notarización y el traslado en cualquier punto del área de El Paso — " + Q_ES + ".",
# forms / hub
"Text or call (915) 302-0902 with the name of the form and where you are — a home in the Lower Valley, an office near Fort Bliss, a room at UMC, the El Paso County Detention Facility — and we confirm the fee before we leave:":
    "Text or call (915) 302-0902 with the name of the form and where you are — a home in the Lower Valley, an office near Fort Bliss, a room at UMC, the El Paso County Detention Facility — and we confirm your quote before we leave; prices vary by form, number of signatures or sworn statements, and location in the El Paso area.",
"Llame o envíe un texto al (915) 302-0902 con el nombre del formulario y el lugar donde está — una casa en el Valle Bajo (Lower Valley), una oficina cerca de Fort Bliss, un cuarto en UMC, la cárcel del Condado de El Paso — y confirmamos la tarifa antes de salir:":
    "Llame o envíe un texto al (915) 302-0902 con el nombre del formulario y el lugar donde está — una casa en el Valle Bajo (Lower Valley), una oficina cerca de Fort Bliss, un cuarto en UMC, la cárcel del Condado de El Paso — y confirmamos la cotización antes de salir; los precios varían según el formulario, el número de firmas o declaraciones juradas y la ubicación en el área de El Paso.",
# forms / school & government
"The statutory fee is $10 for each oath.":
    "Each oath is a separate notarial act, capped by Texas statute.",
"La tarifa legal es de $10 por cada juramento.":
    "Cada juramento es un acto notarial aparte, con tope en la ley de Texas.",
"The fee is $10 per oath plus a $39 travel fee anywhere in El Paso; a residency affidavit signed by a parent and a homeowner is two oaths, $20 plus travel.":
    "Prices vary by the number of oaths and your location in El Paso — a residency affidavit signed by a parent and a homeowner is two oaths — and we quote the total before we come.",
"La tarifa es de $10 por juramento más $39 de traslado en cualquier parte de El Paso; una declaración de residencia firmada por un padre y un propietario son dos juramentos, $20 más el traslado.":
    "Los precios varían según el número de juramentos y su ubicación en El Paso — una declaración de residencia firmada por un padre y un propietario son dos juramentos — y cotizamos el total antes de ir.",
"We confirm the fee — $10 per oath, $39 travel anywhere in El Paso — and pick a time when everyone is home, evenings and weekends included.":
    "We confirm the quote and pick a time when everyone is home anywhere in El Paso, evenings and weekends included.",
"Confirmamos la tarifa — $10 por juramento, $39 de traslado en cualquier parte de El Paso — y elegimos una hora en la que todos estén en casa, incluso tarde o fin de semana.":
    "Confirmamos la cotización y elegimos una hora en la que todos estén en casa en cualquier parte de El Paso, incluso tarde o fin de semana.",
"Each oath is a separate $10 notarial fee.":
    "Each oath is a separate notarial fee.",
"Cada juramento es una tarifa separada de $10.":
    "Cada juramento es una tarifa aparte.",
"Texas sets the notarial fee at $10 per oath.":
    "Prices vary by the number of oaths and your location; Texas caps the notarial fee per oath by statute.",
"Texas fija la tarifa en $10 por juramento.":
    "Los precios varían según el número de juramentos y su ubicación; la ley de Texas fija un tope a la tarifa por juramento.",
"A residency affidavit signed by one parent is $10; signed by a parent and a homeowner it is $20.":
    "A residency affidavit signed by one parent is one oath; signed by a parent and a homeowner it is two.",
"Una declaración de residencia firmada por un padre cuesta $10; firmada por un padre y un propietario, $20.":
    "Una declaración de residencia firmada por un padre es un juramento; firmada por un padre y un propietario, son dos.",
"We add a nominal $39 travel fee anywhere in El Paso, itemized separately, so a typical two-signer affidavit at your home totals $59.":
    "Travel anywhere in El Paso is itemized separately — " + Q_EN + ".",
"Agregamos $39 de traslado en cualquier parte de El Paso, detallados por separado, así que una declaración típica con dos firmantes en su casa suma $59.":
    "El traslado en cualquier parte de El Paso se detalla por separado — " + Q_ES + ".",
# forms / vehicle title
"A few pieces are rejected without one: the affidavit of heirship for a deceased owner's vehicle, the gift affidavit a parent and child sign so the transfer is taxed as a $10 gift rather than a sale,":
    "A few pieces are rejected without one: the affidavit of heirship for a deceased owner's vehicle, the gift affidavit a parent and child sign so the transfer is taxed at the flat gift rate rather than as a sale, and the titles of several other states.",
"Pero algunos se rechazan sin ella: la declaración jurada de herencia (affidavit of heirship) del vehículo de un dueño fallecido, el affidavit de regalo que firman padre e hijo para que el traspaso pague $10 de impuesto como regalo y no como venta,":
    "Pero algunos se rechazan sin ella: la declaración jurada de herencia (affidavit of heirship) del vehículo de un dueño fallecido, el affidavit de regalo que firman padre e hijo para que el traspaso pague el impuesto fijo de regalo y no el de venta, y los títulos de varios otros estados.",
"Text or call (915) 302-0902 with the form name and your address, and we confirm the fee before we leave: the statutory notarial fee plus a nominal $39 travel fee in El Paso, evenings and weekends by appointment.":
    "Text or call (915) 302-0902 with the form name and your address, and we confirm your quote before we leave — evenings and weekends by appointment anywhere in El Paso.",
"Llame o envíe un texto al (915) 302-0902 con el nombre del formulario y su dirección, y confirmamos la tarifa antes de salir: la tarifa legal de notarización más $39 de traslado en El Paso, también por la tarde y los fines de semana con cita.":
    "Llame o envíe un texto al (915) 302-0902 con el nombre del formulario y su dirección, y confirmamos la cotización antes de salir — también por la tarde y los fines de semana con cita, en cualquier parte de El Paso.",
"We notarize your bill of sale in El Paso for $10 for the first signature, $1 each additional, plus the $39 travel fee.":
    "We notarize your bill of sale anywhere in El Paso — " + Q_EN + ".",
"Notarizamos su factura de venta en El Paso por $10 la primera firma, $1 cada firma adicional, más $39 de traslado.":
    "Notarizamos su factura de venta en cualquier parte de El Paso — " + Q_ES + ".",
"Texas caps notarial fees, and we charge the statutory amount: $10 for each oath or affirmation, which is what an affidavit requires, and $10 for the first signature plus $1 for each additional signature on an acknowledgment.":
    "Prices vary by the number of oaths and signatures — an affidavit requires an oath, while a title acknowledgment is priced per signature — and Texas caps every notarial fee by statute.",
"Texas limita las tarifas de notarización y cobramos la cantidad legal: $10 por cada juramento, que es lo que requiere una declaración jurada, y $10 por la primera firma más $1 por cada firma adicional en un reconocimiento.":
    "Los precios varían según el número de juramentos y firmas — una declaración jurada requiere juramento, mientras que el reconocimiento de un título se cotiza por firma — y la ley de Texas limita cada tarifa de notarización.",
"Add our nominal $39 travel fee in El Paso.":
    "Travel in El Paso is itemized separately.",
"Sume nuestros $39 de traslado en El Paso.":
    "El traslado en El Paso se detalla por separado.",
"A 14-317 gift affidavit sworn by a donor and a recipient at the same visit is two $10 oaths plus $39 travel.":
    "A 14-317 gift affidavit sworn by a donor and a recipient at the same visit is two oaths plus one trip — " + Q_EN + ".",
"Un affidavit de regalo 14-317 jurado por el donante y el receptor en la misma visita son dos juramentos de $10 más $39 de traslado.":
    "Un affidavit de regalo 14-317 jurado por el donante y el receptor en la misma visita son dos juramentos más un solo traslado — " + Q_ES + ".",
# loan signing
"Texas caps the notarial portion at $10 for the first signature and $1 for each additional signature on a document, or $10 per oath, itemized separately from travel.":
    "Texas caps the notarial portion by statute, and we itemize it separately from travel and the signing fee.",
"Texas limita la parte de notarización a $10 por la primera firma y $1 por cada firma adicional por documento, o $10 por juramento, aparte del traslado.":
    "Texas limita por ley la parte de notarización, y la detallamos aparte del traslado y de la tarifa de firma.",
"Texas caps the notarial portion at $10 per acknowledgment or oath, itemized separately from any signing-agent or travel charge.":
    "Texas caps the notarial portion by statute, and it is itemized separately from any signing-agent or travel charge.",
"Texas limita la parte de notarización a $10 por reconocimiento o juramento, detallada por separado del cargo de agente de firma o traslado.":
    "Texas limita por ley la parte de notarización, detallada por separado del cargo de agente de firma o traslado.",
"The notarial fee is $10 for the first signature and $1 for each additional signature on the same document, plus $10 per oath.":
    "The notarial portion is capped by Texas statute and itemized separately on the invoice.",
"La tarifa notarial es de $10 por la primera firma y $1 por cada firma adicional en el mismo documento, más $10 por juramento.":
    "La parte de notarización tiene tope en la ley de Texas y se detalla por separado en la factura.",
"Texas caps the notarial portion at $10 per acknowledgment or oath, itemized separately from any travel or signing-agent charge.":
    "Texas caps the notarial portion by statute, and it is itemized separately from any travel or signing-agent charge.",
"Texas limita la parte de notarización a $10 por reconocimiento o juramento, detallada por separado de cualquier cargo por traslado o por el servicio de agente de firmas.":
    "Texas limita por ley la parte de notarización, detallada por separado de cualquier cargo por traslado o por el servicio de agente de firmas.",
# notary services / 24 hour
"The statutory fee never changes — $10 for the first signature and $1 for each additional, or $10 per oath, capped by Tex. Gov't Code §406.024 —":
    "The notarial fee stays capped by Tex. Gov't Code §406.024 at any hour, and travel anywhere in El Paso is itemized separately; an after-hours or holiday visit adds a quoted charge, confirmed before we leave.",
"La tarifa legal tampoco cambia — $10 por la primera firma y $1 por cada adicional, o $10 por juramento, con tope en el §406.024 —":
    "La tarifa de notarización mantiene su tope legal (§406.024) a cualquier hora, y el traslado en cualquier punto de El Paso se detalla por separado; una visita fuera de horario o en día festivo agrega un cargo cotizado, confirmado antes de salir.",
"We reply with the total — statutory fee, $39 travel and any after-hours charge — and an appointment window.":
    "We reply with the quoted total — notarial fee, travel and any after-hours charge — and an appointment window.",
"Le respondemos con el total — tarifa legal, $39 de traslado y cualquier cargo fuera de horario — y una ventana de cita.":
    "Le respondemos con el total cotizado — tarifa de notarización, traslado y cualquier cargo fuera de horario — y una ventana de cita.",
"The notarial fee is fixed by Texas law and does not go up at night: $10 for the first signature and $1 for each additional, or $10 per oath (Tex. Gov't Code §406.024).":
    "The notarial fee is capped by Texas law (Tex. Gov't Code §406.024) and does not go up at night.",
"La tarifa de notarización la fija la ley de Texas y no sube de noche: $10 por la primera firma y $1 por cada adicional, o $10 por juramento (Código de Gobierno §406.024).":
    "La tarifa de notarización tiene tope en la ley de Texas (Código de Gobierno §406.024) y no sube de noche.",
"Our travel fee stays $39 anywhere in El Paso, itemized separately.":
    "Our travel fee anywhere in El Paso is itemized separately; prices vary by location and timing, so " + Q_EN + ".",
"Nuestro traslado sigue siendo $39 en cualquier punto de El Paso, detallado por separado.":
    "Nuestro traslado en cualquier punto de El Paso se detalla por separado; los precios varían según la ubicación y el horario, así que " + Q_ES + ".",
"Not for same-day service during the day: a same-day appointment in El Paso is the statutory fee plus the $39 travel fee, the same as one booked a week ahead.":
    "Not for same-day service during the day: a same-day appointment in El Paso is quoted the same as one booked a week ahead.",
"No por el servicio el mismo día durante el día: una cita el mismo día en El Paso cuesta la tarifa legal más los $39 de traslado, igual que una agendada con una semana de anticipación.":
    "No por el servicio el mismo día durante el día: una cita el mismo día en El Paso se cotiza igual que una agendada con una semana de anticipación.",
# notary services / acknowledgments & jurats
"Fees are capped under Tex. Gov't Code §406.024: $10 for the first acknowledged signature and $1 for each additional, or $10 per oath or affirmation.":
    "Fees are capped under Tex. Gov't Code §406.024, whether the act is an acknowledgment or an oath or affirmation.",
"Las tarifas tienen tope en el Código de Gobierno de Texas §406.024: $10 por la primera firma reconocida y $1 por cada adicional, o $10 por juramento o afirmación.":
    "Las tarifas tienen tope en el Código de Gobierno de Texas §406.024, ya sea un reconocimiento o un juramento o afirmación.",
"Tell us what the document is and whether the recipient asked for an acknowledgment or a jurat — the certificate printed on the page usually says — and we confirm the total, including the $39 travel fee anywhere in El Paso.":
    "Tell us what the document is and whether the recipient asked for an acknowledgment or a jurat — the certificate printed on the page usually says — and we confirm the quoted total, including travel anywhere in El Paso.",
"Díganos qué documento es y si quien lo recibe pidió reconocimiento o juramento — el certificado impreso en la hoja normalmente lo indica — y le confirmamos el total, incluidos los $39 de traslado en cualquier punto de El Paso.":
    "Díganos qué documento es y si quien lo recibe pidió reconocimiento o juramento — el certificado impreso en la hoja normalmente lo indica — y le confirmamos el total cotizado, incluido el traslado en cualquier punto de El Paso.",
"An affirmation is simply an oath without religious language; it carries the same $10 fee and the same penalty for a false statement.":
    "An affirmation is simply an oath without religious language; it carries the same fee and the same penalty for a false statement.",
"La afirmación es simplemente un juramento sin lenguaje religioso; tiene la misma tarifa de $10 y la misma sanción por declarar en falso.":
    "La afirmación es simplemente un juramento sin lenguaje religioso; tiene la misma tarifa y la misma sanción por declarar en falso.",
"We confirm the statutory fee plus the $39 travel fee before we leave.":
    "We confirm the quote before we leave.",
"Confirmamos la tarifa legal más los $39 de traslado antes de salir.":
    "Confirmamos la cotización antes de salir.",
"Texas sets the notarial fee by statute: $10 for the first signature acknowledged and $1 for each additional signature on the same document, or $10 for each oath or affirmation with a jurat certificate.":
    "Prices vary by the number of signatures or oaths, the number of documents and your location; Texas caps the notarial fee by statute.",
"Texas fija la tarifa por ley: $10 por la primera firma reconocida y $1 por cada firma adicional en el mismo documento, o $10 por cada juramento o afirmación con certificado.":
    "Los precios varían según el número de firmas o juramentos, el número de documentos y su ubicación; la ley de Texas fija un tope a la tarifa de notarización.",
"QWIK adds a nominal $39 travel fee anywhere in El Paso, itemized separately, so one signature on one document comes to $49.":
    "QWIK itemizes travel anywhere in El Paso separately and confirms the total before we come.",
"QWIK agrega un traslado de $39 en cualquier punto de El Paso, detallado por separado, así que una firma en un documento sale en $49.":
    "QWIK detalla por separado el traslado en cualquier punto de El Paso y confirma el total antes de ir.",
"A married couple acknowledging the same deed pays $11 plus travel.":
    "A married couple acknowledging the same deed is one document with two signatures — " + Q_EN + ".",
"Un matrimonio que reconoce la misma escritura paga $11 más el traslado.":
    "Un matrimonio que reconoce la misma escritura es un solo documento con dos firmas — " + Q_ES + ".",
# notary services / affidavits
"Tex. Gov't Code §406.024 fixes the fee at $10 per oath or affirmation with certificate and seal.":
    "Tex. Gov't Code §406.024 caps the fee for each oath or affirmation with certificate and seal.",
"El Código de Gobierno de Texas §406.024 fija la tarifa en $10 por juramento o afirmación con certificado y sello.":
    "El Código de Gobierno de Texas §406.024 limita la tarifa por juramento o afirmación con certificado y sello.",
"To book, text or call (915) 302-0902 with the type of affidavit, the number of signers and your location in El Paso; we confirm the total — $10 per oath plus the $39 travel fee — before we leave.":
    "To book, text or call (915) 302-0902 with the type of affidavit, the number of signers and your location in El Paso; we confirm the quoted total before we leave.",
"Para agendar, envíe un texto o llame al (915) 302-0902 con el tipo de declaración, el número de firmantes y su ubicación en El Paso; le confirmamos el total — $10 por juramento más $39 de traslado — antes de salir.":
    "Para agendar, envíe un texto o llame al (915) 302-0902 con el tipo de declaración, el número de firmantes y su ubicación en El Paso; le confirmamos el total cotizado antes de salir.",
"We confirm $10 per oath plus the $39 travel fee and set a time, evenings and weekends included.":
    "We confirm the quote and set a time, evenings and weekends included.",
"Confirmamos $10 por juramento más $39 de traslado y fijamos la hora, incluso tardes y fines de semana.":
    "Confirmamos la cotización y fijamos la hora, incluso tardes y fines de semana.",
"Texas caps the fee for an oath or affirmation with certificate and seal at $10 (Tex. Gov't Code §406.024).":
    "Prices vary by the number of oaths and your location; Texas caps the fee for each oath or affirmation with certificate and seal (Tex. Gov't Code §406.024).",
"Texas fija en $10 la tarifa por juramento o afirmación con certificado y sello (Código de Gobierno §406.024).":
    "Los precios varían según el número de juramentos y su ubicación; Texas limita la tarifa por juramento o afirmación con certificado y sello (Código de Gobierno §406.024).",
"QWIK adds a nominal $39 travel fee anywhere in El Paso, itemized separately, so one affidavit sworn at your kitchen table comes to $49;":
    "QWIK itemizes travel anywhere in El Paso separately; two people swearing to separate affidavits at the same visit share one trip — " + Q_EN + ".",
"QWIK agrega un traslado de $39 en cualquier punto de El Paso, detallado por separado, así que una declaración jurada en la mesa de su cocina sale en $49;":
    "QWIK detalla por separado el traslado en cualquier punto de El Paso; dos personas que juran declaraciones distintas en la misma visita comparten un solo traslado — " + Q_ES + ".",
# notary services / certified copies
"The notary makes or supervises the copy, compares it with the original and attaches a certificate; the statutory fee is $10 plus $1 per page copied.":
    "The notary makes or supervises the copy, compares it with the original and attaches a certificate; the fee, capped by Texas statute, depends on the page count.",
"El Notary Public hace o supervisa la copia, la compara con el original y anexa el certificado; la tarifa legal es de $10 más $1 por página copiada.":
    "El Notary Public hace o supervisa la copia, la compara con el original y anexa el certificado; la tarifa, con tope en la ley de Texas, depende del número de páginas.",
"Text or call (915) 302-0902 with the document and page count; we confirm the total — $10 per certified copy, $1 per page and the $39 travel fee — before we head out.":
    "Text or call (915) 302-0902 with the document and page count; we confirm the quoted total before we head out.",
"Envíe un texto o llame al (915) 302-0902 con el documento y el número de páginas; le confirmamos el total — $10 por copia certificada, $1 por página y $39 de traslado — antes de salir.":
    "Envíe un texto o llame al (915) 302-0902 con el documento y el número de páginas; le confirmamos el total cotizado antes de salir.",
"We confirm whether a Texas notary may certify it and the total — $10 per copy, $1 per page, plus the $39 travel fee.":
    "We confirm whether a Texas notary may certify it and quote the total based on the page count.",
"Le confirmamos si un Notary Public de Texas puede certificarlo y el total: $10 por copia, $1 por página, más $39 de traslado.":
    "Le confirmamos si un Notary Public de Texas puede certificarlo y cotizamos el total según el número de páginas.",
"The Texas statutory fee is $10 for the certificate plus $1 for each page copied (Tex. Gov't Code §406.024), and QWIK adds a nominal $39 travel fee anywhere in El Paso, itemized separately.":
    "Prices vary by the number of pages and copies and by your location; the notarial fee is capped by Texas statute (Tex. Gov't Code §406.024) and travel anywhere in El Paso is itemized separately.",
"La tarifa legal de Texas es de $10 por el certificado más $1 por cada página copiada (Código de Gobierno §406.024), y QWIK agrega un traslado de $39 en cualquier punto de El Paso, detallado por separado.":
    "Los precios varían según el número de páginas y copias y según su ubicación; la tarifa de notarización tiene tope en la ley de Texas (Código de Gobierno §406.024) y el traslado en cualquier punto de El Paso se detalla por separado.",
"A certified copy of a one-page passport data page therefore comes to $50; a five-page contract comes to $54.": "",
"La copia certificada de la hoja de datos de un pasaporte sale entonces en $50; un contrato de cinco páginas, en $54.": "",
"Each additional certified copy of the same document is another $10 plus its pages.":
    "Each additional certified copy of the same document is priced separately — " + Q_EN + ".",
"Cada copia certificada adicional del mismo documento cuesta otros $10 más sus páginas.":
    "Cada copia certificada adicional del mismo documento se cotiza por separado — " + Q_ES + ".",
"A diploma is not a recordable document, so the notary certifies a copy of the original, and the Texas Secretary of State then apostilles the notarized certificate for $15.":
    "A diploma is not a recordable document, so the notary certifies a copy of the original, and the Texas Secretary of State then apostilles the notarized certificate for its per-document fee.",
"El diploma no es un documento registrable, así que el Notary Public certifica una copia del original y después la Secretaría de Estado de Texas apostilla el certificado notarizado por $15.":
    "El diploma no es un documento registrable, así que el Notary Public certifica una copia del original y después la Secretaría de Estado de Texas apostilla el certificado notarizado por su cuota por documento.",
# notary services / hospital
"Booking is easy: text or call (915) 302-0902 with the facility, the room number and the document you have, and we confirm the fee up front —":
    "Booking is easy: text or call (915) 302-0902 with the facility, the room number and the document you have, and we confirm the quote up front, with the notarial fee and El Paso travel itemized separately.",
"Reservar es fácil: envíe un texto o llame al (915) 302-0902 con el hospital, el número de cuarto y el documento que tiene, y le confirmamos la tarifa desde el principio:":
    "Reservar es fácil: envíe un texto o llame al (915) 302-0902 con el hospital, el número de cuarto y el documento que tiene, y le confirmamos la cotización desde el principio, con la tarifa de notarización y el traslado en El Paso detallados por separado.",
"The notarial fees are set by Texas law: $10 for the first signature acknowledged and $1 for each additional signature on the same document, $10 for each oath or jurat, and $10 for any other notarial act.":
    "Prices vary by the number of documents, signatures and oaths; the notarial fees are capped by Texas law.",
"Las tarifas de notarización las fija la ley de Texas: $10 por la primera firma reconocida y $1 por cada firma adicional en el mismo documento, $10 por cada juramento (jurat) y $10 por cualquier otro acto de notarización.":
    "Los precios varían según el número de documentos, firmas y juramentos; las tarifas de notarización tienen tope en la ley de Texas.",
"On top of that we charge a nominal $39 travel fee anywhere in the El Paso area, listed separately on your receipt.":
    "Travel anywhere in the El Paso area is listed separately on your receipt — " + Q_EN + ".",
"Además cobramos un traslado nominal de $39 en toda el área de El Paso, detallado por separado en su recibo.":
    "El traslado en toda el área de El Paso se detalla por separado en su recibo — " + Q_ES + ".",
# notary services / hub
"Call or text (915) 302-0902, tell us what you have and where you are, and we confirm the fee: the Texas statutory fee —":
    "Call or text (915) 302-0902, tell us what you have and where you are, and we confirm your quote: prices vary by document, number of signatures and location in El Paso, with the notarial fee and travel itemized separately.",
"Llame o envíe un texto al (915) 302-0902, díganos qué tiene y dónde está, y le confirmamos el costo: la tarifa legal de Texas —":
    "Llame o envíe un texto al (915) 302-0902, díganos qué tiene y dónde está, y le confirmamos la cotización: los precios varían según el documento, el número de firmas y la ubicación en El Paso, con la tarifa de notarización y el traslado detallados por separado.",
"Texas caps notarial fees by law: $10 for the first signature on an acknowledgment and $1 for each additional signature, $10 for an oath or affirmation, and $10 plus $1 per page for a certified copy.":
    "Prices vary by document, number of signatures and location; Texas caps notarial fees by law (Tex. Gov't Code §406.024).",
"La ley de Texas fija el máximo: $10 por la primera firma en un reconocimiento y $1 por cada firma adicional, $10 por juramento y $10 más $1 por página en una copia certificada.":
    "Los precios varían según el documento, el número de firmas y la ubicación; la ley de Texas fija el máximo de las tarifas de notarización (Código de Gobierno §406.024).",
"QWIK adds one nominal $39 travel fee anywhere in El Paso, itemized separately, so a single-signature document at your kitchen table comes to $49.":
    "QWIK adds one travel fee per visit anywhere in El Paso, itemized separately — " + Q_EN + ".",
"QWIK agrega un solo cargo de traslado de $39 en El Paso, detallado por separado, así que un documento con una sola firma sale en $49.":
    "QWIK agrega un solo cargo de traslado por visita en El Paso, detallado por separado — " + Q_ES + ".",
# notary services / jail
"Text or call (915) 302-0902 with the facility, the inmate's name and the document; we confirm the fee, the statutory $10 per signature or oath plus the $39 El Paso travel fee,":
    "Text or call (915) 302-0902 with the facility, the inmate's name and the document; we confirm the quote and check the facility's hours and procedure for notary visits, since each one decides where the signing happens, how paper reaches the inmate and what we may bring in.",
"Envíe un texto o llame al (915) 302-0902 con el centro, el nombre del interno y el documento; le confirmamos la tarifa — los $10 por firma o juramento que fija la ley más los $39 de traslado en El Paso —":
    "Envíe un texto o llame al (915) 302-0902 con el centro, el nombre del interno y el documento; le confirmamos la cotización y verificamos el horario y el procedimiento del centro para visitas de notarización, porque cada uno decide dónde se firma, cómo llega el papel al interno y qué podemos entrar.",
"The notarial fees are set by Texas law — $10 for the first signature acknowledged and $1 for each additional signature on the same document, or $10 per oath — plus our nominal $39 travel fee in El Paso County, itemized separately.":
    "Prices vary by the number of documents and signatures and by the facility; the notarial fee is capped by Texas law and travel in El Paso County is itemized separately.",
"Las tarifas de notarización las fija la ley de Texas — $10 por la primera firma reconocida y $1 por cada firma adicional en el mismo documento, o $10 por juramento — más nuestro traslado nominal de $39 en el condado de El Paso, detallado por separado.":
    "Los precios varían según el número de documentos y firmas y según el centro; la tarifa de notarización tiene tope en la ley de Texas y el traslado en el condado de El Paso se detalla por separado.",
"A single power of attorney signed at the Downtown Detention Facility or the Jail Annex is $10 plus travel.":
    "A single power of attorney signed at the Downtown Detention Facility or the Jail Annex is quoted before we go — call or text (915) 302-0902.",
"Una sola carta poder firmada en el Centro de Detención del centro o en el Anexo cuesta $10 más el traslado.":
    "Una sola carta poder firmada en el Centro de Detención del centro o en el Anexo se cotiza antes de ir — llame o envíe un texto al (915) 302-0902.",
# notary services / online
"We confirm the $25 fee per notarization — there is no travel fee for an online session — and send a secure link.":
    "We confirm the quote — there is no travel fee for an online session — and send a secure link.",
"Confirmamos la tarifa de $25 por notarización — no hay cargo de traslado en una sesión en línea — y le enviamos un enlace seguro.":
    "Confirmamos la cotización — no hay cargo de traslado en una sesión en línea — y le enviamos un enlace seguro.",
"We confirm the $25 fee, check that the recipient accepts online notarization, and email a secure session link with a time that works — including evenings.":
    "We confirm the quote, check that the recipient accepts online notarization, and email a secure session link with a time that works — including evenings.",
"Confirmamos la tarifa de $25, verificamos que la institución acepte la notarización en línea y le enviamos por correo un enlace seguro con un horario conveniente — incluso de noche.":
    "Confirmamos la cotización, verificamos que la institución acepte la notarización en línea y le enviamos por correo un enlace seguro con un horario conveniente — incluso de noche.",
"Texas caps the fee for an online notarization at $25 per notarial act, and that is what we charge.":
    "Prices vary by the number of notarial acts in the session; Texas caps the fee for each online notarization by statute, and we quote the total before the session.",
"Texas limita la tarifa de una notarización en línea a $25 por acto notarial, y eso es lo que cobramos.":
    "Los precios varían según el número de actos notariales en la sesión; la ley de Texas limita la tarifa de cada notarización en línea, y cotizamos el total antes de la sesión.",
"Texas lets you try again, allows the notary to rely on personal knowledge of the signer where that exists, and we can always convert the appointment to an in-person visit anywhere in El Paso for the statutory fee plus the $39 travel fee.":
    "Texas lets you try again, allows the notary to rely on personal knowledge of the signer where that exists, and we can always convert the appointment to an in-person visit anywhere in El Paso, quoted with travel.",
"Texas permite intentarlo de nuevo, permite que el Notary Public se base en su conocimiento personal del firmante cuando exista, y siempre podemos convertir la cita en una visita en persona en cualquier parte de El Paso por la tarifa legal más $39 de traslado.":
    "Texas permite intentarlo de nuevo, permite que el Notary Public se base en su conocimiento personal del firmante cuando exista, y siempre podemos convertir la cita en una visita en persona en cualquier parte de El Paso, cotizada con el traslado.",
# real estate / deeds
"Text or call (915) 302-0902 with the type of deed, how many grantors will sign and the address; we confirm the statutory fee,":
    "Text or call (915) 302-0902 with the type of deed, how many grantors will sign and the address; we confirm your quote and come to your home, office or title company anywhere in El Paso.",
"Envíe un texto o llame al (915) 302-0902 con el tipo de escritura, cuántas personas otorgan y la dirección; le confirmamos la tarifa oficial,":
    "Envíe un texto o llame al (915) 302-0902 con el tipo de escritura, cuántas personas otorgan y la dirección; le confirmamos la cotización y vamos a su casa, oficina o compañía de título en cualquier parte de El Paso.",
"We confirm the statutory fee plus the $39 El Paso travel fee and set a time, evenings and weekends included.":
    "We confirm the quote and set a time, evenings and weekends included.",
"Le confirmamos la tarifa oficial más los $39 de traslado en El Paso y fijamos la hora, tardes y fines de semana incluidos.":
    "Le confirmamos la cotización y fijamos la hora, tardes y fines de semana incluidos.",
"The notary fee is set by Texas law: $10 for the first signature acknowledged and $1 for each additional signature on the same deed.":
    "Prices vary by the number of grantors signing and by location; the notarial fee is capped by Texas law.",
"La tarifa la fija la ley de Texas: $10 por la primera firma reconocida y $1 por cada firma adicional en la misma escritura.":
    "Los precios varían según el número de otorgantes que firman y según la ubicación; la tarifa de notarización tiene tope en la ley de Texas.",
"QWIK adds a $39 travel fee for the visit anywhere in El Paso, itemized separately, so one deed with one grantor is the $10 statutory fee plus the $39 trip.":
    "QWIK itemizes travel for the visit anywhere in El Paso separately — " + Q_EN + ".",
"QWIK agrega $39 de traslado por la visita a cualquier parte de El Paso, detallados por separado, así que una escritura con un otorgante son los $10 de tarifa oficial más los $39 del viaje.":
    "QWIK detalla por separado el traslado por la visita a cualquier parte de El Paso — " + Q_ES + ".",
# real estate / hub
"Fees are statutory: $10 for the first signature, $1 each additional, plus a $39 travel fee in El Paso.":
    "Prices vary by document, number of signatures and location in El Paso; notarial fees are capped by Texas statute and travel is itemized separately.",
"Las tarifas son las oficiales de Texas: $10 la primera firma y $1 cada firma adicional, más $39 de traslado en todo El Paso.":
    "Los precios varían según el documento, el número de firmas y la ubicación en El Paso; la ley de Texas limita las tarifas de notarización y el traslado se detalla por separado.",
"Texas caps notary fees by law: $10 for the first signature acknowledged on a document and $1 for each additional signature on the same document, and $10 per oath on an affidavit.":
    "Prices vary by the number of documents, signatures and oaths; Texas caps notarial fees by law.",
"La ley de Texas limita las tarifas: $10 por la primera firma que se reconoce en un documento y $1 por cada firma adicional en el mismo documento, y $10 por cada juramento (jurat) en una declaración jurada.":
    "Los precios varían según el número de documentos, firmas y juramentos; la ley de Texas limita las tarifas de notarización.",
"QWIK adds a nominal $39 travel fee for the visit anywhere in El Paso, itemized separately — county recording fees are paid to the Clerk, not to us.":
    "Travel for the visit anywhere in El Paso is itemized separately — " + Q_EN + "; county recording fees are paid to the Clerk, not to us.",
"QWIK agrega $39 de traslado por la visita a cualquier parte de El Paso, detallados por separado; las cuotas de registro del condado se pagan al Clerk, no a nosotros.":
    "El traslado por la visita a cualquier parte de El Paso se detalla por separado — " + Q_ES + "; las cuotas de registro del condado se pagan al Clerk, no a nosotros.",
# real estate / liens
"Text or call (915) 302-0902 with the document, the number of signers and where the crew is; we confirm the fee ($10 per oath on an affidavit,":
    "Text or call (915) 302-0902 with the document, the number of signers and where the crew is; we confirm the quote and meet you at the job site, your office or your home anywhere in El Paso.",
"Envíe un texto o llame al (915) 302-0902 con el documento, el número de firmantes y dónde está la cuadrilla; le confirmamos la tarifa ($10 por juramento en una declaración jurada,":
    "Envíe un texto o llame al (915) 302-0902 con el documento, el número de firmantes y dónde está la cuadrilla; le confirmamos la cotización y lo vemos en la obra, en su oficina o en su casa en cualquier parte de El Paso.",
"We confirm the statutory fee plus the $39 travel fee and set a time that works around the crew's day.":
    "We confirm the quote and set a time that works around the crew's day.",
"Le confirmamos la tarifa oficial más los $39 de traslado y fijamos una hora que se acomode al día de la cuadrilla, temprano o tarde.":
    "Le confirmamos la cotización y fijamos una hora que se acomode al día de la cuadrilla, temprano o tarde.",
"Texas sets the fees: $10 per oath, so a sworn lien affidavit is $10, and $10 for the first acknowledged signature plus $1 for each additional signature on a release or waiver.":
    "Prices vary by the number of oaths and signatures — a lien affidavit is sworn, while a release or waiver is acknowledged per signature — and Texas caps every notarial fee by statute.",
"Texas fija las tarifas: $10 por juramento, así que una declaración de gravamen jurada cuesta $10, y $10 por la primera firma reconocida más $1 por cada firma adicional en una liberación o renuncia.":
    "Los precios varían según el número de juramentos y firmas — una declaración de gravamen se jura, mientras que una liberación o renuncia se reconoce por firma — y la ley de Texas limita cada tarifa de notarización.",
"QWIK adds a nominal $39 travel fee for the trip anywhere in El Paso, itemized separately; early-morning or after-hours job-site visits are quoted when you book.":
    "Travel anywhere in El Paso is itemized separately; early-morning or after-hours job-site visits are quoted when you book — call or text (915) 302-0902.",
"QWIK agrega $39 de traslado por el viaje a cualquier parte de El Paso, detallados por separado; las visitas a la obra muy temprano o fuera de horario se cotizan al agendar.":
    "El traslado a cualquier parte de El Paso se detalla por separado; las visitas a la obra muy temprano o fuera de horario se cotizan al agendar — llame o envíe un texto al (915) 302-0902.",
# real estate / timeshare
"Text or call (915) 302-0902 with the packet's contents and the number of owners who will sign; we confirm the fee ($10 for the first signature":
    "Text or call (915) 302-0902 with the packet's contents and the number of owners who will sign; we confirm the quote and come to your home anywhere in El Paso.",
"Envíe un texto o llame al (915) 302-0902 con el contenido del paquete y el número de dueños que van a firmar; le confirmamos la tarifa ($10 la primera firma":
    "Envíe un texto o llame al (915) 302-0902 con el contenido del paquete y el número de dueños que van a firmar; le confirmamos la cotización y vamos a su casa en cualquier parte de El Paso.",
"We confirm the per-document statutory fees plus the $39 El Paso travel fee and set a time when everyone on the deed can be there.":
    "We confirm the quote and set a time when everyone on the deed can be there.",
"Le confirmamos las tarifas oficiales por documento más los $39 de traslado en El Paso y fijamos una hora en la que todos los dueños puedan estar.":
    "Le confirmamos la cotización y fijamos una hora en la que todos los dueños puedan estar.",
"We schedule evenings and weekends across El Paso so both owners can sign in one visit, which also keeps the trip to a single $39 travel fee.":
    "We schedule evenings and weekends across El Paso so both owners can sign in one visit, which also keeps the trip to a single travel fee.",
"Agendamos tardes y fines de semana en todo El Paso para que los dos dueños firmen en una sola visita, lo que además mantiene un solo traslado de $39.":
    "Agendamos tardes y fines de semana en todo El Paso para que los dos dueños firmen en una sola visita, lo que además mantiene un solo traslado.",
"Texas caps the fee per notarial act: $10 for the first signature acknowledged on each document, $1 for each additional signature on the same document, and $10 per oath on a sworn affidavit.":
    "Prices vary by the number of documents in the packet, the signatures on each and any sworn affidavits; Texas caps the fee per notarial act by statute.",
"Texas limita la tarifa por cada acto: $10 por la primera firma reconocida en cada documento, $1 por cada firma adicional en ese mismo documento, y $10 por cada juramento (jurat) en una declaración jurada.":
    "Los precios varían según el número de documentos del paquete, las firmas en cada uno y las declaraciones juradas; la ley de Texas limita la tarifa por cada acto notarial.",
"QWIK adds a $39 travel fee anywhere in El Paso, itemized separately.":
    "Travel anywhere in El Paso is itemized separately — " + Q_EN + ".",
"QWIK agrega $39 de traslado a cualquier parte de El Paso, detallados por separado.":
    "El traslado a cualquier parte de El Paso se detalla por separado — " + Q_ES + ".",
}

used_keys = collections.Counter()
problems = []

def map_sentence(s, where):
    hits = [k for k in SENT if s == k or s.startswith(k)]
    if len(hits) != 1:
        problems.append(f'{where}: {len(hits)} keys match → {s[:140]}')
        return s
    used_keys[hits[0]] += 1
    return SENT[hits[0]]

def rewrite_text(text, where):
    if not DOLLAR.search(text): return text
    parts = SENT_RE.split(text)
    out = []
    for s in parts:
        if DOLLAR.search(s): s = map_sentence(s, where)
        if s: out.append(s)
    new = ' '.join(out).strip()
    if DOLLAR.search(new): problems.append(f'{where}: still has $ after rewrite → {new[:160]}')
    return new

def walk(o, path, file):
    if isinstance(o, dict):
        return {k: walk(v, path + [k], file) for k, v in o.items()}
    if isinstance(o, list):
        return [walk(v, path + [i], file) for i, v in enumerate(o)]
    if isinstance(o, str) and DOLLAR.search(o):
        field = path[0]
        where = f"{file.split('parts/')[1]}:{'.'.join(map(str, path))}"
        if field == 'feeModel':
            if o in FEEMODEL: used_keys['FM:' + o] += 1; return FEEMODEL[o]
            problems.append(f'{where}: unmapped feeModel → {o}'); return o
        if field == 'bring':
            if o in BRING: used_keys['BR:' + o] += 1; return BRING[o]
            problems.append(f'{where}: unmapped bring → {o}'); return o
        if o in FULL: used_keys['FULL:' + o] += 1; return FULL[o]
        return rewrite_text(o, where)
    return o

EDITS = []  # (old, new) string pairs collected while walking
_walk = walk
def walk(o, path, file):
    r = _walk(o, path, file)
    if isinstance(o, str) and isinstance(r, str) and r != o: EDITS.append((o, r))
    return r

changed = 0
for f in sorted(glob.glob(ROOT + 'src/content/parts/*/*.json')):
    raw = open(f).read(); data = json.loads(raw)
    EDITS.clear()
    new = walk(data, [], f)
    if new == data: continue
    changed += 1
    text = raw
    for o, r in EDITS:
        eo, er = json.dumps(o, ensure_ascii=False)[1:-1], json.dumps(r, ensure_ascii=False)[1:-1]
        if text.count(eo) == 0: problems.append(f'{f}: encoded string not found in raw text → {eo[:100]}'); continue
        text = text.replace(eo, er)
    if json.loads(text) != new: problems.append(f'{f}: textual patch does not reproduce the walked structure')
    if '--write' in sys.argv and json.loads(text) == new: open(f, 'w').write(text)

unused = [k for k in list(SENT) if used_keys[k] == 0]
print(f'files changed: {changed}; sentence keys used: {sum(1 for k in SENT if used_keys[k])}/{len(SENT)}')
if unused: print('UNUSED KEYS:'); [print('  -', k[:150]) for k in unused]
if problems: print(f'{len(problems)} PROBLEMS:'); [print('  !', p) for p in problems]
sys.exit(1 if (problems or unused) else 0)
