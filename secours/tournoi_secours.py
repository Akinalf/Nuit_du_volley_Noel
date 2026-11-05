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
