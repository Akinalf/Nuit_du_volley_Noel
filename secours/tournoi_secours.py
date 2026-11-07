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
