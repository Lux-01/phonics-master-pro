# demo-site

A business website built with Lux Website Designer.

## Development

1. Edit `site.json` to customize theme and content
2. Run local server:
   ```bash
   python3 website_designer.py serve demo-site
   ```
3. Edit files in `src/` with live reload

## Structure

- `src/index.html` - Main page
- `src/css/` - Stylesheets
- `src/js/` - JavaScript
- `src/assets/` - Images, fonts
- `site.json` - Configuration
- `security.conf` - Security headers

## Deployment

1. Build production version:
   ```bash
   python3 website_designer.py build demo-site
   ```
2. Deploy contents of `dist/` folder

## Security

This site includes:
- ✅ Content Security Policy headers
- ✅ XSS protection
- ✅ Clickjacking protection
- ✅ Secure defaults

See `security.conf` for server configuration.

---

Built with ❤️ by Lux
