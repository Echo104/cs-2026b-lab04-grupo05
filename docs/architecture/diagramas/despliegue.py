"""Vista de despliegue de VotoEPIS (E6).

Requisitos: pip install diagrams  y  Graphviz instalado en el sistema.
Ejecución:  python despliegue.py   (genera img/despliegue.png)
"""
import os

from diagrams import Cluster, Diagram, Edge
from diagrams.generic.device import Mobile
from diagrams.onprem.client import Users
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.monitoring import Grafana
from diagrams.onprem.network import Internet, Nginx
from diagrams.programming.framework import Django

BASE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(BASE, "img"), exist_ok=True)

graph_attr = {"fontsize": "20", "bgcolor": "white", "pad": "0.3"}

with Diagram(
    "VotoEPIS - Vista de despliegue",
    filename=os.path.join(BASE, "img", "despliegue"),
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    outformat="png",
):
    usuarios = Users("Estudiantes,\ncomité y auditor")
    navegador = Mobile("Navegador\n(celular o laptop)")
    smtp = Internet("Servidor de correo\n(SMTP, servicio externo)")

    with Cluster("Servidor (VPS)"):
        proxy = Nginx("Nginx\n(HTTPS)")
        with Cluster("Monolito modular"):
            app = Django("Django + Gunicorn\n(5 módulos)")
        with Cluster("PostgreSQL (roles distintos)"):
            db_padron = PostgreSQL("esquema padron\n(participación)")
            db_urna = PostgreSQL("esquema urna\n(votos anónimos)")
        mon = Grafana("Monitoreo")

    usuarios >> navegador >> Edge(label="HTTPS") >> proxy >> Edge(label="proxy") >> app
    app >> Edge(label="rol padron_rw") >> db_padron
    app >> Edge(label="rol urna_rw") >> db_urna
    app >> Edge(label="OTP por correo", style="dashed") >> smtp
    app >> Edge(label="métricas", style="dotted") >> mon
