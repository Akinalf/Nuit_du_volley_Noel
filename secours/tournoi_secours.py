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
