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
