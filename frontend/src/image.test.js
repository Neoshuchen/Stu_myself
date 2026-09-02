import assert from 'node:assert/strict'
import test from 'node:test'

import { pastedImages } from './image.js'

test('pastedImages 只返回支持的剪贴板图片', () => {
  const png = { name: 'clipboard.png' }
  const event = { clipboardData: { items: [
    { kind: 'string', type: 'text/plain' },
    { kind: 'file', type: 'image/gif', getAsFile: () => ({ name: 'clip.gif' }) },
    { kind: 'file', type: 'image/png', getAsFile: () => png },
    { kind: 'file', type: 'image/jpeg', getAsFile: () => null },
  ] } }

  assert.deepEqual(pastedImages(event), [png])
  assert.deepEqual(pastedImages({}), [])
})
