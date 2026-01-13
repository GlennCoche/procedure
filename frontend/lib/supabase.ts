/**
 * Client Supabase pour le stockage des images
 */

import { createClient } from '@supabase/supabase-js'

// Client Supabase pour les opérations storage côté serveur
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY

if (!supabaseUrl) {
  console.warn('NEXT_PUBLIC_SUPABASE_URL non configuré - Supabase Storage désactivé')
}

export const supabase = supabaseUrl && supabaseServiceKey
  ? createClient(supabaseUrl, supabaseServiceKey, {
      auth: {
        autoRefreshToken: false,
        persistSession: false
      }
    })
  : null

// Bucket pour les images des procédures
export const PROCEDURE_IMAGES_BUCKET = 'procedure-images'

/**
 * Upload une image vers Supabase Storage
 */
export async function uploadImage(
  file: Buffer | Blob,
  fileName: string,
  contentType: string = 'image/png'
): Promise<{ url: string; path: string } | null> {
  if (!supabase) {
    console.error('Supabase client non initialisé')
    return null
  }

  const filePath = `images/${Date.now()}_${fileName}`

  const { data, error } = await supabase.storage
    .from(PROCEDURE_IMAGES_BUCKET)
    .upload(filePath, file, {
      contentType,
      cacheControl: '3600',
      upsert: false
    })

  if (error) {
    console.error('Erreur upload image:', error)
    return null
  }

  // Obtenir l'URL publique
  const { data: urlData } = supabase.storage
    .from(PROCEDURE_IMAGES_BUCKET)
    .getPublicUrl(filePath)

  return {
    url: urlData.publicUrl,
    path: data.path
  }
}

/**
 * Upload une image depuis une URL base64
 */
export async function uploadBase64Image(
  base64Data: string,
  fileName: string
): Promise<{ url: string; path: string } | null> {
  if (!supabase) {
    console.error('Supabase client non initialisé')
    return null
  }

  // Extraire le type et les données
  const matches = base64Data.match(/^data:([^;]+);base64,(.+)$/)
  if (!matches) {
    console.error('Format base64 invalide')
    return null
  }

  const contentType = matches[1]
  const base64 = matches[2]
  const buffer = Buffer.from(base64, 'base64')

  return uploadImage(buffer, fileName, contentType)
}

/**
 * Supprimer une image de Supabase Storage
 */
export async function deleteImage(filePath: string): Promise<boolean> {
  if (!supabase) {
    console.error('Supabase client non initialisé')
    return false
  }

  const { error } = await supabase.storage
    .from(PROCEDURE_IMAGES_BUCKET)
    .remove([filePath])

  if (error) {
    console.error('Erreur suppression image:', error)
    return false
  }

  return true
}

/**
 * Lister les images d'un dossier
 */
export async function listImages(folder: string = 'images'): Promise<string[]> {
  if (!supabase) {
    console.error('Supabase client non initialisé')
    return []
  }

  const { data, error } = await supabase.storage
    .from(PROCEDURE_IMAGES_BUCKET)
    .list(folder)

  if (error) {
    console.error('Erreur listing images:', error)
    return []
  }

  return data?.map(file => `${folder}/${file.name}`) || []
}
