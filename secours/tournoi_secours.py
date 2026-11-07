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

PAGE = zlib.decompress(base64.b64decode("eNrFvVuP48iWLvZev4Kl7i6SlZRSlJQ3KZnp6uqa3T3uqu6prG4YzsldRUmUxErdmqSUmaUSMA8GzpkXG/A5gIHzMufFxunjN8OA4VfXP9m/YH6Cv7UiggxelJm9Z8PetTtFBuO6YsWKdYsVp0+Hi0FytwyMSTKbnj05pR9j6s/HXm0U1Sgh8If4mQWJbwwmfhQHiVdbJaP6cU0lz/1Z4NXWYXCzXERJzRgs5kkwR7abcJhMvGGwDgdBnV+ccB4moT+txwN/GnhuoY5kEsyC+mAxXURaNV81+82+26S803B+bUTB1KuF+FwzJlEw8mpDP/G7Dn2PB1G4TM6S6G6z9iPjfeJNF2jpIllE/jhojIPkhySYWaKhmt0LR9bT98mzZzfhfLi4acz8ZDB5HQxD/9mz7NmqWUu0E0Sx6Bo6T8W7xtCPru2aLYoFsY3mapRW6wGqqxk631APr6aBeEdXAcIGd8B7n3z+XJuG40lS620HVIsV2JtHFk4Lnu7LYT95cpqEyTQ4e7dYRfNFaAwDY72YToO7033xARBK7ui3Gy0WyaZen/vru64EcK9ej4Jh96vhSXPUOsLbOAqCeferVnA0bLfw3h93vxq1Rp3RCV5mq6T71UH/sHN0jDdMTND9KmgFh0FAJZt4aY9agUsvLoqNRu3BkF5aeBkG7eEhXgZ+NORveE5uUZ87aLXbbbxhnrVuDSbhEhUGI3dE/Qr7KDUYDttDKjiZchWHAeWMA34Lmsc+1YmM0bjvW02H/jWahzblmfiYbPGh1XQ6TefoAN+O6dtwMQ/6AMFo1OTK6X2ggQDT/lX/uDls0Uuy8GN0usUv/cif68Cb48ugI3POg8Wc+tVud456OSTiSdyK+bikCa6L2SU8usom6Aj/fDkF6YsAn9vCP19BEPPTGh0oCI74fykE3QEAnEKw7bf9jq+mEi/t/kE6lS2/5beP5VS6nbYYJE0l8rXdAzmVnWbrxB3KWWj57oF7ombh0D84dDv6LLQODhz1n4S3Phdykg60eXAHHfQjm4ejPmZ2JOcBc94/8rV5UF0m0I9GB/5hPw9rgun2yfNNf3Fbj8NP4Xzc7S+iYRDVkdKr3wT96zCpJ/6yPsGs8MyIFd9NMLnx0o+wCrdP+ovh3WbmR+Nw3m32RiBTXfdgebvvNjpGfBeDwNRXoVP3l8tpUBcJTu0iGC8C45cfas7bRX+RLJwXEeigE6NegCsKR72+P7geR4sVsAi0y6K5tkX/5Tvm1+4t/eEQHUePk2Qx6x53lrfbJ0Skg2hTqoGQR9XBy0yW7rrN5a3homxvuYhBkYGdcRIOru96yWKJQX0C+gyD2+5BbxjGy6l/1x1Ng9vexxVyje7qkjR3ARJQ9n6Q3IBQ9HxAbF4PMdy4O8DnIOqN/WX3OOuh0d8QuAj4Qdc9RPOq+j7o9PVW5opn/nS6WaDyMLnrNo4OelqpFlXXiJNNPq13M0HLde5Rd764ifzlFrkai+uNHP9JP2id9DnxerFJgdJv+8fbJzM/nGNOb8U21T1qAUA9NceGv0oWOdhtnwC0mxR2o/A2GPbklDR702CU4CciBMJvDoSlOaJFbPckHhL0XUxNvJiGQ0NkoPVYmvdgvrZifxTUgZM+Jgvbgvxka5PHiC5WWNOot2jOaeJFveKDzUMx+iuUnW+oi123NwvnEhBN2TN6qO65AssJKm4ax9qc8njpT30YRsGAIQWwr2aVqFLELQ2D2qg0m+3B1J8tLRdgctqNg/WNQ4vPFhluAob5YbOZWzkgcDLDyJ+F07tuOJ9gzSWYqQSNMNbQGOqNZusgmOkgaQAq5ZVJtD63sPTWj5pNUUO8HjvYrGf0sBHwbBGqTkQ+fo6TaHGNQa0iIi4vqcbeKJxOgcPzQH6Vc9FSr4QRA8CFu6QnflwAXUUqwz2eRLQNoDvUDX0cXLuc2gzhylS6fZAbpkTTyB+Gq5hXQk/0rX2Yjat9WESCx0+3wibM3yqK0ewSQ8KHbQGO7nHWnssUpjGJNg81Ssgklm+DkHdz/2JUo6RpShd/SxHOlDg0eVHl1xqBtFVeadyqMWlvtMLHOeQmXP5b0dwG0H5TWgay6Q4tV+oRGAOdlLqqO9pSysODSaOCBw2SRlCGJOq1S4tQNtjA5JaBD+ZTR7atyDq/TcpZmTOtyExsQjk3MxP5zjA/Qd3ph2Nt+Lwk9eEfFygJllMKwpYA4dTvB9NNbiMrQVCUUMT7kGYHPBJoIgSi5Sq5JBHMS4Lb5CqXEM6CXMJ8NesHUS5p6cfxDebnSi2MZvOb3FZVXuVyJP0SpitUTMnjjvVRZErUYDaKhQLrE/igkbwVg9AU39VmJnbITh6B6uEMslp3FU0tIdnx+z7W/t7tbOp8036JRwOP89gzJ0my7O7v39zcNG7ajUU03m81m03KbBokkX67uPVMWmatDv5vGkRaPZM6YRqCcHrmN622kGNUkqC3ntlOEyTF9UzuYS6ZaK5K/6b9Ct1b+snEGHrm6wPjZHpk4F/9yNwX36hneILoqQ04CgCeBKCRT/q3lMdgWBlE6wy50LVcKUO1S5Iw5Az9/wvmE98/6o/+vwQzuHXexp3LaAGFg3i5cuTii1czrMw7h5fw5WiBpSUh5/fVoz9I1COUAOoxvlFP42CuHqfhOkif11dOIx40oEAAEc7vZbJPXdAMvz8Nhk6jn2RvKvd8gYU0nS5ugiHo1HRNH4s1yWQjbelhVoV2ShQuss8FBkZRLGJIaXmmzPgJGOi5IarQ6UAMcqwyueD3oUdC5xz5a7DMtFgH0QgD6k7C4TCY06gAsSIbzcysJoO0c6wnlAJuq9XUmZJH8JuKMK1i4vZ48gUlKiYwpJPNH+Ve8puy3IGrpC1J+AiskDYs+uJU8fLIYNs6X9ApzxH39XbzCC6uc6DTGzHy+7k61fVj1fPcvlBCFmCKZMY6gr2arvtKmMjBkkBzqNXfNOhNKy9GNagsXD23qkpNaOE6lqqOTILJj5Om6I+h0R8TW0rbqQZUyNmrwYSIC1U/8+fhcjX16eXxegiCU8M3eKj6CnE7+DdQw26neCH4JCrULxXSiQXlWXapa1icoOQYT7fP2888iGPLbbRtbnw+25SkMkyEQzJZ67AokxEnRRxOnYGo4KRIQp0E9q4/v7sBqIIeUXyFEW7DPRDtac1hsq12Cw21O+tJuaFcefEVIwx9/IKHwmQMuiDxgHhE7zFXP2kVaWJK9I5FB2ZqrbXuW2t/ZKm1KlfWblZUWygHrfuwiPs72pRxmuFMf0pUipb6IXEX/nTAhMnYM+5RMzCajAzaujbaZtHsiVUnOsCfG3Ew0HGtDDO3k+flueR0Dd2NqMzAP+JrBfTrbm/XNqdNYI4As5ZMCvTxYJNShHupWh6JdBrH1bFILQgOJTwNZ2T+AIr1tGxZKskaydz5m7P9pX4NYU8Jp7EhmZtNCgTaIZrlcXRHMDPE9XUYh8RhLFYJa4DbBXmBVNjY4sXX+mI0ol26VclxMsW6MqorlpRMKvd1VcuO/LKpOu1ChToEO3PjE53Ki9APynCPVRUoYY8F/6YhZ36mKzJZIL6fAqk5OKDttJUKZbkt9xEiNPe8StGJDj1OpoZSIFrcpHRhHIXDHv2pY+xISRi02OpisF3U11HEyk96SDfaCmip8R0xij2kzJS9AL8XxQnmt04ovdFKscIKCu179BK0QB/Wd+fBTJ0vb0G6KoMbnm127EoqJy2NTmkSSfpC4Ua00dqIhHmH0m82BRyh3Kk0ka47gtjQjydBTlAvacNmoKrT8nwjkcALGpexQwfHleMuQrOEaDsQsqwzUHDpCGUQt18SRzTWpVfaRitkFTmjSXHsRdUTWrvG9tSHrew6vxkgQRgD2wEZG6+HZANo+myuiufKjrdFcRhwuXhmcRQlR7JYmoxiGYDQ8jKnHKb5A0cxJtBgmOCGmsNg7MAwhVYhHX/jyJqMo+Y3FXhaxcMfuM6RC6PYgV3Fvqa0/bCogexISmPopjUwbuiyHHBeqOIByhZEx8rb9IEY8uShdVnQqjfcYKYGO+gPD2AUzuvDpEp2OX+kBrcjsydy+z3RlM/8nFN+56THCh7s8G9sshBdk0aseyB1fD+kOkcHB4cnW65L3214NVfwtzs2O4mmg80jJanjvCSVG7YAa+JHCddZIUBcT/PL9zrPk7UeAYLmIWCgU9qK/bKlEGaoA6b1IGDK5h4AnECcm6gKUVtNChwcjkdNbvpG53qzkWWmzbwM06FmYr2ZdiZ+5lcFVSitnDnWmrmERy2Q1m61r7AmFpZAp6SsaC13mSq5W2rlHWhmGH7eufIUNj4gDP2NF2JcsRBPHoOEx4QXcWHpEUt0P4Zxk/re26RaJn+UDPAaKGjXqKLhvZ1puA+yvVyJgXbmRUy8jxvQ7EZ1tm0Lw1+ZDwWfM73VhWTJyHx10oFzyfEOm2y26vLeAGTlH+9cAPewrkKLbrUdzANp2ZoO2Feo0zLLGCo2huH6fgPg49ZOqyBCd6qYLdlkv8pMJGSITmk2W4+ZTaq0vNW0iRWlb8WZbqU0J2eTI/aJQSkg2HX3627vgWKpLpMxgm2+2lSRs8GW6sWYy91GemMW5G2TgV3Sb8p8hSpmQoCY3ttjt6rHWv8Oy2ZOourTx0hGBy1NMiqpUQ4fJQJVUDFuX8pE4LSnw7xEhI9GIynKEEWNRxnWy6mwimbuNJxWKS1OpnZm167ntoVDqQjePknYEKFZGzOuceov46CrHgqrGyVLhJAXCksGML7MuivYCaMBfBzLc7dbbusIW/sW3ZknEwE6q2XrUhihKJofbnQ5tVUpFd0zcfBjs7fJ8N5WykiVRI1x00gqnA3GTVSHr271V1d8bVV/bdlCobTZpd2uVClUO67s1IDlVEeMDgVZTMOCvMFIdK6o+btPr7HlAtBXVCsxxOfxZBEnm2r9qkbRKO+lsqddZajfORD9ijclowT1mT+VNJrS44wa3WWqKio33aYjHEtZblOGrFZzN/fGrE4Av53drMwkCJJHeqzwYmVCZDTzMmJuwpS324Hkp7mJgnuKlM3iR2qNiCyeEOql+rMKdk1Wf8yUskyFqS2DdZ2bwgZ5vxJD8F/jx3ZTqbQEtv4Wae5/Ld39j7pJlH6LPLoHEsFQbta8ERSZF1jWNw8bQEiJi2UZ+Ndd/ksm3/LaePIV+7gW8Y+33gMmwSxIM+QzcspPNO7/zqofkMahhD1ca6WH6IlEoSrnnwLXppZXUzQtOigTjUbrINZNuZJy1IM1xh+L9ZsB/gRjqWCexOjJFU8zMRf13AXSVDaWLhcYwmxTaY/MswZbmZd5RGlFrNgqqrbPB2yplWbcJ/vPjTr9z/gBZnF46n/53RhMV32ja8CLP3KMPk5kDBwDbY0DY/7l98Vc5n++n3ryj4bd2rd+BK2l8XIBaIM0DWtO7QXgHEbGG/Q+l/7dD29y78IrOZeU+SYTNcpqJMdl440fYZnWnMzhWXNlRm/m3drLiX8d+cbPAc41VLfwcFWZ57CjnOcc8tlyWOvvkDaK/kwdtkc6JGw5rJrQvT3F7IxIdq3wQ249SiIjRUHmv3dPaYlr8yF1Bn+gmncE7+YIdt0RKh1HiJdOZtjM93ZuP8pumWtoU9ERZvWIcyyoVaUK5wG7SbVgzApEo6gCYvpRsO4U1YUHj1MXshw9eaBzO32dlDt80SOzqZuyHHa9NGhfKWlbW8f2zsrJk6Xb7QegsCTBiF26VusVSDMLQS55Q0g/cPki3WWPm5q/7HGBVyPigTNSqR55EEaDaeCUetmySadcSG7axuEBaH0VoVV0eDfohHqY5MEc9JgTqABUm8AIr6/jqm8H9gPNsBY630yrpdekG4gf7rLBCkGm01qNblXfjh/Ttx31HVb2sHNfjco8V6qrU1kX6/pvdzea2QR2N0m25h3fcs7tuzKVPcse0aPOAz0S8kBWkfC42lVgV8utSkTcXY+cTNJaPkCtdtcgDEzxXJ06umeu8wdxKsxebqVlPUeeKeUeBC2J70VwuK17isfZEq8y98gqDstIWLWSHmxILPJ77Ur3Ugp2EczZqg7w7+ieApqDU34AbNL+Qzire1gVCFX10m3dW9m8RAF20DuGyH8z49On6uwppODVIBjWZwvhD8yv9ub5RuO6aUFpjihwCJr5FR+22yc4NCpOgp7uyyO+tLHJA7/gkMKhV5sMcQRYfA8iOqmLQ1L8Af7c+LAEkwo3FK8Gmbt2Bm4vGvM51b/80/92ur9EQcqPYkRvqBQ4l7hmEDtTZ4dbr/bGX4dj7qCxhMlgEC5xKpiaRBEUBPfNBWeLoT+lZCRoySwU1Ax27K3BLJWs0uqBM15tiTWWBFk5dUpWcduChf7Tl9/BUUeQksAm4cDsP7zFyWP8WjP6i9PRQRI7SIqkGcL40THgHhDjMYZf0pf/bBzaen1gycEVxAkq8qzRas6FLHvzxDBE+quXL73LOpDPgZrAPSBNQevQcY+vHOPNt/wl+9e66qXlIv/GW3tnG7BLRuTBuPx8veeCU8HPYYdOMq/PPCikROa59xru0Q04MSwia71/ZO+1elHdA5Y9n9fdpo2/Bwe9bRQkOClsRL1t1g7LOD8vYm6MqvU8z7VFzsur3s76HWLUvPXzzp575ICTX4osgyCcWhYld+x9a/68VW/Z9vOWEwWxd3l4BaYusmhIS4/K1496+NCYBvNxMjmd95Z1j6qyKRFiGw6SW2BxHOiPVNeDWO/8eOZZt86dLeH0yWumDYTeUS88Q0JYr9ubT5716fTUtf9sWZ/Ozs6O7OfNW9f9DtqaP3uWdYek0H7m2s9vUyB90tuJ4u/CtTdEM/Ldmwc3xoso8u+sod0g/3eriU5eDuvulef2eNJAFjxX6w+6cgol0t6evVGJH5H48TSSAOh9pG/R5ccrbzyz6NehSvjc+sc9N81n06c/e/i7516hw9QQFcCv07KrpzmK3wYAFpEpB+vD1oaCV5xpX1oWEps2d1h86huLkUElFJqNvP6fI+iNwlFiYbSN5Sqe0LipBhR75eNEuzVwQlQUXYboIno1cEZ2qU9qoRgz/zqwiEryilGd7d8lQBcGb2MULWYWQfsdcr2a02KNLLsR8JMoave4LAEUSxUg5VcF4zUmYX3qHfbWBF3RAJ06sDSUxmKz1vb+sV3Hcr1cXz1/8y3+2s+PCfRua487JKH//PjUQ3l7Q22te6zG6YHEUpsUYADJcvkY8xW0O9q4CJYvb7xiwyiQNg3HP26cHAD7YYJFc6XXAC2ZZ61xkhh9oTnMsAsJsImkGE9lxfxQdoXfAvoGVWN1HLhh0oM+OAfHtMW7ms++d8aZ8MXOCjcdHgT55XYcMaznx3VuVOKoqLvpWLnkb45t/D8/QVCYeM3bVy97Wr5TVSepU/7Mn/9MK9amSpHkqEoywBKk8otNqw/Lzju2mUj0NSIh1t8xL7y+1weF+EyFLsO9j1c9qlSAEKfJtlpr876npgjbmpo2J9o1sw7O1Mz79ejmm3nfiae5XDf7875NK9JjGmPBocthlWI289TR6yJWixHO+4KepFDwuNMxU85r53ovntaD6Z6FnPF5s+tiVq73KI8CiygYDAYeEwiiD0weCO+pkE151TIX/RKvlI7CiGJhobSdBxCUmmnvC1PCVVw2r7J5AeRFvSkF6TsfbbEZhU89j4fw+fPHMw/dQc1ySkBf0GgOC8SOFERiT8KGrpOQjWiwS5m2DtG6jIRTmqTiI38aB7btjOZ/feFcn4Lk73iPcoY0JnTq8u7q8vbKw5nduXxMolWgVmYeXFS3mGGqxzp0Qif8poUdGrPBKaFzmKXoUzAi0T9Kd0dV7fDOq3d6w7tTj/6i4vTDLX+45Q+3Gk4JbCW7Oj+AqbOGt7aTvdwBWre33u3eEG3deXd7wzvCnttbkKJnz25veRDPnt3d8fvdHb/b3PtbKuEMMcmtZ8/oBxRpqwDBA4BVv40tSTwzx9DREtqOSMpBHKRd8TS8AKvg6i91/MtTg+wbb8dcmim7FRKYnz37yND+/Fl/TwvVXfVFS1JlbFIghXPMtqxVn5YWT0urPC0tnpaWmBaGm78E9hO88fARD3fOIybpKfF1ouEcoswSbwYMkT1Ss265p6dt+/NMsDJgHYYF4gr/QYIdfbLwRzJXeMJec0Ls1UH7yO7lau2D1RoiI4CHfDYI+kHHbTljL/TOsOrVJoWONosAEm16B9wmw+AYa2FshbZcCMdgsMfWYfZ6jNcj9XrEr+kOptd7QmPR6nU79ZBzh1W5qRfHWWZGP/e+AseF6o8FyroHe2G+iP712CGSoCZLIvAsIRqc7gghUKOwJ7DmUfDVrlBDnnnyoU6yQobKIqfnHdri6aDYcSycBNXTjyBC9FRaKq3cElHTfOuJJj86K3BZoq09137WsmkROHfeankuAUe1dulPL62DWChFGZ89wyhPieYr1svWKKhl4cslcgBx2lf4Yx3VLbw+w7SneBTSqpGUUSG+jv5k6vAuJZm0bvfubEFNHZl0l3+9/aatv4oC+SRtd7/db9t72vvdPoShQoXP0cIe/S1UnKUXSliyl7mPV3kKuJze8aJW03UHSAjC29OpC2GQoM89oi150BNkLmdX3KqdQf1p+qi2LMmZBnN/mtx5tDkqjBCCXtMhjUh5TRc6JSTd1VyTmQr9I44gbd2mSjG1tNWcgQpnPfQ89QxhDPLUai6yUd2ed2Av97x2L8BObYjEM0oCjnCS6MB2W+hrsSflvt7hWR+N3lfVJfSHev636VIGPqz26lnFB20rH3jZ1KGZgQYoyJGYcJWw50oMyCXgj+jnNkfUk4UgOc956MhgZXqAbP/BXD1vNWFwTZ6D/O/j18ZOiWeFFFJiWuZoHrPrQQxK5PSXnhuc5OndDAOdgRzPaIyM9Bbi4RChnNmSs116Ei8tZmmXp30Ibqhr2eN6Z71tWk4MS7zSR1GTeHqSdXFD4yTmkvu41YVZeAuUZdnfvEzG5QB0v0np0DRlH2dguXiv95D0pDzFvzV2LFz5QS7d3xra2tjzPrz+enO7N9s6X2/u8DNx1y44kU8f9DU790QVe63nM32MxodTigagjvrXSHX59Wa+5T81AwrNZQAFJfFgIcUOhKYtXr4ajgNo5EQIgdruEALQ0JFuzRDhAGqiSmEbU28cT6BGKvvaPhSP4uQ/vg2zb6iMvlGFZx/UTMgZIoA7+IAZ2tqY+CcFHeDrhdD+rYC8InJeF9oajIa8C8I4DqABBIcJ5SQe4Dwwn2OUlUq/N+/fvXrx+sIDF/Pm/duffnnz3YXXcX5+9Va8QOnwhKbr4p0nVAGsQTVeRZEBdAD8+HkRiQUarQYIXGjN4rETL0bAongF/zh6hz/cJIwbePLwn3ihLN7Tp/RDtEEu8SkUv97CO/v7i5/eNJYUv9HiR9SOMcDTyFoQy5Gi7DAY+atpcgF1aiC0lgrLYaVFibi74VCCXfPNKkwIZCLCIKlO3yy+/O9T0/EHgxUWe9d0j7vNpunwiQF+a9PbdIFzgwfO0sfZ+27nwGEQsOIY7hJQC87CmM7UbR3GvyTw4ThUIXlJSEP4es/6JfPLP/+2ChHJ0oR0C+7CdtheIMtaajakYEbQh0xHc4oRkYixzWAwh/MMJIZPAVR5md627+VhQzhGy3f4+fNT0b8wlgrABvcafL98ktwK+A/Za6UP6lMlw4aCrfdT/yNWQgMAgbxibbZOP/3mZNk+f95s0+aLTYtRc9viUW9cwkB98vryQXRDgMNTD9RML0UAY0gwEqCAAikcXkAnHniW7/Qz3eHsNpMO6YMzk4pi0gtRglTbWsgI6eMYu/T81HMPSUQSSSeURA9HaVqrqdKOszSIUJZIPPn8mR9aTZvVWVLMpt4NiefBSTn/KS83VNOI+0/V0pPsHlzDgiTwIqgoVbaoAat5BEmeK7FVXgwi9uJ0sEvvgheRFdusm04ss2vazsTjZfYDDPdL6DWg5QcY9DSX05j0WxOWgSenrQ46x8+z00MMJJmQExzpFJgeWOZk0p3NzFTtPXl+2NybZcNdXquZ8E/75/6eWTf3+t0+//qgd9mWBPsPeSPFukkCG98jVpi1IWTuhg65TyFQaNNB2NQYP8sR/fHxZ7Fcdi+vtkKIyfTGEQ4dQHN88U5h5yZVjuIT1o+aBQuvmlBsgEzDBp1RCEAEDhjkBfXbylzhZbQIY8SrFdTaIOepL/8lElljHweJAyLNageVs0hdoXY08eepmGns+iWJXHLQMENczho+dLDiqX+lMkAlyPAAe9bPHrOPoz2PULCHR58f+5RvlD36MkNaBFAUOi00AyWb/u6n4iGxkyhF6N23/QZNBZpVLCOlMubbffUplXS2ubmJCRwxbS6NPoIJeDE3J6yLkCycBckkexjz4oprckjT1BiGoxGyLkd1/PGZVRLVsaXXu2w0sMNcYU+KEkuJKXdcvn7LP7SS77hFJNCPSKB6kUA/ImFJr0t+uWViWr/jH4Fios3r4I6WZSxGajrmnhiLfKTK5ONypBE07qowdMQSwWFJve5i93AY02NuSaF7LCdXYL1ozKFmuqI1h9rpiuZoSVBrcg8Lg7Q0SSaiYRFZw8LejP5jFwYJo4fYtiXFPnMdsnkvu5rAGO7DE4bGLrwGXyxBV0KJ78ypgHOZYfOdgp8JjC+/iy0RRjIy+wYcUxnpWDCzMFjdipX15XdeTgEKGXPTh/o9NsiaElHBORehLFDlEHcEC2vEiwzaVeLF4WZk0yJLKczSD6N3tOtZPE4JPl5ttNLE4JXdSlkVM+ujxxkuhQCbqU1gyTjViwolqG4ikgVDuTCJueeWGxM/tpbXTB6Ly1uSJ+L8ReWxNDGGtlJm6+mSr4ApKhskFVZjTFtGIvZbZjLkEC/R/NWVqhTf7TyPKk1DW41U91c4Y/B3vBWLXmgUm450eCk9lduVoqLa0mBeDZYD810AAg/zvWv85Z/+g/GzsrZjVhHsWxqyOzZWicrY4ozw1oSrCuOOzHlAOY/1nG3OeUG8Kbe6UFlPKCtcUUxtfhmjyZTh0FojYUHxZ4Ix0tgzHQHGkG/Gp+3euDDrIZgYgsX5ZZPM5U77ihc09IcCGzrPx3vhlaAY3Uuq1sn/ucrbC4YB6x43OBMxhNXnSoQG65pvMSDiLLk+YEHBzjDwrlO2YE3zIjioyzFvwNdXatten1+uiSdYgwm40vpTUJ3MsJtfi6Ydnb+6jH0n7l958cC6VqzARmVMxHR0xyBfKORwXiCrD39Fv5Eo3qavHvFp1L00R6Yzdq6vtvkegLh51syZ2oJ/Erh8DrBwSQGU6babbUHn2Ju6vF9ptUwXcfCHq+l3s21OIvvI9WbXlolfoN13kBDqQhoD2lousG4dG50AKEnzB52o+G3bhUpaspJWoZKWYbUCqqOd1uHKOlr5OpYjrmIJmJlwa4Z3iRQLDasdkGA4oBpo1Bb6SnmiIdaO8Z0LvlAmt7TklpmvfxRy/VQ9r/vApM1G1PUr5va3FYmpXJtIb+XSs+pAgkZhyvfaG7nWaDlceVR0FDqmaTeSnvYF+hyPO5l+TG3Yy1F1ZXstUR12unJ1bVld+lFUJyiAYGg2Y0dIk4JOXY6vHBlMv3tJo6YRovgIC7F/998Gd92NngpX262Ddbot0NKNaEJRmG0FWb1AG8PVNLBEVp0XpuWbCl0krXpgHOhXiKz0xg8suNJbxp5K6ZUSxZOQfT0SHCxUQi8acUbID+9ygy4Ou2Y4Hy1MRW1eCAnaIG0Xtnfg2FiJ0bIqKWPbCB4HzoS+ZIC7cogidtn2uGX6RhQUHoMeZ9TJKvlGRKdKLuxFBeoKLjnbZC6jq6IfBewBUPmvNZW/pF+ZrVpsh+C2VSmyIiSg5EmmhwzhNdTewwg8ZKQNfKbQQ9G0hGgaNA9EGhSQTEjHIqmvJcVEhZj00W9fErnIdCInhGCS6ioBe9mGgL+ILOlId0o0pwg/Cxag/Eiz90ze6n71xytOgwOWLecF4OW5wO8eI4uajlkspiPVArBuWm3ZOfk03VUMmq09j+rR7XMESXbG2hR7n8Oenwk7sRTAx5kVvRPIW40tHGxlz+MsPSUr3NvYy0w2CxIx/WGykqqkWCz2oLIftGx2duOJBAFlysmSl3K7u1qMLi/LO0Jc2BIQjrNM8eM8yac8GkmPlapPJ+qUJyPLsXl1lVsoGsJXcizKsuoJcgM612B6dnldgey8gXdHhOp9+qGtnH4FVo80tFZ7t0Lr4kzxQORU/QE8vQ81c4j5IHa8ZSrImAAHz9sqNJCE8h5EUOLaKmFCznJPBK8cutIF4g5upcH+Z3AFRkAiBH/EGSrIRgYpCZQYhL+kQPi4QHYScmAJ4H14AMEI+RG8Z2VYhyp7jFN/tIoWUO/Q0H+aiy/TsE8iFGSlxYyehqavehNzk6q5HrG/X34fQ1mGE10OZCqJWY7BDq9ffh+xHEVdHDJSpi0PWUZbLrBDUdPUcT8h/TCtM9Q6+PJ/0iExUlhLJrxHdX75fU08CVZvzJe/QIpfzOdYDdOsj1S8CJQ1HTNJBwJxhxr9ZZ5BZW4yYBPou/orNEwA/20FTRIpzKEkR5cZ/nhczJkMzJHcJSihihhKU3jgUxXDL7+jx9jEQrh1EsVATzCB8zGPczlFqUytg1pTiHCVtCaxLaZluB8YKuX0M1E4lp9xyqmRE02FXvUt+VMHQSz3foduB9EVvYN5UimUkB4PIvaub6BU1eXqJzabc+JQmDw13cuUlS9p+0zi42mDVhIIvVhLBZE1DpUuh/VWU3X7kNxdoEzT0rSVrIkAICnqpVogJnGWRDPSP14E5Nqp1am8ssicLDM2cMLR4ibg5JdL6lNSXli68cOEFUQFWEH5AaXkldKLJN7ZU1UXSfDw6nSwKw21TlUp9rKOFniSyQKe+BpsBW08V7VJwjxryAUFy2wDrKXdzVw2NfMjiy/9OLNA6v1IqB80Ss0RAnNFnVcjKSoZNUES2HeZXMEQ2qwTttHz4Z5FvX/27Cn9yDrOO81u096zCO2QCUOKw7p77opUK9mLw+cH9jcKvPuoMOdTEQ9O+4ARBhEPhO0zKXhFcDb+IlCl2GkeEE2zMIlSx+npCvjJneIX9KrH4xBvaR9mFNzDo0SNTyxNj101LWLnRKC9YHTZgk4lX9H2ya7ZoPWiT4IEr1hOmiYGA+GNRq4F0Mxfoim7MVCcQtRGd4oRPYGKB0roIfHnwdA8V8kwboY4TLyXvpO9ki4465I5Ny+H/AqLKvy0bxhVyCqYmp7Yckef+NovXd0pVKyaIt8pCjxeWXUkqJxXKfw4gOBLML6Jdx+BzLbijcrvyIMQXeqmfHZSQ6EuRwkzHlL4QahFpX0u02KR5iYi7Utwi+0BcXykokIqYKPzVGkqDTOS5sHwAP8Bf9pN7ayOUoV1M8sC6U1FwynoukJDKc2AUjClXoypF+PuuKHk03GDf1M2ZayoTFopV/JezkBX/grtciK1y8xLCvUyFYvlNHT5AfvH/D1iBnQlwln2Vml5NUPzC8YdbIPklhD+hr2YbdQRcAeWaWiAwWVEwRjgi/gTeI4+4qkUT6hoylqYpdiSZ6Uq2mGqqYEPJpjNnCIzdWGXBMv33nB0Wi6FMfW1974yUooa4c1AVkmqkB+fipywXcIuFoxpWn27MrmP5Ng/beJvn//6Zycn9IKfvKnMMnkwCB/BNsqgYao+cA9QUyH7L3PJOaZ35RF7sQxWCbOImFWcnicAC55JMnNZtU+HtCEOiDhnVlGLWXV7V9cmPtisVQDlq+gkcUrucb3J6tLjunvoGO5JHR7LBjxk3GP8uHX3hH9g5GyYmTOgVC4LtWBmn4VKBlzfTyNl/pR6N/pTUNk1WH6mTVrjkgaJjhGpjtzLIUs6tYpiCwk6rz/w9mBqdkL6mTnV2gRpBCzAqvaSDoVLs17BKAEWEizoWJzbApY3ajn+ItUiUM2z4hy8DbBo/mtSwpCUTfBjQTeVLZ7ZklSjm9pm4IDER8B1OsyrnQ1RrG9u0J0Vik3BMv5lrgZEnDDIJSAB/pBsK8Mv/yVmZhZcP+w4a1a4U65slIa1WKl8wvQpNI+UCxINcjgkMERUBYjanG004H9/BHrB2wZHAWM+40Ziz4rOhPOZthDrq6FspAKdKTOM61amFyJ/ZW3ioCeUzCOMcqSQ0POl8LNL6C9UKblxd+WAMVrN+cYnMeEjiTmLGfj5Adab8eviLviERZgbixhwOg4zZ4DxJN3a8ApgskVYL57YkU58QVayNvE3eqYTVKqadDQAyNOd5hZQooeQAKyCwBfbTnHJE+4VW2WzHRaZH30pjWkNQdiHd8a1U+IAsqVkjdmLYEy+2p+fKg2JUIGwkmNkgrGdI7wI6A6sCH90fUCHUWYuGhVqjbIpDCRyRFwbDBLFVn/URT0gyUDJ88Bzlii15S8lwUK/FtOhp8ieNZrZDhmFpfmlCiuGAU2dkZlqkP9KmM/zad6lQBBH4EY2sGuaKQLv58/ysWUWZI75TdanR0FNt+7PbwA3DAsXwhb7SuPCZOJEUtUX+pD5NQv0etQsay5Q8WQ1QuAby7e1E2V+en4Bx8rkOUox0I/6ESZ+pEBj8CWxnwujae/SJ2uaj9MJgCj9OJRwlZ4DJB8CfQf6UzDP7z+8lahN14oYyzMStYPYlNmAiNSvmb+JRtbIN7i4C/2oPEtIWwM6RPqXQGpDCCWFLkNQMvY3gS70U6YTYTY1JsUKnYCX+xQ6oe+CSijPJcJxYhYoLvfz54zyCDs06aJFlls4Z5Qprb55psR0mHUIO8kq3Yyy/Ya4bgUqcQ4PwQgV3Pi8ik6R4OUrkWS3ME9RIlHHjrNfKbvOxnzOKVSJl8ll6znQhX+w3Yh1IWi2vuaLZLBAe6XgUKUx0M7a8pGFghYhm4uP8HEWbgQk6cKNgNSyZOdUZx95fDt8HjJPBM4lSU8Bx16sBtjWfN2TA+f5wXBhViAYKGxbxHwtAp9LD0ch0Gyaad0wveTTAQHZLnBDiB6wlhuNYeSxPTtfN2MBZUN52cnJy3mc4HiV/NIvf9nqcJD+PkvnN5J3uBC5wF3tyUeaybpI/y1L/43TUxuevg48US1LUexBwXKUsG4LGzI04vQrXc7ye2ueolzcoJYySalkS6uZUklUEEtB5z5NTTSfuczqus6sxQ84FO9ix45dJ27Rb0ur/HLmXmGL5qfWFW/WPvbnvr4/x66940Pr0Ts363rYu002SvyKltAqk70fZim6DU0QPtamRqBxK2HVkViXkhYkc40S9yR9mC092eJlDKZKe/Zkw5dxS6aLZw9lHppGscwyf6Ki/yspWoT7Kz+VXW8LYHNbpMiPpX59pfgKparwVD2Mg3NeKNLtE2sND9jjJFVuOm06BVhyRC4holSK5JAxZ3bOa4mvQZGAAsLiC0RgG4p5Rfqsa0y2gWrownu2DA+Zicjuki8M9nt2C1MIYlgUJhCa+e+/775+bdPIt2B6cBSVGLht0ey2cCahMLuR/cd0DpyTJtvOyFpoIiqDe8zvmT2cEg85TVh5OFMLC1/vu0as1qnyIOOFiDGmPu3SGaxLC+G7FctLJQaWYlmcThefP6/PJuGOQpMFBKRpOCM7YFqQYbJW9AnVmKwMMsUAYqEaUs7AQ/Fawo1Dwg2Zt4gRbwPMvK6AuZn4dBrPxHk2EwJD0fOcN8KUZnm7Pdx7uZW0TRUEL16+++GnNxfehpdtV0n8Dmwm74UJXLBgTnzj81VgRDylEk+twUzRp+E0cckIiarGtO2VFVgDkmHhLeaTYsqw6DokQsrlqk8KLUixIDgIRstpsKYh6JuAU0/EZSnLf7QPDqMFjumTaoAXcXVElpd/9ydvQyo20yTxoGuShnZqpk7U33/31tuY/jLER7OL3MTGOOZLEeSt/g7aX3h4s+ZNaHb3P0I4ofKYtP0/B3d/vw+iESeWLGrbqLHxYpUAq8JPXMIzv8UVIaCl5p7MlDqsTwOETAHB4ZPkP8MRGwuG1KEA4zvcCAXzpxU5OFUApPTju/lAO2bUt0jFDO9rYXIAxNvQCxBDSgpABFRmmQrCBgGVDHJk0yN1gglhnOCIWItr+u0xV8t7HHQEU1GJgDIxjDJ35/ZWqAyIi0Ja3lOTOLu25p5JtCknFUWeT/p4Y0SBIRlWmJM9HkHh/IOIPBR3AUZnAE4FGnRckhrjUEwAVw8Ml09C6EJT1BCBgM68gyYUheoVa6nTOrE36KynOdV//+7dz5gJlQtRubljPBVWu9lUwktq+dAMI08j3C1f9tMvVZk/ziYaiBqEOIofzah1Vvv+n7mijkQoSVsCREPHjIyDlOVPjTE0smBX/3Ou37IgTdu2iEk8Jb8KRb6lhDtfzhfQzNwnd9f9tbsvdTXvaZjBOcIxBb813GfidjNPmgJMcchBiY1lYK1BnrMzDT5FgZBFe9Vde7u4+bd3i8OT/BV96ynqGS0HnkVcAQwn4xgMQa4L+Lpv7vHnzSzA2odTxM8/XbwzHQ4dWTh9xTUQEy0VhOIuP8MDwkxD8jMA/0XG82kgrOMkh5KnGZn0hQkA4gZeUrV/QKsYNnF8mLKmEGyaEBmgNA3I/ZvDIcfshIBzd0LFFrASsABy9EUMkzqu8SoUCkNsIJf0WWhaEbBUWodIwRd1q/jRrU4piOGaLckdTD6dHqqnohva4kYnGYwESqB5wGImyM9obvEQNMYIXaaekfA4IJseZj3f/6Chzt3hkX62vUeMb5t3K5fdBkpYZoyAtQIvTWezfB/cLoGTZNbSbGfL93wVM4w5y/dLuALhv8+fhXyjK7Gg+QB7AvIje7S47pJJwOHau5lhcZPa55Bdx360sLW35SrR8RE2N2wjOiXBUaO8TqfVaZaIYg44WY38TlzxqxRBWcYNUxED9gzEz550nz7NSlGCvS14dUq4v4sWS9qiBFKLjRiajXBGXiakiwFqs/Erhgz+iZGubEbL9vBKTuFrOk8yxHWE1NcGrbG7C6YhwN04PQ8WwFwfp+JALK0sptmFmQCOQ2Tts/Yvn52e1cyr/bEzINnVfAYW4hnuSu2Bkz+l52lCj2f0OObHGj3+tlrQS82s4eWr9knP3F4OWEqWdooZn+dHrA1r9o3bwYTs8V9+VlRL9kyT2Wf7dLoMFunhBUkRFhyImyb8Grvmnsw8+wY5ihnIORwQfF1iwNjFh/kytmlAJBaEhjg3fFF8haW4OHLNCQbXhNzGvpEtCWmoINcsMlHMTaX0neJpTOTiLYxvU/KxYkpFKT+9/dMLj/3EFFDevfj24v23Ly5eeRBSyFcC0JS+tOzBJ222SH3NEiwnkqkWKZkjo3D2Y6455/GnWqE4hj8Ck9klIG1SHe2gXp2jeX8IgQzl036b5PFPUg0fABaWbVTlMRN6AcxCpsY4SH4ACYSE4fdNWjZiFADXjnz4wvmwiKhBAQ9ndrerWnDuMj+x9kBqT7rixwn2fQ/RBxdzuqGEYxA55CFHjkA5KM9nHh+UOKO/ypHo/ELIy5ci8apr8QP7AZJM/E+kK2BrKklVxZ0GtCARPCzRaWdx/RpnnLMNh3YZjz6rc5b78CdfLpZWqqqkMIBE6TOam9+8dJGYwkZaxNXPofGkxuGOv9L2emEgeqIooyRhslyW0JOfmVZtNGSkyYKnR24CQPVwqaQ2ZT1xWt7SIuFRJEPSPHgc7JBWRU9Ny0XKF6XF0LoAk+iXeNajIoLqsb81rvVQYBZZE8VBBd7Xlili66NDmDWcQZfCDpyBAuHYTpjOuk+TGToEovYjJY8kdDEL9MCZhEJLQi8oxi3KIsxlk4NSlWcf8moq/Cqqy/fAwtsyuWOxl8RhcW+8Kbc9qdySAkSDQ1vD0GK+f2/aQltNwwOXBGRhK8z3717/6JmnsQzkKaOXUkx3hCCYtM8w9lE4XkW+jEQ4JxfHJEAE1HYx2umLIUAcswfjAJbMTJ6dM1eF+PYQYNgDY0jKXHLmJDQQcVFlB85MOV087amYpFQhGseTcuQ9bXFmNr8LqDSg4JLIoma3kmu68PJuRymGaVyIhppPStKJ7IAkCGkP7D8Oarn6MkagCs66JpI8dzHJwvlW7SyZ2Rg2YrH9QDW+XiTSUigboVDoc0xWT02FYhFwQhjlE6oQrjilCZIcyBDB+75nYdRidV6KpFgYr8iYTsgeYNwkNyi0FWpTk6PDbR7AbHnpsWmLtcBqdakXWI+9pXdWEYCj1cH/ZcRbsTIQExeIUTv7erPcppEwRDU/vPzpjUdTSBtKlwKTmGkcjddtw3WnJ/VjnNg71gNsvD7A/S9rtzlxO7+6zdwXXGLaaq7rh5PO+hAfTPaCUt5RonoRtt4YoLtuq2YM7sRvhJ9CXS2cEnxxgtZFpPlWs3FyggjjjfZx6Vu7cYTLwI8aByelTy5upjdajWbrNRVFroPG0dELF4NrZxU3T4xDhMd+fdg4OMYHRILP5UBK8wCONo2Tg9d4dl2DepGvpHF8aBw1TtrpsPnUsBgzBzLBgNs1Qw5XRjU5yEKaMIhVxpMGFBWc+aAqr3ugZ3YPRbWVWQ/S/kh/tsIkH2NYk+MS4I/WnVzakdGZYNIP/AMc9WSQ1Onu2k+FTIff40o/Q8GkbeQrcZFh0k4zuHWRQXSPGZVi7zrG0aSIFsdIa1GSjkmHApOOGJFauQIdjGbSKqKpqyrWajmW6JjVIhF4sSj1rAVMavsCzVyGBgHkCP8kytD/P6VVxKv5g/jfKc5Ca93inyZ+Casn+GmK307jpInrfOnvFNeI4pn/AsSNI3rhn9wXUcI9abjqQz1XBBid/8B9f5KqQcP4OwrPZWVhPRBFVNEu9fBqGoh3SJPY/xsc6VyxH8k5a68pyJNJch2cIBDwXLhMvqag5vBBT58tMw1xzgHi6+QOCRplUHHbtFN/bhJCMt0EhWV6RxlThdDM2yGxmVDD+Kyq8Libop0roQKa2bOGvMbDEyO37HPzq+YR/vmQi+TlAKbun5AsxpBJ8q3PtdJTWpEoywDoPQ523pwZ2BzXGKdsO+UwnbnOx25zmxJdNAcb0OOhWt651H4VyODZ0s+du4XnHQIF9yzt1y36xecSEvuRww7U/J5LfJHQ6+WHlxu5Fq5Iy0S7m44WtHkTW4Iw9jm25ANFkD877WObhARvXUB0UaaMhoxt9E56oqVOoaaNDbV/dspXbZ69zcWGMv6f/wtLNfNfwmtbncuJsQ1zERGEnmPXS/5mQsH1tXdSO2wEe3VuLggQ1wtzS5u5SkTSX/6X/0nZqMZzKMFlteI6D1VTMpnVOAJyHUIQvQIc+cD7X28yZGWhHiUhmXXFS8wHm0TbaT5iIBpE3PiBCCVBhNuVg/uQM2vRzLyjUG88Lyxo4C03EUqQlo4bCXE5ciTi9gRIx+hqAt0r4nzJweHdJw9iSj0nuYKOfRZSxVhxuoyu3cBFAMDYGufDgKj7l5TtiqTg7SldkXpGjbhXxDPRWzquD9J9zzTtnBIJcw2mXx41ggJ1BRa/7Fs9A08N14rc2aKlVx2OiA70eXykQbbY1d0KrnG/7tzbdYYnyzfw52So80gYffYsGMLTaUlZ6aREk02okan5bt+88D58vRGfMfquem7h2f8ABcG3u7/3P+Sb5WBQvLOLhrnLmmMECQ3yM39Ct+7o/IRJ/cN5AjUupYWiNJLiZnfaEUDuDaPw+Qd96cymNbmY5WdbLowPNOm5nJiTr8lUjuVkiCtuBAIZMvUDY564QOJrqBNG2xpXcsaIkq6wAIv3HfVGrnOFOh9IJNr7kM88Q+U8D8rx2rzhRpGslDBwTb95cW7CUJF2R06m7FF8Q/1BJtUfMd75jIMC2fn2EXNfTgliY9F1s+fpwqIjLF5NvKRrKh4YdNPO/UAQiYSnadq2QFQEXF/7Ee2/LKWxxyZskGPSHbNl16cVe0G+clkOgKJrFAakYtVoyXC6YpoEmHzNvrtbPo7Nz/3tB7i26+2nzQjaLVd0Nz838eC+Cs11bKaQtaunNkonVwRc2jG53z5mcr+tmNx+aXK19XKe7w5dgvX1pryEzsEBiabPxMlZ8lfMNkCpueMCV3Kjky2ikI0xV9B3UNcLuIGAvCtlc0MdaCGXg6HwwyOP5qfqJCPIUcyXEds6M0XOJN9CR4fTX6lTT+lYo1T5fCioBwC0aeEAwrn5Qj8JqjkOpz5b8Ozo6hpJyP4wHeUjjTVo4pcikqQcoNYp2q7obIWg8DLKe26vyOyW6B1rm6EsHAlvWv3wZwY1e/dJRg7oldsbMF6qTsW3RJyKbUF9mW1WKppExQ519y1F2k91b1AbE0lW8UhLN/wslIer0K+oI8TsH7DGTZXG4sv/TSoxcTR4TW6wpNH/xGoVbedBSI3ZHaxV0Gum3psa0hA60l4ujs3Ob5N0m7sHept7j84qCUE/x0rtYRLFwVVqD8SSdlVuGrhqVW/VthQbNtQx4J8z2+p3frBpM/prewwXIXFf96O6Lg5RoruP6C36VO4scORHGJjXdMybzXLKzLyMFuR7agkvfLiKpOfHbbb0BHSAHT5d7BUoiDvoBZ8Vz06kT1PnYuGGEnEEshnueUwCeehEKqLX0kMYXfUjO1iriAJdOpJOMUO7PsXgcmb0O0uDX2IGcpnRW86MdJGbHmR25NOj0d0igwjIgoBy6lFjuW4mCy8gXTb79lMvzj/8Sggtz8h/yugnyDSEGLkL98/UxlX83pffsQW9rM4h0fCcc3f1OjVma7p+UeqYkduvqWCOWGzVJVlq2wevzNpy6BF5w8lqn0BTWqzezEktyADWZ4GAd4ABr/zZA/u92D3MXDu4wpWayXFxy7lxXafuXxM/j3FC1uOtUPSFJjffF9wtWjv7+e1PL79/gdtsX7949/L7rK1tPmdB2FrSKKQ09+7V27eoIJXUeFYaOmvXrxDflvNBLc8U4jrUWtZdAboXb7/94d3bF396RbIVdTDlJ/J1DankhNAgxcVtVZspo8sZc7xu7m+u0A0VAkITPMV3tIV5zN41/GIglOYmrpybfI5/K0RjhmguYVIrzn9+ugHVDMLbqiorAStlvjIcpfinqnkIbBrwiOxPZLxu8i1ZK8ZFmE0mex5QHsmQwzJXjoDiwNn4xnCSr5lVZX6blAIrjbFn5k6hUdzaRnoU7dz8lbdmpt9EheXh1i+/kymXrCVaMNWu2LSn/6hs7NLWTexRZTUwuvji/FXuxGLxHEnu3GLDVC5qGGcRp5LpLc0PhqUjYuarpo7G5XhLcQK8xF3aKmgvfeEtlCCbIxiYAqZdrNtRZ3eMf/2X//GfJd3o5dq8B85p1Wd/C3gXW7+/8r9qFrQmiO0AxwDrrApJapemJhmLpSjWLhlyYePYyuWdJlAwqnOTRS3WRSlVV18QxrPMp6K8tFTFFEZ1mxX5Fd5HAFKQfjtDC7Eg6DvrEOPQamGGW/uUVSLOylZ+ytefoaMKuZxj66PvF7NAj6FM8dVSmainkwMGbrUllAkP8Yhgse+I7a2dvV7MFWN9us/fMSbWZIu7MGW2U3i/Un1wPVthZ6+d/eWf/qMhOPQIQux/PN0XGQAgKd/psQg+FIpDz8diqRQdQyU2ioYR3EKTSnlnkpVrCjICH+cWBJhvF0V34d+IqB10GzZuj+W1rmSOlIYqa+sHiZyAYkY1P+y2IetkHGWKVDwvp/dpguReQJnTPVbOOeojYVKKotSFbaFnachRT6NGyumACjjzW/1TFjJ2lzyckfr5rf34sc5vHxiqHCby3T9KtFocZOmM3RKXpl00csEtsuMutqLGdAwxDSnUe8Tc7SDC3D80KTfPvJYP6eFqVpM5GJtvJTaLzfnS/Nd/+V//HXyu8PPvxc8/m1c4Zro97UcFZQe6e5VyPzkszvSGBdA8eWhQP8ubIeQ4NFzgc4nTIr87NVh/wfFrTfoLz0HSFgGZzk38kSqb/PTKydXZxAwJ5CDLLI1exWASLh/XspZJTZSeUe1LZepZpAsaGDOvhn942yBD6UVDRj6xHyCWQ1jxwmmMwaxmoCt3Z//6L//h/zB+BhB8Op02oFBg5K2jPufVF4oi8Q3MfB9clxypSZF7MSDR9RPVoG7/hcSbneeFq7V09+myf4g2h78xTaGrRcrMJ4ZUS7FOjTHjHNVo8uDB+NmD8B40K3thlqeXJq12Rs7kI33xFzQ6LNAu6ajHpzSKAh+nkZefLEV08JjP5MhDgEP9qH5AQUzXETE1ZT9NhlXeMoU74MG+DHTrFG0GtbN/QAyIRMiQs+LwNDNTCiomMd1HY4o8dZSvNcWTcI5LRHl3hWteTarIaew3OM1bM/gz9cqrzWHIjEL0n517JzidD9ep2stij2FsWyWL9GqJ2gL31uzaEcsQ0qGzmgv4fAcljQqcEegQ2YFGOs+SaQKF12uFIhDnvr5N5jhfFAW6sQqnc3+69vjoNw6h584Oq8FpigkY4DjrOTSd53CPH/mh8NVKQg48CN0QaWBALd7lEmS0Q8G/IrZxV5QHHgn2NYiyzzIQa9f8085vCNJq+aW4+Lapx5L8UIGXZNQgjmcglfQ8CWNyqsIX9R5Ji8i5220yxyRgxLbZIWYf9qQhc0qARmZ1yGUrrMF3TFixAIf/KMIE8AJUkQM0yOghCIRCdfshC/nDc/MjcAXn3SGqPBUmQIri0oZRTY/dUnhtiGBbKpYL5xYORCLCAEJhpcGuREo+MKiduz4oei1yCs64IBSLPkmriJCg8rD4y7/7HwylWqLzZlhFmprZmn35rzMZtcAWqqeULGUa5nxo404ppjFxXl4GgSvoC2Nvh3zJmUjVvuc+iqsR58OBH3vu1qjac6nxdOmonVdutfxNTMY5P8u7REw4ypt7nCKinJlg79P9Fo1lM48gZzBrlhqunelBd2RBuWmj1x8yjYPWB3vDY81P0M8V1hSIarxjmaQ2gIzLsQhwqCaS8VdzlDE1q0h0ICxIiY+wo8jzJBkjCp+qaRZ2ktioTVFevcFBglolC6Q8xmHXM22oV+Sx3Id45zJ7JfiavZ1GoKf5edDNQVv9hKJYBNoEiztjn1qPWaQ5cOlXgirkNCucV6v3Ai1wc3k/iHDfwbUu3frzu5yxRsQnoTWS6hA0f4AoU1KR6PMDCUlCgSLGgeFquhRngBDpA4rocp4OehBdpZE3BRW5Z9lpQxlmzIv0zpHMONo4/1DNEfb9wfVYnHpe+5FVr49dilsypJF2D5e3cO9b3vb6HNmjHvkQQmKxdavlPuD1TiaOBR1esbg1pZTYF2+8dLdplFzmLW15fCbrPqt2cPCXFtFHInDCksZXs/C3NOAME7wPpd3kx1x1AXteZLWJMCEjOrYeqLjJDC25nxQqA9OxFNw1qa6kYiaWcQa/BZkGA/QJQezUF4a+PyQ3cp/fs+tjEGRSFKPbcWjfBoGgTiyxRhLJKia0e+Inwn+Ts69O9/GXnmQ8hfT91/Tp79Mn6k0jffsOjci3fVSnGGsdgWWkmA9oTo15DEZexGQioSsZSvWSVH2xypoS8V9elBQGS0iTlBl3/YAE/+U//WdJX2UJWVWm7MqqijP1lZZGNwrlUwhyZ81zc49rVikyDw9Tt0AraiCAqnZgLGOiLFXrGB23K/fk/4Qg1v8s4x4SSQdblwSCzg9TBMERLzo7CGRKxOmJYUhOyyxICfbPNny2BE6zAOvZpl2x1QjCvHOJNrMl6mKJHpdW6CGtULfeye66kZTceKBm91E1H8BbPrsc55FVtx5VNUI/tvTrdNIdaPk4Ll9qlavIuow/lovriHBs99sUMhrMmauY2EL8tiyEPohWGhA8iCU5ow+dlEyLHClhy2NFyovKqKz37AJiUcpArfZW0v3xju2aN89qLUVpGT1u6+GOCin7UZSMliwpifK6NerlbYkuaSc4cQ0aC5+4LZfuAtMolfxQpC+pYu68pP9KWckKErJVtONROHchLtvbN16Qj18V6vEHKx/xJhfw5sFtPtUsFOT4sl7jDQX00RUVDjnN+mL3EqFoiHx9wka0yB88VUofSaiUGEZnuABjIT+zkR+dRYJcapzSEw4vUp1CDhLkSFGlVtG5cdahVGtXGhUr/n5sLI071URWWACE7aGslWAapGIYQSwBb5MaIoSmRChISJGWehCS1iK1JUgrQQ3czq1Q5OJATLOWx6571R50MJiDzNTOXmmBDQiGFKypSiP0MHS+lyhAEB9yuB8BHxQUwDh7R54d9wyWVETxeyYwheHGiuzUuDpNNEkNaaJW6YxV3UhIftqiERnuqdSMuviHFr5mCBO1gWEDYLQQXQ82w0JOqREp+qgm5IhUKy/TuzKwou3KJuYcpSltBAYHrQ1xm9K2UrFWMSjtOptHt8ghqXJNcsq9bRZHmVH2x7aacd65prPkR4+5cG/Ko3sgaFuudZF0f8vp+B9clCrOU25d/nXL8cIHoRzjtfLg5zt2sQdZjMZZEBTJkuixgi2iB46krI4k2Olt3bYg3Styw4QmhGId/5KEU+myCJyio650leWKNdgRWDOhUSdLeiDEOb5fRI+aNBWGBnQBoH+klhvRPqDp5OOe+bGJwEqxBou/Bpb//YIqwbHj7Bztg13iSF3sJE6zORr5pLLh0KVaYMlA3qSskdxyxQglWKr4xXTKrhYJQQ5OtkkICSImOeGOpzGSF7zQ9Nm7Bl3Na9CcrapYDHlsWTkRX2jnxHOHibKjKfq9o+kJZscPspNkZEJZB/LokpKiEO3d50NjdMIHr/AW3f/hzc+/vPt88erHVy/fyahNPo7U++M3OHeGDJY4oCLjQnz+jI8h+31yOAB7o0It8NFu7Vx4IQQD3Q+cnaBBiCw6zsvOCOndBEoHy9dBdFmVo644kAKAiBXRFTzZ1r5E164ePNg8wqcYE5odaJZdswvn/zccR7wSgAjgVwWo6swp8OzsQLpz0BT6tAwdQNJ8cTxceB+WEWOBjoqw9eyCncUx8vLO2SKOkcIaziNcq72ROkvGjZVPk6WrwSdjTc6TZhIEifK/xLm86WIsj2JxVfLEdu4cReFwhDSYS69a/cwJnTQrG3wlR6P3ASJPXjtaPDaimcBiv1bcWirsXxRqBM6jxOHhDPOJtuNo9w1AUORDFYUd9oFu9au71f83d6uf61Z/V7dA0eKHzHK8FfLkGKVTMdU744PkmANr7K5T0Of76htPEEQlXyNu33xNWIZjH5C/C4bDgssoE9ziStbjhMSImYYrGrVVQOsFpHAGde4sI4fVi9m2YVohCpKu4txhkrSrlojaUV5nsCL9+Ktwq995srQcd2S6Jv07B0JRpfN04Ud08d9GFtjh39PQvtnd48v6+p6GdCKx35ORPmQAa4+jwfG9Glb1+Vpy6uaAPVSLAPkCN4iTg7c4A/Ls2XdgKhpzCu9Rh4no1G00j4MjOPx7i4bfw7XYjT6c/bXDswaBgvCKrgnePgaaHP6FQfkkd1UyLinGHUB2wa9luh6ALF1vS4toul5K/JyuCbWvt3t5yvfLXCiEBXuW0oSEz33lLDXT9XxWO8vlqDLoIJtgjadr7pFsjR3lEWkjTDhYxnpHWcQSyHu677nFE6KlEc4KI6znR/gWV0xGzPTJkUINURjnX/79/+yWT9Y+avuhgVXuNWpnqXLPz+9X07XSvf6BLUfApAiK213E6O+g6yvTolwn2A7HVzBT7GuKue6zfp1T+pTSx73Y26qio9r91JZm5lPtrMlH/ZqPo9BUZkagknouPK/IKHNf6el6ca0Vx8vZrxwnMNvaK8lx/pjddP0duFUt6CWhAQ6ughb35XNfkAXf9nMRnH78FcufbnCz+8X0/j2hBpjgOIUolUQtuijIRIMe6GpSqshJuhn5oVCsGqHJjUJcXIULRxR3/uOv+TBO7OOPY+98LIpaEHZRakRaSMnAEEbooq4SktNonJu2qg9ykLyGSfaY+8u9lRZmjb1WLWNGzTRykicK9vRtqadxkZU1fEJ57nezx51u9tTc6bmV7vOarhQZ4sflc9l7JjxKcK/Gj79exjLIPngY+FiKRyjNTk4c/rg3FJEtaQbn/joc+5hBhBTqI2wVNuNSkgXb7Lnb6h7nIygYKWZVhIHNIEjgExfJ8y1XuZPsdMZIWte7hI5wKfWW6Tnz88LFyt09iv+PM1n4bV3plTqkzu2SXXzbzV9cO5aFrrvFMtvek3KYTY4iZ+4jgPO+OFYsY7+pmPvQB+RQTgvuJt8ozuezZwrR0u975j/O/3Guo50wZAiHlAz1KgEnzPQ6CuhYVVqIeqQ4sfnr8yYiuGUctqToxB2Sb6Z6z+6AM6vmd7jgyxDCLIq+cspJzyyHwywMWB7Zs1PNVF6PIlhZQoSPj3AlAi5BALLLAjrmXEYth65KwAUA4VD70MtVLufMhft01ErD+H35Z3kVbBonjAN5CWcAofsJDM1xSI+8p/WyjEBoGnFagbbcdXBv1H10E0/U1a2j4vzHSn1PCmW9+jLc4bqR+dgxyulkLfOYK9xmyxciZTe6aKSuqudpDHfqPrpZvME8c9wRuCE3FhGek0OEiV5rKitrZyjvihhzTn+66HOUbTj6963L4lZSdWckx6RVkXu3DkfEcO0rZ0MiX1XIdShpMh3NAHbJRAkaxDCk/jZ+Y0KM8i9vf5SZRIBxvFvUSwT8Btd7Ax9Lf+iZmRLuvQojjTjOGMd3DAK4cPxw8ZM8IZHF9XcP9WCv3XcU6RW3TgHSHOQ7Pf2U9pZoUgMjApq8nCAWHzZudGOA6q7pot2CBEZdh+/g4lrruhgVlZJiDolUxxRbUS6KTLVqJJmuUc54PuR4uUQWkM+UEQCdFCeEO6qVc6hbehbxIazGarC8TYFV1P0HLDwttXZSp2oRN9bMLUNdOCqET07jxnL0ZA6OnPOrkhGRNxR9c9mr5m249NLucbBOVrTJbpVdqll4ZfKZKZ/ETVr5MKAYK7v/huQVRy4PpnJge0TA0RS6EqrlIKL3bg8ikKi2OwAMOS2jTW8ihKw2DI5SpgxsaFWjHWwmBID5ypOuuFoFTh0zqzqyFpS8ltlISH/JtsXQOwsFCtggPGyN1LYiIo5p4+klKIrpGoP2e2eESXB2HEpM6ukUWZZA9+SdrIipLYxxpLMVdjGRqO5KseV985work1BEoxPMoWuMcEtUWQaEiniKhN4pKUmG5GuXWliO8KiIj7Ie01ouJl5sWLImrLdYm4jY2al5v3dT79cVGremd5rcOCqAAS6I6Rrijy4DUGGNFa8QL7lFxxgVW+2QjXviItwlHYezWaskPkrBseb6rkhbheTgerlpe4jrmdNl63s7ivdZoKOqrM/euu80jLkYBaqr1Aj9lMFlEALumaWU/oqpadueKVLYuQNs5VEh3bT1a0ErUZ8Ms6tnwYo05hf6ZnqMPumFHXUw13leAvjP/myivVz+CYGEUAuF06Obmnp3aeH551CRGnTAmqQqQHmpEQLstH3SIeDBgkGlyqilgx7l6DvRB2SrNt43UE3KRg1xaoucGR500RKYGS0v3gARcT03QJ7ZLNCBIJMXOredC17N13bm1RmnK7TLiK9oqZZRU3ARVUXgl+kmr7pLKsL71Wi2UCvDaO4VNpYWV88EPXJm34H+rRX1XdT7l18o+rCxd+SGY9v0oqQWq5nXK4GnJ6sB8GyibfcG6d14NUZa12jFeGaFfVWYAmWtqy3D0OXYAwvMzyhz3Z1skVXPtO2fA/+4s4b4rkEBpMGmW7Boe69igc+bth59qxS0wVioMtNeZlEq4SOdIEGpAkGkTG1OpQzWDmlgDi4KqZBZzbQ8+/E3UtSA8BYlBbO49L2gZHrARZ54LIWYQcUJ3tBtRCFJ/0kiNuOVUnZEepdZ1HYNGYVxI7+guM0cbwXeq4zd/B8X0SMZz6IrHlwMdho7NcDzBcZDgUj9ZSvwumld+JsHhcAXddJc8xI4Rm/k4HRZB0OkUxwoMkGiCxKclrNJpsVbJK9oJTELVLL5AxPxHHT7ySZTc+e/L8Oofod")).decode("utf-8")
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
