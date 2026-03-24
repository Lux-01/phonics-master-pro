# 🌐 How to Connect a Website to a Domain

## Quick Overview

Connecting a website to a domain involves 3 steps:
1. **Buy a domain** (Namecheap, GoDaddy, Cloudflare)
2. **Host your website** (Vercel, Netlify, GitHub Pages, AWS, etc.)
3. **Point domain to hosting** (DNS settings)

---

## Step 1: Buy a Domain

### Recommended Registrars

| Registrar | Price | Features |
|-----------|-------|----------|
| **Namecheap** | $8-15/year | Free WHOIS privacy, good support |
| **Cloudflare** | ~$10/year | Wholesale pricing, fast DNS |
| **Google Domains** | $12/year | Simple, clean interface |
| **GoDaddy** | $12-20/year | Popular, frequent sales |

### Steps:
1. Go to registrar website
2. Search for your domain (e.g., "yourname.com")
3. Add to cart and purchase
4. Create account and complete payment

---

## Step 2: Host Your Website

### Option A: Static Site (HTML/CSS/JS)

| Platform | Free Tier | Custom Domain | Best For |
|----------|-----------|---------------|----------|
| **Vercel** | ✅ Yes | ✅ Yes | React, Next.js, static |
| **Netlify** | ✅ Yes | ✅ Yes | Static sites, JAMstack |
| **GitHub Pages** | ✅ Yes | ✅ Yes | Simple sites, portfolios |
| **Cloudflare Pages** | ✅ Yes | ✅ Yes | Fast, secure |

### Option B: Full Server (Node.js, Python, etc.)

| Platform | Free Tier | Custom Domain | Best For |
|----------|-----------|---------------|----------|
| **Railway** | $5/mo | ✅ Yes | Full-stack apps |
| **Render** | ✅ Yes | ✅ Yes | Web services, databases |
| **Heroku** | $7/mo | ✅ Yes | Easy deployment |
| **AWS EC2** | Free tier | ✅ Yes | Full control |
| **DigitalOcean** | $4/mo | ✅ Yes | VPS, full control |

---

## Step 3: Connect Domain to Hosting

### Method 1: Using Nameservers (Easiest)

**What:** Point your entire domain to the hosting platform

**Steps:**
1. Go to your domain registrar
2. Find "DNS Settings" or "Nameservers"
3. Replace default nameservers with hosting nameservers:

| Platform | Nameservers |
|----------|-------------|
| **Vercel** | `ns1.vercel-dns.com`, `ns2.vercel-dns.com` |
| **Netlify** | `dns1.p01.nsone.net`, `dns2.p01.nsone.net` |
| **Cloudflare** | `lara.ns.cloudflare.com`, `greg.ns.cloudflare.com` |

4. Save changes
5. Wait 24-48 hours for propagation

---

### Method 2: Using DNS Records (More Control)

**What:** Point specific records to your hosting

**Steps:**
1. Go to domain registrar → DNS Management
2. Add these records:

```
Type: A
Name: @ (or yourdomain.com)
Value: [Your hosting IP address]
TTL: Auto

Type: CNAME
Name: www
Value: [Your hosting domain]
TTL: Auto
```

**Example for Vercel:**
```
Type: A
Name: @
Value: 76.76.21.21

Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

**Example for Netlify:**
```
Type: CNAME
Name: @
Value: [your-site].netlify.app
```

---

## Step 4: Configure SSL/HTTPS

### Free SSL Options

| Platform | How |
|----------|-----|
| **Vercel** | Auto SSL (Let's Encrypt) |
| **Netlify** | Auto SSL (Let's Encrypt) |
| **Cloudflare** | Free SSL in DNS settings |
| **GitHub Pages** | Auto SSL for custom domains |

### Steps:
1. In your hosting dashboard, go to Domain/Settings
2. Add your custom domain
3. Enable HTTPS/SSL
4. Wait for certificate to issue (5-30 minutes)

---

## Complete Example: Vercel + Namecheap

### 1. Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow prompts
```

### 2. Add Domain in Vercel
1. Go to Vercel Dashboard
2. Select your project
3. Click "Settings" → "Domains"
4. Add "yourdomain.com"
5. Vercel shows you what DNS records to add

### 3. Configure Namecheap
1. Log into Namecheap
2. Go to Domain List → Manage
3. Click "Advanced DNS"
4. Add records Vercel provided:
```
Type: A Record
Host: @
Value: 76.76.21.21

Type: CNAME Record
Host: www
Value: cname.vercel-dns.com
```

### 4. Wait
- DNS propagation: 15 minutes - 48 hours
- SSL certificate: 5-30 minutes

### 5. Done!
Your site is live at https://yourdomain.com

---

## Troubleshooting

### "Site not found" error
- DNS hasn't propagated yet (wait 24-48 hours)
- Wrong DNS records
- Domain not added in hosting dashboard

### "Not secure" warning
- SSL certificate still issuing
- Mixed content (HTTP + HTTPS)
- Certificate expired

### Domain shows old site
- Browser cache (clear cache)
- DNS cache (flush DNS)
- Wrong nameservers

---

## Quick Reference

| Task | Where |
|------|-------|
| Buy domain | Namecheap, Cloudflare |
| Host static site | Vercel, Netlify (free) |
| Host full app | Railway, Render |
| Manage DNS | Domain registrar or Cloudflare |
| Free SSL | Let's Encrypt (auto on most platforms) |

---

## 🚀 Pro Tips

1. **Use Cloudflare** as DNS manager for better performance
2. **Enable HTTPS** - Most platforms do this automatically
3. **Add both www and non-www** - Redirect one to the other
4. **Test with incognito** - Avoids cache issues
5. **Use `dig` command** - Check DNS propagation:
   ```bash
   dig yourdomain.com
   ```

---

## 💡 Want Me To Help?

I can:
- Create a website for you
- Walk through the deployment process
- Set up DNS records
- Configure SSL
- Troubleshoot issues

**Just let me know which platform you want to use!** 🚀
