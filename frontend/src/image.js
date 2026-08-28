const DEFAULT_MAX_BYTES = 8 * 1024 * 1024
const MAX_IMAGE_EDGE = 2400

/** 使用浏览器原生 Canvas 缩放上传图片，并在提交前执行最终体积限制。 */
export async function resizeUploadImage(file, maxBytes = DEFAULT_MAX_BYTES) {
  if (!file?.type.startsWith('image/')) return file
  const bitmap = await createImageBitmap(file, { imageOrientation: 'from-image' })
  try {
    const scale = Math.min(1, MAX_IMAGE_EDGE / Math.max(bitmap.width, bitmap.height))
    if (scale === 1 && file.size <= maxBytes) return file

    // 大照片先在浏览器降采样，避免把原始高像素内容交给服务器解码。
    const canvas = document.createElement('canvas')
    canvas.width = Math.max(1, Math.round(bitmap.width * scale))
    canvas.height = Math.max(1, Math.round(bitmap.height * scale))
    canvas.getContext('2d').drawImage(bitmap, 0, 0, canvas.width, canvas.height)
    const type = ['image/jpeg', 'image/png', 'image/webp'].includes(file.type) ? file.type : 'image/jpeg'
    const blob = await new Promise((resolve, reject) => {
      canvas.toBlob(
        (result) => result ? resolve(result) : reject(new Error('图片压缩失败，请更换图片后重试。')),
        type,
        0.88,
      )
    })
    if (blob.size > maxBytes) {
      throw new Error(`压缩后的图片仍超过 ${Math.floor(maxBytes / 1024 / 1024)}MB，请选择尺寸更小的图片。`)
    }
    return new File([blob], file.name, { type, lastModified: file.lastModified })
  } finally {
    bitmap.close()
  }
}
