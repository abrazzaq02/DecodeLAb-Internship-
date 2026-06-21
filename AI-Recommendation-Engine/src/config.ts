export interface SiteConfig {
  language: string
  siteTitle: string
  siteDescription: string
}

export interface NavigationLink {
  label: string
  href: string
}

export interface NavigationConfig {
  brandName: string
  links: NavigationLink[]
}

export interface HeroConfig {
  titleLines: string[]
  subtitle: string
}

export interface ManifestoConfig {
  headingText: string
  bodyText: string
  videoPath: string
}

export interface ExhibitionArticleSection {
  heading: string
  body: string
}

export interface ExhibitionItem {
  slug: string
  title: string
  image: string
  year: string
  eyebrow: string
  intro: string
  sections: ExhibitionArticleSection[]
}

export interface ExhibitionsConfig {
  sectionLabel: string
  countLabel: string
  detailBackText: string
  items: ExhibitionItem[]
}

export interface PavilionVideoItem {
  src: string
  caption: string
}

export interface PavilionsConfig {
  sectionLabel: string
  videos: PavilionVideoItem[]
}

export interface FooterLink {
  label: string
  href: string
}

export interface FooterConfig {
  visitLabel: string
  visitLines: string[]
  connectLabel: string
  connectLinks: FooterLink[]
  brandName: string
  rightsText: string
  coordinatesText: string
}

export const siteConfig: SiteConfig = {
  language: "",
  siteTitle: "",
  siteDescription: "",
}

export const navigationConfig: NavigationConfig = {
  brandName: "",
  links: [],
}

export const heroConfig: HeroConfig = {
  titleLines: [],
  subtitle: "",
}

export const manifestoConfig: ManifestoConfig = {
  headingText: "",
  bodyText: "",
  videoPath: "",
}

export const exhibitionsConfig: ExhibitionsConfig = {
  sectionLabel: "",
  countLabel: "",
  detailBackText: "",
  items: [],
}

export const pavilionsConfig: PavilionsConfig = {
  sectionLabel: "",
  videos: [],
}

export const footerConfig: FooterConfig = {
  visitLabel: "",
  visitLines: [],
  connectLabel: "",
  connectLinks: [],
  brandName: "",
  rightsText: "",
  coordinatesText: "",
}
