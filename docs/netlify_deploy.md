# Netlify Deployment (Landing + OAuth)

## 1) Connect Repo
- Connect `SkyBlueAI` repo in Netlify
- Build settings are in `netlify.toml`

## 2) Enable Identity
- Site settings -> Identity -> Enable
- Registration preferences: Invite only (recommended)
- External providers: enable Google/GitHub and add OAuth credentials

## 3) Configure Domain + HTTPS
- Add custom domain
- Netlify issues TLS automatically

## 4) Environment Variables
Set in Netlify UI -> Site settings -> Environment variables:
- `VITE_API_BASE` set to your backend URL (e.g. `https://api.yourdomain.com`)

## 5) SPA Redirects
- `_redirects` is included to allow client-side routing

## 6) Test OAuth
- Open the site, click "Sign in with OAuth"
- Use enabled provider to authenticate
