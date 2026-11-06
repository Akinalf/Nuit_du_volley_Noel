#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nuit du volley de Noël – SERVEUR DE SECOURS (plan B)

Fait tourner, sur un ordinateur, EXACTEMENT la même page que le site du tournoi
(arbitrage, verrouillage des rondes, droits joueurs / organisateurs, finales...).
Les téléphones s'y connectent par le wifi (ou le partage de connexion) : aucun
internet n'est nécessaire.

  Démarrage        :  python tournoi_secours.py     (le code organisateur est demandé)
  Code en direct   :  python tournoi_secours.py --code MONCODE
  Reprendre le tournoi du site (fichier de sauvegarde téléchargé depuis
  Réglages > « Télécharger une sauvegarde ») :
                      python tournoi_secours.py --etat sauvegarde_tournoi_....json

Les données sont enregistrées dans le dossier « tournoi_donnees » (à côté du script) :
tournoi_etat.json = état courant ; tournoi_historique.jsonl = toutes les versions.
Rien n'est perdu si on arrête et relance le script.

Nécessite seulement Python 3 (aucune installation de paquet).
"""
import argparse, base64, json, os, socket, sys, threading, time, zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

PAGE = zlib.decompress(base64.b64decode("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")).decode("utf-8")
N_TEAMS, N_ROUNDS = 12, 4
LOCK = threading.RLock()


class Store:
    def __init__(self, folder, pin):
        self.folder, self.pin = folder, str(pin)
        os.makedirs(folder, exist_ok=True)
        self.f_state = os.path.join(folder, "tournoi_etat.json")
        self.f_hist = os.path.join(folder, "tournoi_historique.jsonl")
        self.version, self.data = 0, {}
        self.fails, self.locked_until = 0, 0.0
        if os.path.exists(self.f_state):
            with open(self.f_state, encoding="utf-8") as f:
                d = json.load(f)
            self.version, self.data = int(d.get("version", 0)), d.get("data", {})

    def _write(self):
        tmp = self.f_state + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"version": self.version, "data": self.data}, f, ensure_ascii=False)
        os.replace(tmp, self.f_state)

    def _hist(self, version, data):
        with open(self.f_hist, "a", encoding="utf-8") as f:
            f.write(json.dumps({"version": version, "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"), "data": data}, ensure_ascii=False) + "\n")

    def import_state(self, path):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        data = d["data"] if isinstance(d, dict) and "data" in d and "teams" not in d else d
        self._check_shape(data)
        with LOCK:
            self._hist(self.version, self.data)
            self.version += 1
            self.data = data
            self._write()

    @staticmethod
    def _check_shape(d):
        ok = (isinstance(d, dict) and isinstance(d.get("teams"), list) and len(d["teams"]) == N_TEAMS
              and isinstance(d.get("rounds"), list) and len(d["rounds"]) == N_ROUNDS and len(json.dumps(d)) <= 200000)
        if not ok:
            raise ValueError("Données invalides.")

    def check_pin(self, p):
        with LOCK:
            if self.locked_until > time.time():
                return {"ok": False, "error": "Trop d'essais : réessayez dans une minute."}
            if self.pin == (p or ""):
                self.fails, self.locked_until = 0, 0.0
                return {"ok": True}
            self.fails += 1
            if self.fails >= 8:
                self.fails, self.locked_until = 0, time.time() + 60
            return {"ok": False, "error": "Code incorrect."}

    def save_state(self, expected, data, pin):
        with LOCK:
            admin = False
            if pin:
                chk = self.check_pin(pin)
                if not chk["ok"]:
                    chk["auth"] = True
                    return chk
                admin = True
            try:
                self._check_shape(data)
            except Exception:
                return {"ok": False, "error": "Données invalides."}
            if expected != self.version:
                return {"ok": False, "conflict": True}
            old = self.data
            refus = {"ok": False, "error": "Action réservée aux organisateurs.", "forbidden": True}
            if not admin and "teams" in old:
                # mêmes règles que la base du site : noms / horaires intacts, aucune ronde créée ou supprimée,
                # rondes verrouillées (suivante générée, ou finales commencées) intactes.
                if data["teams"] != old["teams"] or data.get("settings") != old.get("settings"):
                    return refus
                for i in range(N_ROUNDS):
                    o, n = old["rounds"][i], data["rounds"][i]
                    if not isinstance(o, list) and isinstance(n, list):
                        return refus
                    if isinstance(o, list):
                        if not isinstance(n, list):
                            return refus
                        locked = isinstance(old["rounds"][i + 1], list) if i < N_ROUNDS - 1 else bool(old.get("finals"))
                        if locked and n != o:
                            return refus
            self._hist(self.version, old)
            self.version += 1
            self.data = data
            self._write()
            return {"ok": True, "version": self.version}


STORE = None


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        b = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
        self.wfile.write(b)

    def do_OPTIONS(self):
        self._send(204, b"")

    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ("/", "/index.html"):
            return self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
        if u.path == "/rest/v1/tournoi_state":
            sel = parse_qs(u.query).get("select", ["*"])[0].split(",")
            with LOCK:
                row = {"id": 1, "version": STORE.version, "data": STORE.data}
            return self._send(200, [{k: row[k] for k in sel if k in row}] if "*" not in sel else [row])
        self._send(404, {"error": "introuvable"})

    def do_POST(self):
        u = urlparse(self.path)
        try:
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._send(400, {"error": "requête invalide"})
        if u.path == "/rest/v1/rpc/check_pin":
            return self._send(200, STORE.check_pin(body.get("p_pin")))
        if u.path == "/rest/v1/rpc/save_state":
            return self._send(200, STORE.save_state(body.get("p_expected"), body.get("p_data"), body.get("p_pin")))
        self._send(404, {"error": "introuvable"})


class Server(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 128
    allow_reuse_address = True


def local_ips():
    ips = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ips.append(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    try:
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if ip not in ips and not ip.startswith("127."):
                ips.append(ip)
    except Exception:
        pass
    return [i for i in ips if not i.startswith("127.")] or ["(adresse introuvable : voir les réglages réseau)"]


def main():
    global STORE
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Serveur de secours du tournoi de volley")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--code", default=None, help="code organisateur (demandé au démarrage s'il est absent)")
    ap.add_argument("--etat", help="fichier de sauvegarde à reprendre (téléchargé depuis Réglages)")
    ap.add_argument("--dossier", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "tournoi_donnees"))
    a = ap.parse_args()
    if not a.code:
        try:
            a.code = input("Code organisateur à utiliser (à communiquer aux arbitres) : ").strip()
        except EOFError:
            a.code = ""
        if not a.code:
            print("Un code organisateur est nécessaire (option --code).")
            sys.exit(1)
    STORE = Store(a.dossier, a.code)
    if a.etat:
        try:
            STORE.import_state(a.etat)
            print("Sauvegarde reprise :", a.etat)
        except Exception as e:
            print("Impossible de lire la sauvegarde :", e)
            sys.exit(1)
    srv = Server(("0.0.0.0", a.port), Handler)
    print("=" * 62)
    print(" Nuit du volley de Noël – serveur de secours en marche")
    print("=" * 62)
    print(" Adresse à donner aux téléphones (même wifi) :")
    for ip in local_ips():
        print("     http://%s:%d/" % (ip, a.port))
    print(" Ouvrez AUSSI cette adresse sur cet ordinateur (pas « localhost »)")
    print(" pour que le QR code affiché dans la page soit le bon.")
    print(" Code organisateur : %s   (Accueil > Accès organisateur)" % a.code)
    print(" Données : %s" % a.dossier)
    print(" Arrêt : Ctrl+C")
    print("=" * 62)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur. Les données sont conservées.")


if __name__ == "__main__":
    main()
