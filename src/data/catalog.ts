// Master catalog: hubs (service groups) and services (landing pages) for QWIK Mobile Notary Public.
// URLs are nested: /<hub-slug>/<service-slug>/ (EN) and /es/<hub-slug-es>/<service-slug-es>/ (ES).
// Content for each hub lives in src/content/<hub-id>.json (merged from src/content/parts/<hub-id>/*.json).

export type Lang = 'en' | 'es';
export type L = { en: string; es: string };

/** Where the notarization happens — drives the card tag and the "Where" fact on each page. */
export type Where = 'mobile' | 'facility' | 'office' | 'online' | 'courier';

export interface CatalogService {
  id: string;
  slug: L;             // slug relative to the hub, no slashes
  name: L;             // short name for menus and cards
  where: Where;
  hubId?: string;      // filled in below
}

export interface CatalogHub {
  id: string;
  slug: L;
  name: L;
  icon: string;
  services: CatalogService[];
  /** 'notary' hubs form the service silo; 'other' pages (wedding officiant) live outside it. */
  kind?: 'notary' | 'other';
  /** true when the hub page itself is one of the 30 core categories (apostille). */
  isCategory?: boolean;
  /** where the hub-level service happens (rich hubs only) */
  where?: Where;
}

export const WHERE_LABEL: Record<Where, L> = {
  mobile: { en: 'Mobile — we come to you', es: 'Móvil — vamos a donde usted está' },
  facility: { en: 'Mobile — hospital, care facility or jail', es: 'Móvil — hospital, asilo o cárcel' },
  office: { en: 'At the title company or attorney’s office', es: 'En la oficina de título o del abogado' },
  online: { en: 'Online by video (RON)', es: 'En línea por video (RON)' },
  courier: { en: 'Mobile pickup + Secretary of State handling', es: 'Recogemos el documento + trámite ante la Secretaría de Estado' },
};

