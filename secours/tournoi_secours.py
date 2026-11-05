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
