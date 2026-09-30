/**
 * Viewport mobile init script for Camoufox.
 *
 * Camoufox locks the browser viewport for anti-detection — window.resizeTo(),
 * --window-size CLI arg, and page.setViewportSize() are all ignored.
 *
 * Inject this via context.addInitScript() BEFORE page navigation.
 * It sets a mobile viewport meta so responsive CSS matches mobile breakpoints.
 *
 * Usage (in camofox-browser-fork server.js, after context creation):
 *
 *   await context.addInitScript(() => {
 *     const meta = document.createElement('meta');
 *     meta.name = 'viewport';
 *     meta.content = 'width=390, initial-scale=1, maximum-scale=1';
 *     document.head.appendChild(meta);
 *   });
 *
 * For extraction/research purposes the desktop viewport works fine —
 * this is only needed when you need the page to render its mobile layout.
 */
