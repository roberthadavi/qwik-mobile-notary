import { HUBS, ALL_SERVICES, type CatalogHub, type CatalogService, type Lang, type L } from '../data/catalog';

export interface Faq { q: L; a: L }
export interface Step { title: L; body: L }
export interface Section { heading: L; body: L[] }
export interface Outbound { label: L; url: string }

/** Hub pages. Rich optional fields are used when the hub page is itself a core category (apostille, officiant). */
export interface HubContent {
  title: L; metaDescription: L; eyebrow: L; h1: L; summary: L; intro: L[]; faqs: Faq[];
  feeModel?: L; timeline?: L;
  sections?: Section[]; documents?: L[]; bring?: L[]; process?: Step[]; outbound?: Outbound[];
  keywords?: string[]; related?: string[];
}
export interface ServiceContent {
  title: L; metaDescription: L; eyebrow: L; h1: L; summary: L; feeModel: L; timeline: L;
  intro: L[]; sections: Section[]; documents: L[]; bring: L[];
  process: Step[]; faqs: Faq[];
  keywords: string[]; related: string[]; outbound: Outbound[];
}
interface HubFile { hub: HubContent; services: Record<string, ServiceContent> }

const files = import.meta.glob<HubFile>('../content/*.json', { eager: true, import: 'default' });
const byHub: Record<string, HubFile> = {};
for (const [p, data] of Object.entries(files)) {
  const id = p.split('/').pop()!.replace(/\.json$/, '');
  byHub[id] = data;
}

export function hubContent(hubId: string): HubContent {
  const f = byHub[hubId];
  if (!f) throw new Error(`No content for hub ${hubId}`);
  return f.hub;
}
export function serviceContent(hubId: string, serviceId: string): ServiceContent {
  const f = byHub[hubId];
  const s = f?.services[serviceId];
  if (!s) throw new Error(`No content for service ${hubId}/${serviceId}`);
  return s;
}

export type ServiceWithHub = CatalogService & { hubId: string };
export function serviceById(id: string): ServiceWithHub {
  const s = ALL_SERVICES.find((x) => x.id === id);
  if (!s) throw new Error(`Unknown service ${id}`);
  return s as ServiceWithHub;
}
export function hubOf(service: ServiceWithHub): CatalogHub {
  return HUBS.find((h) => h.id === service.hubId)!;
}

/** Static path params for /<hub>/ pages */
export function hubParams(lang: Lang) {
  return HUBS.map((h) => ({ params: { hub: h.slug[lang] } }));
}
/** Static path params for /<hub>/<service>/ pages */
export function serviceParams(lang: Lang) {
  return HUBS.flatMap((h) => h.services.map((s) => ({ params: { hub: h.slug[lang], service: s.slug[lang] } })));
}
export function hubBySlug(slug: string, lang: Lang): CatalogHub {
  const h = HUBS.find((x) => x.slug[lang] === slug);
  if (!h) throw new Error(`Unknown hub slug ${slug} (${lang})`);
  return h;
}
export function serviceBySlugs(hubSlug: string, serviceSlug: string, lang: Lang): { hub: CatalogHub; service: ServiceWithHub } {
  const hub = hubBySlug(hubSlug, lang);
  const s = hub.services.find((x) => x.slug[lang] === serviceSlug);
  if (!s) throw new Error(`Unknown service slug ${hubSlug}/${serviceSlug} (${lang})`);
  return { hub, service: { ...s, hubId: hub.id } };
}

export function pick(l: L, lang: Lang) { return l[lang]; }
