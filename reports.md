# Frontend Server - Issue Report

## Problem
Running `npm run dev` inside `frontend/` fails because two critical things are missing.

---

## Issue 1: Missing `vite.config.js`

There is no `vite.config.js` inside `frontend/`. Without it, Vite doesn't know to use the React plugin, so JSX won't compile and you'll get an error like:

```
[vite] Internal server error: Failed to parse source for import analysis
because the content contains invalid JS syntax.
Install @vitejs/plugin-react to handle .jsx files.
```

**Fix:** Create `frontend/vite.config.js`:
```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
```

---

## Issue 2: Missing `@vitejs/plugin-react` dependency

`frontend/package.json` does not include `@vitejs/plugin-react`. This plugin is required to handle `.jsx` files and React Fast Refresh in Vite.

**Fix:** Run inside `frontend/`:
```bash
npm install @vitejs/plugin-react --save-dev
```

---

## Summary of Fixes (in order)

```bash
cd frontend
npm install @vitejs/plugin-react --save-dev
```

Then create `frontend/vite.config.js` (see Issue 1 above), and start:
```bash
npm run dev
```

---

## Note on Vite 7

`package.json` uses `vite: ^7.3.1`. Vite 7 requires **Node.js 20.19+, 22.12+, or 24+**.
Run `node --version` to confirm you meet this requirement. If not, upgrade Node.js or pin Vite to v6.
