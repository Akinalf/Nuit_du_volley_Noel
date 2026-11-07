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
