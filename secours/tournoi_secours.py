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

PAGE = zlib.decompress(base64.b64decode("eNqtfVuT20iW3rt+BVXdLQAqkEWyLiqRhaqQ1NrpXvdtVdUdDteyJZAASah4EwDWRRQj5sER63mxH3YjHLEvuy92bNtvDkc4/Gr9k/kF+xP8nXMygQSIuszMTo+KQCKRl5Mnzz0Pjh4H80F6swhr43Q6OX50RD+1iT8beVvDeIsKQj/AzzRM/dpg7MdJmHpby3RYP9zSxTN/Gnpbl1F4tZjH6VZtMJ+l4QzVrqIgHXtBeBkNwjrfuNEsSiN/Uk8G/iT0WqU20nE4DeuD+WQeG8180dprH+71qe4kml3U4nDibUV4vFUbx+HQ2wr81O+49DyN0kl4fDZfxrN5VAvC2uV8MglvjnbkwaOjJL2h3048n6eren3mX950VPvdej0Og84Xg+bu8zbdjeIwnHW+aIfPgt027vujzhfD9nBv+Bw302Xa+eKg/2z3cB93GFfY+SJshwdhSG82cbM7bIctumnhteFwdxDQTRs3QbgbHKwfPV3159f1JPoYzUad/jwOwriOkm79KuxfRGk99Rf1cTQaT/AvFah00tifJQs/BmDWj/rz4GY19eNRNOs0u0PAq9PaX1zvtBp7teQmScNpfRm5dX+xmIR1KXC3TsPRPKz9/O2W+2ben6dz90WMBXETtFtPwjgadvv+4GIUz5ezoHPpxzZN3OlK91+0Bu3d3d3uwg8CjBrDTdP5tHO4t7hePyJUCePVxusE5KwBQEK/3Wk1F9e1Ft7tLuYJ8GI+6yRpNLi46abzBWb0sR7NgvC6s98NomQx8W86w0l43X2/RK3hTV0hSAfwAH71w/QK69X1Aa5ZPcJck84Aj8O4O/IXncN8hLX+imBFkA87rQN0r5vvT+aDi7WqlUz9yWQ1R+NRetNpPNvvGm+1qblGkq6KZd2rMXqu84g6s/lV7C/WqNWYX6zU/J/3w/bzPhdezFcZUPq7/uH60dSPZljQa9ksnWdtAKirF7jmL9N5AXbrRwDtKoPdMLoOg65akmZ3Eg5T/MSEPfgtgNBYI14RhX0E9hbWJJlPoqAmq0eo7ZQXPJxd2ok/DOvARB+rBKqgHjnGqjF6j/1gfoXR19u02LTi8ajv2+2mu9d0n+27jeahwxOp9ZdoYLaiAXZa3Wk0U2BoquHRRWncGTSwvLWmsUCDiT9d2C1Mxt1t7F9eubQxHKlwFTJIDppNhZQyUexoVWHoT6PJTSeajbEfUgAyBRbxolJf9UazvR9OzTE3MOz70d7s/FmzCfwZ+HGwumUtYj+IlolgVTbNtt4wGVI0GaZFUNMStm8BNPdZG++ujBYAPBO3940d8RduuAaAutoAsup6j9aMRjSOFuY+aunhGAtVBArvCw0UminNwIRjGA5bw2cby6s6awyWFWQKxN9crrVUnV2nm1WZM1RUDuazsLCewXDYDIaFcci7GEk/GhmzbrdLsz4soaegkwJdW0A38fvhZFWgXhuQkzf0xj2gVUnCSThIwYsXy/ScuL+Xhtdpr1AQTcNCwWw57YdxoWjhJ8kV1qW3kn3aaja/KtAnvW9zkvLFIAh2gzKOa/zLdlxpSwBYV/5lWKa1pf20uZlpVnXmmMN5PO0sF4swHvhJWN7RjeZeONWgZRLVrO0J+sbzqwy+ozgKuvSnDlxHScqiynI6Szq7zMmGMdNouuAtQKylYndoED1jmnUf6VWjAHWPk7Q+H9YJ9ivjLdpCaPauHUTQuZ8+FReFBs8A5BmUx64QsJFOV/PLMB5O5ld14nYdf3ZzhUUMs5q7qLmX4YLR+hovN+KV0QezKm60cbUq7QWqfU6CXj256q3my5RFLoJY4CfjEKjVfz5oB7td7O0EM1rMIxowdwJ8L1HZsHnoE/8erHI2s39YOeO7sExAWEF4NvFbg2NPqBV33giDKL2XEJVn9KhxAbbbh/R6AWG1vddqDiBYXkx4XkFA4ugFRvLc391rtdeoPPVTrlygXfJGMBi2wl31RuvgYH93D+0vHsLNSmzKnCPLVAWORLNuVbCk9r7D/Y3vw97yjm1hw6rBDPrBPgTtIp0T8Qgtx6sCK7uFWbX2VPVU0bLnNIWx9M/X9DbmE0MBqZBDSsA4KHNQfjuIYpBdktSEbFQNpsxqpViGpiTSOyB1eCekDD7IzZliMCM/bam6mnTrTmZ0Ics2WD1glkoYKAh05swFsqkfp9zmYhP3LiZOsffA6d7BC6qg0DwAGEySxG9tShU8hMAAzN7efYDhV66UPCV0vF0UqA7KTTT2aAUScykxpmqEpgaVtjErdNIsI9ltuN2u4sSmcF/C3j1zKzczWG3w5CTbLYw9anJ8fetu0ehzByVp/9tvnqRi8zx/CNYcQs7nt829Qsz+XpRIZiZvaVIr4z916zLSlhCfGgr+ZLmRmOrkWkkNzLw113y+5+/2D29RhGSoexsaMmm+o1uR8Q45KQ4XoZ/auy5AAz3XbrqQlRzHUBjQcC2ILm/Rih6GwKbKdKjEjw3GrvrqV4nPAtmNnd9oPwDS0uomrd4liYeeYXlnZVG2QlEhFs9AFNh1Wjv1Vvee1zI1nXX/3YNMUeRFIg18Te1i0hXjxoPGNNQmif7e/m7z+YbOqmplLah6JKRO7hxuq2q4xuAONpU+IqyTh0jf+21D+s74jcaAgweJ2RX0hPtXcjfUu0lQlLrxsNZIV/fKh1RRNMPMlrTPZSUtlND8IGzmqn29QIkPlOq/fpT6/Ulo6lxqWOh54i+SsKMvSpsYb26QoFtVpGplqlIX2BNzwxrDmaVjAZXddkzJnvAR3QcrU/dpV8rblQvFYmPTpf9AFZ11GtzZ1SYmpXFj1KylQYUu30RzeNqqftqSp+3qp21W5NPZKrdQFUlRs8g577AMZcpvGaEyVtzSxp+iQtA1MMHYUEJOMTaoP4PVPcYRhahUG9pHtUoij0fjeVLQWWbA7AoBE3XPsXUJVWEgyDB/b18GlRQlR03/+VGNIVqSp+g1dFq2drLpsShiMK60mq5oGY39/dwk2W7eLjGxlBHOgjukiHEYpqv7Rf8a/4FhragQFZZJm3j3ldDJbZfMckqHSR5ogyAC+JzwjYW+ZrXtQTVvmEsL9Jb6qrGJZ1VihHcrxiLzjB46TG0gERz9EBs277Zp86ZhEk1fo04tuRyZRE8xZSb5ZelkGU/K9oOKCZDtqt6HAfuiw3/xdFIlOn2Rzn3gfAnzmMXuM/VljZNBn1NSvqKJ/3u7jlpFK0G73a7yhzxXuFNl7SzJY3pDNaVLGZgqrEGtTjKc3wUaCqGoh5eYeCI7Nof4c8yhQjqSWZNlW/fVWj8K4KuLJkktWU6xRDerEiXatHAv5pjCdHOzl0QTNgdJXZb+lA+ggjts8ssKilsW/jbGdbSjHIFHO8rBSb405e6E7ycKvK1xAAeoPA9j8lPCOcMP4E/Dg0UNPoYk8bZA77aOX8E1OoLzcpb+8ff//WhngRepPl4jLwG9Ba6dUHu4RykmyaXTeeBPqBgFRjHDPi9OBnG0SI8f7Tyt1bP/1X73+bfZ599i4NgyJl/n37yBzxS/9pT+wq8bpomLolhpTrXv3BpsdQkuk1qr9vmfaweO2d7TnUegeUmKhjx7uJzxS7azelSrSfnrV6+883rLfeaCvLb2icK2D9zWYc+t/fCSn+T/tXvd7L3Yv/IuveMV9Jta7Nmtg6eX2632oYOfg71uNLQvjz0wcak8877303EDFsV5bF/uPHO229247tnt/aezeqvp4O/+fncdhymcvLW4u877YUz5aZ5wZ9Ss53ktR2qe97q3tu/SvvIun+5tt5658JIupMogjCa2TcV7zo49e9qutx3naduNw8Q7P+gBq2KbprTw6P36sy4eNCbhbJSOj2bdRd2jphwqBPLDBW63IL4snK4eepiYgx9NPfvavXEUnD56zayDyHvWjY5RENXrzuqjZ388Omo5v9r2x+Pj42fO0+Z1q/U1uNyvnm3foChynrScp9cZkD6a/cTJ19GlF6Abde/Nwqvaizj2b+zAaQyjycRuYpDnQb3V81pdXjR4y72WMR4M5QjMd3vbWenC9yh8fxQrAHTf07P4/H3PG01t+nWpEYdW+/12K6vn0KNfPfzdbvUwYOqIXsCv23aqlzlO3oQAFhmDXewPx5gKbhtTf2HbKGw6PGB51K/NhzV6Q6PZ0Ov/GoPtRsPUxmwbi2UypnlTC3jttT8Y2/bAjdBQfB5hiBjVwB06G2PSG6U29S9CmygW7xg92P5NCnRh8DaG8XxqE7TPUOv1jDZrbDuNkK/kVafL7xJAsVUBUr7VML7EIlweeQfdS4KudDDwF55toDQ2m33p7Bw6dWzX88ve0x9e4q/z9JBA32pv84AU9J8eHnl431lRX5dd5oLd9Zr7RO3HKFbbpzZbgjka8yJYvrryyh3jhaxruIu4c3Ib9aMUm6ZntgAhw7MvEXqAsdAa5tiFAiiPGcbTu7I+VF3jt0C/Rs3Ye+4edF9cmJNzD8F0+V6vZ9875kp44uQvN12eBCwSaEem9fSwzp0qHJW2m65dKP7q0MH/iwsExuM1r1+/6hr1jnSbxJZ+5ce/0o51qFEUubqRHLAEqeJmM9rDtvMOHSYSfYNIyP475I3X9/qgEJ/opfNo+32vS40KCPsAnNHbrO/pJUJUjV42N75tZd1Z4s369fjqq1nfTSaFWlc7s75DO9JjGmOHE8dliSxfeRroRRmrZYazvtCTDAoeDzphynnhXmwnk3o42bZRMzlpdlpYlYttqqPBIi+Gg4HHBILoA5MHwnt6yaG6epvLuOSWyvHyAIYpvO0UAQSZMBt9aUm4ifNmL18XQF7azShI333vCDOKHnseT+HTp/fHHoaDltWSgL6g0wIWCEcKY+FJYOgmCVlJhx2qtHaJ1uUknMoUFR/6kyR0HHc4+/NfLowpTP+KeZQb0JwwqPOb3vl1zwu6w5m6TONlqHdmEVzUtqwwtWMfuJEbfdUGh8ZqcEnkHuQl5hIMSZCNM+6omw1uvPpeN7g58ugvGs4eXPODa35wbeCUYCvZHfkCApkdXDtufnMDaF1fe9fbAfq68W62gxvCnutrkKInT66veRJPntzc8P3NDd87PPpresMNsMjtJ0/oBxRprQHBE4DVcxcsSa5ZYtgzCnZdKSpAHKRdyzS8Aavg6i9M/CtSg/wZs2N+mym7HRGYnzx5z9D+9Mm8z16qt/QTo0i/45B6HM2w2qpVc1navCztzWVp87K0ZVkYbv4C2E/wxsV7XNy4D1ikxyTXSccFRJmm3hQYokakV91uHR3tOp+mIspAdAhKxLXVZNjRIxt/lHCFK/Ca5yRe7e8+c7qFVvsQtQJUBPBQzwFB34e31R15kXeMXa+ZFAbaLANI+vT2uU+GwSH2wsiOHLURDiFgj+yD/PYQt8/07TO+zTiY2e5zmovRbmuvHnHtqKo2jeIwr8zo17rrhcNS84eCsq397aj4ivn00CWSoBdLIfA0JRqccYQIqFHiCRwKIHJ1S0LYjj11USddIUdlqel5B45c7ZcHjo2Tonn6ESJEVxtbpV3YInqZrz3p8r27hJQlfW23nCdthzaBe+MtFycKcNRqh/50szZIhNKU8ckTzPKIaL4WvRyDgto2npyjBhBnt4c/9rO6jdsnWPYMjyLaNYoyasQ30R9/A+9ckUn7evvGEWrqqqKb4u31V7vmrbxQLDK4+/XOrrNt3N/sQBkqNfgUPWzT31LDeXnpDVuNsvCwV6SAi8kNb2q9XDeAhBDerkldCIOEPneJthRBT5A5n/a4VyeH+uPsUrMsJZmGM3+S3njEHDVGiKLXhIAYX2zu6dKgRNNdzgydqTQ+kgiy3h1qFEtLrOYYVDgfoefpayhj0KeWM6lGbXvevrPY9na7ITh1TQqPqQg4wkUygPW6NNbySDbHeoNrczbmWPWQMB4a+b/NkHLwYbdXryoeGKx84OVLh24GBqCgR2LBdcF2S2FAoQB/ZJzrAlFP50JynvLUUcHO7QA5/8FaPW03YbZKn4L87+DXAafEtUYKpTEtCjSPxfUwASVy+wuvFT4v0rspJjoFOZ7SHBnpbYTSEqGcOkqyXXgKL20WaRdHfShuaGvR5Xan3XX2nkxLbumhtCRXj/IhrmieJFzyGNemMgtj66Yu+8HLdVwawuMPSju0LDXGKUQu5vUeih5tLvGHxi0bVz1QW/dDw9gb2967779cXW9P1+6Xqxv8jFuXLUgiH9+Ze3bmSRPb7adTc461d0eYS41OJ7ycX3tbZFj/cjVb85+tGiKUFiHcGySDRXTqAZa2ZPE6GIXJVu16OoG6szVO00VnZ+fq6qpxtduYx6OddrPZ3EGzsNCRba0mBx22pEkxTOs7EqZxhAG2yq0dGA2BRQAOngX5MzRGz6jB43d6JdQKEcBdPMAKrR0s/KOSDfD7uVj/lkBeOfTQgbUGsyEbbZQkISyAkDBx2AIXMMHOZphlpdHvh7dnr198f+pBivnh7Zsff/7h61Nvz/3p9Ru5gdHhES3X6ZknpgC2ftZex3EN6AD48fU8lg0aLwcp1neajNxkPgQWJUs4FukejsRxlDRw5eGf3FAV7/Fj+iHaoLb4BGZqb+4d//Xpjz80FnTyxOZLtI45wENjz0nkyFA2CIf+cpKepjCIitVSYznCKvBG0lnxKZCO9cMySglkcjiETKc/zD//z4nl+oPBEpu9Y7UOO82m5XJUEt/t0t1knnba++7CX8LJurfvMgjY6AuzM8yC0wjl7ebaZfxLQx9+lwrNS0Eaytdbti9Zn//wYRnhDI4F7RbSheOygVu9a+vVUIoZQR86Ha0pZkQqxjqHwQyuB2gMH0OY8nK7bd8rwoZwjLZv8OnTYxlflCgDYINHDblfXSlpBfKHGrW2B/WpkaChYev92H+PndAAQKCv2Ku128+euXm1T59W66z7ctcya+5bLs3OFQz0I6+vLmQYAg5PX1A33QwBagHBSEABA1IUnMImHnq27/Zz2+H0OtcO6YE7VYZisgtRgTLb2qgI7eMQXHp25LUOSEWSoudURBfPsrJ2U5cd5mVQoWwpfP7pE1+0mw6bs5SaTaMLSOZB5Kr/mLcbmmkk/cd66ylxD561MA29GCZKXS1uwMkTQ5PnRhxdF5NIvCSb7MI75U1kJw7bplPb6liOO/Z4m307g10Kdg1Y+QEGs6zFZUz67THrwOOj9h4Gx9fTowNMJB2TD5FsCkwPbGs87kynVmb2Hj89aG5P8+kuLvRK+Ef9E3/bqlvb/U6ff33Qu5wlpf6MvDqJ6ZIA43vADrNXhMydyCUnFM54Nd0rAAQ/iyH98fFnvlh0zntrUWJyu3E8C8hyfHqmsXOVGUfxCPtHr4KNW0MproFMT8JaTiEAkVp/vhyFtQ9La4mb4TxKcNJOqHUNNaLP/xJL1cSPkigk0qw5qFpFGgr1Y6g/j2WlwfU3NHIlQcMNcT5t+LDBylW/pyvAJMjwgHjWzy/zh8Ntj1Cwi0ufL/tUb5hf+qpC9gqgKDYtdAMjm3nvZ+ohiZN4i9C77/gNWgp0q0VGKmXMd/r6UabprAtrkxA4EmIujf5yMPYS7g7AWMJiCFl/TjrJNuY873FLLlmaGkE0HKLqYljHH59FJWmO3YjeeaMBDtMDT4pTW6spN/x+/Zp/aCffcI8ooB8poHZRQD9SsKDbBd9cMzGt3/CPoJj0eRHe0LZMZKaWa23LXNQlNaYuF0ODoPFQxdGRKASHF/iiA+7hMqYn3JNG90QtrmC9dOZSNx3pzaV+OtIdbQnqTfGwKMzeJs1EOgYfgi/WBm/G+MGFQcLoInEcRbGPWy45aRcdQ2GMdvYc3l5rlmFeLEBXIoXvLKlAcpmC+U4gz4S1z78JS4STDNs+Dfk0KMqxYaZRuLyWnfX5N95OIV6qzSwf5vekRt6UmF6c8StUBaYcko5qfhzzJoN1lWRxOK0d2mQZhVn4UXxGXM/meSrw8W6jnSaT134r7VXMvY8eVzgXBTY3m8CTcWS+KkZQ00WkXozUxiThnntujP3EXlwweSxvb0WeSPKXxhPlYowcbcw2y5VcAVdUPkl6Wc8x6xmF4LcsZKgpnqP7Xk83iudOUUZVrqG1Qar7S8Rl/RWzYhmFQbEpEs7L6KliV5qKGluDZTV4DqyzEAQervdW7Y+///vaT+Bbg2jhT7CqOKasHNl7DnaJrtjmiq/QynzCuKNq7lPNQ7PmLtc8JdmUe53rqs+paqvtWMb6MkaTK8OlvUbKgpbPRDAyxDMTAUbQb0ZHu91RadUjCDEEi5PzJrnL3d0eb2jYDwUb9p6OtqOeUIzOOTXrFv/0iv6CIGTb4wqBZAG8Pj2XD4d1rDeYEEmW3B6woORnGHgXmVhwSesiEtT5iBnwRU+z7cuT80uSCS4hBPSM8ZRMJ1Nw8wvp2jXlq/PEd5N+z0sG9oUWBVa6YirL0RmBfOEll+sCWf3gpuM3Ui3b9PUlHg0759bQckfuRW9dHAGIm2dP3Ykj8pPg8gnAwm8KUCbrTs6CTsCbOsyvjFYm8yT8k5vpd3I2p5B92PKmF7aFX6Dd19AQ6qKNAW3tFrDuMqnthUBJWj/YROV31yk10laNtEuNtGt2O6Q2drM2WqqNdrGNxZCbWABm1k8h9lao1MKavRuSYjigFmjWNsZKdeIAe6f2dQtyoSpuG8Vtq9j+MOL2qXne96FFzEba+gVr+2FJaiq3JuXtQnneHEjQMMrkXmel9hpth55Hrw4j17KcRto1nsCe4/Egs4eZD3sxrG5suy3NgdNtNrermsseSnNCAUSgWY1c0SaFTp2Pei7OWQ3GYdI5p1nTDPH6EBuxf/PvwpvOyixFDNnaxT5dl2jpSrrQFGZdQVZP0UewnIS2VDVlYdq+mdJF2qoHwYF+RWWlO75gxZXucvFUaa9UKFei+3qkONhohG4M4ozzd975CkMMOlY0G84tTW1eiAZdI2sX2DtwbKTVaNWU0rEdFzaDDj/JAddziSJ22Pe4ZvpGFBRBZh5XNMkqxUbER1ov7MYl6gopOWcy53GvHEcBfwBM/peGyV/Rr9xXLewQ0rZ+i7wIKSh5mtshI0QN7W5jBh4qEgOfavTQNC0lmgbLA5EGDSQL2rEU9Y2ihKgQkz767SsiF1tu7EZQTDJbJWCv+hD48xwtVwW/ojtN+FmxAOVHmbNtMav7xR8tuQwBWI5aF4CX1wK/24wsejmmiSxHZgVg27Rm2QX9NOMqNVqtbY/aMf1zBEkOxlqVR1/Anp8IO7EVIMdZFaMT5K3GFqfLHXOVrtYV7uzsVa6bhaksf5QulSkpkc0eVo6Dts2tw3ikQECVCrrkuWJ3vfnw/HyTIyQlltBzzzcpflIk+VTHIOmJNvWZRJ3q5GQ5sXq9wkYxEL5SYtGeVU/IDehcg+nZ+UUFsjMD7wwJ1fv0Q6ycfgWrhwZaa96t0bq8UjwRtVR/Ap7ehZoFxLwXO94wFWRMWMTRdRUaKEJ5ByJodW2ZMiFnvSdGVE7sj0jdQT4d8L8aN1ALSYXgh59/gyYS18hIoNUg/CUDwvs5qpOSA08A8+EBFCPUn4X+smYf6OoJgqZpF81h3qGp/ziTJ5OoTyoUdKX5lK4Cy9ejSbhL3V2XxN/Pv41gLEs//+ZCp1KY5dZITUKPQ9ajaIgBI2XWc8A62mIODkVd08D9lOzDtM/Q6uDz/0aTbLBWQniX2vz82yXJJNi9CeftgRY/n82wGyb5GOn1MlBg10e7eiJQd6jTn2c5VGYWAzaFvau/RMcE8A9LWJLIYA4jOYbM8MflfMZkYIbiDkEJTSQwmvopr03w+TeMGEwsQlgnUQyMBAs4G/E8FxO8lZt10GoGEW6S9iTYYvYOjwNTpZp+rgon6vEsdRoF1VTsqm/CIY7Wh4ni/W5CsoAhAQxmaaVSQnY8qNi3PQOlqn6v/txhd04SicvTsL1M2PiS9c8kPpk0aCeB0MteKqmsSaRtOWy3mjTUzlHcBcY0o8zYyYYKAJKib6oVYlJnSTUj++NpSKGdRps6KovcyapiA5HiNneBIL9CUZ+KisrSlR+lbCAqwQrGDxgle9ouknrHj3VbpMEjqtMFVwqMQVUZ9vKBlmSS8Ry5sQzYCm080a0pwjxtqA0Fz2wDoqXTyUM2Dfcjqy/9JPdAmuNIaRw0SyMQAmtFg9czKRsZDUUS2Hee9uAIbdYJ2+j6YNum0T958ph+VBsne81O09m2Ce1QCVNKonrrpCWldrqdRE/3na80eHfQYCGmIhkc9QEjTCIZiO8zLUVFcDV+IqhSHjRPiJZZXKI0cLrqAT95UHyDUXV5HnKXjWFKZyA9KjTkxI3lcaqWRTgnsl6Ew/M2bCrFhtaPblsN2i/mIijwynYyLDGYCDMatRdAM3+OJxzGQElD0BqiE32iJzDxwAgdkHweBtaJLoZzM8KRjO3snvyVlJqtQ+7coh7yCzyqiNO+YlQhr2DmemLPHT1qcMC1qTawidUw5LtlhcfbNB0JlfMqlR8XEHwFwTf17iKQOSte6fquOgjRoWGqazdzFJp6lLjxUMIXYhZV/rncikWWm5isL+E12APOOStDhTLAxieZ0VQ5ZhTNg+MB8QP+pJP5WV1tCuvkngWym0rHGeg6YqFUbkClmNIoRjSKUWfU0PrpqMG/mZgy0lQma5QbeatWoKN+xbqcKusyy5JiXqbXErUMHb4A/5i9xZGrjkI421lrK6/haH7BuAM2SGEJ0QfwYvZRx8AdeKZhAYaUEYcjgC/mR5A5+jiIWj6hYhhr4ZZiT56dmWiDzFKDGEwImwVDZhbCrgiW7/3AOY34Lcypb9z3tZNSWkQ0A3klqUG+fCw14buEXywc0bL6TmVxH8WJf9TE3z7/9Y+fP6cb/BRdZbbFk8HpO/ZRhg1Lj4FHgJZK1X+eKckxS3NI4sUiXKYsImJVo5gBLDKTEubyZh8HxBAHRJxzr6jNorpz29DGPsSsZQjjqwySJKXWYb3J5tLDeuvArbWe1xGxXEOETOsQP6166zn/wMnZsPJgQGVcFrNg7p+FSQZS349D7f5Udjf6UzLZNVh/JiZtSEmD1MSIzEbuFZAlW1pNsUWDLtoPvG24mt2IfqZutTVBOQFLsNp6RVkclFuv5JSACAkRdCTntoDlja2CfJFZEajlaXkN3oTYNP8j3cCQTEzwE6Gb2hfPYklm0c18MwhACofkADfoMO92dkSxvbnxHr4RLaZgG/880xMiSRjkEpCAfEi+leDzvyQszELqhx/nkg3uVCufZc2eL3U9cX2K5ZFqQaNBDZcUhpiaAFGbsY8G8u93QC9E2/iQuPmMG6k9SzrCyGfaIuyvhvaRCjpTZTjX7dwuRPHKxsLBTqiERzjlyCBh1svg52ygv5hSCvPuqAljtkbwjU9qwntSc+ZTyPMD7LfaL/Ob8CM2YWEuMuFsHlbBAeMpurXiHcBki7BerjiQTp6gKnmb+Bld0wkq3Uw2GwDk8a3uFlCi+5AAooLgi+NkuORJeMVa+2yDsvBjbqUR7SEo+4jOuHA3JIB8K9kjjiIYUaz2p8faQiImEDZyDC0ItrPBZAm6Ay/Cn7o/YMPYFC4aFWaNTVcYSOSQpDY4JMq9fmeqekCSgdbngeesURrbX2mCpXHNJ4GnyZ49nDouOYWV+6UKK4KQlq6Wu2pQvyfu82KZdy4I4gpu5BO7oJUi8H76pC7bVknnmF3lY3oQ1Ezv/uwKcMO0nNXGWGleWEycSKp6Qg/yuGZBrwetshEClYyXQxwftn3HOFHmZ+cXcKxMnaOUib43jzDxJQSgALEkzlNxmnbPffKm+TidAIjSj0sFvewcIMUQmBzod+GsyH+YlWima8eM5TmJuoXYbIoBMZlf83gTg6xRbHCZC32nI0vIWgM6RPaXUFlDCCXFliGUjONNYAv9mNtEWExNyLBCx6sVn8IgTC6olfJCIQInpqGWcj99yimP+KHJFi1VrhGcsUlpTeaZEdMgHxA4yTJjRjm/Ialbg0rO4SFri4Ybn1cxKRKifBWS3K7MUy4dtHHL2a9MXGdnPtcUU+J5et5+CnThH7Ab2RdCs809XyaDJdqrFIcqi4Fx1paPLJSsCPlavEeMs4QRkKaLMAIyy5KfU5995PndEvOQRyJwLUV6Sjj2YjkAW/PNSA7kIoDAhVWBYqCxbQ7VrD+Rc+nRMAKaTXKrG5aXYjqgIDslaWiBdhSjqdWK2J6fr5uygrKiuhzk5BUiTnC8Sj3pbz5Zm3BQ8T4L9wPpO/wShcD1ttUlrWRdyj/k5R+4PPPhmfvAk2ZZi+IICtajxLstPmRYxOlXhZwVeWuRopxeoZVNklIpllYLpYqoIPODKX1ahmo+bbGo23Knbb7AofgWOHbScpM2/baNxs+nrR5YNF+1e8ysffDnvsmfk5Zzy4P2gzk323o4uk11SvKKUdDeJHvfTjN0CywQPramxqBxS/HqKKzLSAuKuUWFe4o+TBee6vE8gVBlXHuq4/Okrcrl2sM79y2jbLM8nqgc/0qGFgl/5avN0NsS2FptMuQnyr6+1HKFNlV4uh3GwRlvFBX2ib2GC/A4RZWb7i6dAtwIRN5ARGUUKSBjwe1ctBJfgCIBBcTjC0RgH4rVI3vWBRa7hmZSZBFhz3DAQsR6QAtkh3hQnOw3HBamEaRmU5IVWOa/+abz/fcOzXwNoQdHUUmAW5fdbnN3HInbjfw/lrvvPm+y74y8hRayMrQO+T73h1PhAZeJl4crtbHxzbEbxOoyMx7kshAJxjSm22wGlxsb4esl60sbAizlsjiazD99ujweR7e8NJ5DQZpEU/IDZi8yTC41fUIzFhuDLJlAIqYhHQwcyO0GbhwQbqi6ZYx4E2LlTQPM1din03gWzrNZUBjKkefMCDOa5d0e4d4t7KR1ZiB48ers2x9/OPVWvG07WuN34TN5Ky5wEcHc5IqyEQvxVEY8vQdzQ5+B0yQlI5WUntO6u2nAGpAOi2gxnwxTNZuSaBNSLpZ9MmhBiwXBQQYvLoM3DVlnBE5dycuyqf8RHwziOY7pk2mAN3F1RpZXf/U7b0UmNssi9aBjkYV2YmVB1N98/cZbWf4iwkOrg9okxrjWK0lhVT+D9RcR3mx5E8vuznsoJ/Q+Fm3n1/Dmr3dANJLUVq86DlpsvFimwKroI7/hWS9DZPuPQRxUpSxgfRIiZQoIDp8k/wmB2NgwZA4FGM+QRxzuTzt2caoASOknN7OBccyob5OJGdHX4nIAxHdhFyCBlAyAyETHOhWUDQIqOeTIp0fmBAvKOMERn6y4pN8uS7XM42AjmEgjAmUSGFXtvetrMRmQFIWyYqQmSXa7Rngm0aaCVhR7Ptnja8OQiBSBAWuyzTMonX+QrEFJB2B0B5BUYEGfzZHlFqiKUA9Ml09CmEpTTEE26TI59vabMBTqW+ylvfZzZ4XBekZQ/TdnZz9hJXQtpC/kgfFS2LvNplZeMs+H4Rh5HON7FJtx+htNFo+zSQdxgxBHy6M5tc5b3/mVG9pTCKVoS4ikkViRUZiJ/JkzhmYW3jb+Qui3epGWbV3GJF6SX8SQb2vlzlfrBTSzdijcdeeytaNsNW9pmuEJsi2FHxqtJ5IT31OuAEsOOWi1cRNYlyDP+ZkGn7JAqFe71UN7M7/6y4fF6Un+jLF1NfWMFwPPJqkAjpNRAoGgMAQ83bG2+fEKX+UZzxEU8dOPp2eWS9mxOqXTV9wCCdHKQOjLbD36Pk9EcQaQv8h5PgnFO056KEWakUtfXABQN3CTmf1D2sXwiePBhC2FENNEZYDRNKTwb84ml3AQAs7diYktZCNgCeQYi0yTBm7IKpQKQxjIOT0WS+twpjwEtMmQzaxKHl2blIIErumCwsHU1dGBviqHoc2vTJLBSKAVmns8ZkJ+hjObp2AIRhgyjYyUxwH59LDqxfGHDX3uDpf0s+4+YH7rYli5GjZQwrYSfHxB8NJyV4u34fUCOEluLcN3tnjLX2GCM2fxdoFQIPz79En0G9OIBcsHxBOQHzWi+UWHXAIut97JHYurzD+H6ib2o4e1s95sEgMfgrmBjZiUBEeNijad9l5zgygWgJO3yPckFb/OEJR13ChTMeDPQPrBcefx4/wtKnDWpahOBfezeL4gFiVILYwYlo1oSlEmZIsBarPzK4EO/pGRbtONlvPwSknhSzpPgo96LWmsDdpjN6dMQ4C7SXYeLIS7PsnUgUR5WSyrAzcBAofI22fvnD85Ot6yejsjd0C6q/UEIsQTfFanC0n+iK4nKV0e0+WIL7fo8sNyTjdb1hZuvth93rXW5wPWkpWfYsrn+ZFrw55+1drDgmzzX77WVEuNzNDZpzt0ugwe6eCUtAgbAcRNC3GNHWtbVZ5+hRrlChQcDgh+vyGAcYgPy2Xs04BKLISGJDc80XKFraU4Cs0JBxeE3LWdWr4llKOCQrPIRTGztNF3gqsRkYs3cL5NKMaKKRWV/Pjmdy88jhPTQDl78fL07csXp689KCkUKwFoqlhajuBTPluUfs8aLBeSqxYleSCjBPux1FyI+NO9UA7C74DJHBKQdamPdtCoTtC9H0Ahw/vZuC2K+Cethg8Ai2cbTXkshJ4Cs1CpMQrTb0ECoWH4fYu2jcwC4LqlHp5wPWwi6lDg4U5vbmsWkruqT6I9kNpTofhJCr7vIfvgfEapnDkHkUsRchQIVIDybOrxQYlj+qsDiU5ORV8+l8Jex+YLjgMknfj3ZCtgbyppVWVOA1qQigxLdNqdX3yPM845w+Hv2tFjfc5yB/Hki/nCzkyVlAaQKH1Oc4vMy1SJKSukTVL9DBZP6hzh+EuD14uD6JGmjIqEqffygq56zLRqZSAjLRYiPQoLAKqHL7wYS9aV0/K2kQmPMhmS5cHjZIe0K7p6WU4zuSh7Db0LmGRccm1mRQTV43hr5ELWYJaqqZagQu9L25IMpRgQVg1n0JWyg2CgUALbCdPZ9mmxQDeYQH/R+khKGa1hB841FNoS5osyb3kXaS6bnJRqc/Whr2bKr6a6lzCn9xFtmd6w2kvq8DgKYIG3FNtTxi2lQDQ4USscLdbbt5Yj1mqaHqQkIAt7Yb45+/47zzpKVCJPlXmUPuWFFATj3WPMfRiNlrGvMhHOKMQxDZG9dLecqfRFABAnHME4gCcz12dnLFUhnzIUGI7ACMiYS8GchAaS01QN4NhSy8XLnqlJ2hRiSDyZRN41Nmfu8zuFSQMGLoUsenUrpaZTrxh2lGGYIYUYqPloQztRA1AEIRuB86eDWu2+XBCogrNpiaTIXSyyBN9qzpK7jeEjFvYD0/jlPFWeQtUJpb2dYbG6eim0iIATwng/pQYRirOxQEoCCZC87xtWRm0252VIio3xmpzphOwh5k16g0ZbMZtanB1udQ9mcxFMSo7sBTar5zkZjN5pFQjWyKtbgPU7ynp7fNQ//nIFscQ+BT3W9pmGStiw8UFPy1kf7fSPj/grC8dvCgkvav/v/+DoXu6Uxe2uDjZOACF+RTLrcr5dtWgkO60ER06s+QXkiou5td46zgv/+F//Cxkl5EskeE73yuo2mkGtlzbfFUxkBIAzShuTTZ94cGH+mikrJxCiR98dyWcFORdknTgtEoak0OOQM0SNFvc+RSNR6QnRKDpCQoNN4ZIg2HADx++UF9+ynIIsCehg76uIY+hRS+z0zRAr+u4YPCyFEOOFV52VgOL6PY5sVD12TO/CBb6FOfNuC+XN6w38GdnrPOJJT56EARyeC6pKAZNNtqTGlhHCdfXCe/flSh5j2h193ca1/w5ywsvbn/ffFbvlnBAsiUjHPGQjiJ8bYqHg5J2JN9PJlsJc9djRiEBLUqgJcIKG0Pc/dBHQcuv4jFpWCIp36fnxOyJQ2++KlafAUAaHDoOyrnjdUaxFIgSKXb04sWA2EIzAIwXTk3fq62mEPKi03uIBqrHPpnxE37mr/2SgWiNQnVj08bJCJ1wsvfBneb+ETDPMu8EIvuS4lTUfReLr/vpdx86bPCVHdIxGLxPLuQcUcQYMSRdwCzBePgQYLyuA0S8Dw+bAXyUzFodD31T5cqXVEKpGbHx6c2JNQ7Uz5dwHedtzSqfkTn6hpyia6hEvOZhzBUXByZNTODFAULSq1NDhmGQwD8SLTPE4j3UcPnZRwl8gccxQBXKFvISEidjlzCW1EZSvBJZ3JeYGoE1K4XMn1gvzHIMR9pJ5HOGX6JjyNDgXDB/FPBkNoqMLyYOkJmgMiggkRQYKYVI5SgskLre6YXSsK0HUHUosiHl0IYeac3scPqejKJA0zJea09mZcMpyXRK+cxqrz0JWENabl5QnNpMcofSQk0hn09rILT/X8RkiHegDMGzdvpwDkPPP/5cEOjnYcklBHKSPfmShwCCYOBA6vYGtBVJ5FntgIA2hI/EUOfSBL59m1PkO6K3uPPihAxvNUxjUHxZRjl1Qf0iDQ8yAuwau2tUcxmHNYeqsaGDAP3e6NjNWs2Eu/nNHDAeXfKTnQUOXIwAY7gNGizFtDhY48h3Mo5d0SImNStpIuojnFDlhSwwZHB3Z6SeH7RQhHb+CR5J92iMya2GnzfikU36eapKFxogTJeb8GVN8xiENVcikUqMuVXwLhurHTnipz8N16EAVZbzq+JRBwp3S7zRL3YQVKFTGaLkyyqU2XajqqGfmUrlGBTlOjHQo+tKQFK7Gcy8kTYwj02gUJ+9+IYRWJ7w+5vQTZBqmTsW1+sc6RUj5eV89f9d596q6hkLDE67dMds0ZAR8rpcGVuD9i1ntoo6mGhcse6lBEzROrGK98dbxT29+fPXNi29/qH3/4uzVN0LarbKMgA9Wbh0XC+g7ECK0nr1+8wYNZDIsT6Nhyg79CsEWn2ksSR34yKIxXIax9eLNy2/P3rz43WsMiQdoae5XbCugN8cEt2zxlLxT+Ft454rewcJCFVtXPU+0BMWNFoSojANmMh9NfWMhEnMhig/+UvAlDL5CwXhjsYtrCxDm4FxXNXkHFOnPHdAijlDjj5d4W6WvwZnfhq4174OpAVkinWOVsZG8C5ea+YviPN72gPwohgieG/NDygTi4BlDU93mevXsOt04Wj8C3ynEIVPmskYWjHxi/cLsjWkgUTJ1vOHzb2TMI33ZSKfVEcY3+VttZVXWThIxKpuB2u1LBG4hZr0cSViIXG9Y2kmJeZYRDh9UJBhjWmsDlrm3UgdHF+QzOQO0IaE5Om0bPWE2RJAt0BAsAVQFpQjr6M3av/7Tf/6DIiXdQp93wDlr+vjfAt7l3u9u/M9aBaMLYt3gurDP6aRUzsbSpCPZsLLDyZQHO/laEYGsgNIRQIkhbYN1d20X6AutPM6t6poO5vtTN0yJtNb5K7/A/wQghdmzY/SQCI2/tQ2Zh9EKC63Go7wROS1R+ajYfo6OOuleQTSOv6EAXPPcMDJsZHpF1yQHDNxqWxjTFJKzQJRuSHTcOv5+PtPC6dEOP8ec2PskHztS1Y4Q/0Dtwfm4BBnbOv7j7/8B3hWScmPohv9wtCMVACClI5mn0d6VXv9yFbFqp9SvSKte0jGONxqaHZNZ1bhhGyHwcW0htYq8Fj+mx3tdy+0ZJdX2tncKOQHFnGq+u92KKMNBbU2aawUOjQ8bLmhVFJugehmXUAvNjWQ6HPW7Lg0nyzTlGSRI25rpBXd2bT7KM4Xdpkjm9H127dw9wdczORzTqSlR6/r2mapZosrdk0Sn5TluRFbjI2KYU+FIYx7k6GgKTMHn2UHy7gPW6xbCy+NDl4phFi1D8j2zLVWDMfhaYbAw+XPrX//pv/0dPG34+U/y8werh8MF66N+XDISYLi9zLJUwNzc1lQCzaP7JvWTyges5mGgAkejT8rS7qTGej9nLbPoL/zFZGUBLp1Y+KNMHUVLjVpcU86RxeW/MklTQskfFjbDg3o2KumFMitqXrRJMcu0wACjEjsvR97fvGlQWuzThjrv6txDINXH8jAZ+Vre8b/+09//r9pPAIJPMckDSgBBPhr9uKj2ayq08Q28rePTAal8H6kF/c03aIr5KQ4E2CgnT4e9AsYafmCSQgmlN0VLTGkrwzo9x1xm1LMpggfzZ7/xHWi26XvfXF5atK1jCiEampu/ZAlhRXBBAX4fs7NzHESpUl4vJCdkwpGYKvQ7MA9ohZS66jImQWbTO8+wUpZ3LXSlMD+Fgy2xxGN43hYxgK3jvwFxS7nz2rQ8vcz6boCKSUznwZiiYk2LrWZ4wh/oZI4Kh+xWjc724xIN0hctt+T7nTQqb2sGt00cYfwc0jHGmSw4zLZelUe8xV/ZzBIKb82Rrfw2LrgJIRM6y5nA52sYN/RxydCEyC1oZMopuQVNYh0qDGiI9n2ZzhBVGoembwJnMn688PjAD44eFU6M6MnlWxoUR6qe2GR7RuoAPxIPXRpxuhnYVMhyAWpxVihQOW5EZkVGu468DzwSkTWM88cq/VbH+t2tz5Cay/Y3sqE6lplB6F0FXpJ5naScgTJu8yIAMGx41/dxKHb4kxa+WE1SksCIQn0s/Xlelo4AjdxtVKhW2oNnTFixAYO/lcNhvAH1eTEDMubBMzFErt/lB715bb4DruCUE9STx+LxobO7uziya57YLd02JMWCPsHLtSXkRc6VIQFCluJASorpoJxC0vj4e6kp0nBJEZYxKW+CaE1FWPzx7/5jDZIBGvjIUcbYRYZ51p5+/h9TdVbNEWNtRpZyy2wxod3eRiY7Ery8HAI92NkS7xadkiuRiXq79SCpRk4FAT+2W1UCKCRrdJ5tHc15FavlZ7IYJ3ytMkhbCI+ytrlEcltYEOkzfovO8pVHaosTq0oeNI9aqxcV08ao3+VWBmMMzornWlygnyq8EFDPmGNZZCqAfMon0BBKGausWwXKmLkjFDoQFmTER/wPKoowF0Rx7GKSJxsiMWpV1lGvED62VRJ+dIQQnGOWA2OKOoYBgRke7A0ZiqWW7VtdI4+LUDadJGsz6lxQ3Fg++Q7YY/shW7AADPMzTxr1rIqAhGpKbyTj26T2MXLYXpj6qj+7Kbgw5Mwp7YDMKmA4d+Pc7ER6zbekAYlJROaB6RrWEXeAtJcDOqV7kk16EPeybEpCI+7YVMZUglw0UcEJStRGHyfvquW90heOdwdB9jlj/rZ4c+P70MyW9VYe8F4ms/+cwhFt7ksbGXbkjrflOst7xnKjowIi88GzqQZHOWiDvCfiJd4lTrbNz7IjxEzM3m1wiu8KzYX8GYK8NTn4OaSDSKHOhMewUryi1BgEioVIzmSKUoaWRGWOeQkSDOHmI9KS6CcMez+gwCCf7/OE4EgbJK9RvnPiydj8NAj+irUSA1PijPiJ8W98/MXRDv7SlTohl93/kl39dXZFo2lkd1+jE3W3g+a00Gyirzr7+w7d6TmPIKTLKXtSqNJAmYuUKYsN1VSIf0U1UZx40BSpMrK3g7z+8R//WdFO9YZqKjde5U0luTnKKKMc8cUSgtxx88Ta5pZ1iarD0zS9spoWCFA1d8UmJrpStYsxcKeS3/4j0hL+QWWyIXINkY1tDHRIPEMQBO1SNDiQKZV4OInYYSVJRDun5rN3bJKnzMwZcgUbEQ61uUHlM/GjppNt0Ra26OHGDj2gHdqq7+XZyxVTq93TcutBLe/XD4105w9suv2gppHMp20mSM+Us8XDJHhlJa4i6iqjRCFTDxJs3O0jyCkwV64SUEsZOfKkqCBaWYrHMFHkjB7sZURaamSErYgVmZyp8mzda95TqbectaL6o1uYNbPOagvExjZ6GOPhgYoG/SBKRluWDEBFuxmN8nqDLhkx+fiwBSuW+P4Zfd3BoFTqQZm+ZEa3kw3bViYmVpCQtaYdD8K5U/l8yk7tBUVzVaEeP7CLZ5gLR5jvZfKZ1aCko2/aLH6gI9qmEcKloEFfuJccLiby9RGMaF48SqANOopQaRWLonIBY9GN2fGNwaJAbTUu6UoQiDKVUNAABRdUmUxMSZvtI9WWk0bFjr8bGzfmnVkZKyz64kvYtDgwDdKn0qFyQLbJHAtiBRHjBxnJsthIskhkvgFl9d+CtHMtRlpvaxfO0QJ23WnSoKMefGx46/i1cVSNYEjH76usPfdD5xuFAgTxgA9wC3zwogDj+IyiHe6YLJl/krdMYErTTTTZ2eLmDLUjc4xJqypAqboThMXrTtQB/o1udCp32viGY0tag8AGwBhJF+7thnWbjU6UxqO7UDPSvbzKsh9jRzuVXcz43H3WCZwJRh+SH39daTSrmJSRoPzBPXKSgUKXXHJnn+VZ5pT9ob3mkneh67z4wXMuZcJ+8AiEthV6l6K7e87mf++m1Cf3C/vyz9uOpz4I5Qi3laH8ZxwtDbIYj/JjrUokMbO/2UQPXEVZXUWws+8vOkK6lxSaCCsHZa/7OY0mKowPOEWHF+jjREu2TscQzcRaTp7xUNQ5zhhtnoOfiBMBQwDoH2jBxvlNWDE5gL84Nzkqnxiw+HNg+R/m1AgOkuQnI+4dEude4CBgWs3h0CdzDCejMlIFherbeAbJ3WwYyWE2Gn4xmXDoREqQQ+BpGkGDSEhPuOFljFXKblo+57ZJV8satGbLKhFDHUTRgbWnxsmfwpGM/ICA+SWp7EyK64defmQDbV+Grye8f7UWhfydPp3gS+l4A24RQbnz7Q8//Xz26fT1d69fnalz+D4OSfmjH3CsDBVsOTygTvp9+oSHEcdC8gEvZ6UPz/FhHeOkT+lQHX3xLT/HgKQHUOA6HFyQZZvV9lVO8NthQ45OWqsUADn91xGZbO2cY2i9e4+qDPEowYLmR1TU0JzSia4VZ4asBCBSslQBqrpyBjwnP2Lk7jfFmpajA0iaLwd+GFMrEGOOgUoiUg5Lzk+me8WAZTmZrrGG60i4sccfgiME4c42j9Jku8EnR0whMmYchqnyZ6tgUfPogdgZy/5YJZSYzeTnGG45PWB4qBJ/q8wdKtxTdP5zq8lCmrf1/LnBNIwksND1+PhAiUneM6x+9bD6f/Gw+oVh9W8bFohScp/XjLkZIUXmtcmPT1Qzt3spKp92vL1NIbF3tTca42RrsUV8Eul7wjmcZoAKXfLrVQUWljejeXgzQSILfDfHQGRCeVCzKeyx05yiVe9Hx4Hng4hAthELZySyodpylHJzq8DJs5GoA0wryPam+goZp0gunH+i8wDGR1PpkK63yE4nnZS+ytPZ5s+mTum33TMbdUlz7JABft0pfvVkpF666JTfWXcfbeZo4CPI1g6y/+ww1bHUwWGdsA2iR+HYqXEyWN1Rkgh8I50OkcbT/Pm29bezv52ZSo/YTMSvdWI5OrN2FeDEH2AwD3NRunKeN9/akmA6JLSkmA19n2cEl9MdpQUL5pwaL8pzqmlnXXYGKAryQ6HGYCiOMDslRO+bZ8or35BkYjES5CElHhLBqRdMVDiP2y4lzkM6uCgwHnQLjatFaCGqKm5nh7o//0F9GCQ7NcrHOsWNIHJjWDMciuY5bGOUmxiBrpG1A3jIQ+9s8/AxTFzRUNeuzvqWaNWflFGz+U24w+mT+94ZhzgzqaCP4UkvfduE0+Pm+T1zBOpWjTzL6EXDxzDL37PKHXqCG0p2kmQNHo1MRm2Iu/atiZ0qThy7/cm8zzmXEPTXt89L6W9WVV8Q4AwlOo/LWr7V2HJ67op4TVUCLgh4uXw3gE0z1RTOtnzLyb+sOyb6/fOb71QlSTeFe5tGifRPCHu6QuyFH3hWLsC/1UmFkNUH8/iaQQD3z7enP6poyTzLGz5lbaT+6JxR3g/kIAakOeVTFgmdjZaITAMzApq8GuNkNjLuYhgDNHdBn10pkX4aOmIK5hfG0GVW9JY6bE+0/JBO2qtNkatltTTXU9SKFxNQbb6RH8+21HlwN8MJCVOxC472hWcTq2ARuMGMnpJN6Gx4LI8tjH6yYCvJImIVtqGgWGUynSyLCOfS4VQ5BY+syo+zolwMi2IqhsRMneEunC6nbmAhXQ1rM9SKuSaTz1xwlbzKxaQQmCuHBUXkLecDztqx/YD0Exl0FVQ3U0oQOO5JK5Gv5RpgKGgoDt1JQhFjGtRhZpxDrwbtYBMjAMwJMDvGF8KrM+NAQbStRkq6j/4IayQo4IDwsCXTYEVEHLPOs5SYOnnBCLTfOyZMQhBEoDCpa1Jk9QaGp77QgQxLYsgjfU9salKoM2fqT/VxoSTRdPgDj6qEklo68pFHKZHElo6bm3uk3Ehw6ahPPsoDleWSppubJiumbCjqNosPGdXXWvvZjz+fVmrtTO8NOHBTAAJljOxYUge58VSCGy0LFHt+wek2zG4r1HpX0qJqzR7d5rKN9Qsmx0z1pCa5plXaMvWJryG3c0mpN28fK+W2xEB1TLDZO++0HDlYJupr1Ej8TPIVtKCPjnBJX5d09fc+KGWo+t5IJdEhborPYCuw5cQnF8X6zIQw7oYhzaqIFZflMa0h0Ahvey//5nDxXS3LPYJIeoeizuzAcnFea2WcQiVbBOxNqXEyte+B/1GrNNFznfigJ1pBigESCUjzseH2FuJI+YcoPVFJ7CraLjIqAi84OCfCqWIkljibgxE2N8U++rqVMTzUPtc6lRphMsCnLTPVPhmYMKxq72pzusmVbgvfVFKSbXKVNYTSzXZGm81AbFLtIA8RCWrbo6wN3LojY2iEXi2rot2K1cA+Ue32YXESKes8Xw967FQX2/Q1HeJxd+GJyjgSislGI4gyS8nBEWwEHJTOHsl+uQUHqDpySZlcjy01dkmS7c/5KD0fyaXrOjOcpzuSkopZKxmXYPFeGRz9Hn5OdizhzY8512Y3S7q5eliGpbXBC4kZqujIW3miIT5zDhaCA4WKA0Q2FbntZpNVZIfEeVhDkKZ2kR7jioQ4+h2n08nxo/8PefPqXQ==")).decode("utf-8")
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
