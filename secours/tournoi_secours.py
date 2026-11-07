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
