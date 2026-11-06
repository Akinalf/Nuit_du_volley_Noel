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

PAGE = zlib.decompress(base64.b64decode("eNrtfVuT20iW3rt+BVTdLQAqkEWQrBtZqLJarZ3udau7V1Xd4XANRwJJkISKNwEgq0oUI+bBEet5sR92IxyxL7svdmzbbw5HOPxq/ZP5BfsT/J2TmUDiUpeZnUdPj4pAIq8nT548tzx58nS4GCS3y8CYJLPp6ZMT+jGm/nzs7YyiHUoI/CF+ZkHiG4OJH8VB4u2sklHtaEclz/1Z4O2sw+B6uYiSHWOwmCfBHNmuw2Ey8YbBOhwENX5xwnmYhP60Fg/8aeC5hTqSSTALaoPFdBFp1XzhtptH7T7lnYbzKyMKpt5OiM87xiQKRt7O0E/8jkPf40EULpPTJLrdrP3IeJt40wVaOk8WkT8O6uMg+S4JZpZoaMfuhiPrbWIDBqsZmqqrh1fTQLyjYgy4ztm9t0l3O/CTwcQK7M32ZE829uQkCZNpcHqxWEXzRWgMA2O9mE6D25M98QHdSm7ptxMtFsmmVpv769uOHFW3VouCYeeLQaN13KS3cRQE884XzeBw2GrivT/ufDFqjtqjY7zMVknni4P+YetoH2+ARtD5ImgGB0FAJRt4aY2agUsvLoqNRq3BkF6aeBkGreEBXgZ+NORveE5uUJ87aLZaLbwBuFq3BpNwiQqDkTs6pI996uVw2BpSwcmUqzgIGniJA34LGkc+1YmM0bjvWw2H/qs3DmzKM/GHi2vxodlw2g3ncB/fjujbcDEP+p0vhqNRgyun94EGghlG2W/vtxoEgmThx+h0s9nsMqIAlWh2OtNwPEm2T/7NLBiGvrUEYgRRXMtlGfrRlb3hWejMF4l1SfNbE5PLxXt2OjvN/Xbr8FDCvzFwm81GCjv3oNlggDH4gv3AH6XgS98E+JrtVqN9rMDX8tuHBy01j8e+f9gfpfPYPGg1276cR/ew5Tf35Ty2/FbL3Zfz2G40j92hnAJ8cfkLT8GBv3/gtvUpaO7vO+qfBLY+EXKG2tokuIO23/SzSTjsY1pHchJG/f6o2c4modVv+wf9bgnI23thbNSvan7UB6jjOeFl3z9sP1xi5ieyxNFBMPIH261YT3p2arv3/6fwLzeFJeDePXeVWUuT9uT5pr+4qcXhx3A+7vQX0TCIakjp1q6D/lWY1BJ/WZtg1nnmxfLtJJE/j5d+BJK8fdJfDG83Mz8ah/NOozvCJtFx95c3e269bcS3Mch7bRU6NX+5nAY1keDsnAfjRWD8/N2O82bRXyQL50WEXciJUS/gHoWjbt8fXI2jxWo+7GDnsAhpbAEV+Q5EsbtLfzhEx9HjJFnMOkft5c32CW2RQbQp1UBYqOpgeitLd9zG8sZwUba7XMTYDxfzTpyEg6vbbrJYYlAfgYfD4Kaz3x2G8XLq33ZG0+Cm+36FXKPbmtwYOwAJ9tV+kFxjx+j6gNi8FmK4cWeAz0HUHfvLzlHWQ6O/IXAR8IOOe4DmVfV97JJXW5krnvnT6WaBysPktlM/3O9qpZpUXT1ONvm07vUELde4R1jE15G/3CJXfXG1keM/7gfN4z4nXi02KVD6Lf9o+2Tmh3PM6Y1gEjqHTQCoq+bY8FfJIge77ROAdpPCbhTeBMOunJJGdxqMEvxEhED4zYGwNEdEDeyuxEOCvoupiRfTcGiIDLSwS/MezNdW7I8CLIXAx2SBR5CfbG3yGNHFUm0YtSbNOU28qFd8sHkoRn+FsvMNdbHjdmfhXAKiIXtGD9U9V2A5RsUN40ibUx4v/akNwygYMKQA9tWsElWKuKVhUAuVZrM9mPqzpeUCTE6rvr++dmjx2SLDdcAwP2g0cisHlFJmGPmzcHrbCecTrLkEM5WgEcYaGkOt3mjuBzMdJHVA5eF1pTd+2GiICuL12AHjNqOHjQBnkzB1IvLxc5xEiyuMaRURbXlJNXZH4XQKFJ4H8quciqZ6JYQYACzcIz3x/QLYKlIZ7PEkou0E3aFu6MPg2uXMZvhWpvat/dwwJZZG/jBcxbwQuqJvrYNsXK2DIg48frYVMmH6VlGMZpcYEj5sC3B0j7L2XCYw9Um0eahRwiWxeuuEu5v716IaJU1Tuvabim6mtKHBayq/1AikzfJC41aNSWujFT7K4Tah8l+K5NaB9ZvSKpBNt2m1Uo/AYOiU1FXd0VZSHh5MGRU8aJA0gjIkUa9dWoOywTomtwx8CCE6sm1F1vlNUs7KEkpFZmI3yrmZKcl3hvkS6k4/HGvD5yWpD/+oQEiwnFIQNgUIp34/mG5y+1gJgqKEot0HNDvgtUASIY0uV8klyb9eEtwkvVxCOAtyCfPVrB9EuaSlH8fXmJ+eWhiNxle5naq8yuVI+iVMV6iYUsc71keRJwEYr/11sCmg8YNwfOxyVQDnxdcwmOOpJzOdl2CkLDZIJLGmiEQKlH1awc0UMDli9gg05p5X8Rro0OPwGgszWlynGDOOwmGX/tQwdqQkrH7AJhl3WsyljSLmP+iBQULktQJaanyHBKQH+QnZC3AuUZzUFqMaYdNGK8WbBnjKe2jDYaOCKShtjXkwU+cJ0Ws8gmLf5ZICLDeLdRCNpovrGkG3489vr4GTQZoTLAEhQrl2moh6tNHaiIRYTunXmwKOUG4hNsTXvc1ilbAURRAb+vEkyC2W0o40q2MRl+cbiQTeeLDJ2Kj9o8pxF6FZQrQ7ELK8bhVc2oIgc/t16CGSB/GxOK4nqXwFQXTQbLuNAWS1K6FfGQ5JTrwaktzZarukGiHRSrxsU3HrKk+nRfHhYOQGLVncPTjYb7VlcfGClpeP4bUK61YfPYsUuZ24LVe7UVD7NPdtbm/yEIIXOMS6G8xUZwb94T40XXniLvmL5fyR7EhbZk8kAT/WOCl+znFyOkJUAePgL8x+i65JgeweSB3dCymNAeDqdMrNKyNPqe/bOK7EtA02jxil5IRy0ow+cgHZxI8SrnNZxr2raZ74Xw3tgij6IBQaBwCDTrUq9p6mwpmhDpjmg4ApSy+AOYE4N1ftCqyWGAzF7dGowU1fS6ZUbBnNPFd6UOxKvU3NxHozJKRVLgyqUArt81wjjUfICbxGmnezMUI4LqyCtk4SGinMK7kZ7pZafPuaWMHPdy4+hY33EKbmX34txhVr8fgxSHhEeBEXlh6xF/djGDep72MNqmXyp1ICXgP6OornNlU0vLczdfdBFpIrMdDOvIiJ9+2smhxUY1WNEGTLPB14humNZIqYN5FMwRfHbb/VP7pDxZCturxyi5RW4zsXwD1sYBQsAz+xWg7mASoqKFzBCtq2JumhYmMYru8XaB+3dnRp90gyWSXGRTbZrxJ7BD/eLs1m8zGzSZWWd5sWsXX0rTjTzZTm5GRMYl8YlAKCHXev5nYfKJYq2BgjWIehTRXpzrZUL8Zc7jbS67MgL2sHdkkpJPMVqpgJZnx6b4/dqh5r/Tsoi+1E1aePkTL2m5qUkW6aCgcOHiVOVFAxbl/KF+Bap8O8dIGPRj0p8uP6mI8KYxawXk6FlJ9qh/c5rVLymkztTE9Ty20LB1KPs32S+P1poEvPsptoeuov46CjHgqrGyVLhJAXCtsKRoto1lktl0E0gP22PHd3y0BtoTvaojvzZCJAZzVtXaIhFEXzw40u8zUrJYx7Jg72HXubDO9tpYxUSVQfN4ykQnk2bqA6fHWrv7ria7P6a5OVMcl8k6mbHyGeV+phU/VFcQ9IWQJXKfHyok9XQwJtbQkSi75B3BtsHqki2HIBiFrV8pf4PJ4s4qSkli3zzMh7iYVMiApFT4r57X3RrzjPDKttgT8ZDNQCa0fF0GjRfsFWhDybw1KT23CE4FTf38+sC83G3cwbczoB1NB3czKTIEgeqYDltcp0yGjkRb3chCnbzb5kp7mJgrZVSmfxIxUwRBWPCfNSVVQFtyarP2JCWSbC1JbBGrtNYX+8Xx8g2K/xY7uptEMCWz9EmjGrqRuzqJtE6LfIoyvUCYZyr+Z9oMi7rKJpiViXB0CqyFofJqmrDv/F12l5bTz5gk2/RfzjnXefKTCL0gz5jJryE43731k15KpQjnCtlfbOY4lCVbrsAtOmlldDNC06KBMN6A3idAW0gI2CctSCNcYfi/WbAf4YY6ngncToybCk2nK3T4bwQQqnsRGvZpip202BNJUMTPXlAkOYlZd+gXNhlZjIyyyitPBV7BRVu2cFES4yh6WewS1JOBud7EnXLTKYS0cuWHfDobczGcK1S3wPIvLAgvmVP8Bojg9LA0a+OPZ2QP92Tl/C6WvM7lB//P1/O9lboiDlRzGyslEp7OEx1Yd3pGKYnDpbDP0pJSNBS2boZ8nKh2rvuVFL/2f85vOv88+/RsC2VUT+VH/zBt5g+LVm9Bcea0ESO0iKpDRnfO8Y0FjGeIwN1/j8T8aBrdf3fO8JaGCcoCLPGq3mXMiyN08MQ6S/evnSu6y5zqEDcuvuE8VtHjjuUc8xfviav2T/NXvdtFzkX3tr73QDmcuIPMs9eL7edZtHNn4O2uRdtj71sK+LzHPvtZ9M6tCrLiJrvXdo7za7Uc2Dze/5vOY2bPzd3+9uoyCBI5kRdbdZO4wrPy1iboyq9TzPtUXOy173zvodWlne+nl71z104AqxFFkGQTi1LEpu23vW/Hmz1rTt500nCmLv8qAHrIosGtLSo/K1wy4+1KfBfJxMTubdZc2jqmxKBPrDuc9y4YOCfVh1PYj1zo9nnnXj3NoSTh+9RtpA6B12w1MkhLWavfnoWR9PTlz7d5b18fT09NB+3rhx3W+w6/3Os6xbJIX2M9d+fpMC6aPeThR/E669IZqR7948uDZeRJF/aw3tOhl2rQY6eTmsuT3P7fKkwXPFc7X+oCsn2Ix3d+2NSnyPxPcnkQRA9z19iy7f97zxzKJfhyphX8L3u26az6ZPv/Pwd9ftocPUEBXAr9O0q6c5it8EABapxB2sD1sbCl7rM39pWUhs2Nxh8alvLEYGlVBoNvL6v4uw/4ajxMJo68tVPKFxUw0o9sqHA6M1cEJUFF2G6CJ6NXBGdqlPaqEYM/8qsIhm8YpRne3fJkAXBm99FC1mFkH7ArlezWmxRpZdD/hJFLW7XJYAiqUKkPKrgvEak7A+8Q66a4KuaABWds/SUBqLzVrbe0d2Dcv1ct17/sPX+Gs/PyLQu81d7pCE/vOjEw/l7Q21te7ydtiFyxi1idxPkSyXjzFfYZfUxkWwfHntFRtGgbRpmAG5cTIH9sMEi6an1wBuw7PW8C9CX2gOM+xCAkTLFOOprJgfyq7wW0DfoGqstgPPLnrQB+fAC0y8q/nse6ecCV/srHDD4UFAcYF6xLCeH9W4UYmjou6GY+WSvzqy8f/8BGHj8Ro3r152tXwnqk7aln7Hn39HK9amSpHkqEoywBKk8otNqw/LzjuymUj0NSIh1t8RL7y+1weF+ESFLsPd970uVSpACCPzVmtt3vfUFMFfWE2bE901s8489ub9WnT91bzvxNNcruu9ed+mFekxjbFgY3KYNctmnjp6VcRqMcJ5X9CTFAoedzpmynnlXO3G01ow3bWQMz5rdFzMytUu5VFgEQWDwcBjAkH0gckD4T0VsimvWuaiX+KV0lEYTssWStt5AIE5THtfmBKu4rLRy+YFkBf1phSk77y3xWYUPvU8HsKnT+9PPXQHNcspAX1BozksEDtSEIk9CRu6TkI2osEOZdo6ROsyEk5pkoqP/Gkc2LYzmv/5hXN9CpK/4j3KGdKY0KnL297lTc+DK89cPibRKlArMw8uqlvMMNVjHTihE37VxA6N2eCU0DnIUvQpGBErG6W7o6p2eOvV2t3h7YlHf1Fx+uGGP9zwhxsNpwS2knqSH8CQWcMb28lebgGtmxvvZneItm69293hLWHPzQ1I0bNnNzc8iGfPbm/5/faW323u/Q2VcIaY5OazZ/QDirRVgOABQDnawpYknpljaGsJLUck5SAO0q54Gl6AVXD1lzr+5alB9o23Yy7NlN0KCczPnr1naH/6pL+nhWqu+qIlqTI2icvhHLMta9WnpcnT0ixPS5OnpSmmheHmL4H9BG88vMfDrfOISXpKfJ1oOIcos8SbAUNkj9SsW+7JScv+NBOsDFiHYYG4ug2GHX2y8EcyV3jCXnNM7NV+69Du5mrtg9UaIiOAh3w2CPo+rMvO2Au9U6x6tUmho40igESb3j63yTA4wloYW6EtF8IRGOyxdZC9HuH1UL0e8mu6g+n1HtNYtHrddi3k3GFVburFUZaZ0c+9r8BRofojgbLu/m6YL6J/PXKIJKjJkgg8S4gGpztCCNQo7AnsECH4alc4qZ568qFGskKGyiKn5x3Y4mm/2HEsnATV048gQvRUWirN3BJR03zjiSbfOytwWaKtXdd+1rRpETi33mp5JgFHtXboTzetg1goRRmfPcMoT4jmK9bL1iioZeHLJXIAcVo9/LEOaxZen2HaUzwKadVIyqgQX0d//B16l5JMWje7t7agpo5Mus2/3nzV0l9FgXyStrvf7LXsXe39dg/CUKHC52hhl/4WKs7SCyUs2cvcx16eAi6nt7yo1XTdAhKC8HZ16kIYJOhzl2hLHvQEmctZj1u1M6g/TR/VliU502DuT5NbjzZHhRFC0Gs45LRfXtOFTglJdzXXZKZC/4gjSFu3qVJMLW01p6DCWQ89Tz1DGIM8tZqLbFS35+3by12v1Q2wUxsi8ZSSgCOcJDqw3Rb6WuxJua+3eNZHo/dVdQn9oZ7/ZbqUgQ+rvXpW8UHbygdeNnVoZqABCnIkJlwl7LoSA3IJ+CP6uc0R9WQhSM5zHjoyWJkeINt/MFfPmw0orpLnIP97+LWxU+JZIYWUmJY5msfsehCDEjn9pecGx3l6N8NAZyDHMxojI70FL3kilDNbcrZLT+KlxSzt8qQPwQ11Lbtc76y7TcuJYYlX+ihqEk9Psi5uaJzEXHIft7owC61rWZb94GUyLnXh6QcpHZqm7OMMLBfv9R6SnpSn+EP9joUrP8il+6GurY1d793rLzc3u7Ot8+XmFj8Td+2CE/n4Tl+zc09Usdt8PtPHaLw7wVgMOnf59eLG2yEN+5eb+Zb/7BhwwloGMHcQDxbSeU5o2uLlq+E4iHeMm9kU4s7OJEmWnb296+vr+nWrvojGe81Go7GHaqGhI92aIY5w7ogqhYZavREzjcOZUPTu7EFpCCwCcPBtmH1DZfSNKjx9p2ZCzhAB3MEHzNDWxsQ/KegAXy+E9m8F5BUHKzvQ1mA0pKUN4ziABhAcJo6R4gFK2Pkco6xU+v3w9uLVi9fnHriYH96++fHnH74599rOT6/eiBcoHZ7QdJ1feEIVwNpP41UUGUAHwI+fF5FYoNFqgMOk1iweO/FiBCyKVzAz0jvMipMwruPJwz/xQlm8p0/ph2iDXOJTKKq9hXf61+c//lBf0plaix9RO8YAi421IJYjRdkhjk6tpsl5AoWo0FoqLIerB0rEnQ2fNO2YP6zChEAmDqCS6vSHxef/MTUdfzBYYbF3TPeo02iYDjte8VuL3qY4e9fcd5b+CibX9r7DIGClL9TOUAvOwpjcfLcO418S+DDAVEheEtIQvt6yfsn8/IcPqxCni01It+AubIdV3LKspWZDCmYEfch0NKcYEYkY2wwGcxghIDF8DKDKy/S2fS8PG8IxWr7DT5+eiv6FsVQA1rnX4Pvlk+RWwH/IXit9UJ8qGdYVbL0f+++xEuoACOQVa7N1+uk3J8v26dNmmzZfbFqMmtsWj3rjEgbqk9eXD6IbAhyeeqBmuikCGEOCkQAFFEjh8Bw68cCzfKef6Q5nN5l0SB+cmVQUk16IEqTa1kJGSB9H2KXnJ557QCKSSDqmJHo4TNOaDZV2lKVBhLJE4vGnT/zQbNiszpJiNvVuSDwPnHf9p7zcUE097j9VS0+yezCxBUngRVBRqmxRHWaeCJI8V2KrvBhE7MXpYJfeOS8iK7ZZN51YZse0nYnHy+y7OfRS0GtAyw8w6GkupzHptyYsA09Omm10jp9nJwcYSDIhYyLpFJgeWOZk0pnNzFTtPXl+0NidZcNdXqmZ8E/6Z/6uWTN3+50+//qgd9mWlPhzsurEukkCG98jVpi1IWTuhA6ZoXCOvOFcAyD4WY7oj48/i+Wyc9nbCiEm0xtH8N2C5vj8QmHnJlWO4hPWj5oFC6+aUGyATE8DI6MQgIjRX6zGgfFhZa7wMlqEMWIICGptIEf4+Z8jkTX2wzgMiDSrHVTOInWF2tHEn6diprHrlyRyyUHDDHE5q/vQwYqnfk9lgEqQ4QH2rJ89Zh9Hux6hYBePPj/2Kd8oe/RlhrQIoCh0WmgGSjb93U/FQ2InUYrQu2/7dZoKNKtYRkplzLf76lMq6WxzcxMTOGLaXOr91WDixdwcgLGCxhC8/oJkkl2MedHjmhzSNNWH4WiErMtRDX98ZpVEdWxG9C7rdewwPexJUWIpMeWWy9du+IdW8i23iAT6EQlULxLoRyQs6XXJLzdMTGu3/CNQTLR5FdzSsozFSE3H3BVjkY9UmXxcjjSCxl0Vho5YIjjswFcd7B4OY3rMLSl0j+XkCqwXjTnUTEe05lA7HdEcLQlqTe5hYZCWJslENIx9CNZYC3sz+o9dGCSMHmLblhT71HXITLvsaAJjuNe2eXltmYd5sQRdCSW+M6cCzmWGzXcKfiYwPv8qtkQYybDsk4DjXCAdC2YWBqsbsbI+/8rLKUAhY276UL/HBllTIio45yKUBaoc4o4MP4p4kUG7Srw4zNY2LbKUwiz9MLqgXc/icUrw8WqjlSYGr+xWyqqYWR89znApBNhMbQJLxoleVChBdRORLBjKhUnMPbdcn/ixtbxi8lhc3pI8EecvKo+liTG0lTJbT5d8BUxR2SCpsBpj2jISsd8ykyGHeInmez1VKb7beR5Vmoa2Gqnur+Cq9Ve8FYteaBSbPOO8lJ7K7UpRUW1pMK8Gy4F5EYDAw/TuGn/8/d8ZP2HfGoRLf4pZRQAWachu21glKmOTM75ELYsp447MuU85j/ScLc55Trwpt7pQWY8pq9u0TW1+GaPJlOHQWiNhQfFngjHS2DMdAcaQb8Ynre64MOshmBiCxdllg8zlTqvHCxr6Q4EN7efj3bAnKEbnkqp18n96eXvBMGDd4wa+ZUNYfXoOH/rrmG8wIOIsuT5gQcHOMPCuUrZgTfMiOKjLMW/AVz21ba/PLtfEE6zBBPS0/hRUJzPs5leiaUfnry5j34n7PS8eWFeKFdiojImYjs4Y5AuFHM4LZPWHtx2/nijepq8e8WnUuTRHpjN2rnrbfA9A3Dxr5kxtwT8JXD4DWLikAMp028m2oDPsTR3er7Rapos4+JOr6XeybU4i+8j1ZleWiV+g3TeQEGpCGgPaWi6wbh0b7QAoSfMHnaj4bdmFSpqykmahkqZhNQOqo5XW4co6mvk6liOuYgmYmT8FWFuBFAsNqxWQYDigGmjUFvpKeaIh1o7xjQu+UCY3teSmma9/FHL9VD2v+8CkzUbU9Qvm9sOKxFSuTaQ3c+lZdSBBozDle+2NXGu0HHoeFR2Fjmna9aSrfYE+x+NOph9TG/ZyVF3ZblNUh52uXF1LVpd+FNUJCiAYms3YEdKkoFOX454zo6hHQdy5pFHTCFF8hIXYv/23wW1no6fCm2zrYJ1uC7R0I5pQFGZbQVbP0cZwNQ0skVXnhWn5pkIXSaseGAf6FSIrvfEDC670lrGnUnqlRPEkZF+PBAcLldCLRpxxCtG73KCLw44ZzkcLU1GbF0KCNkjbhe0dODZWYrSsSsrYtgOdQYe/ZIDrOUQRO2x73DJ9IwoKNzOPM+pklXwjohMlF3ajAnUFl5xtMpdRr+hHAXsAVP5rTeUv6VdmqxbbIbhtVYqsCAkoeZLpIUN4DbV2MQIPGWkDnyn0UDQtIZoGzQORBgUkE9KxSOprSTFRISZ99NuXRC4yncgJIZikukrAXrYh4M9jNB3pDIvmFOFnwQKUH2n2rslb3S/+eMVpcMCy5bwAvDwX+N1lZFHTMYvFdKRaANZNqy07J5+mu4pBs7XrUT26fY4gyc5Ym2Lvc9jzE2EnlgL4OLOidwJ5q7GFz77uepylq2SFext7mclmQSKmP0xWUpUUi8UeVPaDls2d3XgiQUCZcrLkpdzueovR5WV5R4gLW0LPuSxT/DhP8imPRtJjperTiTrlychybPZ6uYWiIXwlx6Isq54gN6BzdaZnl1cVyM4beGdEqN6nH9rK6Vdg9UhDa7V3K7QuzhQPRE7Vn4Cn96FmDjEfxI43TAUZE5ZReFOFBpJQ3oMISlxbJUzIWe6J4JVDYfYg7iBSIPY/gyswAhIh+OPnXyGJRAYpCZQYhL+kQHi/QHYScmAJ4H14AMEI+eeBvzKsA5U9hvc0raIF1Ds09B/n4ss07JMIBVlpMaOnoemr3sTcpGquS+zv51/HUJYln391IFNJzHIMEpPQ4ojlKOrikJEybXnIMtpygR2KmqaO+wnph2mdodbB5/+FKllhLZnwLtX5+dc18SRYvTHHBoQUv5jPsRqmWR+peBEo0OujXjUQiDvU6M/zDCpzkwGbQN/VX6FhAviHFTRJpDCHkhxdZvjjcTFnMjBHcoeghCpiKE39hOdm+PlX9BibWAi3TqIY6AkmcD7mcS6nKJWpdVBrChGuktYktsW0DPcDQ6WcfiYKx/LzPLHrOdFU6FXfULi+IIjl3u9QJDJd0TuYJ5VCCenxIGLf9Q2Uqrpc7dhmc04cCpOnpnuZsvIlbZ9JfDyt00oCoRdrqSCyxqHS5bDealqXK0fuLlCmaWnaStZEAJAU9VItEJM4S6IZ6R/PA3Lt1OpUXllkTpYZ6/AUt7gJOPnlkvqUlBeWrv0wYQVRAVZQfkAp2VN6kcQ7farqIgkeXp0OdqWh1qkqxV7W0QJPMlkgWJwGW0Ebz1RtkjDP6nJBwTJbB2tpdzKXTc38yOJLP84skHo/EuoHjVJzhMBcUefVSIpKRk2QBPZdJj0YQhs1wjZ6Pti1qPfPnj2lH1nHWbvRadi7FqEdMmFIcVhzz1yRaiW7cfh83/5KgXcPFeZ8KuLBSR8wwiDigbB9JgWvCM7GXwSqFDvNA6JpFiZR6jg99YCf3Cl+Qa+6PA7xlvZhRmckPUrU+MTS9NhV0yJ2TsT+CEaXTehU8hVtn9w1G7Re9EmQ4BXLSdPEYCC80ci1AJr5czRlNwYKnYLaKM4r0ROoeKCEHhJ/HgzNM5UM42aIQxm76TvZKynobIfMuXk55BdYVOGnfc2oQlbB1PTEljv6xJFhdXWnULFqinynKPB4ZdWRoHJepfDjAIIvwfgm3n0EMtuKNyq/Iw9CdKib8tlJDYW6HCXMeEjhB6EWlfa5TItFmpuItC/BDbYHHIeWigqpgI3OUqWpNMxImgfDA/wH/GkntbM6ShXWySwLpDcVDaeg6wgNpTQDSsGUejGmXow747qST8d1/k3ZlLGiMmmlXMlbOQMd+Su0y4nULjMvKdTLVCyW09DhB+wf87c4e9WRCGfZW6Xl1QzNLxh3sA2SW0L4AXsx26gj4A4s09AAg8uIgjHAF/En8Bx9HEstnlDRlLUwS7Elz0pVtMNUUwMfTDCbOUVm6sIuCZbv/cCxqrgUxtTX3vvKSClqhDcDWSWpQn58KnLCdgm7WDCmafXtyuQ+kmP/pIG/ff7rnx4f0wt+8qYyy+TB4Bge2yiDuqn6wD1ATYXsP88l55iGUib2YhmsEmYRMathxAAWPJNk5rJqnw5pQxwQcc6sohaz6vZdXZv4YLNWAZSvopPEKblHtQarS49q7oFjuMc1eCwb8JBxj/Dj1txj/oGRs25mzoBSuSzUgpl9FioZcH0/jpT5U+rd6E9BZVdn+Zk2aY1LGiQ6RqQ6ci+HLOnUKootJOi8/sDbhanZCeln5lRrE6QRsACrnZcUWUKa9QpGCbCQYEHH4twWsLy+k+MvUi0C1TwrzsGbAIvmvyclDEnZBD8WdFPZ4pktSTW6qW0GDkjBiAzgGh3m1c6GKNY31ylKo2JTsIx/nqsBEScMcglIgD8k28rw8z/HzMyC64cdZ80Kd8qVjdKwFiuVT5g+heaRckGiQQ6HBIaIqgBRm7ONBvzv90AveNv44Lj5jBuJPSs6xMhn2kKsr7qykQp0pswwrluZXoj8lbWJg55QMo8wypFCQs+Xws8uob9QpeTG3ZEDxmg15xufxIT3JOYsZuDnB1hvxi+L2+AjFmFuLGLA6TjMnAHGk3RrwyuAyRZhvXhiRzrxBVnJ2sTf6JlOUKlq0tEAIE/vNLeAEj2EBGAVBL7YdopLnnCv2Cqb7bDI/OhLaUxrCMI+vDOunBIHkC0la8xeBGPy1f70VGlIhAqElRwjE4ztfDBdge7AivCnrg/oMMrMRb1CrVE2hYFEjohrg0Gi2Or3uqgHJBkoeR54zhKltvylJFjo12I69BTZs0Yz2yGjsDS/VGHFMKCpMzJTDfL3hPk8n+ZdCgRxBG5kA7uimSLwfvokH5tmQeaYX2d9ehTUdOv+/Bpww7DsTamvNC5MJk4kVX2hD5lfs0CvR82y5gIVT1YjHCC2fFs7Uean5xdwrEyeoxQDfa8fYeJHMEBD+JLYz4XRtHvpkzXNx+kEQJR+HEropecAyYdA34F+E8zz+w9vJWrTtSLG8oxE3UFsymxAROrXzN9EI2vkG1zchb5XniWkrQEdIv1LILUhhJJClyEoGfubQBf6MdOJMJsak2KFjlfLfQqd0HdBJZTnEuE4MQsUl/vpU0Z5hB2adNEiyw2cM8qUVt88U2I6zDqEnWSVbkbZfkNctwKVOIeHmC4KbnxeRadI8PKVSHK3ME/BdlDHHWe/UnadjfmcU6gSL5PL5nOgC/9guxHrQtBsfc0XyWCB9krBoUpjoJ215SMLBS1CNhfv4eMs3AhI0oUbAallyc6pzj7y+O7wecg8ETiXJD0FHHuxGmBb83VPDkQjAMOFWYFgoLBtAdGsPxXn0sNRCDSbZlo3TC/5dEBAtgvcEC6nWMuNxjDy2J6dr5uxgLKhvOzk5OU8TnC8Sn7pl79sdThIf5+l84HkHS5ELnC9XflIM1kT6R+y9A+cntrw9HXgiWpZimIPCpajhHVb2JChEadf6XKW31vzFOX8GrWUSUolW1rNlEqigtgPOvdpaqL5zGVW13VmTX7AoXgXO3bsOnGTfpta5Zczt4ctmp+aPd6sfezPfX1/jl37jg/NR+/crOth7zbZKPErWkKzTPa+m6XoNjRB+FibGoHGrYRVR2JdSlqQzDVK3JP0Ybb0ZIuXMZgq7dmTDV/GTZkunj2UeWgaxTLL/ImK/q+kaBHur/xUdr0tgM1tkiI/lvr1leIrlKrCU/UwDs55oUi3T6w1PGCPk1S54bToFGDJEbmEiFIpkkPGnNk5ryW+AkUCCgiLLxCBbShmj/RZV5hsA9XQJURsGR4yE5FdHVQY7LfsFqYQxLAo3Ao0899+23n92qaRb8H04CgqMXDbotlt4UxCYXYj+4/p7DvHDbadkbXQRFQG94jfM3s4JR5wmrDycKYmFr7ed41YrVPlQcYLEWNMfbpLZ7AuLYRvViwvlRhYimVxMl18+rQ+nYR3FJosICBNwxnZAdOCDJO1ok+oxmRlkCkGEAvVkHIGHorXEm4cEG7IvEWMeBNg5nUFzPXEp9N4Js6zmRAYip7nvBGmNMu728O9m1tJ21RB8OLlxXc//nDubXjZdpTE78Bm8laYwAUL5sTXFJNZEE+pxFNrMFP0aThNXDJCS6kxbbtlBdaAZFh4i/mkmDIsCo5OSLlc9UmhBSkWBAdBvTgN1jREnRFw6oq4LGX5j/bBYbTAMX1SDfAiro7I8vKvfuNtSMVmmiQedEy+sMtMnai//eaNtzH9ZYiPZge5iY1xzJcipFXtAtpfeHiz5k1odvfeQzih8pi0vd8Ft3+9B6IRJ5Ysatuosf5ilQCrwo9cwjO/DnCRRwTiIDOlDuvTACFTQHD4JPlPcMTGgiF1KMB4gfjwMH9akYNTBUBKP76dD7RjRn2LVMzwvhYmB0C8Bb0AMaSkAERcOpapIGwQUMkgRzY9UieYEMYJjriXZk2/XeZqeY+DjmAqKhFQJoZR5m7f3AiVAXFRSMt7ahJn19LcM4k25aSiyPNJH2+MAiJSBAbMyS6PoHD+QUQNijsAozMApwIN+nyBQL5AVbh6YLh8EkIXmiJysklW8am334CiUL1iLbWbx/YGnfU0p/pvLy5+wkyoXAhuyB3jqbBajYYSXlLLh2YYeRrhxpmyn36pyvxxNtFAVCfEUfxoRq2z2vd+xxW1JUJJ2hIgqCRmZBykLH9qjKGRBXf1P+f6LQvStG2LmMRT8otQ5FtKuPPlfAHNzD1yd91bu3tSV/OWhhmcIdpS8KHuPhN3HXjSFGCKQw5KbCwDaw3ynJ1p8CkKhCzare7am8X1v75bHJ7kz+hbV1HPaDnwLOIKYDgZx2AIcl3A1z1zlz9vcN/gZAGniJ9+PL8wHYqO1SmcvuIaiImWCkJfjNajmwdD8jMA/0XG82kgrOMkh5KnGZn0hQkA4gZeUrV/QKsYNnF8mLKmEGyaEBmgNA3I/ZvDysXshIBzd0LFFrASsABy9EUMkzqu8SoUCkNsIJf0WWhaR3NpIaBFhnhmVfzoVqcUxHDNluQOJp9ODtRT0Q1tca2TDEYCJdA8YDET5Gc0t3gIGmOELlPPSHgckE0Ps57vf1BX5+7wSD/b7iPGt827lctuAyUsM8bNGQIvTWezfBvcLIGTZNbSbGfLt3y/JIw5y7dLuALh36dPQr7RlVjQfIA9AfmRPVpcdcgk4HDtncywuEntc8iuYz9a2NrbcpXo+AibG7YRnZLgqFFep9NsN0pEMQecrEZ+J674VYqgLOOGqYgBewbiEE46T59mpSjB3ha8OiXcL6LFkrYogdRiI4ZmI5yRlwnpYoDabPyKIYN/ZKQrm9GyPbySU/iSzpOkV3XSGrs9ZxoC3I3T82ABzPVxKg7E0spimh2YCeA4RNY+a+/y2cnpjtnbGzsDkl3NZ2AhnuFeqy44+RN6nib0eEqPY37coccPqwW97Jg7ePmiddw1t5cDlpKlnWLG5/kRa8OafeW2MSG7/JefFdWSPdNk9tkenS6DRXp4TlKEBQfihgm/xo65KzPPvkKOYgZyDgcEX5cYMHbxYb6MbRoQiQWhIc4NXxRfYSkujlxzgsEVIbexZ2RLQhoqyDWLTBRzUyl9p3gaE7l4A+PblHysmFJRyo9vfvPCYz8xBZSLF1+fv/36xfkrD0IK+UoAmtKXlj34pM0Wqa9ZguVEMtUiJXNkFM5+zDXnPP5UKxSD8HtgMrsEpE2qox3UqzM07w8hkKF82m+TPP5JquEDwMKyjaqqb4018cWkZSNGAXDdkQ9fOB8WETUo4OHMbu+qFpy7zE+sPZDak674cYJ930P0wcWcAj1zDCKHPOTIESgH5fnM44MSp/RXORKdnQt5+VIk9joWP7AfIMnEvyddAVtTSaoq7jSgBYngYYlOO4ur1zjjnG04fGMvfVbnLPfgT75cLK1UVUlhAInSZzQ3v3npIjFFhbSIq59D40mNwx1/pe31wkD0RFFGScJkuSyhKz8zrdpoyEiTBU+P3ASA6uGeG23KuuK0vKVFwqNIhqR58DjYIa2KrpqW85QvSouhdQEm0S/xrEdFBNVjf2uER1ZgFlkTxUEF3peWKWKUokOYNZxBl8IOnIEC4dhOmM66T5MZusEU8ouSRxKKbw09cCah0JLQC4pxi7IIc9ngoFTl2Ye8mgq/iuquoU7vw9syuWWxl8ThSTiEBt6U255UbkkBos6hWmFoMd++NW2hrabhgUsCsrAV5tuL19975kksA3nKyKMUiRghCCatU4x9FI5XkS8jEc7JxTEJEL20VYxU+mIIEMfswTiAJTOTZ+fMVSG+MgQY9sAYkjKXnDkJDURMU9mBU1NOF097KiYpVYjG8aQceVdbnJnN7xwqDSi4JLKo2a3kms69vNtRimEaF6Kh5pOSdCI7IAlC2gP7Twe1XH0ZI1AFZ10TSZ67mGThfKt2lsxsDBux2H6gGl8vEmkplI1Q4Ns5JqurpkKxCDghjPIJVQhXnNIESQ5kiOB937IwarE6L0VSLIxXZEwnZA8wbpIbFNoKtanJ0eE2D2A2J0GlZIu1wGp1qRdYj72ld1oRgKPZxv934O4c+jWxMhDyFoixc/rlZrlNI2GIar57+eMPHk0hbSgdCkxipnE0XrcM150e145wYu9ID7Dxeh9xtNduY+K2f3EbuS8u2m+saweT9voAH0z2glLeUaL6QRgNiDtAd90m7li/Fb+Rt3Ocr6pptAZuHQK70ea/DeO4Jp7cJv3kcrfEh8aAc9REuWP6K0sY+6UyLn83jga1tsGlDvm9VTsS6bKAGASfARYj4LAk6H5rx5CdlzFK9rMAJQwwlZHb4cz7VXndfT2zeyCqrcy6n/ZHeqcVpuwI3kCToyIc3cN1O5d2aLQnmMJ9fx8HNzkuOqL/Go2PhUwH3+KeEyiNGvxfy8hX4iLDpJVmcGsig+gesx3F3rWNw0kRYY6Q1qQkHS8OBF4cMlo0cwXaGM2kWUQ6V1Ws1XIkkSurRaLjYlHqWdM13JZ/DExHXQwNAsgh/hNjpyYYPKKKeDV/EJvbxVlorpv808Av5qQ5wU9D/Lbrx4zm+DvF3UqEsPQXIK4f0gv/5L6IEsBgV32o5Yoc1Fv5D9z3J6lSM4y/oWBbVhakAzFBFSVSD6+mgXiHbIjdvM5XaytmIjljXTSFbDJJSoNLA65cEw6Qr3HzHLyFsmfLJPse/EfjWu6eb4OK26ademeTSJFpGijI0gVlTNU7M+8O+cuEUsVnxYPH3RTt9IRCZ2bP6vIKAk+M3LLPTHkjO6ScL9x286jdN3Vvg2QxhoSRb32ulebrwVGWAdB9HOy8ObOjOR4wTplwymE6c50r3ea2GLp9g24efzRUy/uQvvvodeca1eL+aFlom9BnhHZB2t8Ryz23v7+jSOunJ33sNxCFrXPIAMomUJdBgi6kS1fqXWna2Jn6pyd89c/pm1yQJeP//m+i36kjEF5b6oBLjP2Mi4ho7hzjXTIKE4owr72T/L4RfMqZuQDOmlcLc0u7okpE0h//y39Wxp7xHNpkWa24ClrVhKuIdziUcA3SBL0CHHLDZcGGQlBleMLSMUpCxOmIl5hPCIm203y0E9eJrvAD0SiCCLcrB/cuZx+imbmgmGk8L8yx4y03EUoilR4QCbELciTcexIz0dUESkwEzJKDw7tPrriUekYMOp2fpJ5Svy4ptUdy4vaE7mI6pdJuj7gKeks7/E46uJmmnVOzYBLBFsvDOFAxrsAEl72P6WJSOB/kTt8sveqAPXTkzWOnf9liRze8X+Eir7l31ymXLN/An5MpyyNx7dmzYAhfoCVlpbMEDTYyRqbm3Xz9wnv35UZ8xug76rmJZ/8dROiv7/7ef5dvlsMl8W4pGuYua+fbuCJGq7N3OjrPpjtygcnPtkTWdzRhuZwAJ5YCzVCKwQEWxwXVLNeRmsF3xLvvvstnnmHhMDiUh7B5zViBZKUtgA/19YszExp1gS/4JGF69k5er0qohUzbHe6g7Pt8xtFr7PvajweyNgLVmUmXmuYa4WTRCiEDmsFP1gx68CW7dG75lC4/97fvOlZW5Tn5aNHyXMem/QAoohQYIpLOHcD4+jHA+LoCGP0iMCw+EyPVKfnu0H1kX26Uho6ykYQ7uz3DZijXrTgSSY5oGUGWKhku0JOEV7aIQjbGXEFvcCjzHPZ9kBulRayrkwpkSx4KBytyVX2qjqhhFcV8WZet76vkJfA1lC841pN6a5TOq0lZ/l1B7gPQpgXP8jPzhX7ET/MITZ1xYLLv6KomCHWwCeRDSNWJ1i9FiEA5QK1TRD7JaV4QJhm+O0fiMoMUesdqRGiBRsJNUj/Vl0HNvvuIGkdqypE0jJeqU4ELEYBgW9BLZTRWhQmoIKy3X1MI9VSpAn0g+U+oQJOla1cWynVRCM7qbCgbftcLAHLx+f+QrkOc+VyTfyOpaj+yvKwRTMRKmN3CDAGFVeqWpyENoSPtOOI8JC58T6nzPdDb3HsmUjGL+gFFag+TKE4kUnuIEEebATcNXLWqdxhbcpAb6hjwz5lt9csc2GYV/bk9hu+HuM/uUV0Xp+PQ3Uf0Fn0qdxY48j0sh2s6v8v2FmU/XEYLciq0hHs1fADSg8E2q/ADOpkMZx129xqTxQcrbc6HgLOjxtPUa1T4F0QcWmqGO46SQJ4mkBrGtXT9RFf9yA7W6qh4h84aUzDIjk/BlZwZ/c7SqIaYgVxm9JYzI13kpgeZHfn0MGM3yCAibSBSmHrUOIXrycILSEnJTtvUi7N3vxBCy8PPHzP6CTINK6DctfqnKnpW8Xtffn/XefeyOodEwzPO3dHr1HiEfjimjuX2/uXcuKqhqvoVc2ay0wSNMzOfb7Jz+tObH19+++K7H4zXLy5efitIu1nkEXBddZ5bxjXNO4odv3j15g0qSFltHkZd5x36Ffw3LmkucB24YlnrLsPYfPHm6+8u3rz4zStijqmDZspM5uoaUskJwS2dvG1VmylXxBlzjFHub67QNRUCBkD4yeXVpoGHXpqIWJ+I/Id/LfhiBl8uYVKa7PzcAoQZOLdVVVZCUTLyZaBJnl5VUw0jDVJECicyODEZ0tdqMxc64smuB2RGMljqzG4dUNArG98YOvI1UyHPb5JSFJkx9pHckRsK0llPz92cmb/wdsU0jSiTPMn3+VeyW5FqWIsc2REb2fS3yqAoDXvEMlRWAw2zLw6b5I5nFZ3mc4e06qbyx8E4iwiEK4ZpVjCsrQbLzDFHnQPK8VviuGuJ47JVhFL6wtsKQTZHEzAFYP2l/K0OKhj/8o//6Q+SNHRzbd4D57Tq078EvIut31/5nzULWhO0FWMXhSlKxV+0S1OTjMUCFCuWrFZQAW/lok4TKPIOhBKSHlhfoNQRfUH7TjMDcnlBqYopZuQ2K/ILXC0ApCD9dooWYkGz76xDjEOrhZlQ7VNWiTgYWPkpX3+Gjiq+bI7Vjb5dzAI9YCwFk0rlhK5ODhi41WYfJjfEN4HtvCVWcOf09WKumM2TPf6OMbGiT9zrJ7OdwNWP6oOfzSrwdnZO//j7vzcE1xpB1vv7kz2RAQCSMo9+8PpdoTh0MSyqSXEqVKKUaBgn+TVJjTcfWbmm6yDwcW5BdvkaRHQ3d5Usr3XFh6eUVJmW3knkBBQzqvnuboOZTrxRpki787JrnyZI7gCUOd1G5ZyjPhKwpHhGXdgWepbGV/Q0aqQsrFTAmd/on7L4mHfJiBmpn9/Yjx/r/OaBocphIt/9o0SrxUGWDhTh9kwMKneSP/PttxU1pjNXafyU7iPm7g4izP1Dk3LzzGt9xEWeOzIHY/ONxGaxQ1+a//KP//Vv4WCCn/8ofv5g9nCmbnvSjwoKAHS3l2qNclic6ZEKoHny0KB+kmHw5Tg0XOBDWNMiJzs1WKbnYJ0m/YWbFGlQgExnJv5INUZ+euXk6pxghgRykGVGRq+CLm1+XMtaJjVReka1L5WpZ5EuaGDMTLh/86ZOdqTzugzzYD9ALOUtsRiMuCb29F/+8e/+p/ETgODTUZwBxT0i1wT1OS/SK4pUuvx15/R8QOLcR6pBXXUKKTA7vAi/Uunb0GFjuDaHH5im0D0KZZYTQ9pJsU6NMeMf1Wjy4MH42V3qHjQru5yVp5cmbeeUPGdH+uIvaDlYyFuSX/vH9Mg4nx2QNz0sRSjkmA8gyBNPQ/1cckARG9cRMTVlpzSGVd56gPu4wb4MdAsCbQY7p3+DA+8JN27MisPTTAEpqJjEdB6NKfKIRb7WFE/4gmreXeGHtGNQSBs8okK60XlH3F9NvfJ25jBvRSH6z56MExxFhp/Izstij3f4luk0jv7OApd03LUjliGkQ2c1F/D5BooLFSUg0CFyBxrpPEumHRMufhXKMRxy+TqZ4zBFFOh2BxxF/PHK43OuOHGbOyipBpctaVAckfXMIr0yIub4oXBMSUKOsgZ9CWklQC0ucgkytJvgXxHItSPKA48E+xpE2WcZdbJj/ubOb4hIafmlIOC2qQfOe1eBl6Q6J45nIBXXPAlj8iDBF/UeBULHfuZ2GswxCRix/UzdUs+cEqCR2bBy2Qpr8IIJKxbg8LfiTDQvQHVMWoOMft5aKBm377L4Jjw33wNXcLgXospTYc2hkBUtRKrQA1UUXusispAKXMG5hX+FOE6NuD9pZB+Rko+CaOfuSolei5yCMy4IxaJP0lIgJKg8LP74t//BAGeACj7y4RqsIk31as0+//eZPKJtC0VsSpYyrWs+jmu7FMCVOC8vg0APOrTYu0O+5Eykft51H8XViMOwwI9dd2tU7bnUeLp01M4rt1r+JibjjJ/lxQkmvILNXU4RIZ1MsPfpfovGsplHRKczs9zwzqkeYUQWlJs2ev0u0zhofbA3PNb8BP1UYWGAqMY7lklqA8i4fPAaJwgiGWwyRxlTU4NEB8KClPgI24J0ns8YUbicTLMYe8RGbYry6jW8pncqWSDlHgvzl2lDvSLPID7EO5fZK8HX7N5pGHmanwfdRLLVj2OJRaBNsLgg86n1mEWaA5d+/6FCTrPCU696L9Ci1Jb3gwjB3a906daf3+YMGCIYA62RVIegmXajTElFos93JCQJBYoYB4ar6VKcAeJBDyh8xVk66EHUS8MMCipyz7LThjLMmBfpQSGZcbRx9q6aI+z7g6uxOOK59iOrVhu7FKRhSCPtHCxv4P20vOn2OYxBLfIhhMRi61bLfcDrndT+C/LUt7g1pZTYE2+8dLdpSFDmLW15ViDrPqt2cMqRFtF7InDCusT3UPC3NLoGE7x3pd3k+1x1Ad/Qk9UmYiKM6IxuoILEMrTkflKoDEzHUnDXpLqSiplYBlX7GmQaDNBHROxSXxj6/pB8Zn1+z+7KQEQ9UYyuAqF9GwSCOrHEGkkkq5jQ7omfCP8mp1+c7OEvPcnD4+n7L+nTX6dP1Jt6+vYNGpFve6hOMdY6AsuwGO/QnBrzGIy8CEBDQlcylOolqfpiRTUl4l9elBRGPEiTlBkXm4AE//Ef/knSV1lCVpUpu7Kq4kx9paXR9Sn5FILcaePM3OWaVYrMw8PUrbKKGgigqh0Yy5goS9U6Rsftyj35HxCx9w8yyBuRdLB1SSDo/DBFEJxnoYNSQKZEuIoPQ/LpZEFKsH+24bN1bJpFk8427YqtRhDmO5doI1uiLpboUWmFHtAKdeHdml7sISm58UDN7qNq3odrcHYTyCOrbj6qasS5a+p3h6Q70PJxXL7UKleRdRlsKRfEDrGn7rcpZDSYM1cxsYVgVVm8cBCtNPpxEEtyRh/aKZkWOVLClseKlBeVISjv2QXEopRRKe2tpPvjO7Zr3jyrtRSlZfS4rYc7KqTsR1EyWrKkJMrr1qiXNyW6pB1Xw51PLHzialC6+EijVPJDkb6kirmzkv4rZSUrSMhW0Y5H4dy5uFlsz3hB3lxVqMcfrHx4j1x0jwe3+VSzUJDjy3qNHyh6ia6ocMix0Re7l4i7QeTrIzaiRf6UnVL6SEKlxDA6sAIYC/mZDd/oLBLkUuOUrnACkeoUchog54IqtYrOjbMOpVq7Uq9Y8fdjY2ncqSaywgIgbA9lrQTTIBWwBWIJeJvUECE0JUJBQoq01HOStBapLUFaCXbA7dwIRS7OCzR28th1r9qDTkFyRI2d01faKW6CIUWmqdIIPQydbyUKEMSHHNtEwAcFBTBOL8jb4Z7BkooofssEpjDcWJGdHa5OE01SQ5qoVTooVTcSki+taETGtik1o245oYWvGcJEbWDYABgtHtGDzbCQU2pEij6qCTki1crL9GIArGi7sok5h6RJG4HBQWtDXB2zrVSsVQxKu7vj0S1y/J1ck5xyb5vFUWaU/bGtZpx3ruks+dFjLlwS8egeCNqWa10k3d9yOv4HF6UKapNbl3/ecjz3QSjHeK085XbB3tIgi9E4i/ggWRI9MKpF9MCRlNWRBDu9mtgWpHtFronQhFBg15+TcCrd+IBTdK6P7u1bsQY7AmsmNOpkSQ+EOMeXKeghYqbC0IAuAPSP1HIjtAE0nXy2LT82EUUm1mDx58Dy3y+oEpyxzA4NPtglDkvETsA0m6ORTyobjtOoRdEL5LWxGsktV4y4aaWKX0yn7GqREOTgeJqEkCBikhNueRojeZsFTZ9916CreQ2as1UViyHPaCrH2nPtUGzuKEl2fEC/ZDE9run4QXbQhkwo60AeaFFSFEJb+3ymhk5h4BUelHvf/fDTzxefzl99/+rlhQxR4+P8sD/+AcdykMESRwvkIfhPn/AxZF9IPvtsb9S5cj7Hqh2CLZw3p8tQs1MOiAdEZxfZGSENxK50sBz7vsOqHBXPXQoA4mB8R/BkW/sSXes9eIpzhE8xJjQ7vSm7ZhcOO284aHIlABGtrApQ1ZlT4NnZ6VtnvyH0aRk6gKT54iwsY2oFYizQURGjm92Ss6AtXt5hWQRtUVjDeYS7sTdS5324sfKJn3Q1+GSsyXnSTIIgkTZv6SyqHz2gAz1lm61kSvRqsnMMd5we0KxYsb9T3B0qTFgUGmGnwUwaTmkea5uGFh8dsh4fHyhskg90q1/drf6/ulv9XLf6d3ULRCl+yLLGuxkhRWrZyY5PVG9uD1JUDgRwd52CxN5X33iCoA/5GnFb4GvCOZxmgAhdsP1VOSIWF6Me1yBGjCdcKachMqE8qNkMGtlZRtGq16NtwzpCRCBdiLkzEmlXLRFloLxUTLMcwwqb1jBdm/KCTr49IHf+ic4DaPeJU/wKb5meTjorXFjX2eUbxWf02+zplTokOXZIBb/t5C8EG8tCV51imW33STl8EUfnMPcQGG+PqY4pY2qoWKZgPXIRGbSgGfKN4ic9e0ZKszCaZd93zd/OfzvXhR6hMxG2rzPTVpdOVAFOWAS0zUOflK4IdZEtbXH3QkBoSX4d6j27LEOc7ihM2HDBUWPDLNyoMuilZ4DCYRYvQesM+R2mp4SovB5upbKEiLMZIXYsosUiRqosoKPCZdR0KKYsIqWGQ+1DN1e5nAQXrldRM4138vkP8s6sNKACRzwQhgTBNwaGZnTUQ5RovSxjBJpGQCvgIXe9s8vdRzfxRF3dOiogaqxEfxJG9erLcIfZJ7PPMw5x0G6BPpq1vXDtF0eOz0JfZwjUrep5GuySuo9uFq96zIx+Ajck7yTiGHEsBdFrjd217ox5WBGMw+lPF30ORwgnwb51WYgMt6m6XIeDd6kQZ1txjbFr95wN7TVVsSnB4GX83QA6zURROMv0TTu7dH5C9PvnN9/LTCISI94t6iUiI8I16hr+Gf7QMzMG/q2Kt4eAdxjHNwwCmH++O/9ReldmAVDdAz0qVueCQmIhPD8gzdEQU8/ptLdEZOoYEdDk5QRBSxCMHt0YoLorupGsQPqp6/A7WFxpXRejolIyDg3R8iMKQiMXRSaWGUkmp8gZz8dmLJfIIpeYMlSKk+KEcGWxcsb4pWfRVsEscJ03ejpfqwLFMj+21NpJHbJEgC0ztwwFilXGmUsDbHGYOY4il7PJytBxGwpTtOxWn1Dn0ku7y1GNmEmX3Sq7Y/GuyeQzY1zFlQP5eEkYK7sOhWRRJ3OJqYzfj4jMlEJXQrUcbal02r4ccUk79w4w5CQUm95ErC1tGBwAQinn0KpGO1jFCABzbOiOiEENg9DMqg5aAAHRMusJyT7qfvJQoIANwsOaTG0rIuKYNp5Gi1ahCcag/d4pYRIcJYYSk7o6RZYl0D15eRWCDwpFHsl7QqcmElVQaXWLLSeK+NI2330sUyjesy3uPxYpIuaz7WTqHpGuxX625W3I4oMMAE3DzVSTFUPWBHWL2YeU6iup/eLHn88rpXam9xocuCoAgYIpd0yRB2FjZew3xQvkW37Bkaj0ZivEekdEDFeSPZrNeBvzFwyON9UzQ1zDICN6ytsvR1zPmqJS391XCvuMjiq/Yb11XmkZcjBP1FeoEfsp5yvQgu7j4pS+Sumqq7Aomra8iquS6NBuurqRoNWIT8aK9dOQFxo3K71aHObHlIRAPbyrHG9h/CdfVvFyDoesFbE5cpE6KJx19z4ZnncK08FRro12QJXUFFBFJdqh1b6HrZEaJBhcqogJMqJIgr4TdUiybuP1DrpJUfsoqF+BI8urNVICIwOpxIMIoTEuFtgjG2WOkO6E1LqH3JdK3JI9jAe4EDqV+uOBDt6q+q7Lw42vVV24iVAyvfF1WhFSy/WMy9WAo5L1IHof8XC747QOvDpjrWuEea5ZUW/FbGAJyXr7UEYJBuwymw/6bFcnW3QHHW1/9+GJjJQSCG2OQhCpsRJnULBGcIY6/SSW0h04QNkRgVHfEFmJYxWY3P6CT9nzaV16rvFe9HxPBHLkXZf0TlCGb7TN/oGtnlRcYtt+yhGqu2mo6s3j4hJutW2S9knpXHnndqlx1hy5jOBAnuYAkUVJTrPRYOnZJk4fihIEd18mp3gi/o5+J8lsevrk/wENEPFr")).decode("utf-8")
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
