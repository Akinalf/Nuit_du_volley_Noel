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