export const HUBS: CatalogHub[] = [
  {
    id: 'notary-services',
    slug: { en: 'notary-services', es: 'servicios-de-notarizacion' },
    name: { en: 'Mobile Notary Services', es: 'Servicios de Notarización Móvil' },
    icon: '🖋️',
    kind: 'notary',
    services: [
      { id: 'acknowledgments-and-jurats', slug: { en: 'acknowledgments-and-jurats', es: 'reconocimientos-y-juramentos' }, name: { en: 'Acknowledgments & Jurats', es: 'Reconocimientos y Juramentos' }, where: 'mobile' },
      { id: 'affidavits', slug: { en: 'affidavits', es: 'declaraciones-juradas' }, name: { en: 'Affidavits & Sworn Statements', es: 'Declaraciones Juradas' }, where: 'mobile' },
      { id: 'certified-copies', slug: { en: 'certified-copies', es: 'copias-certificadas' }, name: { en: 'Certified Copies', es: 'Copias Certificadas' }, where: 'mobile' },
      { id: '24-hour-notary', slug: { en: '24-hour-notary', es: '24-horas' }, name: { en: '24/7 Same-Day & After-Hours Notary', es: 'Notarización 24/7, Mismo Día y Fuera de Horario' }, where: 'mobile' },
      { id: 'hospital-notary', slug: { en: 'hospital-notary', es: 'hospitales' }, name: { en: 'Hospital, Nursing Home & Hospice Notary', es: 'Notarización en Hospitales, Asilos y Hospicios' }, where: 'facility' },
      { id: 'jail-notary', slug: { en: 'jail-notary', es: 'carcel' }, name: { en: 'Jail & Detention Center Notary', es: 'Notarización en la Cárcel y Centros de Detención' }, where: 'facility' },
      { id: 'online-notary', slug: { en: 'online-notary', es: 'en-linea' }, name: { en: 'Remote Online Notarization (RON)', es: 'Notarización en Línea (RON)' }, where: 'online' },
    ],
  },
  {
    id: 'estate-planning',
    slug: { en: 'estate-planning', es: 'planificacion-patrimonial' },
    name: { en: 'Estate Planning Documents', es: 'Documentos de Planificación Patrimonial' },
    icon: '📜',
    kind: 'notary',
    services: [
      { id: 'power-of-attorney', slug: { en: 'power-of-attorney', es: 'carta-poder' }, name: { en: 'Power of Attorney', es: 'Carta Poder' }, where: 'mobile' },
      { id: 'medical-power-of-attorney', slug: { en: 'medical-power-of-attorney', es: 'poder-medico' }, name: { en: 'Medical Power of Attorney & Advance Directives', es: 'Poder Médico y Directivas Anticipadas' }, where: 'mobile' },
      { id: 'wills-and-trusts', slug: { en: 'wills-and-trusts', es: 'testamentos-y-fideicomisos' }, name: { en: 'Wills & Living Trusts', es: 'Testamentos y Fideicomisos' }, where: 'mobile' },
    ],
  },
  {
    id: 'family-documents',
    slug: { en: 'family-documents', es: 'documentos-familiares' },
    name: { en: 'Family Documents', es: 'Documentos Familiares' },
    icon: '👨‍👩‍👧',
    kind: 'notary',
    services: [
      { id: 'child-travel-consent', slug: { en: 'child-travel-consent', es: 'permiso-de-viaje-menores' }, name: { en: 'Minor Travel Consent & Passport Consent (DS-3053)', es: 'Permiso de Viaje para Menores y Consentimiento de Pasaporte (DS-3053)' }, where: 'mobile' },
      { id: 'guardianship-adoption', slug: { en: 'guardianship-adoption', es: 'tutela-y-adopcion' }, name: { en: 'Guardianship & Adoption Documents', es: 'Tutela y Documentos de Adopción' }, where: 'mobile' },
      { id: 'divorce-custody-name-change', slug: { en: 'divorce-custody-name-change', es: 'divorcio-custodia-cambio-de-nombre' }, name: { en: 'Divorce, Child Custody & Name Change', es: 'Divorcio, Custodia y Cambio de Nombre' }, where: 'mobile' },
    ],
  },
  {
    id: 'loan-signing',
    slug: { en: 'loan-signing', es: 'firma-de-prestamos' },
    name: { en: 'Loan Signing Agent', es: 'Agente de Firma de Préstamos' },
    icon: '🏡',
    kind: 'notary',
    services: [
      { id: 'mortgage-closings', slug: { en: 'mortgage-closings', es: 'cierres-de-hipoteca' }, name: { en: 'Mortgage Purchase Closings (Conventional, FHA, VA)', es: 'Cierres de Hipoteca (Convencional, FHA, VA)' }, where: 'mobile' },
      { id: 'refinance', slug: { en: 'refinance', es: 'refinanciamiento' }, name: { en: 'Refinance Signings', es: 'Firmas de Refinanciamiento' }, where: 'mobile' },
      { id: 'home-equity-heloc', slug: { en: 'home-equity-heloc', es: 'home-equity-heloc' }, name: { en: 'Home Equity & HELOC Signings', es: 'Firmas de Home Equity y HELOC' }, where: 'office' },
      { id: 'reverse-mortgage', slug: { en: 'reverse-mortgage', es: 'hipoteca-inversa' }, name: { en: 'Reverse Mortgage Signings', es: 'Firmas de Hipoteca Inversa' }, where: 'mobile' },
      { id: 'commercial-loans', slug: { en: 'commercial-loans', es: 'prestamos-comerciales' }, name: { en: 'Commercial Loan Signings', es: 'Firmas de Préstamos Comerciales' }, where: 'mobile' },
      { id: 'seller-packages', slug: { en: 'seller-packages', es: 'paquetes-de-vendedor' }, name: { en: 'Seller Packages & Cash Closings', es: 'Paquetes de Vendedor y Cierres en Efectivo' }, where: 'mobile' },
    ],
  },
  {
    id: 'real-estate',
    slug: { en: 'real-estate', es: 'bienes-raices' },
    name: { en: 'Real Estate & Property Documents', es: 'Documentos de Bienes Raíces y Propiedad' },
    icon: '🏠',
    kind: 'notary',
    services: [
      { id: 'deeds', slug: { en: 'deeds', es: 'escrituras' }, name: { en: 'Deeds (Warranty, Quitclaim, Deed of Trust)', es: 'Escrituras (Garantía, Finiquito, Deed of Trust)' }, where: 'mobile' },
      { id: 'timeshare', slug: { en: 'timeshare', es: 'tiempo-compartido' }, name: { en: 'Timeshare Documents', es: 'Documentos de Tiempo Compartido' }, where: 'mobile' },
      { id: 'liens-and-releases', slug: { en: 'liens-and-releases', es: 'gravamenes' }, name: { en: 'Liens & Lien Releases', es: 'Gravámenes y Liberaciones de Gravamen' }, where: 'mobile' },
    ],
  },
  {
    id: 'business',
    slug: { en: 'business', es: 'negocios' },
    name: { en: 'Business & Employment', es: 'Negocios y Empleo' },
    icon: '🏢',
    kind: 'notary',
    services: [
      { id: 'business-documents', slug: { en: 'business-documents', es: 'documentos-comerciales' }, name: { en: 'Business Documents & Contracts', es: 'Documentos Comerciales y Contratos' }, where: 'mobile' },
      { id: 'i-9-verification', slug: { en: 'i-9-verification', es: 'verificacion-i-9' }, name: { en: 'I-9 Employment Eligibility Verification', es: 'Verificación de Elegibilidad de Empleo I-9' }, where: 'mobile' },
      { id: 'financial-documents', slug: { en: 'financial-documents', es: 'documentos-financieros' }, name: { en: 'Financial, Debt & Bankruptcy Documents', es: 'Documentos Financieros, de Deudas y Bancarrota' }, where: 'mobile' },
      { id: 'attorneys-law-firms', slug: { en: 'attorneys-law-firms', es: 'abogados-y-despachos' }, name: { en: 'Notary for Attorneys, Law Firms & Court Reporters', es: 'Servicios para Abogados, Despachos y Reporteros Judiciales' }, where: 'mobile' },
    ],
  },
  {
    id: 'forms',
    slug: { en: 'forms', es: 'formularios' },
    name: { en: 'Vehicle, School & Government Forms', es: 'Formularios de Vehículos, Escuela y Gobierno' },
    icon: '🚗',
    kind: 'notary',
    services: [
      { id: 'vehicle-title-transfer', slug: { en: 'vehicle-title-transfer', es: 'traspaso-de-titulo' }, name: { en: 'Vehicle Title Transfers, Bill of Sale & Towing (VSF) Forms', es: 'Traspaso de Título, Factura de Venta y Formularios VSF' }, where: 'mobile' },
      { id: 'school-and-government-forms', slug: { en: 'school-and-government-forms', es: 'escuela-y-gobierno' }, name: { en: 'School, Residency & Government Forms', es: 'Formularios Escolares, de Residencia y Gubernamentales' }, where: 'mobile' },
    ],
  },
  {
    id: 'apostille',
    slug: { en: 'apostille', es: 'apostilla' },
    name: { en: 'Apostille Services', es: 'Servicios de Apostilla' },
    icon: '🌎',
    kind: 'notary',
    isCategory: true,
    where: 'courier',
    services: [
      { id: 'apostille-mexico', slug: { en: 'mexico', es: 'mexico' }, name: { en: 'Apostille for Mexico', es: 'Apostilla para México' }, where: 'courier' },
      { id: 'apostille-birth-certificate', slug: { en: 'birth-certificate', es: 'acta-de-nacimiento' }, name: { en: 'Apostille for Birth, Marriage & Death Certificates', es: 'Apostilla de Actas de Nacimiento, Matrimonio y Defunción' }, where: 'courier' },
      { id: 'apostille-fbi-background-check', slug: { en: 'fbi-background-check', es: 'antecedentes-fbi' }, name: { en: 'FBI Background Check & Federal Document Authentication', es: 'Antecedentes del FBI y Autenticación de Documentos Federales' }, where: 'courier' },
      { id: 'apostille-diploma-transcripts', slug: { en: 'diploma-transcripts', es: 'diplomas-y-certificados-de-estudios' }, name: { en: 'Apostille for Diplomas & Transcripts', es: 'Apostilla de Diplomas y Certificados de Estudios' }, where: 'courier' },
      { id: 'apostille-single-status-affidavit', slug: { en: 'single-status-affidavit', es: 'constancia-de-solteria' }, name: { en: 'Single Status Affidavit Apostille', es: 'Apostilla de Constancia de Soltería' }, where: 'courier' },
    ],
  },
  {
    id: 'wedding-officiant',
    slug: { en: 'wedding-officiant', es: 'oficiante-de-bodas' },
    name: { en: 'Wedding Officiant', es: 'Oficiante de Bodas' },
    icon: '💍',
    kind: 'other',
    isCategory: true,
    where: 'mobile',
    services: [],
  },
];

for (const h of HUBS) for (const s of h.services) s.hubId = h.id;

/** Hubs that form the notary service silo (menus, footers, services index). */
export const NOTARY_HUBS = HUBS.filter((h) => h.kind !== 'other');
export const OTHER_HUBS = HUBS.filter((h) => h.kind === 'other');

export const ALL_SERVICES = HUBS.flatMap((h) => h.services.map((s) => ({ ...s, hubId: h.id })));

export function findHub(id: string) {
  return HUBS.find((h) => h.id === id)!;
}
export function findService(id: string) {
  return ALL_SERVICES.find((s) => s.id === id)!;
}
export function hubPath(hub: CatalogHub, lang: Lang) {
  return lang === 'en' ? `/${hub.slug.en}/` : `/es/${hub.slug.es}/`;
}
export function servicePath(svc: CatalogService, lang: Lang) {
  const hub = findHub(svc.hubId!);
  return lang === 'en' ? `/${hub.slug.en}/${svc.slug.en}/` : `/es/${hub.slug.es}/${svc.slug.es}/`;
}
