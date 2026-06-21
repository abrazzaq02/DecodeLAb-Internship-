import { exhibitionsConfig, type ExhibitionItem } from '../config'

export type Exhibition = ExhibitionItem

export const exhibitions = exhibitionsConfig.items

export function getExhibitionBySlug(slug: string) {
  return exhibitions.find((exhibition) => exhibition.slug === slug) ?? null
}
