"""Smooth sampling for unfiltered data textures on the finished module (no model calls).

A DataTexture keeps three.js's NearestFilter defaults unless the module sets its filters, so procedural grain, fabric or
sand reads speckled at the judge's resolution. Textures with both filters still at NearestFilter get linear filtering
with mipmaps; textures the module filtered itself are left alone. Applied last, around the module's own generate()."""

EXPORT = "export default function generate(THREE)"
TEXFIX = r'''
function __texfix404(THREE, root) {
  const seen = new Set();
  root.traverse(function (node) {
    const list = node.material ? (Array.isArray(node.material) ? node.material : [node.material]) : [];
    for (const m of list) {
      if (!m) continue;
      for (const key of Object.keys(m)) {
        const t = m[key];
        if (!t || !t.isDataTexture || seen.has(t)) continue;
        seen.add(t);
        if (t.magFilter === THREE.NearestFilter && t.minFilter === THREE.NearestFilter) {
          t.magFilter = THREE.LinearFilter;
          t.minFilter = THREE.LinearMipmapLinearFilter;
          t.generateMipmaps = true;
          t.needsUpdate = true;
        }
      }
    }
  });
  return root;
}

export default function generate(THREE) {
  return __texfix404(THREE, __texBase404(THREE));
}
'''


def texfix(source: str) -> str:
    """The module wrapped so its data textures sample smoothly; as it is when generate() is not where expected."""
    if source.count(EXPORT) != 1 or "DataTexture" not in source:
        return source
    return source.replace(EXPORT, "function __texBase404(THREE)", 1).rstrip() + "\n" + TEXFIX
