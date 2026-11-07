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
