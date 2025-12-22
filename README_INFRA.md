# Déploiement du site tpl-creil.fr

## 1. Hébergement et réseau
- Le site tourne sur une Raspberry Pi, connectée à une Freebox à domicile.
- La Pi utilise une IP privée locale (ex : 192.168.x.x) et la Freebox une IP publique (visible sur Internet).
- La Freebox n’a pas besoin de redirection de port grâce au tunnel Cloudflare.

## 2. Noms de domaine et DNS
- Le domaine principal (tpl-creil.fr) et le sous-domaine (www.tpl-creil.fr) sont gérés chez OVH.
- Les enregistrements DNS sont configurés sur Cloudflare :
  - CNAME tpl-creil.fr → <tunnel_id>.cfargotunnel.com (Cloudflare Tunnel)
  - CNAME www.tpl-creil.fr → <tunnel_id>.cfargotunnel.com
- Les mails sont gérés par OVH (enregistrements MX).

## 3. Tunnel Cloudflare
- Un tunnel Cloudflare (cloudflared) tourne en service systemd sur la Pi.
- Le fichier de config /etc/cloudflared/config.yml contient :
  - hostname: tpl-creil.fr → http://localhost:8000
  - hostname: www.tpl-creil.fr → http://localhost:8000

## 4. Application Django
- Le projet Django est dans /home/romain/programmation/TPL
- Le venv Python est dans /home/romain/programmation/TPL/venv
- Les domaines tpl-creil.fr et www.tpl-creil.fr sont dans ALLOWED_HOSTS

## 5. Gunicorn
- Gunicorn sert Django sur 127.0.0.1:8000
- Il tourne en tant que service systemd (gunicorn.service)
- Commande de gestion :
  - sudo systemctl start|stop|restart|status gunicorn

## 6. Nginx (optionnel)
- Si utilisé, Nginx fait le reverse proxy vers gunicorn (non obligatoire avec Cloudflare Tunnel)

## 7. Résumé fonctionnement
- Un visiteur accède à tpl-creil.fr ou www.tpl-creil.fr
- Cloudflare reçoit la requête, la transmet via le tunnel à la Pi
- cloudflared relaie vers gunicorn/Django sur localhost:8000

## 8. Différence IP publique/privée
- IP privée : utilisée sur le réseau local (ex : 192.168.1.10)
- IP publique : visible sur Internet (ex : 88.191.xxx.xxx)
- Cloudflare Tunnel évite d’exposer l’IP publique ou d’ouvrir des ports sur la Freebox

## 9. Pour relancer le site
- Activer le venv :
  source /home/romain/programmation/TPL/venv/bin/activate
- Redémarrer gunicorn :
  sudo systemctl restart gunicorn
- Redémarrer cloudflared :
  sudo systemctl restart cloudflared

## 10. Pour vérifier l’état
- sudo systemctl status gunicorn
- sudo systemctl status cloudflared

---

**Pense-bête** :
- Le site fonctionne grâce à OVH (domaine/mails), Cloudflare (DNS/tunnel), cloudflared (tunnel), gunicorn (serveur Django), et éventuellement Nginx.
- La Pi doit rester allumée et connectée à Internet.
