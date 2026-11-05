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

PAGE = zlib.decompress(base64.b64decode("eNqtfUuT28iW3l6/gmJ3C4AIskjWQyWyUBVqte7tHvdrVNUdDvOyJZAESahIkALAqqIoRszCEeO7sRfjCEfMZmZjx/R453CEw1vrn9xfMD/B3zn5QAJEPbpnbl8VgUQiHydPnncenDweLYbpehlUpul8dvrohH4qMz+aeNVxXKWCwB/hZx6kfmU49eMkSL3qKh3Xj6uqOPLngVe9CoPr5SJOq5XhIkqDCNWuw1E69UbBVTgM6nzjhlGYhv6sngz9WeC1Cm2k02Ae1IeL2SI2mvmsddA+PhhQ3VkYXVbiYOZVQzyuVqZxMPaqIz/1Oy49T8N0FpxeLFZxtAgro6BytZjNgvXJnnjw6CRJ1/TbiReLdFOvR/7VuiPb79brcTDqfDZs7j9v090kDoKo81k7eDbab+N+MOl8Nm6PD8bPcTNfpZ3PjgbP9o8PcYdxBZ3PgnZwFAT0ZhM3++N20KKbFl4bj/eHI7pp42YU7I+Oto+ebgaLm3oSfgijSWewiEdBXEdJt34dDC7DtJ76y/o0nExn+JcKqHTS2I+SpR8DMNtHg8VovZn78SSMOs3uGPDqtA6XN3utxkElWSdpMK+vQrfuL5ezoC4K3Op5MFkElZ++qbqvF4NFunBfxFgQN0G79SSIw3F34A8vJ/FiFY06V35s08Sdruj+s9awvb+/3136oxFGjeGm6WLeOT5Y3mwfEaoE8WbndQKybgCQUG93Ws3lTaWFd7vLRQK8WESdJA2Hl+tuulhiRh/qYTQKbjqH3VGYLGf+ujOeBTfddyvUGq/rEkE6gAfwaxCk11ivrg9wRfUQc006QzwO4u7EX3aOsxFWBhuCFUE+6LSO0L1qfjBbDC+3slYy92ezzQKNh+m603h22DXealNzjSTd5Mu611P0XOcRdaLFdewvt6jVWFxu5PyfD4L28wEXXi42GiiDff94+2juhxEW9EZsls6zNgDUVQtc8VfpIge77SOAdqNhNw5vglFXLkmzOwvGKX5iwh785kBorBGviMQ+AnsLa5IsZuGoIlaPUNspLngQXdmJPw7qwEQfqwSqIB85xqoxek/90eIao6+3abFpxePJwLfbTfeg6T47dBvNY4cnUhms0EC0oQF2Wt15GEkwNOXw6KIwbg0NLG+laSzQcObPl3YLk3H3G4dX1y5tDEdUuA4YJEfNpkRKMVHsaFlh7M/D2boTRlPshxSATIFFvKjUV73RbB8Gc3PMDQz7frQ3O3/WbAJ/hn482tyyFrE/CleJwCo9zbbaMBopmgzTPKhpCdu3AJr7rEz3N0YLAJ6J24fGjvhXbrgGgLrZAbLs+oDWjEY0DZfmPmqp4RgLlQcK7wsFFJopzcCEYxCMW+NnO8srO2sMVyVkCsTfXK6tqBrdpLtVmTOUVB4toiC3nqPxuDka58Yh3sVIBuHEmHW7XZj1cQE9BTpJ0LUF6Gb+IJhtctRrB3LiDbVxj2hVkmAWDFPw4uUq7RH399LgJu3nCsJ5kCuIVvNBEOeKln6SXGNd+huxT1vN5hc5+qT2bUZSPhuORvujIo4r/NM7rrAlAKxr/yoo0trCftrdzDSrOnPM8SKed1bLZRAP/SQo7uhG8yCYK9AyiWpWDgT6xotrDd9JHI669KcOXEdJyqLKah4lnX3mZOOYaTRd8BYg1lKyOxSInjHNuo/0ylGAusdJWl+M6wT7jfEWbSE0e9cOIujcT5/yi0KDZwDyDIpjlwjYSOebxVUQj2eL6zpxu44fra+xiIGuuY+aBxoXjNa3eLkRb4w+mFVxo43rTWEvUO0eCXr15Lq/WaxSFrkIYiM/mQZArcHzYXu038XeTjCj5SKkAXMnwPcClQ2axz7x7+EmYzOHx6UzvgvLBAhLCM8ufitwHAhqxZ03glGY3kuIijN61PDjwYbxUKBfp7VXbxWEk93NoDg4iwX7R5qHMA4Rc95Su5CNdibIDxrzQEkrg4PD/ebzHXYma+kWZD3C39mdw22VDdcY3NEuP0Cjy9lDNuZh29iYii/pxTh60A4s2cPcv9ySoPyzUX5D4mGlkW7uRR2qKJiGFjMPuazAoAgNjoJmxvXrQmo2ptFigpX6g1lgkmM5LPQ885cJ5CJ5YcJfvDktEpBbqWc5nS0lEwdCEtliOFE6FaCy24656Qkf0f1oY5LFdulWLF0oFnKaLv3XaB4523R0Z1e7mJTGjUmzko5K2HwTzeFpq/xpSzxtlz9tM49Po00mvOYFu2ZeZrlDaNR8sYhQmtm2lFyYpxVdAxOMDSXoD8YGyjjc3CM3SUSl2iBM5dRKPJ5MF0mOnEXA7F0ZjOr2sHUJVSE7aMw/OBSDSjY54VPJkvyowhA1piIVMeq0qAixVpLXGRhXWk1XyMSNw8NMW2kXNCRzz1NBPYhGO4KwJgbgQEF6nyTP25RJTsVYOqJuuWVS2t9huyn4BLVdkNhb8tEDxRMigM8J3wiYjHglYols3tCkcvSW+qqw9GdKrQf38sxjfnvy0GEq2Ung6PvYUIfbpjpMwySavkWdSnI1MYneVPTMJD+v2j9qrOJZUbQomQCJtfUBdNvLDv/F01nJrnj0WbrwgfMFzGMWe8jUl4VuBn1GSfmKJv7v7Tpq5QWIdrtdZip5LnGnTBHKk/Ku2lBN0aUYmCysNNqHicb5faChIBT14AoTT8SOzSD+HHPYAY6aNSm9qq/W9tEIZrxwllSS1RxLtN4UKNGu8rtcYArz3c1eEE1YUhR1K6PwSpkHSrjDLr8sobgKoMdSLN0Z18metBGe7EnbJ5nZpCUUZqFw5FWnI9hGxfMgJhMm7Db8AKY2PFhWYH5IEq8Kelc9fQmr6QR2zSj9y9/8j5O9JV6k+niNDAj0Frh2Qu3hHqWYJJfOFyN/RsUoMIoZ9llxMozDZXr6aO9ppa7/V/njp1+jT7/GwLFVTGbQv34Ncyp+7Tn9hck3SBMXRXEMRRD4UfnWrUCMT3CZVFqVT/9YOXLM9p7uPQLNS1I05NnjVcQv2c7mUaUiyl+9fOn16i33mQvy2jokCts+clvHfbfy/Zf8JPuv3e/q92L/2rvyTjfQyCqxZ7eOnl7VWu1jBz9HB91wbF+demDionLkfeen0waUjUVsX+09c2rtblz37Pbh06jeajr4e3jY3cZBCvtvJe5us34YU35cJNwZNet5XssRNXv97q3tu7SvvKunB7XWMxcG1KWoMgzCmW1T8YGzZ0dP2/W24zxtu3GQeL2jPrAqtmlKS4/erz/r4kFjFkSTdHoSdZd1j5pyqBDID+u43YL4snS6auhBYg5+MvfsG3ftSDh98Jq6g9B71g1PURDW687mg2d/ODlpOb/Y9ofT09NnztPmTav1FbjcL55tr1EUOk9aztMbDaQPZj9x8lV45Y3Qjbz3ouC68iKO/bU9chrjcDazmxhkb1Rv9b1WlxcNhnSvZYwHQzkB863VnI0qfIfCdyexBED3HT2Le+/63mRu069LjTi02u9qLV3PoUe/ePhba/UxYOqIXsCv23bKlzlOXgcAFumJLvaHY0wFt425v7RtFDYdHrB4NKgsxhV6Q6HZ2Bv8EoPthuPUxmwby1UypXlTC3jtlT+c2vbQDdFQ3AsxRIxq6I6dnTGpjVKZ+5eBTRSLd4wa7GCdAl0YvI1xvJjbBO0L1HoV0WaNbacR8JV41enyuwRQbFWAlG8VjK+wCFcn3lH3iqArOhj6S882UBqbzb5y9o6dOrZr76r/9Psv8dd5ekygb7VrPCAJ/afHJx7edzbU11WXuWB3u+U+UfsxiuX2qUQrMEdjXgTLl9desWO8oLuGJYk7J4vSIEyxafpmCxAyPPsKXgmMhdYwwy4UQHnUGE/vivWh6gq/BfQr1Ix94B5A98WFOTn3GEyX79V6DrxTroQnTvZy0+VJwEaAdsS0nh7XuVOJo6Ltpmvnir84dvD//AKB8XjNm1cvu0a9E9UmsaVf+PEvtGMdahRFrmokAyxBKr/ZjPaw7bxjh4nEwCASYv8d88YbeANQiI/0Ui+svet3qVEBwgEAZ/QWDTy1RHC4qWVz49tW1o0SLxrU4+svooGbzHK1rveigUM70mMaYwczx2WJLFt5GuhlEavFDKOBoCcaCh4POmHKeele1pJZPZjVbNRMzpqdFlblskZ1FFjEi8Fw6DGBIPrA5IHwnl5yqK7a5mJc4pbK8fLQT2287eQBBJlQj76wJNxEr9nP1gWQF+1qCjJw3zmCGYWPPY+n8PHju1MPw0HLcklAX9BpDgsERwpiwZPA0E0SshEddqjS1iVal5FwKpNUfOzPksBx3HH0+1/OjSlI/8A8yh3RnDCo3rrfu+l7o+44kpdpvArUzsyDi9oWK0zt2Edu6IZftMGhsRpcErpHWYm5BGMSZGPNHVWzo7VXP+iO1ice/UXD+sENP7jhBzcGTglsheQr6CUEMnt047jZzRrQurnxbmoj9LX21rXRmrDn5gak6MmTmxuexJMn6zXfr9d87/Dob+gNd4RFbj95Qj+gSFsFCJ6Ave/ugyWJa5YYDoyCfVcU5SAO0q5kGt6AZXD1lyb+5alB9ozZMb/NlN0OCcxPnrxjaH/8aN7rl+ot9cQoUu84pB6HEVZbtmouS5uXpb27LG1elrZYFoabvwT2E7xx8Q4Xa/cBi/SY5DrRcQ5R5qk3B4bIEalVt1snJ/vOx7kQZSA6jArEtdVk2NEjG3+kcIUr8JrnJF4d7j9zurlWBxC1RqgI4KGeA4J+eNBquxMv9E6x6xWTwkCbRQCJPr1D7pNhcIy9MLFDR26EYwjYE/souz3G7TN1+4xvNQcz231OczHabR3UQ64dltWmURxnlRn9Wne9cFxo/ligbOuwFuZfMZ8eu0QS1GJJBJ6nRIM1RwiBGgWewF4CIVe3hHf71JMXddIVMlQWNT3vyBFXh8WBY+OkaJ5+BBGiq52t0s5tEbXMN57o8p27gpQl+qq1nCdthzaBu/ZWyzMJOGq1Q3+6ug0SoRRlfPIEszwhmq9EL8egoLaNJz3UAOLs9/HHfla3cfsEy67xKKRdIymjQnwT/fF35PUkmbRvamtHUFNXFq3ztzdf7Ju34oV8kcHdb/b2nZpxv96DMlRo8Cl6qNHfQsNZeeENW44y97Cfp4DL2Zo3tVquNSAhCG/XpC6EQYI+d4m25EFPkOnN+9yrk0H9sb5ULEtKpkHkz9K1R8xRYYRQ9JoQEOPL3T1dGJTQdFeRoTMVxkcSge7doUaxtMRqTkGFsxF6nrqGMgZ9ahWJatS25x06y5q33w3AqSui8JSKgCNcJAaw3RbGWhzJ7ljXuDZnY45VDQnjoZH/2wwpAx92e/mq4oHByodetnToZmgACnokFlwV1FoSA3IF+CPGuc0R9XQhSM5Tnjoq2JkdIOM/WKun7SbMVulTkP89/DrglLhWSCE1pmWO5rG4HiSgRO5g6bWC53l6N8dE5yDHc5ojI72NKBsilHNHSrZLT+KlzSLt8mQAxQ1tLbvc7ry71e+JaYlbeihaElePsiFuaJ4kXPIYt6YyC2Prri773st0XBrC4/dSO7QsOcY5RC7m9R6KHu0u8fvGLRtXPpBb933D2Bs17+13n29uavOt+/lmjZ9p66oFSeTDW3PPRp5ootZ+OjfnWHl7grlUKHDxy8WNVyXD+uebaMt/qhWE0ywDuDdIBgspIBKWtmT5ajQJkmrlZj6DulOdpumys7d3fX3duN5vLOLJXrvZbO6hWVjoyLZWETGQVdGkMEyrOxKmEd0IW2V1D0ZDYBGAg2ej7Bkao2fU4OlbtRJyhQjgLh5ghbYOFv5RwQb43UJY/1ZAXhEP2YG1BrMhG22YJAEsgJAwEYeJC5hgowizLDX6ff/m4tWL7849SDHfv3n9w0/ff3XuHbg/vnotbmB0eETLdX7hCVMAWz8rr+K4AnQA/Ph6EYsNGq+GKdZ3nkzcZDEGFiUrOBbpHo7EaZg0cOXhn7ihKt7jx/RDtEFu8RnM1N7CO/2r8x++bywpKNXmS7SOOcBDYy9I5NAoOwrG/mqWnqcwiAqrpcJyBILgjaSz4QDRjvX9KkwJZCJulEyn3y8+/c+Z5frD4QqbvWO1jjvNpgVboA+mTnf7dDdbpJ32obv0V3CyHhy6DAI2+sLsDLPgPER5u7l1Gf/SwIffpUTzkpCG8vWG7UvWpz+/X4UIz7Wg3UK6cFw2cMt3bbUaUjEj6EOnozXFjEjF2GYwiOB6gMbwIYApL7PbDrw8bAjHaPuOPn58LMYXJtIA2OBRQ+6XV1JagfwhR63sQQNqZNRQsPV+GLzDTmgAINBX7M3WHehnblbt48fNVndf7FrMmvsWl2bnEgbqkTeQF2IYAhyeuqBuuhoBKiOCkQAFDEjh6Bw28cCzfXeQ2Q7nN5l2SA/cuTQUk12ICqTZ1kZFaB/H4NLRidc6IhVJFD2nIrp4psvaTVV2nJVBhbJF4fOPH/mi3XTYnCXVbBrdiGQeBLX4j3m7oZlGMnistp4U9+BZC9LAi2GiVNXiBpw8MTR5bsRRdTGJxEv0ZJfeOW8iO3HYNp3aVsdy3KnH2+ybCHYp2DVg5QcYzLIWlzHpt6esA09P2gcYHF/PT44wkXRKPkSyKTA9sK3ptDOfW9rsPX161KzNs+kuL9VK+CeDM79m1a3aoDPgXx/0LmNJqR+RVycxXRJgfA/YYfaGkLkTuuSEQvh3070GQPCzHNMfH38Wy2Wn198KJSazG8fRiCzH5xcKOzfaOIpHBSU4e21OL1EFQ1F5LNYE/HlHd5ayLhwGvXnDh7VUXA36qgKMdzxyCFKD7DJ7OK55hCxdXPp8OaB64+zSlxX0K5ivsD6hG5jDzHtfK3Ik+OEtQsSB4zcIaOhWCXdUyjjqDNQjrZNsc1BMCBwJsYHGYDWcegl3B2CsYNuDVL4g7aGGOS/63JJLNqHGKByPUXU5ruOPz0KNaI4dfl6v0QAv6IN7xKmtFIo1v1+/4R/ac2vuEQX0IwqoXRTQjyhY0u2Sb26Y7NXX/COQQfR5GaxpAyVippZr1cRc5CU1Ji+XY4P08FCFSyKRqAh/7WUHdN5lnEy4J4WYiVxcgZ+iM5e66YjeXOqnI7oj5KXeJLcJA/026RCiY3AMeE1tcFGMH/wSxIYuEseRtPW05ZI7ddkxVLtw78DhjbBlaePFEhQgZDYnZQrIGHOwyRkkj6Dy6VfBvODOwgZNAz7SgfKZD6oTrG6Em/TTr0Hl/coK8FIlsnwYypMK+T1iejHiV6gKjC4kx1T8OA4//RMeJiFJzXAvOySpaFqw9MP4gviTzfOU4OPdRjtNTF55mJT/L/MTelyhJ1TNzMABn8OJ+aowV5rOHPliKDcmieHcc2PqJ/bykglZcXtLQkIyumg8kc7A0FFmZ7NcSgBwGmWTpJfVHHXPKARnZHFATrGH7vt91SieO3lpUjpxtgZRHawQQfUHZppiFAZtpZg1T1M+yVgU1zG2BktVsPFbFwFIMZzkrcpf/ubvKj+CwwzDpT/DquKskXQ5HzjYJapimyu+RCuLGeOOrHlINY/Nmvtc85ykSO51oao+p6qttmMZ68sYTU4Hl/YaifVKkhIijCFImQgwgSYyOdnvTgqrHkLcIFic9Zrk2Hb3+7yhYekT2HDwdFIL+4JidHrUrJv/089b9kcBWwk3CPkawT/TdznCu2O9xoRIBuT2gAUFj8DQu9QM/IrWRcg6vQmzysu+YrBXZ70r4t5XYNd9YzwFI8ccfPdSdO2aklAv8d1k0PeSoX2pmPZGVUzFcnQmIF94yeW6QFZ/tO74jVRJIQN1iUfjTs8aW+7Evexv8yMAcfPsuTtzhKQjcPkMYOE3BVBm207Ggs7AmzrMr4xWZosk+M3NDDoZm5PIPm5580vbwi/Q7ivI8nWhNwFt7Raw7iqpHARASVo/WC/F775TaKQtG2kXGmlX7HZAbezrNlqyjXa+jeWYm1gCZtaPAfZWIBW4ir0fkAo3pBZo1jbGSnXiEfZO5asWJDhZ3DaK21a+/XHI7VPzvO8Di5iNaOtnrO37FSmU3Joob+fKs+ZAgsahllCdjdxrtB36Hr06Dl3Lchpp13gCy4vHg9QPtbd5OS5vrNYWzYHT7Ta3L5vTD0VzggIIgWYzcYXeJ+hUb9J35346nAZJp0ezphni9TE24mD974J1Z2OWItpr62Kfbgu0dCO6UBRmW0JWz9HHaDULbFHVlFpp+2r1iPRKD4ID/Qrlku74glVMustUTalnUqG4ElqqRyK+jUboxiDOCKL3ehsMcdSxwmi8sBS1eSF03QrZpcDegWMTpfDKpqQ27LjQ7jv8JANc3yWK2GEv4ZbpG1FQhIN5XNEkqxTFEJ8oDa4bF6grpOSMyfTifjHiAZZ7GOevDOO8pF+ZV1mwQ0jb6i2y96eg5GlmMQwR37Nfwww8VCQGPlfooWhaSjQNNgIiDQpIFvRYUTQwihKiQkz66HcgiVxsubEbQoXQVkXAXvYh4M9ztFwZporuFOEngw1RfpQ5NYtZ3c/+ZMVlCJVy5LoAvLwW+K0xsqjlmCdiObS+zlZkxbJzmqTmKhVarZpH7ZieNIIkh01tiqPPYc+PhJ3YCpDjrJLRCeQtxxanyx1zla7SFe7s7KVGfsJWXs8wXUmjTyI2e1A6Dto2tw7jkQQBVcppfT3J7vqLca+3yxGSAkvou71dip/kST7VMUh6ooxyJlGnOhlZTqx+P7dRDIQvlViUD9QT5AZ0rsH0rHdZguzMwDtjQvUB/RArp1+B1WMDrRXvVmhdXCmeiFyq34Cnd6FmDjHvxY7XTAUZE5ZxeFOGBpJQ3oEISl1bpUzIWe+JET8T+xNSd3AoHvyvwg1UAlIh+OGnX6GJxJVVlKlB+AvjR+XdAtVJyYHNnvnwEIoR6keBv6rYR6p6gvBm2kULGGJo6j9E4sksHJAKBV1pMaerkeWr0STcpequS+Lvp18nMGuln351oVNJzHIrpCahxzHrUTTEESOl7nnEOtpyAQ5FXdPA/ZQsubTP0Orw0/9Gk2xalkJ4l9r89OsVySTYvQkfvocWv4gi7IZZNkZ6vQgUWODRrpoI1B3q9Kcog0pkMWBTWKYGK3RMAH+/gs2HTNswZ2PIDH9cLiImAxGKOwQlNJHAvOmnvDajT79ixGBiIQIwiWJgJFjAaMLzXM7wFg1uvAiTCm1BDRFukvYk2KJ+h8eBqVJNP1OFE/k4Sp1GTjUVFtDXwRjn44JE8n43IVnAkACGUVqqlJDFDSr2bc9Aqcrfqz932PGShMI5adheZmx80f0ziU9mDdpJIPRiLxVU1iRUthy2W80acudI7gKzsVFm7GRDBQBJUTflCjGps6SakaXwPKAgTKNNFT9Fjl9ZsYGYbpu7QDhermhARXll6doPUzYQFWAF4wfMh31lF0m908eqLdLgEX/pgiuNjEGVGfaygRZkkukCCS4M2AraeKZak4R53pAbCj7UBkRLp5MFVxqOQlZfBknmKzTHkdI4aJZGyALWigavZlI0MhqKJLCvl/bhsmzWCdvo+qhm0+ifPHlMP7KNs4Nmp+nUbEI7VMKUkrDeOmuJUjutJeHTQ+cLBd49NJiLfkiGJwPACJNIhsJLmRbiF7gaPxGoUhw0T4iWWTgvaeB01Qd+8qD4BqPq8jzEnR7DnE4relRoyIk7y+OULYvgnDi6Gox7bdhU8g1tH922GrRfzEWQ4BXbybDEYCLMaOReAM38KZ5xwAGd/EVriCP0iZ7AxGNBXCT5PBhZZ6oYbsgQhydq+p48i5RfpUOO17we8jN8n4iovmZUIf+ddhKxj40eNTg02lQb2MRqmNzdosLj7ZqOBJXzSpUfFxB8CcE39e4ikBkr3qj6rjyy0KFhymtXu/RMPUo43FDCF8IsKj1pmRWLLDcxWV+CG7CHpCM9J8oAG59po6l0oUiaBxcBPP3+rKM9oq4yhXXUhR2T3VR0rEHXERZK6bCTiimNYkKjmHQmDaWfThr8q8WUiaIyulFu5I1cgY78FdblVFqXWZYU5mV6LZHL0OEL8I/oDQ5HdSTC2c5WWXkNl/ALxh2wQQogCN+DF7M3OQbuwIcMCzCkjDiYAHwxP4LMMcCR0eJZEsNYCwcS+9xsbaIdaUsNoiUhbOYMmTrYXBIs3/ueExPwW5jTwLgfKHeiaBFxB+Q/pAb58rGoCS8jPFjBhJbVd0qLByhO/JMm/g74r3/6/Dnd4Cfv1LItngzOybE3MWhYagw8ArRUqP5TJCVHnauIxItlsEpZRMSqhjEDWMhMUpjLmn08IoY4JOKc+S9tFtWd24Y29SFmrQIYX8UgSVJqHdebbC49rreO3ErreR2xxRXEsrSO8dOqt57zD9yRDSsL25PGZWEWzDypMMlA6vthrByV0u5Gfwomuwbrz8SkDSlpmJoYoW3kXg5Z9NIqii006Lz9wKvBKeyG9DN3y60Jyl2Xh1X1JWWIEOESRacEREiIoBNxwgpY3qjm5AttRaCW58U1eB1g0/xzuoMhWkzwE0E3ldecxRJt0dW+GYQKBWNyVRt0mHc7O6LY3tx4B9+IElOwjX+K1IRIEga5BCQgH5JvZfTpnxIWZiH1w49zxQZ3qpXNsmIvVqqexTKysDxSLWg0qOGSwhBTEyBqEftoIP9+C/RCXIwPiZtPo5Has6LDhnz6LMT+YhlZLcWIgmh8uMHtzC5EkcXGwsFOKIVHOOXIIGHW0/BzdtBfmFJy8+7ICWO2RpiMT2rCO1JzFnPI80Pst8rPi3XwAZswNxcxYT0PK+eA8STd2vAOYLJFWC+uOORNPEFV8jbxM7qms06qGT0bAOTxre4WUKL7kACigsAXx9G45IlAiK3y2Y6Kwo+5lSa0h6DsI47i0t2RALKtZE/Y3z+hqOqPj5WFRJhA2MgxtiDYRsPZCnQHXoTfuj9gw9gVLholZo1dVxhI5JikNjgkir1+a6p6QJKh0ueB56xRGttfaoKFcS1mI0+RPXs8d1xyCkv3SxlWjAJaukrmqkH9vnCf58u8nkAQV+BGNrFLWikC78eP8rJtFXSO6Dob04OgZnr3o2vADdNyNjtjpXlhMXF2qOwJPcgikAV6PWiVjWClZLoa46Cv7TvG2S9fnzTAATB54lFM9J152IgvIQCNEPXhPBVO027PJ2+aj3MEgCj9uFTQ1yf2KIbA5EB/DKI8/2FWopiuHTOWZyTqFmKzKwbEZH59rKVCg6xRFG+RC33rS4pN1hrQIbK/BNIaQigpbBmCkiV+mJAH/kNmE2ExNSHDCh2ElnwKgzC5oFLKc4UInJgHSsr9+DGjPMIPTbZoUeUGwRm7lNZknpqYjrIBgZOsNDPK+A1J3QpU4sQc8qsouPHJEpMiIR5XIsntyjxlvUEbt5zS0uI6O/O5pjAl9tJe+ynQhX/AbsS+EDTb3PNFMligvVJxKLMYGKdi+XBBwYqQrcU7RCOLMALSdBFGQGZZ8nOqU4o8v1tiHrJIBK4lSU8Bx16shmBrvhnJgawBELiwKlAMFLYtoJoNZuIEeTgOgWazzOqG5aWYDijITkEaWqIdyWgqlTy2Zyfh5qygbKguBzl5uYgTHISSTwa7T7YmHGS8z9J9T/oOv0TBav2avKSVrIvy91n5ey7XPjxzH3iiWdaiOIKC9Sjh3RY+ZFjE6VcGh+V5a56inF+jlV2SUiqWlgulkqggR4MpfVqGaj5vsajbcudtvsDx9RY4dtJykzb9to3Ge/NWHyyar9p9ZtY++PPA5M9Jy7nlQfvBnJttPRzdJjslecUoaO+SvW/mGt1GFggfW1Nj0LiV8OpIrNOkBcXcosQ9SR/mS0/22EsgVBnXnuy4l7Rlubj28M59yyi2WRZPVIxUJUOLCFTlq90g2QLYWm0y5CfSvr5ScoUyVXiqHcbBiDeKDNDEXsMFeJykyk13n87r7YQM7yCiNIrkkDHnds5biS9BkYACwuMLRGAfitUne9YlFruCZlLk+2DP8IiFiO2QFsgO8CA/2a85LEwhSMWmdCiwzH/9dee77xya+RZCDw6NkgC3LbrdFu40FG438v9Y7qH7vMm+M/IWWsif0Drm+8wfToVHXCa8PFypjY1vjt0gVlfaeJDJQiQY05husxlc7WyEr1asL+0IsJR14mS2+Pjx6nQa3vLSdAEFaRbOyQ+oX2SYXCn6hGYsNgZZYgKJMA2psN2RuN3BjSPCDVm3iBGvA6y8aYC5nvp0bs7CyTMLCkMxRpwZoaZZ3u2x6N3cTtpqA8GLlxff/PD9ubfhbdtRGr8Ln8kb4QIXIpibXFNKQUE8pRFP7cHM0GfgNEnJSPqk5rTt7hqwhqTDIlrMJ8NUxaZMmISUy9WADFrQYkFwkGuLy+BNQ34YAaeuyKCyq/8RHxzFCxyoJ9MAb+Ly3Ckv//BHb0MmNssi9aBjkYV2Zulw56+/eu1tLH8Z4qHVQW0SY1zrpUg2Vb+A9Rex2Gx5E5bdvXdQTuh9LNreL8H6r/ZANJLUlq86DlpsvFilwKrwA7/hWV8GSNkbgzjISjq0fBYguQkIDp/5/hEh09gwZA4FGC+QDBTuTzt2Ef8PpPSTdTQ0DgQNbDIxI05auBwA8X3YBUggJQMgcsaxTgVlg4BKDjny6ZE5wYIyTnBE3ukr+u2yVMs8DjaCmWhEQJkERln74OZGmAxIikJZPlKTJLt9IzyTaFNOK4o9n+zxlXFARIrAgDWp8QwKJxVEfp+kAzC6Q0gqsKBHi3qC4ysBQj0wXT6zYCpNMQXZpKvk1DtswlCobrGXDtrPnQ0G6xnh719fXPyIlVC1kGiQB8ZLYe83m0p50Z4PwzHyOEZS6d2I+p0m8wfPRAdxgxBHyaMZtc5a3/uFGzqQCCVpS4D0jliRSaBFfu2MoZkFt40/F/otX6Rl2xYxiZfkZ2HIt5Vy58v1AppZexTuunfV2pO2mjc0zeAMeZGC943WE5HY1pOuAEscR1Bq4y6wrkCes9MHPuVrkK92y4f2enH9rx8WJxL5HWPrKuoZL4eeTVIBHCeTBAJBbgh4umfV+PEGqfWnCwRF/PjD+YXlUh6rTuGcFLdAQrQ0EPpith4l2Q8pzgDyFznPZ4HwjpMeSpFm5NIXLgCoG7jRZv+AdjF84ngwY0shxDShMsBoGlD4N+d9SzgIASfkhIktYCNgAeQYi5gmDdyQVShphWAgPXosLK3jSHoIaJMh71iZPLo1KQUJXPMlhYPJq5MjdVUMQ1tcmySDkUApNPd4zAT5GUc2T8EQjDBkGhkpj0Py6WHV8+MPGuqEHC7pZ9t9wPy2+bByOWyghG0lyKAs8NJyN8s3wc0SOEluLcN3tnzDn1KAM2f5ZolQIPz7+FHoN6YRC5YPiCcgP3JEi8sOuQRcbr2TORY32j+H6ib2o4ets91tEgMfg7mBjZiUBIeC8jad9kFzhyjmgJO1yPckFb/SCMo6bqhVDPgzkChw2nn8OHuLCpxtIapTwv0iXiyJRQmkFowYlo1wTlEmZIsBarPzK4EO/oGRbteNlvHwUknhczpPgi9zrGisDdpj63OmIcDdRJ/cCuCuT7Q6kEgvi2V14CZA4BB5++y93pOT06rV35u4Q9JdrScQIZ4gN34XkvwJXc9SujylywlfVuny/WpBN1WripvP9p93rW1vyFqy9FPM+eQ9smLY8y9aB1iQGv/la0W15MgMnX2+R+fA4JEenZMWYSOAuGkhrrFj1WTl+ReoUaxAweGA4Hc7AhiH+LBcxj4NqMSC0JDkhidKrrCVFEehOcHwkpC7slfJtoR0VFBoFrkoIksZfWe4mhC5eA3n24xirJhSUckPr//4wuM4MQWUixdfnr/58sX5Kw9KCsVKAJoylpYj+KTPFqXfsQbLheSqRUkWyCiC/VhqzkX8qV4oW+C3wGQOCdBdqqMdNKozdO+PoJDhfT1uiyL+Savho7rCs42mPBZCz4FZqNSYBOk3IIHQMPyBRdtGzALguqUennA9bCLqUMDDna9vaxaSu6xPoj2Q2pOh+EkKvu8hT+AioqTLnC3IpQg5CgTKQTmae3xQ4pT+qkCis3OhL/dEYb9j8wXHAZJO/DdkK2BvKmlVRU4DWpAKGZbotLu4/A6nkTOGwx+nocfqROQe4smXi6WtTZWUsI8ofUZz88zLVIkpf6NNUn0Eiyd1jnD8lcHrhYPokaKMkoTJ97KCrnzMtGpjICMtFiI9cgsAqoc07caSdcW5dtvIWUc5B8ny4HFaQtoVXbUs51ou0q+hdwEmMS5xbeYvBNXjeGtkLVZgFlVTJUEF3ue2JXKJYkBYNZwWl8oOgoECEdhOmM62T4sFuuEM+ovSR1LKPQ07cKah0JYwXxTzFu8iIWWT00ftrj70Va38Kqp7BXP6ANGW6ZrVXlKHp+EIFnhLsj1p3JIKRINTqsLRYr15YznCWk3Tg5QEZGEvzNcX333rWSeJTLkpc4TS9ziQLGC6f4q5j8PJKvZlzsCIQhzTAHlG94s5RV+MAOKEIxiH8GRm+mzEUhUyH0OB4QiMERlzKZiT0EBkH5UDOLXkcvGyazVJmUIMiUdL5F1jc2Y+v3OYNGDgksiiVrdUajr38mFHGsMMKcRAzUc72okcgCQIegTObwe13H2ZIFAGZ9MSSZG7WGQRfKs4S+Y2ho9YsB+Yxq8WqfQUyk4oQW2ExeqqpVAiQhjQ+yk1iFCcnQWSEsgIafa+ZmXUZnOeRlJsjFfkTCdkDzBv0hsU2gqzqcV53Db3YDYXwaTkiL3AZvUse4LRO60CwRoZcHOwfkv5aU9PBqefbyCW2Oegx8o+05CpFXa+ymU525O9wekJf2jp9HUuNUXl//0fHN3LnLK43VfBxgkgxK+IHLicGVcuGslOG4EjZ9biEnLF5cLaVk+zwr/8t/9CRolRSNk58JzupdVtEkGtF22+zZnICAAXlOBFT594cG7+iilLJxCiR9+eiG8DcdbGOnFapPZIocchu4ccLe59ikai0jOiUXSEhAabwiVBsOEGTt9KL75lOTlZEtDB3pcRx9CjVtjpuyFW9PEQeFhyIcZLrzx/AMX1exzZKHvsmN6FS3zQKvJuC+XN6g39iOx1HvGkJ0+CERyeS6pKAZNNtqTGlhHCdf3Ce/v5RjzGtDvquo1r/y3khC9vfz54m++WszewJCI65iEbQfzcEAsFZ29NvJnPqhJz5WNHIQItSa4mwAkagk/HaLICtKyeXlDLEkHxLj0/fUsEqvY2X3kODGVwqDAo65rXHcVKJEKg2PWLMwtmA4EReCRhevZWfgKFkAeVtlUeoBx7NOcj+s5d/SdD2RqB6syiL5DkOuFi0Qt/W+9zyDTjrBuM4HOOW9nyUSS+HmzfduysyXNyRMdo9CqxnHtAEWtgiHQBtwDjy4cA48sSYAyKwLA58FfKjPnh0NdPPt8oNYSqERufr8+seSB3pjj3Qd72jNJJuZNf6EuKJnvESw7mXEJRcPLkHE4MEBSlKjVUOCYZzEfCi0zxOI9VHD52UcLfCnHMUAVyhXwJCROxy9oltROULwWWtwXmBqDNCuFzZ9YL8xyDEfaiPY7wS3RMeRqcC4YP1sO0CtMgOroUGYvkBI1BEYGkyEBBmGQ20RyJy6xuGB3rShB1xyIWxDy6kEHNuT0On9NR5Ega5kvNqTxKOGW5LQjfGY1VZyFLCOv6S8roqiVHKD3kJFJ5r3aywC9UfIaQDtQBGLZuXy0AyMWn/0sCnTjYckVBHKSPfmChwCCYOBA6X8PWAqlcxx4YSEPoSDxFHPrA58s0db4Deps7D36owEbzFAb1h0UUxy6oPySsIWbAXQNX7XIO47DmMHc2NDDgnzvfmrml2TAX/94Rw8ElPqfzoKGLIwAY7gNGizHtDhY48i3Mo1d0SImNSspIuowXFDlhixgyODr06SeHthTJ7XQACz5JWEvJhwGHPhm3ZCSktC/Hf6DPC3l+TMF/ANfHjz4lghDHeE9QoG/M4Pzl0sOjM5ue67U5E3eIVRCl2bESmbwinPAu41cFY+SPIAB3c1+PwwcTCryPPntHSFY9/ZEmTUfBeNaSBO5KaOiKKM90budmsCUJT2V0+HwjxpmxU9WKou3iVcmpwYn+q0otoukyyD9g4SiCrHi5IXeQCGnOelmYs/xSzm+bcOU3Tu0hY18WRg4QghEBMX7HUoHxKDYGdHzAKhk4V5wJHt2xRuJFc4mYpMkzfh9ys+WWfDnhMnBwhcF9q6mh8huWshQgld80dZ7c7lzUPMomkS0pUbypTIkIWiN3vTOteWKZaxmeUhUVrAssknX4UU3N36yTkynEuZUdqcJRScHoCZNOatbawQWlvKmIw8q//MN//rNYCCvfZy5GmfKPNXSgsm769GdmgcvcDiKJggx+pFNnogRkLWaOsz8pS6y0iDaKvd/dOBR2X8Tu5qLdizGIuZh3s4tsbcAuJPTvnOxZUQL4t5nzkiz1D2n5d054qadLM4UJTeWNogkXJUjj9D3snXSkRErGZHqDXXurryhvALQNUgtYycY2F7sGzymT1RaHgOHegFaui07xQiK0AToAw+ViMFsxRaMkq1uUO6c5eTL+mqJWzcO2SEuhhfGuuRl5uuUGJCZqJJwADGuSt6qn3y0iJdGd7PFz0Bp22Yhv+chqJwgaoPbgsVuBPFVPmfyzaBgTQE72RAWAUCoW5hGut4XXP9+ErA9JnSVU+oroGGcCDXUoJbIjGzcMCqQdce3TElaiySbUPCXsKkKvjVRvJboAitJGdwfkYGETw0FtzRtuIcpMg6mepMCaWXEjWvGhfreF4ej0TJ5BA5WBll5woxvzUZZe6zbtK/N/RjfO3RN8FYkTJR1F+W9un6kWhe6ZJDotznEnHBnfyMKccucAs8hAR7EAitjWp6+7D1ivWyg/jw9dShUzb04Rn+uqyhqMwTcSg4WA0LP+5R/++9/CPYWf/yR+/mz1EZG/PRnEBc0aw+1rc0wOczMDTQE0j+6b1I8y3a2ch4EKHMI9kyPV85lVWFnmVF8W/YWTlUwTwKUzC3+kfSBv3pCLm8kQanH5r5hkJiKZD3Ob4UE9G5XUQpkVFW+QJNKQ+oq0wACjlKyuJt5fv25Q1ufzhjwk6txDIOW34DAZ8TG403/5h7/7X5UfAQSfAnmHlDWBHBvqcZ6tKCq084m36uk5TD8RhMdh9kkzqFfZ0QdEpUjPSIdN6cYavmeSQvmSd8VdTKmqsU7NUVM6PZs8eDB/drbegWa7Duvd5aVFq55S3M3Y3Pw7LJ70SoqK+6APnHHkoczovBSJFBMOX5Tx0iPzVFNA+Z6uYpIqdl3aDCtprlZSXwqbTTCsCvM1hudViQFUT/8axC3lzivz4vS0ydoAFZOYzoMxRQZo5lvVeMLfn2SOCi9mtcKfIa+q75BXxecpaVReFd8rR9pujJ/jIKY4yAQvU/VlccRV/oikzpdbXSAZ963Kww6ETOisIgGfr2ARUGcMAxMit6CRKadkZicRIFBidUKI7JdphFDMODAN+jjI8MOlx6dkcF4nd8xCTS7b0qA4ouqZTQZbnLf3Q+HWSkPO0YLwTDpKAWpxkSuQiWGEDIk0cB3xPvBIiJBBnD2WOas61h9vfYZ8Vra/k0LUscy0O29L8JJs0iTlDKVFmBcBgGFrtbqPA2G8Pmvhg8wkJQkYUXyMpb4+y9IRoJH5WnLVCnvwggkrNuDoT+JEFW9AdcjKgIx5WkuI1Nu32eloXptvgSs4GgSV4bFwk9CB132cczWPuRZuGyIvgTr2yrVFnIg4jIWsATovgCjJ51BycjnR4+9ETSENF9RQMSZpghdqWx4Wf/nb/1iBZIAGPnBoLnaRYdO055/+eS4PeDnCwqnJUqZj5LPAHeykfyPBy8sg0IedNvFuUWq5Etl1a60HSTXiKA3wo9YqE0AhWaNzvXUU55Wslp+JxTjja5l22UJMkVXjEpEQwoJIr/ktOstWHvkgzqwyedA8nyxflEwbo36bubyNMTibEtXsxxLTPXQr5lgWmfAhn/KxLcQfxjJVVY4yahu+RAfCAk18hNFeht5lgijOKsyyDD0kRomhGaz2GjFX1YLwo8Jq4FGyHPj45NkFYXTZkaFYaqnd6k94nIey6VnYmqHaAsWN5ROfuXpsP2QL5oBhfsVIoZ5V4sUvp/SGDr1L7WMkfr009VU/Wufs/uKgJu0AradnVqU78N/odZRJEdL5XiaAgK0thfxG1gmpqycy6ceXIARgsR+QUUI94Wb9EcV0+Hyf5XJGxhfxGqWqJs4AFCT6yZ8KlsIIf8gePzH+TU8/O9nDX7qSh5v0/c/66q/0FY2moe++Qifybg/NKdHNBKI8tvkW3ak5TyAqigPSJNanIxHakAirhjBCUiH+5ZUV4X+BvkKVkXgbm/wvf/+PcgfLN2RTbPYoNKWWcZsro/Te+RKC3GnzzKpxy6pE1uFpmg41hZECqNqcFa0Ju8twCQN3Sqn+3yOj3J9lEhIiGhAcWNOl870aQRBvSYG8wKlUhDKJYAsW1YWA4VR8Mj8x/xybpi2tV+T7FXRSimU7X6CfNJ3sc+r4rPPxzmeyj0h8a9UPssTTytB7T8utB7V8WD82MlU/sOn2g5pGHpa2mdtaqwjLh8mR0nBYRlpkMoBckhXkRrjbqpkRF65cJiYVkilk+SxhkdTZ+YJE+jnpwYGmP6KGPtaexwot7cgUSfcamWTWJGcr1fzJLSyDCXi5HryzjR5GU3mggow+iJLRliUzRN56Q6O82aFLRjg1vknA6g0+MkWJ+Q1KJR8U6Ys2/ZztWFi0sFJCQraKdjwI5zgAJIAs9IICccpQjx/Y+eOnudOn9/IvrbsWNMVdxvU9na41VWGX4r18wb3EuVAiXx/AiBb5KHBlVpCESgn6FFAJGAsNjS3ZGCwK5Fbjkq5wdkmFnby95BcuU9xNeY+19HL9vVGy4+/Gxp15a1tXiV1ZWLR39V6mQepAMQRfSMvavC10caGCk6lGh7WRXqwt1NL2XIXJ/kaYCr3qfrOax647FWuK0ucTn9XTV8YpI4IhnZwuszncD52vJQoQxEd89lbABy8KYJxekJvyjsmSESJ5wwSmMN1EkZ0qN2cIv/RVMLYpiVZlbEl5J4hoVp3Is9c73ags3LTxM/erbBwCGwBjnJe/txuWsHc6kXK36kLOSPXyUieuxY52SruI+Mi07gQmbaMPkdp8W2q6KZmUkVv6wT3y+fBcl1xyZ5/FWWaU/aG9Zt68XNdZ8YPnXEhi/OARCNqW610U3d2znv+9m1Idus7ty9+3Hc99EMoJbkujsC840BVkMZ5kJxKlSGIm7rKJHriSsrqSYOuP3DmCdK8oqgy6NiUe+ykNZzICCzhFcef0XZkV20hjiGbCZkv+UhxUZJYQqpzC8gjzTJiyMQSA/oF2VBy9gy2NY6/zcxOnnBMDFr8Hlv9hQY3gDEAW1H7vkPjYPMdv0mqOxz4ZBTiPkJHlJZAfIDNI7m7DyOux0/CL2YwjCFKCHGIG0xAaREJ6wpqXMZbZlmn5nNsmXS5r0JqtykQMeYZAxUSeG4c2ctH0WWy3+REgfZzA9QMvi7ZH21fBqxnvX6VFIfWiT4evUopMxy2C3/a++f7Hny4+nr/69tXLC3mE2sf5Fn/yPU4EoYIt4r7lIS0EdsE7yWFsfDbH2ahzT3zOwjikUTgPRR/rykLQcV4dClyHXdw6Uaiy8nFu1g6bE1S+UakAiINbHSGTbZ0ehta/95TBGI8SLGh2ukAOzSkcxtlwUr9SACKbRhmgyitr4DnZ6RD3sClsOhk6gKT54qwGY2oJYiwwUJFDkiNKs0PFXj7WVBwqVljDdUSkqMff8CIE4c52T0Ho3eCTOyB3OmEaBKn0qupQIiOOiK1dRa+gFErMZrIQ9FsCvw0/SeJXi9yhxElCR/eqTRbSvOrz5wbTMPJ3QtfjyO8Ck7xnWIPyYQ3+1cMa5IY1uG1YIErJfb4b5maEFNp3kEW+lzO3eykqH1S7vU1BYu9qbzLFocR8i/iazXeEcwhYgwpd8C5p3q3jzflr67nNaJ67S5CDAJ88MRCZUB7UbA4j6DyjaOX70XFgfycioDdiLrxdD9UWp+B2twpcDTs5FsC0Rnpvyg9IcXbb3NEVCuU2vkxJ5yu9pT5Yclb4oEqnxt+mnNNvu2826pLm2CEz8LaT/2DFRL502Sm+s+0+2j1ez6dHrT0kbtljqmPJM58q1xZEj9yJQeNQp7yj8/38KfJxGM+z5zXrT9GfIlPpETYT4V05sxyVFLkMcMIqbTAPc1G64ihmtrVFbuCA0JIiB9R9lsxZBOYXFmy04KxmYZYOS7mM9PGNcJSd5zMGQ/Fl+oAHvW8eBy59Q+SBipHbDNnMkMNLvmCiQi9uu5TzDJm8wpHxoJtrXC5CC7E9cVufx/30Z/lNB33gj0/kCQu5kBuDiuHWMo/QGqPcxQh0jYQLwEMeeqfGw8cwcUVD3boqYVeiVH9SRs3md+EO10PmAWYc4qSSAn0Mf27hsxSc2TRLzZghULds5DoZEw0fwyx+iihzKwnckLKTOGfv0cjEqA1x1741J0/JYVF3MFsMOF0OQs8Gdq+QuWRTlvydk0uoFBxb8Zm9ltN3N8RrynInQcDL5LshbJqponC25VtO9lHUKdHvn15/KyuJTEG4t2mUyNyD4JtrRAD4+Lx5JsC/UflgkJAF8/iKQQDf4DfnP8iYvSxBF74XbGRt6FxQygakjwWkOVuPpYaiR0tEpoEZAU1eTnGoFslSMYwhmrukL2YUSD8NHZ7txaUxdDErekuekyZafkyHpOWmyNSySprpKXLF87mDdt/ITtZa8iivq3FCBEvYOXfv0rOJVbAI3GBGT3kCVCIzlseWRj865EckgLBy21CgWGkeFJ0AgtOgcJaTnF9QpjbZ0DH6Zf4UfWJmPXCXTpdP3bOQLoe1G/DDXJPJZya4ipS4+fP8mCsHp4Tks+Wzqcq9+oDMARq6Eqq72QAIHPdkBMjWcgsw5DQUh+5ELghjGtShNs6hV4N2sIkRAObcheaHzsuTmkBBtK1GSrqP+n5mKFDAAeFhS6bBiog46s51NkN17nwC2u+dEibBFT+SmNQ1KbJ8A8OTH1dAchxhyCN9T37nnQtV0kP1lTUuFPkPHfHNd1FC+Qgd+fF3LhE5CR3zM/BcbuQmdNRX4fmBTFBI081MkyVTNhR1m8UHTfWV1n7xw0/npVo703sDDtwUgEDJ/jqWqIO0ZjI3iZIF8j2/4EwJZrclar0rMloqzR7dZrKN9TMmx0z1rCLSBMuMU/LrTGNu54qyJt4+VkpLiIGqyFSzd95pGXKwTDRQqJH4WvIVaEHfi+CSgSrpqk81ULZH+amIUqJD3BRfMJZgy4hPJooNmAlh3A1DmpVxEy7LY0pDoBHe9l72udj8u0qWewSR9A5FndmB5SJbysY4QEi2CNibUuNQ4cAD/6NWaaI9dWa9L7SCFAMkEpBmY8PtLcSRUsdQZpmC2JW3XWgqAi84OCeCemLkBLhYgBE2d8U++jCRMTzU7imdSo4wGeKrhFq1T4YmDMvau96dbnKt2sLncKRkm1zrhlC6285ktxmITbIdpJAhQa020W3g1p0YQyP0alkl7ZasBvaJbHcAi5OQsnrZetBjp7zYpg+hEI+7C09ksohAmGwUgkizlDi+gI2AM676kdgvt+AAVUcaIJPrsaXGLkiygwWfgubTlHRdZ4bzdE9kE2LWSsYlWLw3Bke/h5+THUvw5secJrGr8yVuHpYcZ2vwQmKGMkbvVp5oiM+cPoPgQAHLAJFNRW672WQV2SFxHtYQZBhdpqe4IiGOfqfpfHb66P8DYvJNWg==")).decode("utf-8")
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
